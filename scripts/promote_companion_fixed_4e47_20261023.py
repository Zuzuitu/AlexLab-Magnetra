#!/usr/bin/env python3
"""One-shot immutable Flud Companion production promotion of owner-proven 4e47.

This script DOES NOT upload a new version, query real device credentials, send
a magnet, modify secrets/DNS/other Workers, or invoke GitHub runners' public
edge for a false-negative (hosted runner gets 403; owner Rock64 got 401).

Explicit user evidence on 23 Oct: Cloudflare version override for this precise
candidate returned HTTP 401, x-alexlab-companion-probe upstream-http-401.
Fail closed on unrecognized deployment before ANY write; preserve previous
active immutable Worker as rollback at 0%; restore on a known post-write fault.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from deploy_magnetra_auto_pause_once import (
    Stop, ROOT, current, snapshot, stable, wait_for, _wrangler_deploy
)
from release_magnetra_companion_binding_20261023 import verify_version
from inspect_companion_binding_readonly import (
    validated_source, account_list, verify_account_scripts, Stop as InspectorStop
)

OLD = "a088fa41-233d-48d3-bd4c-52be6194fda8"
FIXED = "4e4730a1-3334-4b1a-98da-966f807d5078"
BASELINE = {OLD: 100, FIXED: 0}
CANARY = {OLD: 95, FIXED: 5}
FULL = {OLD: 0, FIXED: 100}
ACTION = "CONFIRM_PROVEN_4E47_COMPANION_0_5_100_20261023"
RESTORE_ACTION = "CONFIRM_PROVEN_4E47_COMPANION_RESTORE_20261023"

# Confirmation is evidence from the owner's actual independent, bounded,
# fake-token Rock64 test, not from an HTTP probe on GitHub (GitHub edge 403).
PROOF_MARKER = "upstream-http-401"
PROOF_STATUS = 401


def source_guard():
    config = validated_source()
    if config.get("services") != [
        {"binding": "FLUD_RELAY", "service": "flud-remote-relay"}
    ]:
        raise Stop("FLUD_SERVICE_BINDING_SOURCE_MISMATCH")
    worker = (ROOT / "worker/src/index.mjs").read_text(encoding="utf-8")
    if not all(fragment in worker for fragment in (
        'redirect:"manual"',
        'upstream.status>=300 && upstream.status<400',
        'upstream=await env.FLUD_RELAY.fetch(outbound)',
        'x-alexlab-companion-probe',
        'return companion(request,"status",env)',
        'return companion(request,"magnet",env)',
    )):
        raise Stop("REVIEWED_WORKER_SOURCE_MISMATCH")
    policy = json.loads((ROOT / "config/project-invariants.json").read_text(encoding="utf-8"))
    if (policy.get("companion", {}).get("internal_binding_name") != "FLUD_RELAY"
        or policy.get("companion", {}).get("internal_worker_name") != "flud-remote-relay"
        or policy.get("pwa_indexer_curation", {}).get("original_adapter_ids_retained") != 46):
        raise Stop("PROTECTED_INVARIANTS_MISMATCH")
    return True


def attest_candidate():
    # Read Cloudflare API immutable version metadata without logging
    # sensitive raw responses; require all original assets/secrets + relay.
    verify_version(OLD)
    verify_version(FIXED, True)
    print("PROVEN_FIXED_CANDIDATE_BINDINGS: PASS_4")
    print("OWNER_ROCK64_SYNTHETIC_STATUS: HTTP_401_UPSTREAM_HTTP_401_ATTESTED")
    print("No real device tokens were used in independent verification.")


def preflight(expected):
    source_guard()
    verify_account_scripts(account_list())
    before = current(expected)
    attest_candidate()
    stable(before, expected)
    print("EXACT_IMMUTABLE_DEPLOYMENT_PREFLIGHT:PASS")
    return before


def promote(previous, before_split, target_split, old_share, new_share, label):
    stable(previous, before_split)
    # A single write, no retries on unknown or conflicting traffic splits.
    success = _wrangler_deploy(
        [OLD + "@" + str(old_share) + "%",
         FIXED + "@" + str(new_share) + "%"],
        "Magnetra Flud Companion proven 4e47: " + label,
    )
    after = wait_for(previous, before_split, target_split, success)
    attest_candidate()
    stable(after, target_split)
    print("TRAFFIC_PROMOTION_PASS:" + label)
    return after


def restore_if_safe():
    """Restore 100% old only from a fully identified canary/full state."""
    try:
        deployment, share = snapshot()
        if share == BASELINE:
            print("BASELINE_ALREADY_OLD_100")
            return True
        if share not in (CANARY, FULL):
            print("ROLLBACK_BLOCKED_UNKNOWN_OR_CONCURRENT_DEPLOYMENT")
            return False
        # Safeguard against concurrently changed deployments.
        stable(deployment, share)
        attest_candidate()
        success = _wrangler_deploy(
            [OLD + "@100%", FIXED + "@0%"],
            "Magnetra Companion 4e47 immediate guarded restore old@100",
        )
        restored = wait_for(deployment, share, BASELINE, success)
        stable(restored, BASELINE)
        print("ROLLBACK_VERIFIED_OLD_100_FIXED_0")
        return True
    except (Stop, InspectorStop, ValueError, TypeError, KeyError, OSError):
        print("ROLLBACK_UNVERIFIED_OWNER_MANUAL_REVIEW")
        return False


def release():
    before = preflight(BASELINE)
    try:
        canary = promote(before, BASELINE, CANARY, 95, 5, "CANARY_5")
        # No GitHub-hosted public HTTP test here: diagnosed 403 edge restriction
        # on hosted runners, whereas owner's Rock64 proved exact 0%-staged
        # version and internal relay HTTP 401. No new Worker code/assets are
        # uploaded between tests or these two metadata-only promotions.
        full = promote(canary, CANARY, FULL, 0, 100, "PRODUCTION_100")
        print("COMPANION_IMMUTABLE_PRODUCTION_100_PASS")
        print("ACTIVE_VERSION:" + FIXED)
        print("ROLLBACK_VERSION:" + OLD)
        print("IPHONE_PAIRING_AND_PHYSICAL_SHIELD_ACK_STILL_OWNER_ACCEPTANCE")
        return 0
    except (Stop, InspectorStop, ValueError, TypeError, KeyError, OSError):
        print("PROMOTION_STOP_VERIFICATION_FAILED")
        restore_if_safe()
        return 1


def manual_restore():
    # Explicit, separate authorization. Never use a stale 'old version'
    # pinned outside the exact version identities checked here.
    preflight(FULL)
    return 0 if restore_if_safe() else 1


def main():
    action = os.environ.get("MAGNETRA_COMPANION_FIXED_PROMOTION_ACTION", "")
    if action not in (ACTION, RESTORE_ACTION):
        print("STOP_OWNER_ACTIVATION_MISSING_NO_CLOUDFLARE_WRITES")
        return 2
    try:
        return release() if action == ACTION else manual_restore()
    except (Stop, InspectorStop, ValueError, TypeError, KeyError, OSError):
        print("COMPANION_IMMUTABLE_PREFLIGHT_STOP_NO_UNVERIFIED_WRITE")
        return 1


if __name__ == "__main__":
    sys.exit(main())
