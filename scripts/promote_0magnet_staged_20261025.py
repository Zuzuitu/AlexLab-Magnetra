#!/usr/bin/env python3
"""Promote ALREADY staged immutable 0Magnet code from 0 to 5 to 100.

No version uploads. Refuse any unexpected Cloudflare deployment, account,
bindings, sources or candidate assets. Roll back to previously working
916d@100 only if known canary/full deployment fails.
"""
from __future__ import annotations
import os
import sys
import release_0magnet_details_first_20261024 as g
from inspect_companion_binding_readonly import Stop as AccountStop

CANDIDATE = "763defbe-38aa-4299-acf1-1639a59e7be6"
ACTION = "CONFIRM_0MAGNET_STAGED_CANDIDATE_PROMOTION_20261025"
BASELINE = {g.ACTIVE: 100, CANDIDATE: 0}
CANARY = {g.ACTIVE: 95, CANDIDATE: 5}
FULL = {g.ACTIVE: 0, CANDIDATE: 100}


def preflight():
    g.source_guard()
    g.verify_account_scripts(g.account_list())
    initial = g.current(BASELINE)
    for version in BASELINE:
        g.verify_binding_payload(version, g._get_api("/versions/" + version))
    g.stable(initial, BASELINE)
    print("EXACT_STAGED_916D100_CANDIDATE0_AND_FOUR_BINDINGS: PASS", flush=True)
    # Live read-only evidence #40137647537 confirms the exact immutable
    # candidate app.js SHA and provider catalogue. Recheck immediately here.
    g.verify_candidate(CANDIDATE)
    g.stable(initial, BASELINE)
    g.prove_real_owner_magnet(CANDIDATE)
    g.stable(initial, BASELINE)
    print("ORIGINAL_0MAGNET_EXACT_OWNER_SOURCE: PASS", flush=True)
    return initial


def promote():
    before = preflight()
    # No upload, no 0%-slot creation, no legacy release workflow rerun.
    staged = g.transition(before, BASELINE, CANARY, "OWNER_CANARY_5", CANDIDATE)
    g.verify_candidate(CANDIDATE)
    g.stable(staged, CANARY)
    print("CANDIDATE_CANARY_5_POSTFLIGHT: PASS", flush=True)
    full = g.transition(staged, CANARY, FULL, "OWNER_FULL_100", CANDIDATE)
    g.public_postflight(CANDIDATE)
    g.stable(full, FULL)
    print("MAGNETRA_0MAGNET_PRODUCTION_CANDIDATE_100_PASS", flush=True)
    print("THE_RARBG_PRIOR_ACTIVE_PRESERVED_AT_0_FOR_ROLLBACK", flush=True)
    print("REAL_IPHONE_SAME_CARD_ACCEPTANCE_PENDING", flush=True)
    return 0


def main():
    if os.environ.get("MAGNETRA_0MAGNET_PROMOTION_ACTION") != ACTION:
        print("STOP_EXPLICIT_0MAGNET_PROMOTION_APPROVAL_REQUIRED", flush=True)
        return 2
    try:
        return promote()
    except (g.Stop, AccountStop, ValueError, TypeError, KeyError, OSError):
        print("PROMOTION_STOP_UNVERIFIED_OR_FAILED_NO_SUCCESS_ASSUMED", flush=True)
        g.rollback_if_safe(CANDIDATE)
        return 1


if __name__ == "__main__":
    sys.exit(main())
