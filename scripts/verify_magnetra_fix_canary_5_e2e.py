#!/usr/bin/env python3
"""Read-only exact-5%-canary E2E with version-specific static asset attribution.

Validates Cloudflare 249d@95%/540b@5% and selects EACH immutable version via
Workers-Version-Overrides, NOT random unauthenticated 95/5 routing. Runs one
bounded 2026 OxTorrent/Torrent9 query and two original detail resolves on the
540b fix. Never contacts BTDigg/EZTV, downloads torrents or sends Flud.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request

from deploy_magnetra_zero_percent import _current_deployment, _get_api, _shares
from inspect_magnetra_fix_stage import ACTIVE, STAGED, EXPECTED, binding_pairs
import verify_magnetra_fix_zero_e2e as source
from deploy_magnetra_fix_canary_5 import FIVE

ACTION = "RUN_READONLY_FIX_540B_CANARY"
OLD_OVERRIDE = 'alexlab-magnetra="' + ACTIVE + '"'
MAX_ASSET_BYTES = 800_000


class Stop(Exception):
    pass


def metadata_gate() -> str:
    version = _get_api("/versions/" + STAGED)
    if (not isinstance(version, dict) or version.get("success") is not True
            or not isinstance(version.get("result"), dict)
            or version["result"].get("id") != STAGED):
        raise Stop("CANARY_FIX_VERSION_ID_UNVERIFIED")
    pairs = binding_pairs(version)
    if not all(any((name, kind) in pairs for kind in allowed)
               for name, allowed in EXPECTED.items()):
        raise Stop("CANARY_FIX_BINDINGS_UNVERIFIED")
    record = _current_deployment(_get_api("/deployments"))
    if _shares(record) != FIVE:
        raise Stop("EXACT_CANARY_249D95_540B5_NOT_CONFIRMED")
    if not isinstance(record.get("id"), str) or not record["id"]:
        raise Stop("CANARY_DEPLOYMENT_ID_MISSING")
    print("CANARY_METADATA_GATE: PASS (249d 95%, 540b 5%, 3 bindings).")
    return record["id"]


def get_explicit_old_asset() -> bytes:
    req = urllib.request.Request(
        "https://index.alexlab.media/app.js",
        headers={
            "Cloudflare-Workers-Version-Overrides": OLD_OVERRIDE,
            "Accept": "text/javascript,application/javascript",
            "Accept-Encoding": "identity",
            "Cache-Control": "no-store",
            "User-Agent": "AlexLab-Magnetra-ExactOldVersionAssetAudit/1.0",
        },
        method="GET",
    )
    try:
        with urllib.request.build_opener(source.NoRedirect).open(req, timeout=17) as response:
            if response.status != 200 or "javascript" not in response.headers.get("content-type", ""):
                raise Stop("OLD_249D_ASSET_UNVERIFIED")
            body = response.read(MAX_ASSET_BYTES + 1)
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, TimeoutError):
        raise Stop("OLD_249D_ASSET_TRANSPORT_UNVERIFIED") from None
    if not body or len(body) > MAX_ASSET_BYTES:
        raise Stop("OLD_249D_ASSET_LENGTH_UNVERIFIED")
    return body


def verify_versions_immutable_assets():
    new_asset = source.http_get("/app.js", staged=True)
    old_asset = get_explicit_old_asset()
    reviewed = (Path(__file__).resolve().parent.parent / "web" / "app.js").read_bytes()
    digest = lambda b: hashlib.sha256(b).digest()
    if digest(new_asset) != digest(reviewed):
        raise Stop("FIX_540B_APP_JS_DOES_NOT_MATCH_REVIEWED_CODE")
    if digest(old_asset) == digest(reviewed):
        raise Stop("OLD_249D_APP_JS_IDENTICAL_TO_FIX_OVERRIDE_UNVERIFIED")
    print("EXACT_TWO_VERSION_APP_JS: PASS (fix matches GitHub, old differs).")


def execute() -> int:
    if os.environ.get("MAGNETRA_FIX_CANARY_E2E_ACTION") != ACTION:
        raise Stop("EXPLICIT_CANARY_E2E_OWNER_APPROVAL_REQUIRED")
    before_id = metadata_gate()
    verify_versions_immutable_assets()
    source.verify_provider_catalog()
    source.verify_original_sources()
    if metadata_gate() != before_id:
        raise Stop("DEPLOYMENT_CHANGED_DURING_CANARY_SOURCE_TEST")
    print("FIX_540B_CANARY_E2E: PASS (redacted valid BTIH per original HTML provider, no deploy/retry/BTDigg/Flud).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(execute())
    except (Stop, source.Stop) as exc:
        print("FIX_540B_CANARY_E2E: STOP " + str(exc))
        sys.exit(1)
    except (ValueError, TypeError, KeyError):
        print("FIX_540B_CANARY_E2E: STOP_UNVERIFIED_METADATA (sanitized)")
        sys.exit(1)
