#!/usr/bin/env python3
"""One exact owner-approved TheRarBg detail HTML read; sanitized structural counts only.
No redirect, torrent download, hash/magnet, source URL, title or HTML is logged.
GitHub runner HTML does not prove identical Cloudflare Worker HTML.
"""
from __future__ import annotations
import argparse
from html.parser import HTMLParser
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler

MAX_HTML = 3_000_000
TIMEOUT_SECONDS = 11
AGENT = ("Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
         "(KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36")
HEX40 = re.compile(r"^[0-9a-fA-F]{40}$")
LABELLED_HEX = re.compile(r"\bInfo\s*Hash\s*:\s*([a-fA-F0-9]{40})\b", re.I)
MAGNET = re.compile(r"^magnet:\?xt=urn:btih:(?:[0-9a-fA-F]{40}|[A-Z2-7a-z]{32})(?:&|$)", re.I)
CACHE_PATH = re.compile(r"^/torrent/[0-9a-fA-F]{40}\.torrent$")

class DiagnosticStop(Exception):
    """Fixed enum only. Never raise a raw upstream exception."""

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def valid_detail(value: object) -> bool:
    if not isinstance(value, str) or not 20 <= len(value) <= 1500:
        return False
    if any(ord(ch) <= 32 or ord(ch) == 127 for ch in value):
        return False
    try:
        u = urlsplit(value)
        return (u.scheme == "https" and u.netloc == "therarbg.com"
                and bool(re.fullmatch(r"/post-detail/[^?#\\]+", u.path))
                and not u.query and not u.fragment
                and not re.search(r"%(?:2f|5c|00|0a|0d)", u.path, re.I)
                and "//" not in u.path and "/../" not in u.path
                and "/./" not in u.path)
    except ValueError:
        return False

def is_cache_link(value: str) -> bool:
    if not value:
        return False
    try:
        u = urlsplit(value)
        return (u.scheme == "https" and u.netloc == "itorrents.org"
                and bool(CACHE_PATH.fullmatch(u.path))
                and not u.query and not u.fragment)
    except ValueError:
        return False

