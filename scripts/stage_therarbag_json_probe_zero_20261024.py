#!/usr/bin/env python3
"""One-shot Cloudflare zero-traffic staging of reviewed original-source JSON fix.
Fail closed unless active 36019925 has exactly 100% and all four bindings.
No normal traffic mutation, release promotion, raw secrets, hashes, magnet
or torrent downloads. No hidden reruns; production version retained.
"""
from __future__ import annotations
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from deploy_magnetra_zero_percent import _get_api,_current_deployment,_shares,_wrangler_deploy
from deploy_magnetra_auto_pause_once import uploaded_version_id,UUID
from inspect_companion_binding_readonly import validated_source
from inspect_magnetra_fix_stage import binding_pairs

ROOT=Path(__file__).resolve().parents[1]
ACTIVE="36019925-2308-4f99-8223-13854012d372"
PREVIOUS_ZERO="8c79bf41-40b0-4c2b-96a1-9506b706bf8a"
EXPECTED={
    "ASSETS":{"assets"},
    "BTDIGG_GATEWAY_TOKEN":{"secret_text","secret_key"},
    "MAGNETRA_GATEWAY_TOKEN":{"secret_text","secret_key"},
    "FLUD_RELAY":{"service"},
}
class StageStop(Exception):pass

def bindings_ok(ver):
    if not isinstance(ver,dict) or ver.get("success") is not True:
        return False
    pairs=binding_pairs(ver)
    return all(any((k,typ) in pairs for typ in typs) for k,typs in EXPECTED.items())

def live():
    dep=_current_deployment(_get_api("/deployments"))
    return dep,_shares(dep)

def upload():
    cfg=validated_source()
    code=(ROOT/"worker/src/legacy-adapters.mjs").read_text(encoding="utf-8")
    if ('theRarBgOriginalJsonHash' not in code
        or 'jsonUrl.searchParams.set("format","json")' not in code
        or 'magnet=await theRarBgOriginalJsonHash' not in code):
        raise StageStop("JSON_SOURCE_REVIEW_GUARD_FAILED")
    if "THERARBAG_CLOUDFLARE_SOURCE_JSON_V1" not in (ROOT/"worker/src/index.mjs").read_text(encoding="utf-8"):
        raise StageStop("CF_DIAGNOSTIC_SOURCE_MARKER_MISSING")
    cfg=dict(cfg)
    cfg["secrets"]={"required":["BTDIGG_GATEWAY_TOKEN","MAGNETRA_GATEWAY_TOKEN"]}
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",suffix=".jsonc",
       prefix="therarbag-json-stage-",dir=ROOT/"worker",delete=False) as f:
        path=Path(f.name)
        f.write(json.dumps(cfg,indent=2)+"\n")
    try:
        os.chmod(path,0o600)
        try:
            p=subprocess.run(["npx","--yes","wrangler@4.102.0","versions","upload",
               "--config",str(path),"--keep-vars",
               "--message","TheRarBg read-only JSON egress diagnostic candidate only (zero traffic)"],
               cwd=ROOT,capture_output=True,text=True,timeout=220,check=False)
        except (OSError,subprocess.TimeoutExpired):
            raise StageStop("CANDIDATE_UPLOAD_TRANSPORT_FAILED") from None
        if p.returncode:
            raise StageStop("CANDIDATE_UPLOAD_FAILED")
        try:
            version=uploaded_version_id(p.stdout+"\n"+p.stderr)
        except (Exception):
            raise StageStop("CANDIDATE_UUID_UNVERIFIED") from None
        if not UUID.fullmatch(version) or version==ACTIVE:
            raise StageStop("CANDIDATE_UUID_REJECTED")
        return version
    finally:
        path.unlink(missing_ok=True)

def audit_metadata(version):
    doc=_get_api("/versions/"+version)
    if (doc.get("result") or {}).get("id")!=version or not bindings_ok(doc):
        raise StageStop("CANDIDATE_FOUR_BINDINGS_UNVERIFIED")

def run():
    if os.environ.get("THERARBAG_STAGE_APPROVAL")!="ZERO_ONLY_EXACT_36019925":
        raise StageStop("STAGING_NOT_APPROVED")
    if not bindings_ok(_get_api("/versions/"+ACTIVE)):
        raise StageStop("ACTIVE_FOUR_BINDINGS_UNVERIFIED")
    old,shares=live()
    if shares!={ACTIVE:100,PREVIOUS_ZERO:0} or not isinstance(old.get("id"),str):
        raise StageStop("PREEXISTING_DEPLOYMENT_CHANGED")
    print("PRE_STAGING_ACTIVE_36019925_100: PASS")
    candidate=upload()
    audit_metadata(candidate)
    unchanged,still=live()
    if unchanged.get("id")!=old.get("id") or still!=shares:
        raise StageStop("CONCURRENT_DEPLOYMENT_CHANGED")
    # The ONLY deployment write is current 100% and new candidate 0%.
    if not _wrangler_deploy(
        [ACTIVE+"@100%",candidate+"@0%"],
        "TheRarBg original JSON egress probe at zero traffic; live version unchanged"):
        raise StageStop("ZERO_TRAFFIC_SLOT_WRITE_FAILED")
    for _ in range(4):
        current,values=live()
        if values=={ACTIVE:100,candidate:0}:
            audit_metadata(candidate)
            print("STAGED_CANDIDATE_UUID:",candidate)
            output=os.environ.get("GITHUB_OUTPUT")
            if output:
                with open(output,"a",encoding="utf-8") as out:
                    out.write("candidate="+candidate+"\n")
            print("STAGED_FOUR_BINDINGS: PASS")
            print("ACTIVE_UNCHANGED_36019925_100: PASS")
            print("CANDIDATE_ZERO_PERCENT: PASS")
            print("NO_NORMAL_USER_TRAFFIC_MODIFIED: PASS")
            return
        if values!=shares:
            raise StageStop("UNKNOWN_DEPLOYMENT_SPLIT")
        time.sleep(2)
    raise StageStop("ZERO_TRAFFIC_POSTFLIGHT_UNVERIFIED")

if __name__=="__main__":
    try:run()
    except (StageStop,ValueError,TypeError,KeyError,OSError) as exc:
        if isinstance(exc,StageStop):
            print("STAGING_STOP:",str(exc))
        else:print("STAGING_STOP: UNVERIFIED_METADATA_OR_TRANSPORT")
        sys.exit(2)
