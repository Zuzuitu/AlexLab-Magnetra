#!/usr/bin/env python3
"""Verify the production HTTPS PWA after deployment.

Only publicly accessible endpoints are queried; no auth credentials or
provider-search traffic is required. Uses standard Python only.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "config/project-invariants.json").read_text(encoding="utf-8"))
BASE = CFG["deployment"]["production_url"].rstrip("/")
TOTAL = CFG["provider_parity"]["required_builtin_count"]


def fetch(path: str, *, response_json: bool = True):
    req = Request(BASE + path, headers={
        "User-Agent": "AlexLab-Magnetra-Production-Smoketest/1.0",
        "Accept": "application/json" if response_json else "text/html",
        "Cache-Control": "no-cache",
    })
    with urlopen(req, timeout=15) as response:
        if response.status != 200:
            raise RuntimeError(f"{path}: expected HTTP 200, got {response.status}")
        body = response.read(3_000_000)
    if response_json:
        return json.loads(body.decode("utf-8"))
    return body.decode("utf-8", errors="replace")


def verify() -> str:
    health = fetch("/api/health")
    if health.get("ok") is not True or health.get("product") != "AlexLab Magnetra":
        raise AssertionError("health API does not report AlexLab Magnetra")
    if health.get("total") != TOTAL:
        raise AssertionError(f"health total expected {TOTAL}, got {health.get('total')}")
    providers = fetch("/api/providers").get("providers")
    if not isinstance(providers, list) or len(providers) != TOTAL:
        raise AssertionError(f"provider catalog is not the expected {TOTAL} entries")
    ids = [p.get("id") for p in providers]
    if len(set(ids)) != TOTAL:
        raise AssertionError("provider catalog has duplicate IDs")
    ported = sum(p.get("ported") is True for p in providers)
    if ported != health.get("ported"):
        raise AssertionError("health ported count differs from provider catalog")
    manifest = fetch("/manifest.webmanifest")
    if manifest.get("name") != "AlexLab Magnetra" or manifest.get("display") != "standalone":
        raise AssertionError("PWA manifest identity or standalone mode is missing")
    root = fetch("/", response_json=False)
    if "<title>AlexLab Magnetra" not in root or "/app.js" not in root:
        raise AssertionError("PWA homepage does not contain expected app bootstrapping")
    return f"HTTP+TLS OK; HTML, manifest, /api/health, /api/providers OK; {ported}/{TOTAL} adapters inventoried as ported"


if __name__ == "__main__":
    failures = []
    for attempt in range(1, 9):
        try:
            print(f"Production smoke attempt {attempt}/8: {BASE}", flush=True)
            print("PASS:", verify(), flush=True)
            sys.exit(0)
        except (URLError, HTTPError, TimeoutError, ValueError, AssertionError, RuntimeError, OSError) as exc:
            message = str(exc)
            failures.append(message)
            print(f"Attempt {attempt} FAILED: {message}", file=sys.stderr, flush=True)
            if attempt < 8:
                time.sleep(8)
    print(f"Production smoke FAILED after 8 attempts: {failures[-1]}", file=sys.stderr)
    sys.exit(1)
