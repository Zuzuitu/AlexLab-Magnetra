#!/usr/bin/env python3
"""Read-only public 100% postflight attribution; no deployments, retries or secrets output.

Checks Cloudflare version-only traffic metadata, compares SHA-256 of the reviewed
PWA JS to fixed-version, old-version and unauthenticated public responses, and
executes one bounded public Resolve E2E for each of two known HTML providers.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import sys
import urllib.error
import urllib.request

from deploy_magnetra_zero_percent import _current_deployment, _get_api, _shares
from inspect_magnetra_fix_stage import ACTIVE, STAGED
import verify_magnetra_fix_zero_e2e as source
from diagnose_magnetra_detail_routes import route_shape
from urllib.parse import urlencode

ORIGIN = "https://index.alexlab.media"
MAX_JS = 800_000


def asset(label: str, *, version: str = "", suffix: str = "") -> bytes:
    headers = {
        "Accept-Encoding": "identity",
        "Accept": "text/javascript,application/javascript",
        "Cache-Control": "no-cache, no-store, max-age=0",
        "Pragma": "no-cache",
        "User-Agent": "AlexLab-Magnetra-ReadonlyPostflight/1.0",
    }
    if version:
        headers["Cloudflare-Workers-Version-Overrides"] = 'alexlab-magnetra="' + version + '"'
    req = urllib.request.Request(ORIGIN + "/app.js" + suffix, headers=headers)
    try:
        with urllib.request.build_opener(source.NoRedirect).open(req, timeout=20) as res:
            status = res.status
            mime = res.headers.get("content-type", "")
            cache = res.headers.get("cf-cache-status", "unreported")
            age = res.headers.get("age", "unreported")
            body = res.read(MAX_JS + 1)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(label + ": HTTP_" + str(exc.code)) from None
    except (urllib.error.URLError, OSError, TimeoutError):
        raise RuntimeError(label + ": TRANSPORT_UNVERIFIED") from None
    if status != 200 or "javascript" not in mime or not body or len(body) > MAX_JS:
        raise RuntimeError(label + ": ASSET_RESPONSE_UNVERIFIED") 
    print("ASSET_" + label + ": SHA256=" + hashlib.sha256(body).hexdigest()[:16] +
          " BYTES=" + str(len(body)) + " CF_CACHE=" + cache[:35] + " AGE=" + age[:20])
    return body


def public_original_sources() -> None:
    providers = source.http_get("/api/providers", staged=False).get("providers")
    if not isinstance(providers, list):
        raise RuntimeError("PUBLIC_PROVIDER_CATALOG_INVALID")
    ids = [x.get("id") for x in providers if isinstance(x, dict)]
    print("PUBLIC_PROVIDER_CATALOG: unique=" + str(len(set(ids))) + " total=" + str(len(ids)))
    query = urlencode({"q": "2026", "providers": "oxtorrent,torrent9", "category": "all"})
    payload = source.http_get("/api/search?" + query, staged=False)
    rows, errors = payload.get("results"), payload.get("errors")
    if not isinstance(rows, list) or not isinstance(errors, list) or errors or len(rows) > 200:
        raise RuntimeError("PUBLIC_SEARCH_UNVERIFIED_OR_ERRORS")
    for provider in ("oxtorrent", "torrent9"):
        options = [r for r in rows if isinstance(r, dict) and r.get("provider") == provider
                   and route_shape(provider, r.get("details")) == "CANONICAL_DETAIL"
                   and not source.valid_magnet(r.get("magnet"))]
        print("PUBLIC_SEARCH_" + provider + ": unresolved_canonical=" + str(len(options)))
        if not options:
            raise RuntimeError("PUBLIC_SOURCE_NOT_RESOLVABLE_" + provider)
        resolved = source.http_get("/api/resolve", staged=False,
                                   payload={"provider": provider, "details": options[0]["details"]})
        if resolved.get("provider") != provider or not source.valid_magnet(resolved.get("magnet")):
            raise RuntimeError("PUBLIC_RESOLVE_FAILURE_" + provider)
        print("PUBLIC_RESOLVE_" + provider + ": PASS valid redacted BTIH")


def main() -> int:
    dep = _current_deployment(_get_api("/deployments"))
    shares = _shares(dep)
    old_share, new_share = shares.get(ACTIVE), shares.get(STAGED)
    print("LIVE_CLOUDFLARE_SPLIT: 249d=" + str(old_share) + "% 540b=" + str(new_share) +
          "% known_versions=" + str(len(shares)))
    if shares != {ACTIVE: 0, STAGED: 100}:
        print("DIAG_STOP: NOT_EXACT_249D0_540B100; no traffic actions")
        return 2

    reviewed = (Path(__file__).resolve().parent.parent / "web" / "app.js").read_bytes()
    print("REVIEWED_APP_JS: SHA256=" + hashlib.sha256(reviewed).hexdigest()[:16] +
          " BYTES=" + str(len(reviewed)))
    new = asset("FIX_OVERRIDE", version=STAGED)
    old = asset("OLD_OVERRIDE", version=ACTIVE)
    public = asset("PUBLIC_UNOVERRIDDEN")
    busted = asset("PUBLIC_CACHE_BUSTED", suffix="?magnetra_postflight_audit=20261020")
    for label, body in (("FIX_OVERRIDE", new), ("OLD_OVERRIDE", old),
                        ("PUBLIC_UNOVERRIDDEN", public), ("PUBLIC_CACHE_BUSTED", busted)):
        classification = ("REVIEWED_FIX" if body == reviewed else
                          "OLD_VERSION" if body == old else
                          "FIX_OVERRIDE_DIFFERENT_LOCAL" if body == new else "UNKNOWN")
        print("ATTRIBUTION_" + label + ": " + classification)
    print("ASSET_ROOT_CAUSE_CLUE: public_vs_busted=" + ("SAME" if public == busted else "DIFFERENT"))
    try:
        public_original_sources()
    except (RuntimeError, source.Stop) as exc:
        print("PUBLIC_SOURCE_E2E: NOT_VERIFIED " + str(exc))
    print("READONLY_DIAGNOSTIC_COMPLETE: metadata and asset hashes only; NO_DEPLOY_NO_ROLLBACK")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, ValueError, TypeError, KeyError) as exc:
        # Deliberately sanitize unexpected transport/data exceptions.
        print("READONLY_DIAGNOSTIC_STOP: " + (str(exc) if isinstance(exc, RuntimeError) else "UNVERIFIED_METADATA"))
        sys.exit(1)
