#!/usr/bin/env python3
"""One bounded GET-only exact 352.7MB Cyberpunk-card link identity audit.

Authoritative input: owner iPhone screenshot and owner-copied final Safari URL.
Output contains safe shape booleans, hash prefixes and normalized-path match only.
Never log the original title, URL, magnet, torrent infohash or response body.
"""
from __future__ import annotations
import json
import re
import sys
import urllib.parse
from diagnose_therarbag_iphone_linkshape_20261024 import api_search, fingerprint, source_shape, Stop

PUBLIC_URL = ("https://therarbg.com/post-detail/95bf8b/"
              "2026-10-20-cyberpunk-edgerunners-2-original-series-soundtrack-flac-44-1khz-24bit/")
IPHONE_FP = "b12d9fd36aa0"
SEARCH = "Cyberpunk Edgerunners 2"

def exact_title_and_size(r):
    if not isinstance(r, dict) or r.get("provider") != "therarbag":
        return False
    title = r.get("name")
    size = r.get("size")
    # Must be this exact screenshot edition and numeric public size.
    return (isinstance(title, str) and len(title) <= 600
            and "cyberpunk" in title.casefold()
            and "edgerunners 2" in title.casefold()
            and "original series soundtrack" in title.casefold()
            and isinstance(size, str)
            and bool(re.fullmatch(r"\s*352[.]7\s*MB\s*", size, re.I)))

def inspect(payload):
    rows = payload.get("results")
    if not isinstance(rows, list) or len(rows) > 250:
        raise Stop("SEARCH_SCHEMA_INVALID")
    matches = [r for r in rows if exact_title_and_size(r)]
    print("SCREENSHOT_ITEM_MATCH_COUNT:", len(matches), flush=True)
    if not matches:
        print("NO_MATCH_DIFFERENT_SEARCH_SNAPSHOT_NO_INFERENCE", flush=True)
        return
    canonical = urllib.parse.urlsplit(PUBLIC_URL)
    for r in matches[:3]:
        url = r.get("details")
        if not isinstance(url, str) or len(url) > 1500:
            print("MATCHED_DETAILS_MISSING_OR_OVERSIZED", flush=True)
            continue
        try:
            u = urllib.parse.urlsplit(url)
        except ValueError:
            print("MATCHED_DETAILS_MALFORMED", flush=True)
            continue
        print("SOURCE_CARD_DETAILS_FP:", fingerprint(url), flush=True)
        print("SAME_AS_IPHONE_FP:", fingerprint(url) == IPHONE_FP, flush=True)
        print("EXACT_OWNER_FINAL_URL:", url == PUBLIC_URL, flush=True)
        print("SAME_FINAL_URL_PATH:", u.path == canonical.path, flush=True)
        print("SAME_FINAL_URL_ID:", len(u.path.split("/")) > 2 and u.path.split("/")[2] == "95bf8b", flush=True)
        print("SOURCE_DETAIL_SHAPE:", source_shape(url), flush=True)
        print("SOURCE_DETAILS_HAS_QUERY:", bool(u.query), flush=True)
        print("SOURCE_DETAILS_HAS_FRAGMENT:", bool(u.fragment), flush=True)
        print("SOURCE_DETAILS_HAS_HOST_MISMATCH:", u.netloc != canonical.netloc, flush=True)
        print("SOURCE_DETAILS_HAS_ENCODED_PERCENT:", "%" in u.path, flush=True)
        print("SOURCE_DETAILS_CHAR_COUNT:", len(url), flush=True)
        print("RAW_SOURCE_URL_TITLE_HASH_MAGNET_SUPPRESSED: PASS", flush=True)

def main():
    if sys.argv[1:] != ["--approved-readonly"]:
        print("OWNER_READONLY_APPROVAL_MISSING")
        return 2
    try:
        inspect(api_search(SEARCH))
    except Stop as e:
        print("EXACT_SOURCE_CARD_READONLY_STOP:", str(e))
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
