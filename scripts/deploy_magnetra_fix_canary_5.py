#!/usr/bin/env python3
"""Exact-version 5% canary for the owner-tested Magnetra Resolve PWA fix.

Only manual GitHub workflow_dispatch with explicit owner action can mutate
Cloudflare traffic. Current 249d stays at least 95% until separate approval
for a future 100% promotion. The staged 540b version has already passed
zero-percent authenticated source E2E (#39311804881). No source/Flud calls here.
"""
from __future__ import annotations

import os
import sys
import time

from deploy_magnetra_zero_percent import _current_deployment, _get_api, _shares, _wrangler_deploy
from inspect_magnetra_fix_stage import ACTIVE, STAGED, EXPECTED, binding_pairs

CANARY = "CONFIRM_FIX_540B_CANARY_5"
RESTORE = "CONFIRM_RESTORE_249D_100"
ZERO = {ACTIVE: 100, STAGED: 0}
FIVE = {ACTIVE: 95, STAGED: 5}


def valid_binding_metadata() -> bool:
    data = _get_api("/versions/" + STAGED)
    if (not isinstance(data, dict) or data.get("success") is not True or
            not isinstance(data.get("result"), dict) or
            data["result"].get("id") != STAGED):
        return False
    pairs = binding_pairs(data)
    return all(any((name, kind) in pairs for kind in types)
               for name, types in EXPECTED.items())


def current() -> tuple[dict, dict[str, float]]:
    record = _current_deployment(_get_api("/deployments"))
    if not isinstance(record.get("id"), str) or not record["id"]:
        raise ValueError("deployment identity unverified")
    return record, _shares(record)


def unchanged(record: dict, shares: dict[str, float]) -> bool:
    newer, latest = current()
    return newer.get("id") == record.get("id") and latest == shares


def wait_for(expected: dict[str, float], before: dict[str, float],
             confirmed_write: bool) -> tuple[bool, dict[str, float] | None]:
    last = None
    for index in range(4):
        _, last = current()
        if last == expected:
            return confirmed_write, last
        # Do not retry the WRITE; allow only bounded Cloudflare metadata reads.
        if not confirmed_write or last != before or index == 3:
            break
        time.sleep(2)
    return False, last


def safe_restore() -> bool:
    """Restore 249d@100/540b@0 only if known IDs and stable deployment."""
    try:
        record, shares = current()
        if shares == ZERO:
            print("ROLLBACK_ALREADY_SAFE: current 249d 100%, new 540b 0%.")
            return True
        if set(shares) != {ACTIVE, STAGED}:
            print("ROLLBACK_REFUSED: unknown or concurrent Worker deployment.")
            return False
        if not unchanged(record, shares):
            print("ROLLBACK_REFUSED: concurrent change before write.")
            return False
        print("ROLLBACK_APPLYING: current 249d 100%, staged 540b 0%.")
        wrote = _wrangler_deploy(
            [ACTIVE + "@100%", STAGED + "@0%"],
            "Magnetra owner-requested guarded Resolve fix rollback to 249d",
        )
        ok, observed = wait_for(ZERO, shares, wrote)
        if ok:
            print("ROLLBACK_POSTFLIGHT_PASS: current 100%, fix 0%.")
            return True
        if observed == ZERO:
            print("ROLLBACK_SAFE_BUT_CLI_UNVERIFIED: current 100%, fix 0%.")
            return False
        print("ROLLBACK_UNVERIFIED: Cloudflare metadata not confirmed.")
        return False
    except (ValueError, KeyError, TypeError):
        print("ROLLBACK_UNVERIFIED: Cloudflare metadata error withheld.")
        return False


def activate_canary() -> int:
    if not valid_binding_metadata():
        print("CANARY_STOP: exact 540b staged bindings not verified.")
        return 2
    record, shares = current()
    if shares != ZERO:
        print("CANARY_STOP: expected exact active 249d 100%, fix 540b 0% slot.")
        return 2
    if not unchanged(record, shares):
        print("CANARY_STOP: concurrent deployment before write.")
        return 2

    print("CANARY_PREFLIGHT_PASS: exact 249d 100/540b 0, three bindings verified.")
    print("CANARY_APPLYING: bounded 249d 95%, 540b 5%.")
    wrote = _wrangler_deploy(
        [ACTIVE + "@95%", STAGED + "@5%"],
        "Magnetra explicitly owner-approved Resolve fix 540b bounded 5% canary",
    )
    try:
        ok, observed = wait_for(FIVE, ZERO, wrote)
    except (ValueError, KeyError, TypeError):
        print("CANARY_POSTFLIGHT_UNVERIFIED: metadata unreadable, guarded restoration.")
        safe_restore()
        return 1
    if ok and observed == FIVE:
        print("CANARY_POSTFLIGHT_PASS: old 249d 95%, fix 540b 5%.")
        print("NOTE: canary percentage confirmed, NOT full production promotion or mobile acceptance.")
        return 0
    if observed == FIVE and not wrote:
        print("CANARY_SHARE_95_5_BUT_CLI_UNVERIFIED: manual inspection required.")
        return 1
    if observed == ZERO:
        print("CANARY_NOT_CONFIRMED: Cloudflare still shows safe old 100/new 0.")
        return 1
    if observed is not None and set(observed) == {ACTIVE, STAGED}:
        print("CANARY_UNEXPECTED_KNOWN_SHARES: guarded restore current 100%.")
        safe_restore()
    else:
        print("CANARY_CRITICAL_UNKNOWN_DEPLOYMENT: refusing speculative rollback.")
    return 1


def execute() -> int:
    choice = os.environ.get("MAGNETRA_FIX_CANARY_ACTION", "")
    if choice not in (CANARY, RESTORE):
        print("STOP: explicit owner canary/rollback action required; no Cloudflare requests.")
        return 2
    if choice == CANARY:
        return activate_canary()
    try:
        _, shares = current()
        if shares == ZERO:
            print("ROLLBACK_ALREADY_SAFE: current 100%, staged 0%.")
            return 0
        if shares != FIVE:
            print("ROLLBACK_STOP: permitted only from exact 95/5 canary, or already 100/0.")
            return 2
        return 0 if safe_restore() else 1
    except (ValueError, KeyError, TypeError):
        print("ROLLBACK_STOP: unverified Cloudflare metadata.")
        return 2


def main() -> int:
    try:
        return execute()
    except (ValueError, KeyError, TypeError):
        print("STOP: sanitized Cloudflare metadata failure.")
        return 2


if __name__ == "__main__":
    sys.exit(main())
