#!/usr/bin/env python3
"""Read-only local EZTV gateway acceptance check.

Does not print or persist credentials, IMDb IDs, release names, magnet links,
hashes or response bodies. One recent-source GET and one gateway search GET.
No torrents are downloaded or magnets sent to Flud.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

CONFIG = pathlib.Path("/etc/magnetra-eztv/gateway.env")
RECENT = "https://eztvx.to/api/get-torrents?limit=2&page=1"
LOCAL_HEALTH = "http://127.0.0.1:8797/healthz"
LOCAL_SEARCH = "http://127.0.0.1:8797/v1/torrents?imdb_id="
MAX_BYTES = 1_000_000
IMDB = re.compile(r"^(?:tt)?([0-9]{5,12})$", re.I)
MAGNET = re.compile(r"^magnet:\?xt=urn:btih:(?:[0-9a-f]{40}|[a-z2-7]{32})(?:&|$)", re.I)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def read_token():
    data = CONFIG.read_text(encoding="ascii")
    match = re.fullmatch(r"MAGNETRA_EZTV_TOKEN=([A-Za-z0-9_-]{48,256})\n", data)
    if not match:
        raise ValueError("Local EZTV credential file invalid")
    return match.group(1)


def get_json(url, headers):
    request = Request(url, headers=headers, method="GET")
    with build_opener(ProxyHandler({}), NoRedirect()).open(request, timeout=12) as response:
        if response.status != 200:
            raise ValueError("Response status was not HTTP 200")
        if "application/json" not in (response.headers.get("content-type") or "").lower():
            raise ValueError("Response was not JSON")
        if int(response.headers.get("content-length") or 0) > MAX_BYTES:
            raise ValueError("JSON too large")
        body = response.read(MAX_BYTES + 1)
        if len(body) > MAX_BYTES:
            raise ValueError("JSON too large")
        parsed = json.loads(body)
        if not isinstance(parsed, dict):
            raise ValueError("JSON root not an object")
        return parsed


def choose_known_positive(recent):
    """Use a positive original EZTV magnet row, never the global torrents count."""
    if not isinstance(recent, dict) or not isinstance(recent.get("torrents"), list):
        return None
    for entry in recent["torrents"][:2]:
        if not isinstance(entry, dict):
            continue
        imdb = IMDB.fullmatch(str(entry.get("imdb_id", "")))
        magnet = entry.get("magnet_url")
        if imdb and isinstance(magnet, str) and MAGNET.match(magnet):
            return str(int(imdb.group(1)))
    return None


def inspect_filtered(data, target):
    actual = IMDB.fullmatch(str(data.get("imdb_id", "")))
    rows = data.get("torrents")
    if not actual or str(int(actual.group(1))) != target or not isinstance(rows, list):
        return 0, 0
    valid = 0
    for entry in rows:
        if not isinstance(entry, dict):
            continue
        raw = str(entry.get("imdb_id", ""))
        match = IMDB.fullmatch(raw)
        magnet = entry.get("magnet_url")
        if match and str(int(match.group(1))) == target and isinstance(magnet, str) and MAGNET.match(magnet):
            valid += 1
    return len(rows), valid


def main():
    try:
        token = read_token()
        auth = {"Authorization": "Bearer " + token, "Accept": "application/json"}
        health = get_json(LOCAL_HEALTH, auth)
        if health.get("ok") is not True:
            raise ValueError("Local EZTV service health response invalid")
        print("EZTV local authenticated health: PASS")

        recent = get_json(RECENT, {"Accept": "application/json", "User-Agent":
            "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36",
            "Accept-Encoding": "identity"})
        target = choose_known_positive(recent)
        if not target:
            raise ValueError("No recent release with a valid IMDb and magnet")
        result = get_json(LOCAL_SEARCH + target, auth)
        rows, valid = inspect_filtered(result, target)
        print("EZTV filtered source rows:", rows)
        print("EZTV rows with matching IMDb and valid magnet:", valid)
        if valid < 1:
            raise ValueError("No genuine filtered magnet found")
        print("PASS: genuine EZTV magnet metadata reached isolated local gateway")
        return 0
    except (OSError, HTTPError, URLError, ValueError, TypeError, TimeoutError, json.JSONDecodeError):
        print("FAIL: local EZTV gateway or genuine source validation did not pass (no secrets printed)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
