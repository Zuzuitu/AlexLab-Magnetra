#!/usr/bin/env python3
"""Safe GET-only reason codes for an already staged 0% curated-11 PWA candidate."""
import hashlib
import json
import sys
from release_curated_11_indexers_50_20261025 import (
    ROOT, ACTIVE, Stop, snapshot, verify_binding_payload, candidate_http,
    verify_reviewed_html
)
from deploy_magnetra_zero_percent import _get_api
from inspect_companion_binding_readonly import validated_source

NEW="74754dac-1842-47b2-8e6f-92a10731f124"
SPLIT={ACTIVE:100,NEW:0}
ASSETS=(("/app.js","web/app.js"),("/styles.css","web/styles.css"),
        ("/i18n.js","web/i18n.js"),("/sw.js","web/sw.js"),("/","web/index.html"))

def check_asset(path,local):
    expected=(ROOT/local).read_bytes()
    try:
        served=candidate_http(path,NEW)
        if path=="/":verify_reviewed_html(expected,served)
        elif hashlib.sha256(expected).digest()!=hashlib.sha256(served).digest():
            raise Stop("REVIEWED_SHA_MISMATCH")
        print("CANDIDATE_ASSET_"+("HTML" if path=="/" else path.strip("/").upper().replace(".","_"))+": PASS",flush=True)
        return True
    except (Stop,ValueError,TypeError,KeyError):
        print("CANDIDATE_ASSET_"+("HTML" if path=="/" else path.strip("/").upper().replace(".","_"))+": NOT_VERIFIED",flush=True)
        return False

def run():
    validated_source()
    old,shares=snapshot()
    if shares!=SPLIT:
        raise Stop("EXPECTED_100_0_ZERO_SLOT_CHANGED")
    verify_binding_payload(ACTIVE,_get_api("/versions/"+ACTIVE))
    verify_binding_payload(NEW,_get_api("/versions/"+NEW))
    print("CANDIDATE_ZERO_SLOT_8D9C100_NEW7475ZERO: PASS",flush=True)
    print("CANDIDATE_FOUR_BINDINGS_BOTH_VERSIONS: PASS",flush=True)
    passed=[check_asset(path,local) for path,local in ASSETS]
    try:
        _,health=candidate_http("/api/health",NEW)
        healthy=health.get("ok") is True and health.get("total")==46 and health.get("ported")==46
    except (Stop,ValueError,KeyError,TypeError):healthy=False
    print("CANDIDATE_HEALTH_46: "+("PASS" if healthy else "NOT_VERIFIED"),flush=True)
    try:
        _,data=candidate_http("/api/providers",NEW)
        ids=[x.get("id") for x in data.get("providers",[]) if isinstance(x,dict)]
        catalog=len(ids)==46 and len(set(ids))==46 and "subsplease" in ids
    except (Stop,ValueError,KeyError,TypeError):catalog=False
    print("CANDIDATE_CATALOG_46: "+("PASS" if catalog else "NOT_VERIFIED"),flush=True)
    after,now=snapshot()
    if now!=SPLIT or after.get("id")!=old.get("id"):
        raise Stop("DEPLOYMENT_CHANGED_DURING_DIAG")
    print("PRODUCTION_8D9C_STILL_100_NEW7475_STILL_0: PASS",flush=True)
    if not all(passed) or not healthy or not catalog:
        print("CURATED_11_STAGED_ZERO_DIAGNOSTIC: PARTIAL_DO_NOT_PROMOTE",flush=True)
        return 1
    print("CURATED_11_STAGED_ZERO_DIAGNOSTIC: ALL_PASS_READONLY",flush=True)
    return 0

def main():
    try:return run()
    except (Stop,ValueError,KeyError,TypeError):
        print("CURATED_11_STAGED_ZERO_DIAGNOSTIC: STOP_NO_WRITES",flush=True)
        return 1

if __name__=="__main__":sys.exit(main())
