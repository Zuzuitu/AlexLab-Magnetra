#!/usr/bin/env python3
"""Read-only fixed search->details verification for OxTorrent and Torrent9.

Max 4 source-owned HTTPS GETs (2 search, <=2 details). No redirects, proxy,
secrets, raw HTML, titles, hashes, magnet values or .torrent downloads.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

TIMEOUT = 8
MAX_BYTES = 256_000
UA = ("Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36")
MAGNET = re.compile(r"^magnet:\?xt=urn:btih:(?:[a-f0-9]{40}|[a-z2-7]{32})(?:&|$)", re.I)
CHALLENGE = (b"just a moment", b"checking your browser", b"captcha",
             b"verify you are human")


@dataclass(frozen=True)
class Source:
    provider: str
    url: str
    columns: int
    magnet_parent: str


SOURCES = (
    Source("oxtorrent", "https://www.oxtorrent.co/recherche/ubuntu", 4, "btn-magnet"),
    Source("torrent9", "https://www7.torrent9.to/search_torrent/ubuntu.html", 5, ""),
)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def no_proxy_opener():
    return build_opener(ProxyHandler({}), NoRedirect())


def safe_detail(source, raw):
    if not isinstance(raw, str) or not raw or len(raw) > 800:
        return None
    try:
        origin = urlsplit(source.url)
        target = urlsplit(urljoin(source.url, raw))
        if (target.scheme != "https" or target.netloc != origin.netloc
                or target.username or target.password or target.query or target.fragment
                or target.path in ("", "/", origin.path)
                or target.path.startswith("/recherche/")
                or target.path.startswith("/search_torrent/")):
            return None
        return target.geturl()
    except (TypeError, ValueError):
        return None


class SearchRows(HTMLParser):
    """Original Android first-column link in table/tbody/tr with 4 or 5 td."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.rows = []
        self.current = None
        self.first = False
        self.anchor = None

    def handle_starttag(self, tag, attrs):
        parent = self.stack[-1] if self.stack else None
        if tag == "tr" and parent == "tbody" and len(self.rows) < 200:
            self.current = {"cols": 0, "links": []}
        elif tag == "td" and parent == "tr" and self.current is not None:
            self.current["cols"] += 1
            self.first = self.current["cols"] == 1
        elif tag == "a" and self.first and self.current is not None:
            self.anchor = {"href": dict(attrs).get("href"), "name": []}
        self.stack.append(tag)

    def handle_data(self, text):
        if self.anchor is not None:
            self.anchor["name"].append(text)

    def handle_endtag(self, tag):
        if tag == "a" and self.anchor is not None and self.current is not None:
            self.current["links"].append({
                "href": self.anchor["href"],
                "name": " ".join("".join(self.anchor["name"]).split())
            })
            self.anchor = None
        if tag == "td":
            self.first = False
        if tag == "tr" and self.current is not None:
            self.rows.append(self.current)
            self.current = None
            self.first = False
        if tag in self.stack:
            while self.stack:
                if self.stack.pop() == tag:
                    break


class MagnetAnchors(HTMLParser):
    def __init__(self, magnet_parent):
        super().__init__(convert_charrefs=True)
        self.parent = magnet_parent
        self.div_depth = 0
        self.count = 0

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "div":
            if self.div_depth:
                self.div_depth += 1
            elif self.parent and self.parent in (values.get("class") or "").split():
                self.div_depth = 1
        if tag == "a" and (not self.parent or self.div_depth):
            href = values.get("href") or ""
            if len(href) <= 12000 and MAGNET.match(href):
                self.count += 1

    def handle_endtag(self, tag):
        if tag == "div" and self.div_depth:
            self.div_depth -= 1


def html_get(url, opener):
    req = Request(url, method="GET", headers={
        "User-Agent": UA, "Accept": "text/html,application/xhtml+xml",
        "Accept-Encoding": "identity"
    })
    try:
        with opener.open(req, timeout=TIMEOUT) as res:
            if res.status != 200:
                return {"http": res.status, "state": "HTTP_ERROR"}, None
            if "text/html" not in (res.headers.get("content-type") or "").lower():
                return {"http": 200, "state": "NON_HTML"}, None
            if int(res.headers.get("content-length") or 0) > MAX_BYTES:
                return {"http": 200, "state": "BODY_TOO_LARGE"}, None
            data = res.read(MAX_BYTES + 1)
            if len(data) > MAX_BYTES:
                return {"http": 200, "state": "BODY_TOO_LARGE"}, None
            if (res.headers.get("cf-mitigated", "").lower() == "challenge"
                    or any(x in data[:8192].lower() for x in CHALLENGE)):
                return {"http": 200, "state": "CHALLENGE"}, None
            return {"http": 200, "state": "HTML_ACCEPTED"}, data
    except HTTPError as err:
        status = err.code
        err.close()
        return {"http": status, "state": "HTTP_ERROR"}, None
    except (URLError, OSError, TimeoutError):
        return {"http": None, "state": "TRANSPORT_OR_TIMEOUT"}, None


def inspect(source, opener=None):
    if source not in SOURCES:
        raise ValueError("Only the two audited source-owned candidates allowed")
    transport = opener or no_proxy_opener()
    search, page = html_get(source.url, transport)
    outcome = {"provider": source.provider, "search": search,
               "rows": 0, "query_matched_rows": 0, "safe_details_candidates": 0,
               "details_fetched": False, "details": None,
               "well_formed_magnet_in_details": False}
    if page is None:
        return outcome
    try:
        rows = SearchRows()
        rows.feed(page.decode("utf-8", errors="replace"))
        rows.close()
    except (AssertionError, ValueError):
        search["state"] = "HTML_PARSE_ERROR"
        return outcome
    outcome["rows"] = len(rows.rows)
    targets = []
    for row in rows.rows:
        if row["cols"] < source.columns:
            continue
        for link in row["links"]:
            if "ubuntu" not in link["name"].casefold():
                continue
            outcome["query_matched_rows"] += 1
            target = safe_detail(source, link["href"])
            if target:
                targets.append(target)
            break
    outcome["safe_details_candidates"] = len(targets)
    if not targets:
        search["state"] = "NO_VERIFIED_DETAIL_CANDIDATE"
        return outcome
    details, data = html_get(targets[0], transport)
    outcome["details_fetched"] = True
    outcome["details"] = details
    if data is None:
        return outcome
    try:
        matcher = MagnetAnchors(source.magnet_parent)
        matcher.feed(data.decode("utf-8", errors="replace"))
        matcher.close()
    except (AssertionError, ValueError):
        details["state"] = "HTML_PARSE_ERROR"
        return outcome
    outcome["well_formed_magnet_in_details"] = matcher.count > 0
    details["state"] = ("MAGNET_ANCHOR_FORMAT_FOUND" if matcher.count
                        else "MAGNET_ANCHOR_NOT_FOUND")
    return outcome


def main():
    print(json.dumps({"probe": "fixed-source-search-details",
                      "sources": len(SOURCES), "maximum_gets": 4,
                      "redirects_followed": False, "magnet_downloads": 0,
                      "note": "Anchor format is not proof of successful download"}))
    for source in SOURCES:
        print(json.dumps(inspect(source), separators=(",", ":")))
    print(json.dumps({"done": True, "no_changes": True}))


if __name__ == "__main__":
    main()
