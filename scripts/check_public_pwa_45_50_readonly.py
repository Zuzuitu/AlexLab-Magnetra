#!/usr/bin/env python3
"""Read-only external audit of the deployed 45-indexer/50-results Magnetra PWA.

Compare exact public immutable-compatible static JS/CSS/i18n/sw bytes with
reviewed source in the current checkout. Do NOT call provider searches,
resolve magnets, send Flud requests, change traffic or require API credentials.
"""
from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config/project-invariants.json").read_text(encoding="utf-8"))
BASE = CONFIG["deployment"]["production_url"].rstrip("/")
ASSETS = {
    "/app.js": "web/app.js",
    "/i18n.js": "web/i18n.js",
    "/styles.css": "web/styles.css",
    "/sw.js": "web/sw.js",
}
CAP = 3_000_000


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *_args, **_kwargs):
        return None


def fetch(path):
    if path not in (*ASSETS.keys(), "/", "/api/health", "/api/providers"):
        raise ValueError("unapproved public read-only URL")
    request = urllib.request.Request(
        BASE + path,
        headers={
            "User-Agent": "AlexLab-Magnetra-ReadOnly-Postflight/1.0",
            "Accept": "application/json" if path.startswith("/api/") else "*/*",
            "Cache-Control": "no-cache, no-store",
            "Accept-Encoding": "identity",
        },
        method="GET",
    )
    with urllib.request.build_opener(NoRedirect()).open(request, timeout=18) as response:
        if response.status != 200:
            raise ValueError("production response was not 200 for " + path)
        data = response.read(CAP + 1)
        if len(data) > CAP:
            raise ValueError("public response exceeded read-only size cap for " + path)
        return data


def audit():
    app = (ROOT / ASSETS["/app.js"]).read_text(encoding="utf-8")
    html = (ROOT / "web/index.html").read_text(encoding="utf-8")
    for required in (
        'const hiddenIndexerIds=new Set(["subsplease"]);',
        "const RESULTS_PER_PAGE=50;",
        "function renderPagination(total)",
    ):
        if required not in app:
            raise ValueError("reviewed PWA source no longer matches 45/50 requirements")
    if 'id="resultsPagination"' not in html or 'id="selectWorking"' in html:
        raise ValueError("reviewed PWA HTML no longer matches the single-selector/pager contract")
    for endpoint, rel in ASSETS.items():
        expected = (ROOT / rel).read_bytes()
        actual = fetch(endpoint)
        if hashlib.sha256(expected).digest() != hashlib.sha256(actual).digest():
            raise ValueError("public asset SHA-256 mismatch at " + endpoint)
        print("PUBLIC_ASSET_SHA_MATCH:", endpoint, hashlib.sha256(actual).hexdigest()[:16], flush=True)
    public_html = fetch("/").decode("utf-8", errors="replace")
    if 'id="resultsPagination"' not in public_html or 'id="selectWorking"' in public_html or 'id="selectAllProviders"' not in public_html:
        raise ValueError("public indexer picker/pagination HTML mismatch")
    health = json.loads(fetch("/api/health"))
    providers = json.loads(fetch("/api/providers")).get("providers")
    if health.get("ok") is not True or (health.get("total"), health.get("ported")) != (46, 46):
        raise ValueError("public provider/health contract no longer contains 46 ported adapters")
    if not isinstance(providers, list) or len(providers) != 46:
        raise ValueError("public provider catalogue count mismatch")
    ids = [x.get("id") for x in providers if isinstance(x, dict)]
    if len(ids) != 46 or len(set(ids)) != 46 or "subsplease" not in ids:
        raise ValueError("public provider catalog must preserve 46 original backend IDs")
    print("PUBLIC_PWA_45_INDEXERS_50_RESULTS_READONLY: PASS; backend=46; no Cloudflare writes", flush=True)


if __name__ == "__main__":
    try:
        audit()
    except (OSError, TimeoutError, UnicodeError, ValueError, KeyError,
            urllib.error.URLError, urllib.error.HTTPError) as exc:
        print("PUBLIC_PWA_45_INDEXERS_50_RESULTS_READONLY: FAIL (" +
              type(exc).__name__ + ")")
        raise SystemExit(1)
