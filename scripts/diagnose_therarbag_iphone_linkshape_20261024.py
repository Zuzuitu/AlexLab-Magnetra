#!/usr/bin/env python3
"""GET-only iPhone same-card detail URL shape audit via canonical Magnetra search.

Never prints torrent names, full source URLs, item IDs, magnets, BTIH, search
body, credentials or provider response. No resolve, no downloads, no POSTs.
The exact user-visible 12hex diagnostic URL fingerprint is correlation only.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://index.alexlab.media"
FINGERPRINT = "b12d9fd36aa0"  # user-provided iPhone diagnostic screenshot
QUERIES = ("Cyberpunk Edgerunners 2", "Cyberpunk")
MAX_BYTES = 1_000_000
UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) "
      "AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1")


class Stop(Exception):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fingerprint(s):
    return hashlib.sha256(s.encode("utf8")).hexdigest()[:12]


def source_shape(value):
    if not isinstance(value, str) or len(value) > 1500:
        return "INVALID_OR_OVERSIZED"
    try:
        parsed = urllib.parse.urlsplit(value)
    except ValueError:
        return "MALFORMED"
    if parsed.scheme != "https" or parsed.netloc != "therarbg.com":
        return "INVALID_HTTPS_HOST"
    if parsed.username or parsed.password or parsed.fragment:
        return "AUTH_OR_FRAGMENT"
    if parsed.query:
        return "QUERY_PRESENT"
    if not re.fullmatch(r"/post-detail/[a-z0-9]{1,32}/[a-z0-9][a-z0-9._%~-]{0,340}/?", parsed.path, flags=re.I):
        segments = parsed.path.strip("/").split("/")
        if len(segments) != 3 or segments[0] != "post-detail":
            return "PATH_SEGMENTS_DIFFER"
        if not re.fullmatch("[a-z0-9]{1,32}", segments[1], flags=re.I):
            return "ID_PATTERN_REJECTED"
        if len(segments[2]) > 341:
            return "SLUG_TOO_LONG"
        return "SLUG_PATTERN_REJECTED"
    return "JSON_URL_ACCEPTABLE"


def api_search(query):
    path = "/api/search?" + urllib.parse.urlencode(
        {"q": query, "category": "all", "providers": "therarbag"})
    req = urllib.request.Request(
        BASE + path, method="GET",
        headers={"User-Agent": UA, "Accept": "application/json",
                 "Accept-Encoding": "identity", "Cache-Control": "no-store"})
    try:
        with urllib.request.build_opener(NoRedirect()).open(req, timeout=32) as response:
            status = response.status
            typ = response.headers.get("content-type", "")
            data = response.read(MAX_BYTES + 1)
    except urllib.error.HTTPError as err:
        raise Stop("PRODUCTION_SEARCH_HTTP_" + str(err.code)) from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise Stop("PRODUCTION_SEARCH_TRANSPORT_UNVERIFIED") from None
    if status != 200 or "application/json" not in typ or len(data) > MAX_BYTES:
        raise Stop("PRODUCTION_SEARCH_BODY_UNVERIFIED")
    try:
        payload = json.loads(data)
    except (UnicodeError, ValueError):
        raise Stop("PRODUCTION_SEARCH_JSON_MALFORMED") from None
    if not isinstance(payload, dict):
        raise Stop("PRODUCTION_SEARCH_JSON_UNEXPECTED")
    return payload


def inspect(payload, query_number):
    records, errors = payload.get("results"), payload.get("errors")
    if not isinstance(records, list) or len(records) > 250 or not isinstance(errors, list):
        raise Stop("SEARCH_RECORDS_SCHEMA_UNVERIFIED")
    if errors:
        print("SEARCH_" + str(query_number) + "_ERROR_COUNT:", len(errors), flush=True)
    selected = [r for r in records if isinstance(r, dict) and r.get("provider") == "therarbag"]
    print("SEARCH_" + str(query_number) + "_THERARBAG_CARDS:", len(selected), flush=True)
    match = False
    for index, record in enumerate(selected):
        detail = record.get("details")
        if not isinstance(detail, str) or len(detail) > 1500:
            continue
        fp = fingerprint(detail)
        if fp == FINGERPRINT:
            match = True
            print("IPHONE_FINGERPRINT_MATCH: YES", flush=True)
            print("MATCHED_CARD_INDEX:", index, flush=True)
            print("MATCHED_DETAIL_SHAPE:", source_shape(detail), flush=True)
            print("MATCHED_URL_LENGTH:", len(detail), flush=True)
            print("MATCHED_QUERY_PRESENT:", bool(urllib.parse.urlsplit(detail).query), flush=True)
            print("MATCHED_MAGNET_ALREADY_PRESENT:", isinstance(record.get("magnet"), str), flush=True)
            print("NO_URL_HASH_MAGNET_OR_TORRENT_METADATA_DISCLOSED: PASS", flush=True)
            break
    if not match:
        print("IPHONE_FINGERPRINT_MATCH: NO_FOR_SEARCH_" + str(query_number), flush=True)
        for row in selected[:3]:
            detail = row.get("details")
            if isinstance(detail, str):
                print("FIRST_CARD_SHAPE:", source_shape(detail), flush=True)
    return match


def main():
    if len(sys.argv) != 2 or sys.argv[1] != "--approved-readonly":
        print("APPROVAL_REQUIRED_NO_SOURCE_CALL")
        return 2
    try:
        for n, q in enumerate(QUERIES, 1):
            if inspect(api_search(q), n):
                print("SAME_CARD_URL_SHAPE_AUDIT: MATCH_FOUND", flush=True)
                return 0
    except Stop as error:
        print("SAME_CARD_URL_SHAPE_AUDIT_STOP:", str(error), flush=True)
        return 1
    print("SAME_CARD_URL_SHAPE_AUDIT: NO_MATCH_NO_FIX_ASSUMED", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
