#!/usr/bin/env python3
"""Owner-triggered local-only probe of the persistent BTDigg browser gateway.

Does not log source HTML, query strings, magnet links, tokens or cookies.
Nothing is sent to Cloudflare or exposed by the host.
"""
import argparse
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request

LOCAL = "http://127.0.0.1:8798"
STATE = Path.home() / ".local" / "state" / "magnetra-btdigg-browser"
TOKEN_FILE = STATE / "gateway.token"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-search", action="store_true",
                        help="Perform exactly one human-invoked BTDigg browser query")
    args = parser.parse_args()
    try:
        if TOKEN_FILE.is_symlink() or not TOKEN_FILE.is_file():
            raise ValueError("missing private token")
        if TOKEN_FILE.stat().st_mode & 0o077:
            raise ValueError("insecure private token permissions")
        token = TOKEN_FILE.read_text().strip()
        if not re.fullmatch(r"[A-Za-z0-9_-]{48,256}", token):
            raise ValueError("invalid token")
        path = "/healthz"
        if args.test_search:
            path = "/v1/search?q=" + urllib.parse.quote(
                "The Dog Stars 2026", safe="")
        req = urllib.request.Request(
            LOCAL + path,
            headers={"authorization": "Bearer " + token,
                     "accept": "text/html" if args.test_search else "application/json"},
        )
        with urllib.request.urlopen(req, timeout=14) as r:
            body = r.read(3_000_001)
            status = r.status
        result = {"local_gateway_status": status, "search_performed": args.test_search}
        if args.test_search:
            result.update({
                "source_html_bounded": 0 < len(body) <= 3_000_000,
                "source_result_marker": b"one_result" in body.lower(),
                "source_magnet_marker": b"magnet:?xt=urn:btih:" in body.lower(),
            })
        print(json.dumps(result, sort_keys=True))
    except urllib.error.HTTPError as e:
        print(json.dumps({
            "local_gateway_status": e.code,
            "search_performed": args.test_search,
            "verified_results": False,
        }, sort_keys=True))
    except (OSError, ValueError, urllib.error.URLError):
        print(json.dumps({"local_gateway_status": "unavailable",
                          "search_performed": False}, sort_keys=True))


if __name__ == "__main__":
    main()
