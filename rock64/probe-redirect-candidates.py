#!/usr/bin/env python3
"""Read-only candidate canonical-host layout audit for 3 original indexers.

Candidate hostnames are from observed 2026-10-15 Rock64 HTTP 301 responses,
not approved replacements. Exactly one fixed HTTPS GET per hostname, no
redirects followed, no magnets/downloads, no tokens, VPN, DNS or service changes.
HTML hints are NOT validated provider results or working magnet links.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

UA = ("Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36")
MAX_BYTES = 256_000
TIMEOUT = 8

@dataclass(frozen=True)
class Candidate:
    source: str
    url: str
    marker: str

# This is a read-only allowlist of newly observed hosts.
CANDIDATES = (
    Candidate("oxtorrent", "https://www.oxtorrent.co/recherche/ubuntu", "table"),
    Candidate("torrent9", "https://www7.torrent9.to/search_torrent/ubuntu.html", "table"),
    Candidate("bitsearch", "https://bitsearch.eu/search?q=ubuntu&page=1&sortBy=seeders", "space-y-4"),
)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class LayoutHints(HTMLParser):
    """HTML structure counts only; never collects names, href URLs or torrents."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables = 0
        self.table_rows = 0
        self.bitsearch_wrappers = 0
        self.magnet_anchors = 0

    def handle_starttag(self, tag, attrs):
        info = dict(attrs)
        if tag == "table":
            self.tables += 1
        if tag == "tr":
            self.table_rows += 1
        if "space-y-4" in (info.get("class") or "").split():
            self.bitsearch_wrappers += 1
        if tag == "a" and (info.get("href") or "").startswith("magnet:?xt=urn:btih:"):
            self.magnet_anchors += 1


def categorize_redirect(source, location):
    """Never fetch redirect destinations; return no paths or raw URLs."""
    if not location:
        return {"redirect": "MISSING_LOCATION"}
    try:
        base = urlsplit(source)
        dest = urlsplit(urljoin(source, location))
        if (dest.scheme != "https" or not dest.hostname or
            dest.username or dest.password or dest.fragment or
            dest.port not in (None, 443)):
            return {"redirect": "UNSAFE"}
        return {"redirect": "SAME_ORIGIN" if dest.netloc == base.netloc else "OFF_ORIGIN",
                "redirect_host": dest.hostname[:120]}
    except (TypeError, ValueError):
        return {"redirect": "INVALID"}


def describe_body(source, headers, body, truncated=False):
    if truncated:
        return {"classification": "HTML_TOO_LARGE_TO_VERIFY"}
    if "text/html" not in (headers.get("content-type") or "").lower():
        return {"classification": "NON_HTML"}
    first = body[:8192].lower()
    if (headers.get("cf-mitigated", "").lower() == "challenge" or
        any(s in first for s in (b"just a moment", b"captcha",
                                 b"checking your browser", b"verify you are human"))):
        return {"classification": "CHALLENGE"}
    hints = LayoutHints()
    try:
        hints.feed(body.decode("utf-8", errors="replace"))
        hints.close()
    except (ValueError, AssertionError):
        return {"classification": "INVALID_HTML"}
    marker = (hints.tables > 0 and hints.table_rows > 0) if source.marker == "table" else hints.bitsearch_wrappers > 0
    return {"classification": "LAYOUT_HINT_ONLY" if marker else "LAYOUT_NOT_CONFIRMED",
            "table_rows_seen": hints.table_rows if source.marker == "table" else None,
            "wrapper_elements_seen": hints.bitsearch_wrappers if source.marker != "table" else None,
            "magnet_anchors_seen": hints.magnet_anchors,
            "warning": "Do not interpret layout markers as genuine torrent rows"}


def check(candidate, opener=None):
    if candidate not in CANDIDATES:
        raise ValueError("Refusing arbitrary destination URL")
    opener = opener or build_opener(ProxyHandler({}), NoRedirect())
    headers = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml",
               "Accept-Encoding": "identity"}
    req = Request(candidate.url, method="GET", headers=headers)
    try:
        with opener.open(req, timeout=TIMEOUT) as res:
            body = res.read(MAX_BYTES + 1)
            return {"source": candidate.source, "http": res.status,
                    **describe_body(candidate, res.headers, body,
                                    truncated=len(body) > MAX_BYTES)}
    except HTTPError as e:
        try:
            result = {"source": candidate.source, "http": e.code}
            if e.code in (301, 302, 303, 307, 308):
                result.update(categorize_redirect(candidate.url, e.headers.get("location")))
            elif e.code in (403, 401):
                result["classification"] = "ACCESS_DENIED"
            elif e.code == 429:
                result["classification"] = "RATE_LIMIT"
            else:
                result["classification"] = "HTTP_ERROR"
            return result
        finally:
            e.close()
    except (URLError, OSError, TimeoutError):
        return {"source": candidate.source, "http": None,
                "classification": "NETWORK_OR_TIMEOUT"}


def main():
    print(json.dumps({"probe": "redirect-candidate-layout",
                      "candidate_hosts": 3, "allowlist_only": True,
                      "redirection_followed": False}))
    for candidate in CANDIDATES:
        print(json.dumps(check(candidate)))
    print(json.dumps({"done": True, "no_system_changes": True}))


if __name__ == "__main__":
    main()
