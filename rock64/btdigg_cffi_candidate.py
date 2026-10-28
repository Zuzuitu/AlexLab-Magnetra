#!/usr/bin/env python3
"""UNDEPLOYED BTDigg transport candidate; never imported by production gateway.

This module implements ONE fixed-origin source request using an optional,
locally installed curl_cffi. It does not solve challenges, rotate proxies,
retry HTTP 429s, send torrent queries to an arbitrary server, or print content.

The owner obtained a real 200 from Rock64 with curl_cffi, but that says
nothing about sustained availability or whether automated integration is
permitted. Do NOT wire into the gateway without provider terms and the
owner's explicit approval of an opt-in rollout.
"""
from __future__ import annotations

import re

ORIGIN = "https://btdig.com"
SEARCH_URL = ORIGIN + "/search"
MAX_QUERY_CHARS = 180
MAX_RESPONSE_BYTES = 3_000_000
TIMEOUT_SECONDS = 12
QUERY_INVALID = re.compile(r"[\x00-\x1f\x7f]")
CHALLENGE_MARKERS = (b"cf-mitigated", b"just a moment",
                     b"checking your browser", b"attention required")


def fetch_one(query: str, *, client=None) -> tuple[int, bytes]:
    """Return (HTTP-like status, genuine response bytes) for a single request.

    Parameter injection is deliberately restricted to the query text. There
    is no fallback to another hostname, IP, proxy, cookie jar or search.
    `client` is dependency injection for offline tests only.
    """
    if (not isinstance(query, str)
            or not 2 <= len(query.strip()) <= MAX_QUERY_CHARS
            or QUERY_INVALID.search(query)):
        raise ValueError("Invalid BTDigg query")
    if client is None:
        # Deliberately ignore environment-supplied proxies; this candidate
        # must never inherit unrelated Rock64 project network settings.
        from curl_cffi import requests
        with requests.Session(trust_env=False) as session:
            return fetch_one(query, client=session)

    response = None
    try:
        response = client.get(
            SEARCH_URL,
            params={"q": query.strip()},
            impersonate="chrome",
            timeout=TIMEOUT_SECONDS,
            allow_redirects=False,
            stream=True,
        )
        code = getattr(response, "status_code", None)
        if code == 429:
            return 429, b""
        if code in (401, 403) or (isinstance(code, int) and 300 <= code < 400):
            return 503, b""
        if code != 200:
            return 503, b""
        headers = getattr(response, "headers", {})
        if not hasattr(headers, "get"):
            return 502, b""
        try:
            if int(headers.get("content-length", 0) or 0) > MAX_RESPONSE_BYTES:
                return 502, b""
        except (ValueError, TypeError, OverflowError):
            return 502, b""
        if "text/html" not in str(headers.get("content-type", "")).lower():
            return 502, b""
        # Stream bounded chunks; never buffer an untrusted 100MB response
        # before applying the existing 3MB Rock64 gateway limit.
        chunks = []
        total = 0
        for chunk in response.iter_content(chunk_size=65536):
            if not isinstance(chunk, bytes):
                return 502, b""
            total += len(chunk)
            if total > MAX_RESPONSE_BYTES:
                return 502, b""
            chunks.append(chunk)
        body = b"".join(chunks)
        snippet = body[:2400].lower()
        if any(marker in snippet for marker in CHALLENGE_MARKERS):
            return 503, b""
        if not (b"<html" in snippet or b"<!doctype html" in snippet):
            return 502, b""
        return 200, body
    except Exception:
        # Do not emit exception text, URLs, cookies or query fragments.
        return 504, b""
    finally:
        if response is not None:
            try:
                response.close()
            except Exception:
                pass
