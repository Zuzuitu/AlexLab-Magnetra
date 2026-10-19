#!/usr/bin/env python3
"""Owner-gated exact 249d95/540b5 -> 249d0/540b100 release.

Code preparation/PR/merge NEVER changes traffic. ONLY manually dispatching the
reviewed workflow with the explicit action permits one version-only write.
The previous immutable 249d remains as a 0% slot for a separate rollback.
No Worker uploads, secrets mutation, tunnel/DNS/Rock64 changes, Flud or .torrent.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import sys
import time

from deploy_magnetra_zero_percent import _current_deployment, _get_api, _shares, _wrangler_deploy
from inspect_magnetra_fix_stage import ACTIVE, STAGED, EXPECTED, binding_pairs
from deploy_magnetra_fix_canary_5 import FIVE, ZERO
import verify_magnetra_fix_canary_5_e2e as canary

PROMOTE = "CONFIRM_PROMOTE_FIX_540B_100"
RESTORE = "CONFIRM_RESTORE_249D_FROM_FIX_540B_100"
FULL = {ACTIVE: 0, STAGED: 100}


class Stop(Exception):
    """Fail-closed error code: no raw Cloudflare/site response in logs."""


def verify_bindings(version_id: str) -> None:
    if version_id not in (ACTIVE, STAGED):
        raise Stop("UNKNOWN_VERSION_REFUSED")
    data = _get_api("/versions/" + version_id)
    if (not isinstance(data, dict) or data.get("success") is not True
            or not isinstance(data.get("result"), dict)
            or data["result"].get("id") != version_id):
        raise Stop("EXACT_VERSION_METADATA_UNVERIFIED")
    pairs = binding_pairs(data)
    for name, kinds in EXPECTED.items():
        if not any((name, kind) in pairs for kind in kinds):
            raise Stop("REQUIRED_VERSION_BINDING_UNVERIFIED_" + name)


def snapshot() -> tuple[dict, dict[str, float]]:
    record = _current_deployment(_get_api("/deployments"))
    if not isinstance(record.get("id"), str) or not record["id"]:
        raise Stop("CLOUDFLARE_DEPLOYMENT_ID_UNVERIFIED")
    shares = _shares(record)
    if set(shares) != {ACTIVE, STAGED}:
        raise Stop("UNKNOWN_THIRD_OR_MISSING_VERSION_REFUSED")
    return record, shares


def verify_stable(before: dict, expected: dict[str, float]) -> None:
    after, shares = snapshot()
    if before["id"] != after["id"] or shares != expected:
        raise Stop("CONCURRENT_DEPLOYMENT_REFUSED")


def read_only_preflight() -> dict:
    """One real-source E2E and two exact-version JS checks BEFORE any write."""
    verify_bindings(ACTIVE)
    verify_bindings(STAGED)
    before, shares = snapshot()
    if shares != FIVE:
        raise Stop("EXPECTED_EXACT_249D95_540B5_CANARY_MISSING")
    canary.verify_versions_immutable_assets()
    canary.source.verify_provider_catalog()
    canary.source.verify_original_sources()
    verify_stable(before, FIVE)
    print("PROMOTION_SOURCE_PREFLIGHT_PASS: immutable dual assets, 46 IDs, OxTorrent/Torrent9 authentic BTIH (redacted).")
    return before


def confirm_postflight(previous_id: str, before: dict[str, float],
                       target: dict[str, float], wrote: bool) -> bool:
    """Only bounded metadata reads. Never repeat a Wrangler write."""
    for attempt in range(4):
        record, shares = snapshot()
        if shares == target:
            # An already-existing target after a failed CLI call cannot
            # independently prove this dispatch performed a safe write.
            if not wrote or record["id"] == previous_id:
                raise Stop("TARGET_VISIBLE_BUT_WRITE_UNVERIFIED")
            return True
        if shares != before:
            raise Stop("UNEXPECTED_TRAFFIC_SPLIT_NO_AUTOMATIC_ROLLBACK")
        if not wrote or attempt == 3:
            return False
        time.sleep(2)
    return False


def promote() -> int:
    before = read_only_preflight()
    verify_stable(before, FIVE)
    print("PROMOTION_PREFLIGHT_PASS: exact 249d 95%, 540b 5%; stable deployment.")
    print("PROMOTION_APPLYING: previous 249d 0%, fixed 540b 100%.")
    wrote = _wrangler_deploy(
        [ACTIVE + "@0%", STAGED + "@100%"],
        "Magnetra separately owner-approved exact 540b 100% Resolve fix; 249d retained at 0%",
    )
    if not confirm_postflight(before["id"], FIVE, FULL, wrote):
        raise Stop("PROMOTION_NOT_CONFIRMED_CHECK_CLOUDFLARE_MANUALLY")
    verify_bindings(ACTIVE)
    verify_bindings(STAGED)
    canary.verify_versions_immutable_assets()
    canary.source.verify_provider_catalog()
    # Static asset routing may briefly lag a successful Cloudflare version-only
    # deployment. Retry ONLY a successful HTTP-200 /app.js whose hash is old;
    # never retry an HTTP error, provider request, 429 or 504, or write twice.
    reviewed = (Path(__file__).resolve().parent.parent / "web" / "app.js").read_bytes()
    reviewed_hash = hashlib.sha256(reviewed).digest()
    public_asset_verified = False
    post_deployment_id = None
    for attempt in range(4):
        public_js = canary.source.http_get("/app.js", staged=False)
        if hashlib.sha256(public_js).digest() == reviewed_hash:
            public_asset_verified = True
            break
        record, shares = snapshot()
        if shares != FULL or (post_deployment_id is not None and record["id"] != post_deployment_id):
            raise Stop("PROMOTION_POSTFLIGHT_DEPLOYMENT_CHANGED")
        post_deployment_id = record["id"]
        if attempt < 3:
            time.sleep(2)
    if not public_asset_verified:
        raise Stop("PROMOTION_POSTFLIGHT_PUBLIC_ASSET_UNVERIFIED")
    print("PROMOTION_POSTFLIGHT_PASS: 249d 0%, 540b 100%, binding/JS/catalog verified.")
    print("IPHONE_UX_ACCEPTANCE: PENDING explicit human Resolve tests, no Flud auto-send.")
    return 0


def rollback() -> int:
    verify_bindings(ACTIVE)
    verify_bindings(STAGED)
    before, shares = snapshot()
    if shares == ZERO:
        print("ROLLBACK_ALREADY_SAFE: 249d 100%, 540b 0%, no write.")
        return 0
    # Recovery from 5% canary is handled by the EXISTING manual workflow.
    if shares != FULL:
        raise Stop("ROLLBACK_REQUIRES_EXACT_249D0_540B100_SLOT")
    verify_stable(before, FULL)
    print("ROLLBACK_APPLYING: exact 249d 100%, 540b 0%.")
    wrote = _wrangler_deploy(
        [ACTIVE + "@100%", STAGED + "@0%"],
        "Magnetra separately owner-approved Restore 249d 100% after 540b release",
    )
    if not confirm_postflight(before["id"], FULL, ZERO, wrote):
        raise Stop("ROLLBACK_NOT_CONFIRMED_CHECK_CLOUDFLARE_MANUALLY")
    print("ROLLBACK_POSTFLIGHT_PASS: old 249d 100%, fix 540b 0%.")
    return 0


def execute() -> int:
    action = os.environ.get("MAGNETRA_FIX_FULL_ACTION", "")
    if action not in (PROMOTE, RESTORE):
        print("STOP: explicit owner promotion or rollback choice missing; no network or write.")
        return 2
    try:
        return promote() if action == PROMOTE else rollback()
    except (Stop, canary.Stop, canary.source.Stop) as exc:
        print("FIX_FULL_RELEASE_STOP: " + str(exc))
        return 1
    except (ValueError, TypeError, KeyError, OSError):
        print("FIX_FULL_RELEASE_STOP: sanitized metadata/transport failure; no speculative recovery.")
        return 1


if __name__ == "__main__":
    sys.exit(execute())
