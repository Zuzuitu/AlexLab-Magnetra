#!/usr/bin/env python3
"""Owner-directed version-only 0->5->100 resume after independently verified 0% stage.

Never re-upload. Old 8d9c immutable stays rollback; all state transitions gated
by exact Cloudflare metadata, original catalog/source checks and public hashes.
"""
from __future__ import annotations
import hashlib
import os
import sys
import release_curated_11_indexers_50_20261025 as r

NEW="74754dac-1842-47b2-8e6f-92a10731f124"
SLOT={r.ACTIVE:100,NEW:0}
CANARY={r.ACTIVE:95,NEW:5}
FULL={r.ACTIVE:0,NEW:100}
ACTION="CONFIRM_CURATED_11_VERSION_ONLY_RESUME_20261025"

def run():
    r.source_guard()
    r.verify_account_scripts(r.account_list())
    first=r.current(SLOT)
    r.verify_binding_payload(r.ACTIVE,r._get_api("/versions/"+r.ACTIVE))
    r.verify_binding_payload(NEW,r._get_api("/versions/"+NEW))
    r.stable(first,SLOT)
    if hashlib.sha256(r.live_http("/app.js")).hexdigest()[:16]!=r.OLD_PUBLIC_SHA_PREFIX:
        raise r.Stop("REVIEWED_OLD_PUBLIC_APP_SHA_CHANGED")
    print("EXACT_PREVIOUS_ACTIVE100_CANDIDATE_ZERO_AND_FOUR_BINDINGS: PASS",flush=True)
    r.verify_candidate(NEW)
    r.prove_real_owner_magnet(NEW)
    r.prove_owner_search_card(NEW)
    r.stable(first,SLOT)
    print("PRE_PROMOTION_IMMUTABLE_SOURCE_AND_OWNER_E2E: PASS",flush=True)
    five=r.transition(first,SLOT,CANARY,"RESUME_CANARY_5",NEW)
    r.verify_candidate(NEW)
    r.prove_owner_search_card(NEW)
    r.stable(five,CANARY)
    full=r.transition(five,CANARY,FULL,"RESUME_FULL_100",NEW)
    r.public_postflight(NEW)
    r.stable(full,FULL)
    print("CURATED_11_VERSION_ONLY_PRODUCTION_100_PASS",flush=True)
    print("PREVIOUS_IMMUTABLE_8D9C_ROLLBACK_AT_ZERO: PASS",flush=True)
    print("IPHONE_PHYSICAL_VISUAL_ACCEPTANCE: PENDING",flush=True)
    return 0

def main():
    if os.environ.get("MAGNETRA_CURATED_11_RESUME_ACTION")!=ACTION:
        print("VERSION_ONLY_RESUME_OWNER_APPROVAL_MISSING",flush=True)
        return 2
    try:return run()
    except (r.Stop,r.AccountStop,ValueError,TypeError,KeyError,OSError):
        print("CURATED_11_VERSION_ONLY_RESUME_STOP_NO_SUCCESS_ASSUMED",flush=True)
        r.rollback_if_safe(NEW)
        return 1

if __name__=="__main__":sys.exit(main())
