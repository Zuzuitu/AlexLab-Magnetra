#!/usr/bin/env python3
"""Fixed-origin OxTorrent/Torrent9 HTML egress for Magnetra's existing 8798 hub.

This backend is NOT an open proxy: only two statically configured HTTPS
source-owned origins, two exact search templates, and detail paths matching
their validated /torrent/<numeric-id>/<slug> format are reachable. The
existing central gateway authenticates BEFORE invoking this module.
No environment proxy, redirects, retries, token/header forwarding, cookies,
disk cache, .torrent downloads, magnet fetches or sensitive logging.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

USER_AGENT = ("Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36")
MAX_BYTES = 256_000
TIMEOUT = 8
DETAIL_PATH = re.compile(r"^/torrent/[0-9]{1,12}/[a-zA-Z0-9][a-zA-Z0-9._-]{0,180}$")
CONTROL = re.compile(r"[\x00-\x1f\x7f]")
CHALLENGE = (b"just a moment", b"checking your browser",
             b"captcha", b"verify you are human")


@dataclass(frozen=True)
class Source:
    id: str
    origin: str
    search_prefix: str
    search_suffix: str


SOURCES = {
    "oxtorrent": Source("oxtorrent", "https://www.oxtorrent.co",
                       "/recherche/", ""),
    "torrent9": Source("torrent9", "https://www7.torrent9.to",
                       "/search_torrent/", ".html"),
}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def fixed_source_url(provider: str, mode: str, value: str) -> str | None:
    source = SOURCES.get(provider)
    if not source or not isinstance(value, str):
        return None
    if mode == "search":
        if not 2 <= len(value) <= 100 or CONTROL.search(value) or value != value.strip():
            return None
        if "/" in value or "?" in value or "#" in value:
            return None
        encoded = quote(value, safe="")
        if len(encoded) > 320:
            return None
        return source.origin + source.search_prefix + encoded + source.search_suffix
    if mode == "detail" and len(value) <= 210 and DETAIL_PATH.fullmatch(value):
        return source.origin + value
    return None


class HtmlEgress:
    def __init__(self, opener=None):
        self._opener = opener or build_opener(ProxyHandler({}), NoRedirect())

    def fetch(self, provider: str, mode: str, value: str) -> tuple[int, bytes]:
        url = fixed_source_url(provider, mode, value)
        if not url:
            return 400, b""
        req = Request(url, method="GET", headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "identity",
        })
        try:
            with self._opener.open(req, timeout=TIMEOUT) as response:
                if response.status != 200:
                    return 502, b""
                if "text/html" not in (response.headers.get("content-type") or "").lower():
                    return 502, b""
                content_len = response.headers.get("content-length") or "0"
                if not content_len.isdecimal() or int(content_len) > MAX_BYTES:
                    return 502, b""
                body = response.read(MAX_BYTES + 1)
                if len(body) > MAX_BYTES:
                    return 502, b""
                if (response.headers.get("cf-mitigated", "").lower() == "challenge"
                        or any(word in body[:8192].lower() for word in CHALLENGE)):
                    return 403, b""
                return 200, body
        except HTTPError as err:
            try:
                return (err.code if err.code in (401, 403, 429, 504) else 502), b""
            finally:
                err.close()
        except (URLError, TimeoutError, OSError):
            return 504, b""
