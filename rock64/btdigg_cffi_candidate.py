#!/usr/bin/env python3
"""BTDigg fixed-origin curl_cffi transport with privacy-safe outcome diagnostics.

One owner-authorized source request per cache miss. No redirects, retries,
proxy inheritance, source challenge solutions or query/magnet logging.
The original (status, bytes) contract and 12s/3MB limits stay unchanged.

Diagnostics distinguish known libcurl errors. libcurl code 28 alone cannot
identify DNS vs TCP vs TLS vs response headers, so it is explicitly marked
unresolved when headers have not arrived. No invented per-phase timings.
"""
from __future__ import annotations

import json
import re
import time

ORIGIN = "https://btdig.com"
SEARCH_URL = ORIGIN + "/search"
MAX_QUERY_CHARS = 180
MAX_RESPONSE_BYTES = 3_000_000
TIMEOUT_SECONDS = 12
QUERY_INVALID = re.compile(r"[\x00-\x1f\x7f]")
CHALLENGE_MARKERS = (b"cf-mitigated", b"just a moment",
                     b"checking your browser", b"attention required")

# Only documented curl return codes. 28 is a combined timeout, NOT proof
# that TCP (or any specific earlier hop) failed.
CURL_FAILURES = {
    6: "dns_resolution_failed",
    7: "connect_failed",
    28: "request_timeout",
    35: "tls_handshake_failed",
    51: "tls_peer_verification_failed",
    52: "empty_response",
    55: "send_failed",
    56: "receive_failed",
    60: "tls_certificate_failed",
}


def _safe_failure(exc, phase):
    # Do NOT log str(exc), repr(exc), args or traceback. libcurl errors can
    # contain the full query URL, IPs, cookies, or diagnostic TLS messages.
    code = getattr(exc, "code", None)
    if type(code) is not int:
        code = getattr(exc, "curl_code", None)
    if type(code) is not int or code not in CURL_FAILURES:
        code = None
    if code == 28 or (code is None and isinstance(exc, TimeoutError)):
        failure = ("body_timeout" if phase == "body"
                   else "pre_headers_timeout_unresolved")
    elif code is not None:
        failure = CURL_FAILURES[code]
    elif phase == "body":
        failure = "body_transfer_failed_unclassified"
    else:
        failure = "pre_headers_failed_unclassified"
    return failure, code


def _journal(record):
    print(json.dumps(record, sort_keys=True, separators=(",", ":")), flush=True)


def fetch_one(query: str, *, client=None, report=None) -> tuple[int, bytes]:
    """One fixed-origin request and a non-sensitive summary of its outcome.

    report is dependency injection for offline tests. Production defaults to
    one JSON record in the service journal for each *real uncached fetch*;
    cache hits and local rate-limit responses make no new fetch and no record.
    """
    if (not isinstance(query, str)
            or not 2 <= len(query.strip()) <= MAX_QUERY_CHARS
            or QUERY_INVALID.search(query)):
        raise ValueError("Invalid BTDigg query")
    if client is None:
        # Ignore environment proxies, preserve TLS validation and source URL.
        from curl_cffi import requests
        with requests.Session(trust_env=False) as session:
            return fetch_one(query, client=session,
                             report=_journal if report is None else report)

    start = time.monotonic()
    response = None
    phase = "pre_headers"
    failure = "pre_headers_failed_unclassified"
    curl_code = None
    upstream_status = None
    result_status = 504

    try:
        response = client.get(
            SEARCH_URL,
            params={"q": query.strip()},
            impersonate="chrome",
            timeout=TIMEOUT_SECONDS,
            allow_redirects=False,
            stream=True,
        )
        phase = "body"
        value = getattr(response, "status_code", None)
        upstream_status = value if type(value) is int and 100 <= value <= 599 else None

        if upstream_status == 429:
            result_status, failure = 429, "http_429"
            return 429, b""
        if upstream_status in (401, 403) or (
            upstream_status is not None and 300 <= upstream_status < 400
        ):
            result_status, failure = 503, "source_rejected_or_redirected"
            return 503, b""
        if upstream_status != 200:
            result_status, failure = 503, "source_non_200"
            return 503, b""

        headers = getattr(response, "headers", {})
        if not hasattr(headers, "get"):
            result_status, failure = 502, "invalid_headers"
            return 502, b""
        try:
            if int(headers.get("content-length", 0) or 0) > MAX_RESPONSE_BYTES:
                result_status, failure = 502, "oversize_headers"
                return 502, b""
        except (ValueError, TypeError, OverflowError):
            result_status, failure = 502, "invalid_content_length"
            return 502, b""
        if "text/html" not in str(headers.get("content-type", "")).lower():
            result_status, failure = 502, "non_html_content"
            return 502, b""

        chunks = []
        total = 0
        for chunk in response.iter_content(chunk_size=65536):
            if not isinstance(chunk, bytes):
                result_status, failure = 502, "invalid_body_chunk"
                return 502, b""
            total += len(chunk)
            if total > MAX_RESPONSE_BYTES:
                result_status, failure = 502, "oversize_body"
                return 502, b""
            chunks.append(chunk)
        body = b"".join(chunks)
        snippet = body[:2400].lower()
        if any(marker in snippet for marker in CHALLENGE_MARKERS):
            result_status, failure = 503, "source_challenge"
            return 503, b""
        if not (b"<html" in snippet or b"<!doctype html" in snippet):
            result_status, failure = 502, "invalid_html"
            return 502, b""
        result_status, failure = 200, "none"
        return 200, body
    except Exception as exc:
        failure, curl_code = _safe_failure(exc, phase)
        result_status = 504
        return 504, b""
    finally:
        if response is not None:
            try:
                response.close()
            except Exception:
                pass
        if report is not None:
            # Never emit search terms, URL paths, magnets, names, exceptions,
            # IPs or credentials. A logging failure must not affect search.
            record = {
                "event": "btdigg_cffi_transport",
                "duration_ms": round((time.monotonic() - start) * 1000),
                "phase": phase,
                "failure": failure,
                "gateway_status": result_status,
                "source_status": upstream_status,
                "curl_code": curl_code,
            }
            try:
                report(record)
            except Exception:
                pass
