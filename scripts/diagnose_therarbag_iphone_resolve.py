#!/usr/bin/env python3
"""One user-approved, read-only TheRarBg production search and at most one resolve.

Never log torrent names, item IDs, URLs, BTIH hashes, magnet links, raw bodies
or credentials. A preliminary HTTP block/incomplete diagnostic is a FAILURE
of the diagnostic job (not a passing resolution).
"""
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Callable

BASE = "https://index.alexlab.media"
MAX_BODY = 2_000_000
USER_AGENT = "AlexLab-Magnetra-ReadOnlyResolveDiagnostic/2.0"


class DiagnosticStop(Exception):
    """An intentionally sanitized diagnostic failure."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


@dataclass(frozen=True)
class ApiResponse:
    status: int
    content_type: str
    cf_mitigated: str
    cf_ray: str
    payload: dict

    @property
    def is_json(self) -> bool:
        return "application/json" in self.content_type.lower()


def classify(status: int, data: dict) -> str:
    """Finite categories only: no raw upstream error text is emitted."""
    if status == 200:
        magnet = data.get("magnet") if isinstance(data, dict) else None
        return ("RESOLVED_MAGNET" if isinstance(magnet, str)
                and len(magnet) <= 12000
                and re.match(
                    r"^magnet:\?xt=urn:btih:(?:[a-f0-9]{40}|[a-z2-7]{32})(?:&|$)",
                    magnet, re.I,
                ) else "RESPONSE_WITHOUT_VALID_MAGNET")
    msg = str(data.get("error", "") if isinstance(data, dict) else "").lower()
    upstream = re.search(r"provider http (\d{3})", msg)
    if upstream:
        return "UPSTREAM_HTTP_" + upstream.group(1)
    if "details url" in msg or "allowlist" in msg:
        return "DETAILS_URL_REJECTED"
    if "challenge" in msg or "captcha" in msg or "anti-bot" in msg:
        return "SOURCE_CHALLENGE"
    if "no supported magnet" in msg:
        return "DETAIL_HTML_NO_MAGNET_OR_HASH"
    if "too large" in msg:
        return "SOURCE_RESPONSE_TOO_LARGE"
    if "timeout" in msg or "timed out" in msg:
        return "FETCH_TIMEOUT"
    if "htmlrewriter" in msg:
        return "HTML_REWRITER_UNAVAILABLE"
    if "fetch" in msg or "network" in msg:
        return "NETWORK_FETCH_FAILURE"
    return "OTHER_ERROR"


def valid_detail(url: object) -> bool:
    if not isinstance(url, str) or len(url) > 1500:
        return False
    try:
        parsed = urllib.parse.urlsplit(url)
        return (parsed.scheme == "https" and parsed.netloc == "therarbg.com"
                and parsed.path.startswith("/post-detail/")
                and len(parsed.path) > len("/post-detail/")
                and not parsed.query and not parsed.fragment)
    except ValueError:
        return False


def sanitized_ray(value: str) -> str:
    """Ray IDs are correlation IDs, not source IDs, filenames or user data."""
    return value if re.fullmatch(r"[0-9a-fA-F]{12,24}(?:-[A-Za-z]{3})?", value) else "NOT_AVAILABLE"


def api(path: str, body: bytes | None = None) -> ApiResponse:
    if not (path.startswith("/api/") and "//" not in path):
        raise DiagnosticStop("API_PATH_NOT_ALLOWED")
    if body is not None and len(body) > 600:
        raise DiagnosticStop("API_REQUEST_TOO_LARGE")
    req = urllib.request.Request(
        BASE + path, data=body, method="POST" if body is not None else "GET",
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "Accept-Encoding": "identity",
            "Cache-Control": "no-store",
            **({"Origin": BASE, "Content-Type": "application/json"}
               if body is not None else {}),
        },
    )
    opener = urllib.request.build_opener(NoRedirect)
    try:
        with opener.open(req, timeout=28) as response:
            status, headers = response.status, response.headers
            data = response.read(MAX_BODY + 1)
    except urllib.error.HTTPError as exc:
        status, headers = exc.code, exc.headers
        data = exc.read(MAX_BODY + 1)
    except (OSError, TimeoutError, urllib.error.URLError):
        raise DiagnosticStop("PUBLIC_API_TRANSPORT_UNVERIFIED") from None
    if len(data) > MAX_BODY:
        raise DiagnosticStop("PUBLIC_API_RESPONSE_TOO_LARGE")
    content_type = headers.get("content-type", "") if headers else ""
    mitigated = headers.get("cf-mitigated", "") if headers else ""
    ray = headers.get("cf-ray", "") if headers else ""
    payload = {}
    if "application/json" in content_type.lower():
        try:
            obj = json.loads(data)
            if isinstance(obj, dict):
                payload = obj
        except (ValueError, UnicodeDecodeError):
            pass
    return ApiResponse(status, content_type, mitigated, ray, payload)


def response_class(response: ApiResponse) -> str:
    if response.status == 403:
        if not response.is_json or response.cf_mitigated.lower() == "challenge":
            return "HTTP_403_NON_JSON_EDGE_OR_CHALLENGE"
        if response.payload.get("error") == "Cross-origin submission not permitted.":
            return "HTTP_403_WORKER_ORIGIN_REJECTED"
        return "HTTP_403_JSON_UNEXPECTED"
    return "HTTP_" + str(response.status) + (
        "_JSON" if response.is_json else "_NON_JSON"
    )


def print_metadata(stage: str, response: ApiResponse) -> None:
    print(stage + "_HTTP_STATUS:", response.status)
    print(stage + "_RESPONSE_TYPE:", "JSON" if response.is_json else "NON_JSON")
    print(stage + "_CF_MITIGATED:", "CHALLENGE" if response.cf_mitigated.lower() == "challenge" else "NOT_INDICATED")
    print(stage + "_CF_RAY:", sanitized_ray(response.cf_ray))


def run_diagnostic(fetch: Callable = api) -> str:
    """Read-only state machine. Only a tested resolver attempt can finish it."""
    print("THE_RARBG_DIAGNOSTIC: one source search; at most one resolve")
    result = fetch("/api/search?q=2026&category=all&providers=therarbag")
    print_metadata("SEARCH", result)
    if result.status != 200 or not result.is_json:
        print("SEARCH_BLOCK_CLASS:", response_class(result))
        # A single harmless same-origin health check distinguishes a blocked
        # search endpoint from a host-wide/runner-wide block. No indexer fetch.
        try:
            health = fetch("/api/health")
            print_metadata("HEALTH_COMPARISON", health)
            print("HEALTH_COMPARISON_CLASS:", response_class(health))
        except DiagnosticStop as exc:
            print("HEALTH_COMPARISON_CLASS:", str(exc))
        raise DiagnosticStop("SEARCH_BLOCKED_BEFORE_RESOLVE")
    if not isinstance(result.payload.get("results"), list) or not isinstance(result.payload.get("errors"), list):
        raise DiagnosticStop("SEARCH_RESPONSE_SCHEMA_INVALID")
    items, errors = result.payload["results"], result.payload["errors"]
    if len(items) > 100 or len(errors) > 46:
        raise DiagnosticStop("SEARCH_RESPONSE_LIMIT_INVALID")
    print("SEARCH_CARD_COUNT:", len(items))
    print("SEARCH_ERRORS_COUNT:", len(errors))
    if errors:
        first_error = next((e for e in errors if isinstance(e, dict) and e.get("provider") == "therarbag"), None)
        if first_error is not None:
            print("SOURCE_SEARCH_ERROR_CLASS:", classify(502, {"error": first_error.get("error", "")}))
    choices = [item for item in items
               if isinstance(item, dict) and item.get("provider") == "therarbag"
               and not item.get("magnet") and valid_detail(item.get("details"))]
    if not choices:
        raise DiagnosticStop("NO_ELIGIBLE_UNRESOLVED_SOURCE_CARD")
    selected = choices[0]
    print("SOURCE_CARD_TORRENTFILE_PRESENT:", bool(selected.get("torrentFile")))
    body = json.dumps(
        {"provider": "therarbag", "details": selected["details"]},
        separators=(",", ":"),
    ).encode("utf8")
    result = fetch("/api/resolve", body)
    print_metadata("RESOLVE", result)
    if not result.is_json:
        print("RESOLVE_BLOCK_CLASS:", response_class(result))
        raise DiagnosticStop("RESOLVE_RESPONSE_NOT_JSON")
    category = classify(result.status, result.payload)
    print("RESOLVE_CLASS:", category)
    if result.status == 200 and category == "RESOLVED_MAGNET":
        return "RESOLVER_E2E_PASS"
    if category == "OTHER_ERROR" or category == "RESPONSE_WITHOUT_VALID_MAGNET":
        raise DiagnosticStop("RESOLVE_FAILURE_UNCLASSIFIED")
    if category == "RESOLVED_MAGNET":
        raise DiagnosticStop("RESOLVE_UNEXPECTED_HTTP_STATUS")
    return "RESOLVE_FAILURE_CLASSIFIED_" + category


def selftest() -> None:
    assert valid_detail("https://therarbg.com/post-detail/9578f4/example/")
    assert not valid_detail("https://therarbg.com.evil.example/post-detail/abc")
    assert not valid_detail("https://therarbg.com/post-detail/a?redirect=1")
    assert classify(502, {"error": "provider HTTP 403"}) == "UPSTREAM_HTTP_403"
    assert classify(502, {"error": "details page contains no supported magnet link"}) == "DETAIL_HTML_NO_MAGNET_OR_HASH"
    assert classify(502, {"error": "provider challenge requires a browser session"}) == "SOURCE_CHALLENGE"
    assert classify(200, {"magnet": "magnet:?xt=urn:btih:" + "a" * 40}) == "RESOLVED_MAGNET"
    assert response_class(ApiResponse(403, "text/html", "challenge", "1234567890abcdef-LHR", {})) == "HTTP_403_NON_JSON_EDGE_OR_CHALLENGE"
    print("THE_RARBG_OFFLINE_SELFTEST_PASS")


def main() -> int:
    if len(sys.argv) == 2 and sys.argv[1] == "--selftest":
        selftest()
        return 0
    if len(sys.argv) != 2 or sys.argv[1] != "--approved-readonly":
        print("DIAGNOSTIC_STOP: MANUAL_APPROVAL_REQUIRED")
        return 2
    try:
        result = run_diagnostic()
    except DiagnosticStop as exc:
        print("DIAGNOSTIC_STOP:", str(exc))
        return 2
    print("DIAGNOSTIC_COMPLETED:", result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
