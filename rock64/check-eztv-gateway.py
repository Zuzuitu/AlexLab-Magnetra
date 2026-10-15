#!/usr/bin/env python3
"""Read-only local EZTV gateway acceptance check.

Does not print or persist credentials, IMDb IDs, release names, magnet links,
hashes or response bodies. One bounded recent-source GET, up to four source-filter lookups and at most one authenticated gateway-filter GET.
No torrents are downloaded or magnets sent to Flud.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

CONFIG = pathlib.Path("/etc/magnetra-eztv/gateway.env")
RECENT = "https://eztvx.to/api/get-torrents?limit=5&page=1"
SOURCE_FILTER = "https://eztvx.to/api/get-torrents?imdb_id="
MAX_CANDIDATES = 4
SOURCE_UA = ("Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
             "(KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36")
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


def health_when_ready(auth, attempts=9, delay=0.5):
    """Bounded loopback-startup wait ONLY; never retry actual EZTV searches."""
    for attempt in range(attempts):
        try:
            return get_json(LOCAL_HEALTH, auth)
        except URLError as error:
            if not isinstance(error.reason, ConnectionRefusedError) or attempt == attempts - 1:
                raise
            time.sleep(delay)


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


def source_candidates(recent):
    """Deduplicated real recent IDs with source-owned valid magnet records."""
    rows = recent.get("torrents") if isinstance(recent, dict) else None
    if not isinstance(rows, list):
        return []
    candidates = []
    for entry in rows[:5]:
        if not isinstance(entry, dict):
            continue
        imdb = IMDB.fullmatch(str(entry.get("imdb_id", "")))
        magnet = entry.get("magnet_url")
        if not imdb or not isinstance(magnet, str) or not MAGNET.match(magnet):
            continue
        value = str(int(imdb.group(1)))
        if value not in candidates:
            candidates.append(value)
        if len(candidates) >= MAX_CANDIDATES:
            break
    return candidates


def find_source_positive(candidates, get=None):
    """One direct official API GET per candidate; never fallback to unrelated shows."""
    get = get or get_json
    headers = {"Accept": "application/json", "User-Agent": SOURCE_UA,
               "Accept-Encoding": "identity"}
    for ordinal, imdb in enumerate(candidates[:MAX_CANDIDATES], 1):
        result = get(SOURCE_FILTER + imdb + "&limit=100&page=1", headers)
        rows, valid = inspect_filtered(result, imdb)
        if valid > 0:
            return (imdb, ordinal, rows, valid)
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
    stage = "credentials"
    try:
        token = read_token()
        auth = {"Authorization": "Bearer " + token, "Accept": "application/json"}
        stage = "local-health"
        health = health_when_ready(auth)
        if health.get("ok") is not True:
            raise ValueError("Invalid local health response")
        print("EZTV local authenticated health: PASS")

        stage = "recent-source"
        recent = get_json(RECENT, {"Accept": "application/json",
                                "User-Agent": SOURCE_UA, "Accept-Encoding": "identity"})
        candidates = source_candidates(recent)
        print("EZTV recent valid IMDb candidates:", len(candidates))
        if not candidates:
            print("UNVERIFIED: no valid recent IMDb candidates; no gateway request sent")
            return 2
        stage = "source-filter"
        positive = find_source_positive(candidates)
        if not positive:
            print("UNVERIFIED: source returned no positive filtered candidates; no gateway request sent")
            return 2
        target, ordinal, direct_rows, direct_valid = positive
        print("EZTV direct source-positive sample:", ordinal)
        print("EZTV direct filtered rows:", direct_rows)
        print("EZTV direct matching magnet count:", direct_valid)

        stage = "local-filtered"
        result = get_json(LOCAL_SEARCH + target, auth)
        rows, valid = inspect_filtered(result, target)
        print("EZTV gateway filtered rows:", rows)
        print("EZTV gateway matching magnet count:", valid)
        if valid < 1:
            raise ValueError("Gateway did not return a positive filtered source response")
        print("PASS: genuine EZTV magnet metadata reached isolated local gateway")
        return 0
    except HTTPError as error:
        # Output code and controlled stage only; never leak URL, token or body.
        print(f"FAIL stage={stage} HTTP={error.code}")
    except URLError:
        print(f"FAIL stage={stage} cause=network-or-listener")
    except (OSError, ValueError, TypeError, TimeoutError, json.JSONDecodeError):
        print(f"FAIL stage={stage} cause=local-data-or-response")
    return 1


if __name__ == "__main__":
    sys.exit(main())
