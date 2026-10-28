#!/usr/bin/env python3
"""One-request BTDigg candidate diagnostic; NOT a production integration.

Run only after an owner-authorized BTDigg connectivity test. Never prints
filenames, search terms, magnets, hashes, IP addresses, cookies or credentials.
"""
from __future__ import annotations
from html.parser import HTMLParser
import re

from btdigg_cffi_candidate import fetch_one

# A known owner-supplied release filename, not a user-selectable endpoint.
EXACT = "The.Dog.Stars.2026.1080p.10bit.WEBRip.6CH.x265.HEVC-PSA"
_BTih = re.compile(r"^magnet:\?xt=urn:btih:(?:[a-f0-9]{40}|[a-z2-7]{32})(?:&|$)", re.I)


def _tokens(value):
    return set(re.findall(r"[a-z0-9]+", value.lower()))


class BTDiggRows(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.div_depth = 0
        self.row_depth = None
        self.name_depth = None
        self.name_link = False
        self.size_depth = None
        self.size_open = False
        self.title = []
        self.size = []
        self.has_valid_magnet = False
        self.valid_rows = 0
        self.exact_rows = 0

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = set((attributes.get("class") or "").split())
        if tag == "div":
            self.div_depth += 1
            if "one_result" in classes and self.row_depth is None:
                self.row_depth = self.div_depth
                self.title = []
                self.size = []
                self.has_valid_magnet = False
            elif self.row_depth is not None and "torrent_name" in classes:
                self.name_depth = self.div_depth
        if self.row_depth is None:
            return
        if tag == "a":
            if _BTih.match(attributes.get("href") or ""):
                self.has_valid_magnet = True
            if self.name_depth is not None:
                self.name_link = True
        if tag == "span" and "torrent_size" in classes:
            self.size_open = True

    def handle_data(self, data):
        if self.row_depth is None:
            return
        if self.name_link:
            self.title.append(data)
        if self.size_open:
            self.size.append(data)

    def handle_endtag(self, tag):
        if tag == "a":
            self.name_link = False
        elif tag == "span":
            self.size_open = False
        elif tag == "div":
            if self.row_depth is not None and self.div_depth == self.row_depth:
                title = " ".join(self.title).strip()
                size = " ".join(self.size).strip()
                if title and size and self.has_valid_magnet:
                    self.valid_rows += 1
                    if _tokens(EXACT).issubset(_tokens(title)):
                        self.exact_rows += 1
                self.row_depth = None
                self.name_depth = None
            elif self.name_depth == self.div_depth:
                self.name_depth = None
            self.div_depth = max(0, self.div_depth - 1)


def verify(*, client=None, report=print):
    status, html = fetch_one(EXACT, client=client)
    report("HTTP_STATUS: " + str(status))
    if status != 200:
        report("VALID_SOURCE_ROWS: 0")
        report("EXACT_RELEASE_WITH_MAGNET: False")
        return False
    try:
        parser = BTDiggRows()
        parser.feed(html.decode("utf-8", errors="replace"))
        parser.close()
    except (ValueError, TypeError, UnicodeError):
        report("SOURCE_HTML_PARSING_FAILED")
        return False
    report("VALID_SOURCE_ROWS: " + str(parser.valid_rows))
    report("EXACT_RELEASE_WITH_MAGNET: " + str(parser.exact_rows > 0))
    return parser.exact_rows > 0


if __name__ == "__main__":
    raise SystemExit(0 if verify() else 2)
