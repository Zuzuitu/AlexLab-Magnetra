#!/usr/bin/env python3
"""Read-only 8798 acceptance: original EZTV -> 8797 -> 8798, same IMDb/magnets.

No CLI-supplied private IMDb, no token in process arguments or output, no
magnet/title/hash/URL/body logged, no retries for source errors, no mutations.
Uses source-owned recent magnet metadata solely to find a positive same-source
sample; no fallback to unrelated providers and no torrent downloads.
"""
from __future__ import annotations

from collections import Counter
import json
import os
import pathlib
import re
import stat
import subprocess
import sys
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

CENTRAL_ENV = pathlib.Path("/etc/magnetra-gateway/gateway.env")
EZTV_ENV = pathlib.Path("/etc/magnetra-eztv/gateway.env")
SOURCE = "https://eztvx.to/api/get-torrents"
BACKEND = "http://127.0.0.1:8797"
CENTRAL = "http://127.0.0.1:8798"
UA = ("Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36")
IMDB = re.compile(r"^(?:tt)?([0-9]{5,12})$", re.I)
MAGNET = re.compile(r"^magnet:\?xt=urn:btih:(?:[a-f0-9]{40}|[a-z2-7]{32})(?:&|$)", re.I)
TOKEN = re.compile(r"^[A-Za-z0-9_-]{48,256}$")
MAX_BYTES = 1_000_000
MAX_CANDIDATES = 4


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def read_private_token(path: pathlib.Path, variable: str) -> str:
    directory = path.parent.lstat()
    info = path.lstat()
    if (not stat.S_ISDIR(directory.st_mode) or directory.st_uid != 0 or
            directory.st_mode & 0o022 or not stat.S_ISREG(info.st_mode) or
            info.st_uid != 0 or info.st_mode & 0o077 or info.st_size > 400):
        raise ValueError("unsafe private credential file")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        data = os.read(fd, 401).decode("ascii")
    finally:
        os.close(fd)
    match = re.fullmatch(re.escape(variable) + r"=([A-Za-z0-9_-]{48,256})\n", data)
    if not match or not TOKEN.fullmatch(match.group(1)):
        raise ValueError("invalid private credential format")
    return match.group(1)


def normalized_imdb(value: object) -> str | None:
    m = IMDB.fullmatch(str(value or ""))
    return str(int(m.group(1))) if m else None


def source_candidates(payload: object) -> list[str]:
    if not isinstance(payload, dict) or not isinstance(payload.get("torrents"), list):
        return []
    found: list[str] = []
    for row in payload["torrents"][:5]:
        if not isinstance(row, dict):
            continue
        target = normalized_imdb(row.get("imdb_id"))
        magnet = row.get("magnet_url")
        if target and isinstance(magnet, str) and MAGNET.match(magnet) and target not in found:
            found.append(target)
        if len(found) >= MAX_CANDIDATES:
            break
    return found


def matching_magnets(data: object, target: str) -> Counter:
    """Reject wrong-source, wrong-ID, malformed or fabricated response shapes."""
    if not isinstance(data, dict) or "error" in data or "errors" in data:
        raise ValueError("invalid source result")
    if normalized_imdb(data.get("imdb_id")) != target:
        raise ValueError("wrong IMDb echo")
    count = data.get("torrents_count")
    if type(count) not in (str, int) or not str(count).isdigit():
        raise ValueError("invalid reported count")
    rows = data.get("torrents")
    if rows is None and "torrents" not in data and int(count) == 0:
        return Counter()
    if not isinstance(rows, list) or len(rows) > 100 or int(count) < len(rows):
        raise ValueError("invalid result rows")
    result: Counter = Counter()
    for row in rows:
        if not isinstance(row, dict) or normalized_imdb(row.get("imdb_id")) != target:
            raise ValueError("wrong or missing row IMDb")
        magnet = row.get("magnet_url")
        if not isinstance(magnet, str) or not MAGNET.match(magnet):
            raise ValueError("invalid genuine magnet")
        result[magnet] += 1
    return result


def opener():
    return build_opener(ProxyHandler({}), NoRedirect())


def get_status(url: str, token: str | None = None) -> int:
    headers = {"Accept": "application/json", "Accept-Encoding": "identity"}
    if token is not None:
        headers["Authorization"] = "Bearer " + token
    req = Request(url, headers=headers, method="GET")
    try:
        with opener().open(req, timeout=6) as response:
            response.read(1024)
            return response.status
    except HTTPError as error:
        try:
            return error.code
        finally:
            error.close()


