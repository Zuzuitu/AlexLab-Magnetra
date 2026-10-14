#!/usr/bin/env python3
"""Read-only Rock64 egress comparison for original Magnetra HTML indexers.

Only fixed, source-owned HTTPS search URLs (benign 'ubuntu'); no arbitrary URL,
private credentials, torrent downloads, magnet links, HTML bodies or VPN usage.
This probe is NOT a proxy and cannot prove magnets/details resolve.
"""
from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

UA = ("Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36")
MAX_PREVIEW = 128 * 1024
TIMEOUT = 8

@dataclass(frozen=True)
class Source:
    provider: str
    url: str
    signature: bytes


# Exact official adapter endpoints in worker/src/legacy-specs.mjs. Strings are
# hardcoded to preclude caller-supplied targets or redirect-based SSRF.
PRIORITY = (
    Source("torrentz", "https://torrentz2.nz/search?q=ubuntu", b"div class=\"results"),
    Source("uindex", "https://uindex.org/search.php?search=ubuntu&c=0", b"sr-table"),
    Source("1337x", "https://1337x.to/search/ubuntu/1/", b"table-list"),
    Source("bt4g", "https://bt4gprx.com/search?q=ubuntu&category=all&orderby=seeders&p=1", b"notion-list-item"),
    Source("extdotto", "https://ext.to/browse/?q=ubuntu", b"search-table"),
)
EXTENDED = (
    Source("oxtorrent", "https://oxtorrent.co/recherche/ubuntu", b"<table"),
    Source("torrent9", "https://www6.torrent9.to/search_torrent/ubuntu.html", b"<table"),
    Source("torrentdatabase", "https://developify.ca/search?q=ubuntu", b"torrent-table"),
    Source("torrentdownloads", "https://torrentdownloads.pro/search/?s_cat=0&search=ubuntu", b"grey_bar3"),
    Source("tokyotoshokan", "https://tokyotosho.info/search.php?terms=ubuntu&type=0&searchName=true", b"listing"),
    Source("bitsearch", "https://bitsearch.to/search?q=ubuntu&page=1&sortBy=seeders", b"space-y-4"),
)

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def classify(status, headers, body, signature):
    if status in (301, 302, 303, 307, 308):
        return "REDIRECT_NOT_FOLLOWED"
    if status in (401, 403):
        return "ACCESS_DENIED"
    if status == 429:
        return "RATE_LIMIT"
    if status != 200:
        return "HTTP_ERROR"
    content_type = (headers.get("content-type") or "").lower()
    first = body[:8192].lower()
    if (headers.get("cf-mitigated", "").lower() == "challenge" or
        any(m in first for m in (b"just a moment", b"checking your browser",
                                 b"captcha", b"verify you are human"))):
        return "CHALLENGE"
    if "text/html" not in content_type:
        return "UNEXPECTED_CONTENT_TYPE"
    if signature.lower() in body.lower():
        return "HTML_SIGNATURE_FOUND_NOT_YET_PARSED"
    return "HTTP_200_LAYOUT_UNVERIFIED"


def check(source, opener=None, clock=time.monotonic):
    assert source in PRIORITY + EXTENDED, "Only fixed original source URLs"
    opener = opener or build_opener(ProxyHandler({}), NoRedirect())
    started = clock()
    request = Request(source.url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Encoding": "identity",
        "Accept-Language": "en-US,en;q=0.9",
    }, method="GET")
    try:
        with opener.open(request, timeout=TIMEOUT) as response:
            body = response.read(MAX_PREVIEW + 1)
            status = response.status
            headers = response.headers
        label = classify(status, headers, body, source.signature)
        if len(body) > MAX_PREVIEW:
            label = "HTML_TOO_LARGE_TO_CLASSIFY"
    except HTTPError as exc:
        status = exc.code
        label = classify(status, exc.headers, b"", source.signature)
        exc.close()
    except (URLError, OSError, TimeoutError):
        status = None
        label = "NETWORK_OR_TIMEOUT"
    return {
        "provider": source.provider,
        "http": status,
        "classification": label,
        "elapsed_s": round(clock() - started, 2),
    }


def main():
    parser = argparse.ArgumentParser(description="Read-only fixed-origin Magnetra provider diagnostics")
    parser.add_argument("--extended", action="store_true",
                        help="Also check six more previously failing HTML indexers once")
    args = parser.parse_args()
    selected = PRIORITY + (EXTENDED if args.extended else ())
    print(json.dumps({"scope": "residential-HTML-readonly",
                      "sources_checked": len(selected),
                      "query": "ubuntu",
                      "warning": "HTML signature is NOT proof that rows or magnets work"}))
    for source in selected:
        print(json.dumps(check(source), separators=(",", ":")))
    print(json.dumps({"complete": True, "no_services_or_network_changed": True}))


if __name__ == "__main__":
    main()
