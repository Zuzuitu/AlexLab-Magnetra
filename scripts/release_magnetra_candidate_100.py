#!/usr/bin/env python3
"""Manual-only exact-version Magnetra 100% promotion / old-version rollback.

NO automatic deployment. Preserves the original Worker at 0% for rollback,
without modifying Cloudflare secrets, source code, DNS, Tunnel or Rock64.
Only the approved known pair of immutable versions is accepted.
"""
from __future__ import annotations

import os
import sys
import time

from deploy_magnetra_zero_percent import (
    _get_api, _current_deployment, _shares, _wrangler_deploy,
)
from inspect_cloudflare_version import VERSION, ROLLBACK, audit

PROMOTE = "CONFIRM_PROMOTE_CANDIDATE_100"
ROLLBACK_ACTION = "CONFIRM_RESTORE_OLD_100"
EXPECTED_BINDINGS = ("BTDIGG_GATEWAY_TOKEN", "MAGNETRA_GATEWAY_TOKEN", "ASSETS")


def old_id(shares: dict[str, float]) -> str | None:
    old = [version for version in shares if version.startswith(ROLLBACK)
           and version != VERSION]
    return old[0] if len(old) == 1 else None


def canary(shares: dict[str, float], old: str) -> bool:
    return shares == {old: 95, VERSION: 5}


def promoted(shares: dict[str, float], old: str) -> bool:
    # Keep both versions in the deployment for a deterministic rollback.
    return shares == {old: 0, VERSION: 100}


def restored(shares: dict[str, float], old: str) -> bool:
    return shares == {old: 100, VERSION: 0}


def binding_preflight() -> None:
    # audit() purposely only reports success for old-only / old100-new0,
    # but its exact candidate binding checks are valid at any split.
    # Never use its 100/0 deployment gate for this later release phase.
    raw = _get_api("/versions/" + VERSION)
    lines, _ = audit(raw, _get_api("/deployments"))
    if ("VERSION_ID_MATCH: PASS" not in lines or
            any(name + ": PASS" not in lines for name in EXPECTED_BINDINGS)):
        raise ValueError("Exact candidate version or required bindings unverified")


def current() -> tuple[dict, dict[str, float], str]:
    deployment = _current_deployment(_get_api("/deployments"))
    shares = _shares(deployment)
    old = old_id(shares)
    if old is None or old == VERSION:
        raise ValueError("Known old Worker version absent from active deployment")
    if not isinstance(deployment.get("id"), str) or not deployment["id"]:
        raise ValueError("Cloudflare deployment ID missing")
    return deployment, shares, old


def stable(deployment: dict, expected: dict[str, float]) -> bool:
    now = _current_deployment(_get_api("/deployments"))
    return now.get("id") == deployment["id"] and _shares(now) == expected


def wait_for(expected: dict[str, float], before: dict[str, float],
             *, success: bool) -> tuple[bool, dict[str, float] | None]:
    """At most four read-only Cloudflare GETs; no retry of a write."""
    observed = None
    for attempt in range(4):
        observed = _shares(_current_deployment(_get_api("/deployments")))
        if observed == expected:
            return success, observed
        if not success or observed != before or attempt == 3:
            break
        time.sleep(2)
    return False, observed


def guarded_restore(old: str) -> bool:
    """Restore old 100% only if no unexpected concurrent version is present."""
    try:
        deployment = _current_deployment(_get_api("/deployments"))
        existing = _shares(deployment)
        if existing == {old: 100} or restored(existing, old):
            print("RESTORE_ALREADY_SAFE: old 100%.")
            return True
        # Any valid but incorrect split of precisely these two immutable
        # versions is ours to restore after a failed promotion. Unknown or
        # third-party versions must never be overwritten.
        if set(existing) != {old, VERSION}:
            print("RESTORE_REFUSED: unknown/concurrent Worker version.")
            return False
        # Double-check before changing traffic; do not overwrite another deploy.
        if not stable(deployment, existing):
            print("RESTORE_REFUSED: concurrent deployment.")
            return False
        print("RESTORING: old 100%, candidate 0%.")
        deployed = _wrangler_deploy(
            [old + "@100%", VERSION + "@0%"],
            "Magnetra guarded rollback: old 100%, candidate 0%",
        )
        try:
            ok, observed = wait_for(restored_target := {old: 100, VERSION: 0},
                                    existing, success=deployed)
        except ValueError:
            print("RESTORE_UNVERIFIED: read-only Cloudflare postflight failed.")
            return False
        if ok and observed == restored_target:
            print("RESTORE_POSTFLIGHT_PASS: old 100%, candidate 0%.")
            return True
        print("RESTORE_UNVERIFIED: manual Cloudflare inspection required.")
        return False
    except ValueError:
        print("RESTORE_UNVERIFIED: sanitized metadata failure.")
        return False


def promote() -> int:
    binding_preflight()
    before, shares, old = current()
    if not canary(shares, old):
        print("STOP: promotion requires exact old 95% / candidate 5% canary.")
        return 2
    if not stable(before, shares):
        print("STOP: deployment changed during preflight.")
        return 2

    print("PROMOTION_PREFLIGHT_PASS: exact old 95% / candidate 5%; bindings present.")
    print("PROMOTING: old retained at 0%, exact candidate 100%.")
    success = _wrangler_deploy(
        [old + "@0%", VERSION + "@100%"],
        "Magnetra explicitly approved candidate 100% release with old 0% rollback slot",
    )
    expected = {old: 0, VERSION: 100}
    try:
        ok, observed = wait_for(expected, shares, success=success)
    except ValueError:
        print("CRITICAL: promotion postflight metadata unreadable; guarded rollback.")
        guarded_restore(old)
        return 1
    if ok and observed == expected:
        print("PROMOTION_POSTFLIGHT_PASS: exact candidate 100%, old 0% available for rollback.")
        print("NOTE: API traffic state confirmed; end-user PWA UX still requires acceptance.")
        return 0
    if observed == shares:
        print("PROMOTION_UNVERIFIED: Cloudflare last showed 95/5; inspect before retry.")
        return 1
    if observed is not None and set(observed).issubset({old, VERSION}):
        print("PROMOTION_INCORRECT_SPLIT: attempting safe rollback to old 100%.")
        guarded_restore(old)
    else:
        print("CRITICAL: unknown concurrent deployment; refusing rollback.")
    return 1


def rollback() -> int:
    _, shares, old = current()
    if restored(shares, old) or shares == {old: 100}:
        print("RESTORE_ALREADY_SAFE: old 100%; no write.")
        return 0
    if not (promoted(shares, old) or canary(shares, old)):
        print("STOP: rollback allowed only from exact known 0/100 or 95/5 slot.")
        return 2
    return 0 if guarded_restore(old) else 1


def execute() -> int:
    choice = os.environ.get("MAGNETRA_RELEASE_ACTION", "")
    if choice == PROMOTE:
        return promote()
    if choice == ROLLBACK_ACTION:
        return rollback()
    print("STOP: separate explicit 100% promotion or rollback approval absent.")
    return 2


def main() -> int:
    try:
        return execute()
    except ValueError:
        print("STOP: fail-closed Cloudflare preflight error (raw metadata withheld).")
        return 2


if __name__ == "__main__":
    sys.exit(main())