def get_json(url: str, token: str | None = None) -> dict:
    headers = {"Accept": "application/json", "Accept-Encoding": "identity", "User-Agent": UA}
    if token is not None:
        headers["Authorization"] = "Bearer " + token
    req = Request(url, headers=headers, method="GET")
    with opener().open(req, timeout=12) as response:
        if response.status != 200:
            raise ValueError("non-200")
        if "application/json" not in (response.headers.get("content-type") or "").lower():
            raise ValueError("not JSON")
        if int(response.headers.get("content-length") or 0) > MAX_BYTES:
            raise ValueError("response too large")
        body = response.read(MAX_BYTES + 1)
        if len(body) > MAX_BYTES:
            raise ValueError("response too large")
        parsed = json.loads(body)
        if not isinstance(parsed, dict):
            raise ValueError("not a JSON object")
        return parsed


def units_healthy() -> bool:
    for name in ("magnetra-btdigg.service",
                 "magnetra-btdigg-tunnel.service",
                 "magnetra-eztv.service", "magnetra-gateway.service"):
        status = subprocess.run(["systemctl", "is-active", "--quiet", name],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                check=False, timeout=5)
        if status.returncode != 0:
            return False
    return True


def check_smoke(hub_token: str, eztv_token: str) -> None:
    if hub_token == eztv_token:
        raise ValueError("credentials must differ")
    if not units_healthy():
        raise ValueError("Magnetra service inactive")
    for port in (8796, 8797, 8798):
        if get_status(f"http://127.0.0.1:{port}/healthz") != 401:
            raise ValueError("unauthenticated health mismatch")
    if get_json(CENTRAL + "/healthz", hub_token).get("ok") is not True:
        raise ValueError("central auth health mismatch")
    if get_json(BACKEND + "/healthz", eztv_token).get("ok") is not True:
        raise ValueError("EZTV auth health mismatch")
    print("PASS: 8798 auth=200 unauth=401; 8797 auth=200 unauth=401; BTDigg 8796=401")
    print("PASS: existing BTDigg, tunnel and EZTV services remain active")


def acceptance(hub_token: str, eztv_token: str) -> int:
    stage = "recent-original"
    print("Checking ONE real same-source positive sample without revealing identifiers.")
    try:
        recent = get_json(SOURCE + "?limit=5&page=1")
        candidates = source_candidates(recent)
        if not candidates:
            print("UNVERIFIED: no eligible source-owned recent samples")
            return 2
        original: Counter | None = None
        target = None
        for candidate in candidates:
            stage = "filtered-original"
            raw = get_json(SOURCE + "?imdb_id=" + candidate + "&limit=100&page=1")
            found = matching_magnets(raw, candidate)
            if found:
                original, target = found, candidate
                break
        if original is None or target is None:
            print("UNVERIFIED: no positive original filtered metadata")
            return 2

        stage = "local-8797"
        source_gateway = get_json(BACKEND + "/v1/torrents?imdb_id=" + target, eztv_token)
        eztv_magnets = matching_magnets(source_gateway, target)
        stage = "central-8798"
        dispatched = get_json(CENTRAL + "/v1/eztvx/torrents?imdb_id=" + target, hub_token)
        central_magnets = matching_magnets(dispatched, target)

        if not original or not (original == eztv_magnets == central_magnets):
            print("FAIL: original / 8797 / 8798 magnet identities or counts differ")
            return 1
        print("EZTV original matching magnets:", sum(original.values()))
        print("EZTV gateway 8797 matching magnets:", sum(eztv_magnets.values()))
        print("Central gateway 8798 matching magnets:", sum(central_magnets.values()))
        print("PASS: exact genuine magnet multiset preserved through 8798 -> 8797")
        return 0
    except HTTPError as error:
        try:
            print(f"FAIL stage={stage} HTTP={error.code}")
        finally:
            error.close()
    except (URLError, OSError, TimeoutError):
        print(f"FAIL stage={stage} cause=network-or-timeout")
    except (TypeError, ValueError, KeyError, json.JSONDecodeError):
        print(f"FAIL stage={stage} cause=invalid-response")
    return 1


def main() -> int:
    if len(sys.argv) > 2 or (len(sys.argv) == 2 and sys.argv[1] != "--smoke"):
        print("Usage: sudo python3 -B check-magnetra-gateway.py [--smoke]")
        return 1
    if os.geteuid() != 0:
        print("STOP: root required to read local secrets")
        return 1
    try:
        hub_token = read_private_token(CENTRAL_ENV, "MAGNETRA_GATEWAY_TOKEN")
        eztv_token = read_private_token(EZTV_ENV, "MAGNETRA_EZTV_TOKEN")
        check_smoke(hub_token, eztv_token)
    except (ValueError, OSError, TimeoutError, URLError, HTTPError, subprocess.SubprocessError):
        print("FAIL: local credentials, service integrity or authenticated health")
        return 1
    if len(sys.argv) == 2:
        print("PASS: local smoke; real-source acceptance intentionally not run")
        return 0
    return acceptance(hub_token, eztv_token)


if __name__ == "__main__":
    sys.exit(main())
