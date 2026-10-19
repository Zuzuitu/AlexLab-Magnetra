#!/usr/bin/env python3
"""Manual-only Cloudflare 249d 100% / 540b 0% Resolve-fix E2E slot.

Attaching a 0%-share is a deployment RECORD mutation even though it does not
shift normal traffic. Never run without explicit owner action on main.
This workflow DOES NOT upload Worker code, assets, secrets or new bindings.
"""
from __future__ import annotations

import os
import sys
import time

from deploy_magnetra_zero_percent import (
    _current_deployment, _get_api, _shares, _wrangler_deploy,
)
from inspect_cloudflare_version import VERSION as CURRENT, ROLLBACK
from inspect_magnetra_fix_stage import STAGED, audit

APPROVAL = "CONFIRM_CURRENT_100_FIX_0"


def allowed_preflight(shares: dict[str, float]) -> bool:
    previous = [v for v in shares if v.startswith(ROLLBACK)]
    return shares == {CURRENT: 100} or (
        len(previous) == 1 and shares == {CURRENT: 100, previous[0]: 0}
    )


def desired(shares: dict[str, float]) -> bool:
    return shares == {CURRENT: 100, STAGED: 0}


def unchanged(before: dict, shares: dict[str, float]) -> bool:
    """Refuse an operation if any concurrent deployment changed its identity."""
    after = _current_deployment(_get_api("/deployments"))
    return (isinstance(before.get("id"), str) and bool(before["id"])
            and after.get("id") == before["id"] and _shares(after) == shares)


def postflight(expected: dict[str, float],
               original: dict[str, float], written: bool) -> tuple[bool, dict[str, float] | None]:
    observed = None
    for attempt in range(4):
        observed = _shares(_current_deployment(_get_api("/deployments")))
        if observed == expected:
            return written, observed
        # Wrangler may return before the Cloudflare GET API sees the new slot.
        # Never repeat the WRITE or poll if an unknown/modified split appears.
        if not written or observed != original or attempt == 3:
            break
        time.sleep(2)
    return False, observed


def guarded_restore() -> bool:
    """Restore CURRENT=100 only when the exact pair of versions is recognized."""
    try:
        before = _current_deployment(_get_api("/deployments"))
        shares = _shares(before)
        if shares == {CURRENT: 100} or desired(shares):
            print("SAFE_TRAFFIC: current 100%, new fix 0% or absent.")
            return True
        if set(shares) != {CURRENT, STAGED}:
            print("ROLLBACK_REFUSED: unknown or concurrent version.")
            return False
        if not unchanged(before, shares):
            print("ROLLBACK_REFUSED: deployment changed before write.")
            return False
        print("RESTORING_TRAFFIC: current 100%, staged fix 0%.")
        result = _wrangler_deploy(
            [CURRENT + "@100%", STAGED + "@0%"],
            "Magnetra Resolve fix guarded restore: current 100%, fix 0%",
        )
        expected = {CURRENT: 100, STAGED: 0}
        confirmed, observed = postflight(expected, shares, result)
        if confirmed and observed == expected:
            print("ROLLBACK_POSTFLIGHT_PASS: current 100%, fix 0%.")
            return True
        print("ROLLBACK_NOT_CONFIRMED: manual Cloudflare inspection required.")
        return False
    except (ValueError, TypeError, KeyError):
        print("ROLLBACK_UNVERIFIED: metadata error withheld.")
        return False


def execute() -> int:
    if os.environ.get("MAGNETRA_FIX_ZERO_ACTION") != APPROVAL:
        print("STOP: explicit owner approval required; no Cloudflare GET/POST performed.")
        return 2
    # The immutable upload is not sufficient by itself: a fresh Cloudflare
    # metadata check must confirm both secret binding names/types and ASSETS.
    version = _get_api("/versions/" + STAGED)
    deployments = _get_api("/deployments")
    messages, safe = audit(version, deployments)
    if not safe:
        print("STOP: exact 540b bindings or existing 249d 100%-traffic gate failed.")
        for m in messages:
            if m.endswith(("FAIL", "UNVERIFIED")):
                print(m)
        return 2
    before = _current_deployment(deployments)
    shares = _shares(before)
    if not allowed_preflight(shares):
        print("STOP: unexpected Cloudflare version set or percentage.")
        return 2
    if not unchanged(before, shares):
        print("STOP: another deployment arrived during preflight; no write.")
        return 2
    print("SLOT_PREFLIGHT_PASS: 540b three bindings; 249d 100% production.")
    print("APPLYING_ZERO_SLOT: existing 249d 100%, new 540b 0%; traffic unchanged.")
    wrote = _wrangler_deploy(
        [CURRENT + "@100%", STAGED + "@0%"],
        "Magnetra owner-approved Resolve fix E2E slot: existing 100%, new 0%",
    )
    try:
        success, observed = postflight({CURRENT: 100, STAGED: 0}, shares, wrote)
    except (ValueError, TypeError, KeyError):
        print("SLOT_POSTFLIGHT_UNVERIFIED: metadata read failed; inspect before retry.")
        return 1
    if success and desired(observed):
        print("ZERO_SLOT_POSTFLIGHT_PASS: old active 249d 100%, new fix 540b 0%.")
        print("E2E_NEXT: stage is selectable by exact Worker Version Override only.")
        return 0
    if observed == shares:
        print("SLOT_POSTFLIGHT_UNCONFIRMED: latest API still shows previous safe 100% split.")
        return 1
    if observed is not None and set(observed).issubset({CURRENT, STAGED}):
        print("SLOT_UNEXPECTED_KNOWN_SPLIT: guarded restore current 100%.")
        guarded_restore()
    else:
        print("CRITICAL: unknown concurrent deployment; refusing write-based recovery.")
    return 1


def main() -> int:
    try:
        return execute()
    except (ValueError, TypeError, KeyError):
        print("STOP: fail-closed sanitized Cloudflare metadata error.")
        return 2


if __name__ == "__main__":
    sys.exit(main())
