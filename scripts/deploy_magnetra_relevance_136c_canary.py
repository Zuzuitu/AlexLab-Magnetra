#!/usr/bin/env python3
"""Manual owner-gated exact 540b/136c 5% canary with manual zero-share restore.

Requires genuine immutable metadata, fixed 0%-slot and reviewed JS hash.
One Wrangler version-only deployment per manual action. No source searches,
retry after 429, Flud, torrent operations or Rock64 modifications.
"""
from __future__ import annotations
import hashlib
import os
from pathlib import Path
import sys
import time

from deploy_magnetra_zero_percent import _wrangler_deploy
from deploy_magnetra_relevance_136c_slot import (
    CURRENT, NEW, SLOT, snapshot, verify_version, request, Stop as StagedStop
)

PROMOTE="CONFIRM_RELEVANCE_136C_CANARY_5"
RESTORE="CONFIRM_RESTORE_540B100_136C0"
FIVE={CURRENT:95,NEW:5}

class Stop(Exception): pass

def verify_source_asset():
    data=request("/app.js",as_json=False)
    expected=(Path(__file__).resolve().parent.parent/"web"/"app.js").read_bytes()
    if hashlib.sha256(data).digest()!=hashlib.sha256(expected).digest():
        raise Stop("STAGED_ASSET_SHA_MISMATCH_NO_WRITE")
    print("IMMUTABLE_136C_APP_JS: PASS reviewed SHA256="+hashlib.sha256(data).hexdigest()[:16])

def stable(record,expected):
    again,shares=snapshot()
    if record["id"]!=again["id"] or shares!=expected:
        raise Stop("CONCURRENT_DEPLOYMENT_NO_WRITE")

def wait_for(before,target,wrote):
    for i in range(4):
        now,shares=snapshot()
        if shares==target:
            if not wrote or now["id"]==before["id"]:
                raise Stop("TARGET_VISIBLE_BUT_WRITE_UNVERIFIED")
            return now
        if shares!=({CURRENT:100,NEW:0} if target==FIVE else FIVE) or not wrote:
            raise Stop("UNKNOWN_SPLIT_OR_WRANGLER_UNVERIFIED")
        if i==3:raise Stop("CLOUDFLARE_METADATA_UNVERIFIED")
        time.sleep(2)
    raise Stop("METADATA_UNVERIFIED")

def canary():
    verify_version(CURRENT)
    verify_version(NEW)
    before,shares=snapshot()
    if shares!=SLOT:raise Stop("EXPECTED_540B100_136C0_SLOT_MISSING")
    verify_source_asset()
    stable(before,SLOT)
    print("CANARY_PREFLIGHT_PASS: exact two IDs, 3 bindings each, latest reviewed JS")
    print("CANARY_WRITE_ONCE: 540b95 / 136c5")
    wrote=_wrangler_deploy(
        [CURRENT+"@95%",NEW+"@5%"],
        "Magnetra relevance 136c 5% canary after read-only title E2E; keep 540b at 95%")
    wait_for(before,FIVE,wrote)
    print("CANARY_POSTFLIGHT_PASS: 540b 95% / 136c 5%; 540b retained for guarded rollback")
    print("NOTE: provider results and iPhone behavior at canary require separate read-only acceptance")
    return 0

def restore():
    verify_version(CURRENT)
    verify_version(NEW)
    before,shares=snapshot()
    if shares==SLOT:
        print("RESTORE_ALREADY_SAFE: 540b100 / 136c0, no write")
        return 0
    if shares!=FIVE:raise Stop("RESTORE_REQUIRES_EXACT_540B95_136C5")
    stable(before,FIVE)
    print("RESTORE_WRITE_ONCE: 540b 100% / 136c 0%")
    wrote=_wrangler_deploy(
        [CURRENT+"@100%",NEW+"@0%"],
        "Magnetra owner requested bounded relevance canary restore to 540b 100%")
    wait_for(before,SLOT,wrote)
    print("RESTORE_POSTFLIGHT_PASS: 540b100 / 136c0")
    return 0

def execute():
    action=os.environ.get("MAGNETRA_RELEVANCE_CANARY_ACTION")
    if action not in (PROMOTE,RESTORE):
        print("STOP: explicit manual canary/restore action absent; no network or write")
        return 2
    try: return canary() if action==PROMOTE else restore()
    except (Stop,StagedStop,ValueError,TypeError,KeyError,OSError) as e:
        print("RELEVANCE_CANARY_STOP: "+str(e) if isinstance(e,(Stop,StagedStop)) else "RELEVANCE_CANARY_STOP: SANITIZED_METADATA_OR_TRANSPORT")
        return 1

if __name__=="__main__":
    sys.exit(execute())
