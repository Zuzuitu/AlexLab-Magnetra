#!/usr/bin/env python3
"""One-shot confidential EZTV source-vs-local gateway comparison on Rock64.

Companion to the independent provider audit. Compares *the same genuine recent
IMDb ID* through direct API limit=2, direct limit=100 and authenticated local
gateway (which currently uses limit=100). Never prints the IMDb ID, magnets,
hashes, titles, bearer token or raw JSON. Never changes any services or routes.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

SOURCE = "https://eztvx.to/api/get-torrents"
LOCAL = "http://127.0.0.1:8797/v1/torrents"
CONFIG = pathlib.Path("/etc/magnetra-eztv/gateway.env")
UA = ("Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36")
MAGNET = re.compile(r"^magnet:\?xt=urn:btih:(?:[a-f0-9]{40}|[a-z2-7]{32})(?:&|$)", re.I)
IMDB = re.compile(r"^(?:tt)?([0-9]{5,12})$", re.I)
MAX_BYTES = 1_000_000

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def read_token():
    data = CONFIG.read_text(encoding="ascii")
    match = re.fullmatch(r"MAGNETRA_EZTV_TOKEN=([A-Za-z0-9_-]{48,256})\n", data)
    if not match:
        raise ValueError("local token config unavailable or invalid")
    return match.group(1)


def request_json(url, token=None, opener=None):
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "identity",
        "User-Agent": UA,
    }
    if token:
        headers["Authorization"] = "Bearer " + token
    request = Request(url, method="GET", headers=headers)
    opener = opener or build_opener(ProxyHandler({}), NoRedirect())
    try:
        with opener.open(request, timeout=12) as response:
            if response.status != 200:
                return {"http": response.status, "error": "non-200"}, None
            if "application/json" not in (response.headers.get("content-type") or "").lower():
                return {"http": 200, "error": "non-json"}, None
            if int(response.headers.get("content-length") or 0) > MAX_BYTES:
                return {"http": 200, "error": "too-large"}, None
            raw = response.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                return {"http": 200, "error": "too-large"}, None
            try:
                data = json.loads(raw)
            except (ValueError, UnicodeError):
                return {"http": 200, "error": "bad-json"}, None
            return {"http": 200}, data
    except HTTPError as e:
        status = e.code
        e.close()
        return {"http": status, "error": "source-or-gateway-http"}, None
    except (OSError, TimeoutError, URLError):
        return {"http": None, "error": "network-or-timeout"}, None


def norm_id(value):
    m = IMDB.fullmatch(str(value or ""))
    return str(int(m.group(1))) if m else None


def choose_recent(data):
    if not isinstance(data, dict):
        return None
    for row in data.get("torrents", [])[:2]:
        if not isinstance(row, dict):
            continue
        chosen = norm_id(row.get("imdb_id"))
        magnet = row.get("magnet_url")
        if chosen and isinstance(magnet, str) and MAGNET.match(magnet):
            return chosen
    return None


def summarize(data, target):
    if not isinstance(data, dict):
        return {"shape": "not-object"}
    count = data.get("torrents_count")
    rows = data.get("torrents")
    result = {
        "echo_ok": norm_id(data.get("imdb_id")) == target,
        "declared_count": int(count) if type(count) in (int, str) and str(count).isdigit() and len(str(count)) <= 8 else None,
        "list": isinstance(rows, list),
        "page_rows": len(rows) if isinstance(rows, list) else None,
        "valid_matched_magnets": 0,
        "error_field": "error" in data or "errors" in data,
    }
    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict) or norm_id(row.get("imdb_id")) != target:
                continue
            link = row.get("magnet_url")
            if isinstance(link, str) and MAGNET.match(link):
                result["valid_matched_magnets"] += 1
    return result


def main():
    try:
        token = read_token()
        recent_status, recent = request_json(SOURCE + "?limit=2&page=1")
        chosen = choose_recent(recent)
        print(json.dumps({"probe": "recent", **recent_status,
                          "valid_sample_available": bool(chosen)}))
        if not chosen:
            print(json.dumps({"stopped": "no_genuine_recent_imdb", "safe": True}))
            return 2
        for limit in (2, 100):
            status, obj = request_json(SOURCE + f"?imdb_id={chosen}&limit={limit}&page=1")
            print(json.dumps({"probe": f"direct-limit-{limit}", **status,
                              **(summarize(obj, chosen) if obj is not None else {})}))
        status, obj = request_json(LOCAL + "?imdb_id=" + chosen, token=token)
        print(json.dumps({"probe": "local-gateway-limit-100", **status,
                          **(summarize(obj, chosen) if obj is not None else {})}))
        print(json.dumps({"finished": True, "no_changes": True,
                          "note": "Compare matched magnet counts, not global torrent totals"}))
        return 0
    except (OSError, ValueError, TypeError):
        print(json.dumps({"failure": "private-config-or-local-parser", "safe": True}))
        return 2


if __name__ == "__main__":
    sys.exit(main())
