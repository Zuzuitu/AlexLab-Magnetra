#!/usr/bin/env python3
"""Read-only diagnostic: one TheRarBg search and at most one deferred resolve.
Never log names, URLs, hash values, magnet links, tokens or raw response bodies.
"""
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://index.alexlab.media"
MAX_BODY = 2_000_000

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def classify(status, data):
    if status == 200:
        magnet = data.get("magnet") if isinstance(data, dict) else None
        return "RESOLVED_MAGNET" if isinstance(magnet, str) and re.match(
            r"^magnet:\?xt=urn:btih:(?:[a-f0-9]{40}|[a-z2-7]{32})(?:&|$)", magnet, re.I
        ) else "RESPONSE_WITHOUT_VALID_MAGNET"
    msg = str(data.get("error", "") if isinstance(data, dict) else "").lower()
    m = re.search(r"provider http (\d{3})", msg)
    if m: return "UPSTREAM_HTTP_" + m.group(1)
    if "details url" in msg or "allowlist" in msg: return "DETAILS_URL_REJECTED"
    if "challenge" in msg or "captcha" in msg or "anti-bot" in msg: return "SOURCE_CHALLENGE"
    if "no supported magnet" in msg: return "DETAIL_HTML_NO_MAGNET_OR_HASH"
    if "too large" in msg: return "SOURCE_RESPONSE_TOO_LARGE"
    if "timeout" in msg or "timed out" in msg: return "FETCH_TIMEOUT"
    if "htmlrewriter" in msg: return "HTML_REWRITER_UNAVAILABLE"
    if "fetch" in msg or "network" in msg: return "NETWORK_FETCH_FAILURE"
    return "OTHER_ERROR"

def valid_detail(url):
    if not isinstance(url, str) or len(url) > 1500: return False
    try:
        p = urllib.parse.urlsplit(url)
        return (p.scheme == "https" and p.netloc == "therarbg.com"
                and p.path.startswith("/post-detail/") and not p.fragment)
    except ValueError:
        return False

def api(path, body=None):
    request = urllib.request.Request(
        BASE + path, data=body, method="POST" if body else "GET",
        headers={"Accept": "application/json", "Cache-Control": "no-store",
                 **({"Content-Type": "application/json"} if body else {})})
    opener = urllib.request.build_opener(NoRedirect)
    try:
        with opener.open(request, timeout=28) as response:
            status, data = response.status, response.read(MAX_BODY + 1)
    except urllib.error.HTTPError as exc:
        status, data = exc.code, exc.read(MAX_BODY + 1)
    if len(data) > MAX_BODY: return status, {"error": "too large"}
    try:
        parsed = json.loads(data)
        return status, parsed if isinstance(parsed, dict) else {}
    except (UnicodeDecodeError, ValueError):
        return status, {}

def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--selftest":
        assert valid_detail("https://therarbg.com/post-detail/9578f4/example/")
        assert not valid_detail("https://therarbg.com.evil.example/post-detail/abc")
        assert not valid_detail("https://other.example/post-detail/abc")
        assert classify(502, {"error": "Provider could not resolve magnet: provider HTTP 403"}) == "UPSTREAM_HTTP_403"
        assert classify(502, {"error": "provider details page contains no supported magnet link"}) == "DETAIL_HTML_NO_MAGNET_OR_HASH"
        assert classify(502, {"error": "provider challenge requires a browser session"}) == "SOURCE_CHALLENGE"
        assert classify(200, {"magnet": "magnet:?xt=urn:btih:" + "a"*40}) == "RESOLVED_MAGNET"
        print("THE_RARBG_OFFLINE_SELFTEST_PASS")
        return
    if len(sys.argv) != 2 or sys.argv[1] != "--approved-readonly":
        raise SystemExit("STOP: explicit manual approval required")
    print("THE_RARBG_DIAGNOSTIC: one source search; at most one resolve")
    try:
        code, found = api("/api/search?q=2026&category=all&providers=therarbag")
        if code != 200:
            print("SEARCH_HTTP_CODE:", code)
            return
        items, errors = found.get("results", []), found.get("errors", [])
        if not isinstance(items, list) or not isinstance(errors, list):
            print("SEARCH_INVALID_RESPONSE")
            return
        print("SEARCH_CARD_COUNT:", len(items))
        print("SEARCH_ERRORS_COUNT:", len(errors))
        if errors:
            for entry in errors[:1]:
                if isinstance(entry, dict):
                    print("SEARCH_ERROR_CLASS:", classify(502, {"error": entry.get("error", "")}))
        choices = [i for i in items if isinstance(i, dict) and i.get("provider") == "therarbag" and valid_detail(i.get("details"))]
        if not choices:
            print("NO_ALLOWED_DETAIL_CARD")
            return
        selected = choices[0]
        print("SOURCE_CARD_HAS_TORRENTFILE:", bool(selected.get("torrentFile")))
        request_body = json.dumps({"provider": "therarbag", "details": selected["details"]}).encode()
        result_code, result = api("/api/resolve", request_body)
        print("RESOLVE_HTTP_CODE:", result_code)
        print("RESOLVE_CLASS:", classify(result_code, result))
    except (OSError, TimeoutError, urllib.error.URLError) as exc:
        print("PUBLIC_API_TRANSPORT_ERROR_TYPE:", type(exc).__name__)

if __name__ == "__main__":
    main()