class DetailShape(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.script_depth = 0
        self.nonvisible_depth = 0
        self.visible_parts = []
        self.magnet_href_count = 0
        self.hash_input_count = 0
        self.clipboard_hash_count = 0
        self.clipboard_magnet_count = 0
        self.inline_js_magnet_markers = 0
        self.cache_link_count = 0
        self.cache_candidate_count = 0
        self.anchor_href = None
        self.anchor_text = []
        self.script_magnet_markers = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag == "script":
            self.script_depth += 1
        if tag in ("style", "noscript", "template"):
            self.nonvisible_depth += 1
        a = dict(attrs)
        if tag == "a":
            self.anchor_href = a.get("href") or ""
            self.anchor_text = []
            if MAGNET.match(self.anchor_href):
                self.magnet_href_count += 1
        if tag == "input" and HEX40.fullmatch((a.get("value") or "").strip()):
            self.hash_input_count += 1
        for attr in ("data-clipboard-text", "data-clipboard", "data-magnet"):
            v = (a.get(attr) or "").strip()
            if HEX40.fullmatch(v):
                self.clipboard_hash_count += 1
            if MAGNET.match(v):
                self.clipboard_magnet_count += 1
        for k, v in attrs:
            if k.startswith("on") and v and "magnet:" in v.lower():
                self.inline_js_magnet_markers += 1

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "a" and self.anchor_href is not None:
            if ".torrent file" == " ".join(" ".join(self.anchor_text).split()).lower():
                self.cache_candidate_count += 1
                if is_cache_link(self.anchor_href):
                    self.cache_link_count += 1
            self.anchor_href = None
            self.anchor_text = []
        if tag == "script":
            self.script_depth = max(0, self.script_depth - 1)
        if tag in ("style", "noscript", "template"):
            self.nonvisible_depth = max(0, self.nonvisible_depth - 1)

    def handle_data(self, data):
        if self.script_depth:
            if "magnet:" in data.lower():
                self.script_magnet_markers += 1
            return
        if self.nonvisible_depth:
            return
        self.visible_parts.append(data)
        if self.anchor_href is not None:
            self.anchor_text.append(data)

    def summary(self) -> dict[str, object]:
        visible = " ".join(" ".join(self.visible_parts).split())
        return {
            "VISIBLE_INFO_HASH_LABEL": bool(re.search(r"\bInfo\s*Hash\s*:", visible, re.I)),
            "LABELLED_VISIBLE_HEX_COUNT": len(LABELLED_HEX.findall(visible)),
            "INPUT_VALUE_HEX_COUNT": self.hash_input_count,
            "CLIPBOARD_HEX_COUNT": self.clipboard_hash_count,
            "CLIPBOARD_MAGNET_COUNT": self.clipboard_magnet_count,
            "MAGNET_HREF_COUNT": self.magnet_href_count,
            "CACHE_ANCHOR_COUNT": self.cache_candidate_count,
            "STRICT_CACHE_URL_COUNT": self.cache_link_count,
            "INLINE_JS_MAGNET_MARKER_COUNT": self.inline_js_magnet_markers,
            "SCRIPT_MAGNET_MARKER_COUNT": self.script_magnet_markers,
        }

def classify_document(html: str) -> str:
    head = html[:2400]
    if re.search(r"<title>\s*(?:Just a moment|Attention Required)|Checking your browser", head, re.I):
        return "POSSIBLE_BROWSER_CHALLENGE"
    return "HTML_RECEIVED"

def inspect_once(url: str) -> dict[str, object]:
    if not valid_detail(url):
        raise DiagnosticStop("DETAIL_URL_REJECTED")
    opener = build_opener(NoRedirect())
    request = Request(url, method="GET", headers={
        "User-Agent": AGENT,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Encoding": "identity",
    })
    try:
        with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
            status = response.status
            headers = response.headers
            limit = headers.get("Content-Length", "")
            if limit.isdecimal() and int(limit) > MAX_HTML:
                raise DiagnosticStop("SOURCE_PAGE_TOO_LARGE")
            content_type = headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
            if content_type not in ("text/html", "application/xhtml+xml"):
                raise DiagnosticStop("SOURCE_NOT_HTML")
            if headers.get("cf-mitigated", "").lower() == "challenge":
                raise DiagnosticStop("SOURCE_CHALLENGE")
            data = response.read(MAX_HTML + 1)
    except HTTPError as exc:
        if 300 <= exc.code < 400:
            raise DiagnosticStop("SOURCE_REDIRECT_REJECTED") from None
        raise DiagnosticStop("SOURCE_HTTP_" + str(exc.code) if exc.code in
                             (400, 401, 403, 404, 429, 500, 502, 503, 504)
                             else "SOURCE_HTTP_OTHER") from None
    except (URLError, TimeoutError, OSError):
        raise DiagnosticStop("SOURCE_NETWORK_OR_TIMEOUT") from None
    if status != 200:
        raise DiagnosticStop("SOURCE_HTTP_OTHER")
    if len(data) > MAX_HTML:
        raise DiagnosticStop("SOURCE_PAGE_TOO_LARGE")
    try:
        html = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        raise DiagnosticStop("SOURCE_ENCODING_UNEXPECTED") from None
    doc_class = classify_document(html)
    if doc_class != "HTML_RECEIVED":
        raise DiagnosticStop(doc_class)
    p = DetailShape()
    p.feed(html)
    return {"RESULT": "SOURCE_HTML_SHAPE_ONLY", "HTTP_STATUS": 200,
            "BYTES": len(data), **p.summary()}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--approved-readonly", action="store_true")
    parser.add_argument("--detail-url", default="")
    args = parser.parse_args()
    if not args.approved_readonly:
        print("DIAGNOSTIC_STOP: OWNER_APPROVAL_REQUIRED")
        return 2
    try:
        output = inspect_once(args.detail_url)
    except DiagnosticStop as exc:
        print("DIAGNOSTIC_STOP:", str(exc))
        return 2
    for key, value in output.items():
        print(key + ":", value)
    return 0

if __name__ == "__main__":
    sys.exit(main())
