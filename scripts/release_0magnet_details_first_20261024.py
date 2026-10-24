#!/usr/bin/env python3
"""Owner-approved immutable 0Magnet source-details-first PWA fix: upload, 0, 5, 100.

One verified Cloudflare Worker PWA code change. Exact baseline before ANY
write, Cloudflare account+origin+four binding guards; previous active remains
at 0% for rollback. No DNS, preview settings, Rock64, Flud or secret writes.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
import subprocess
import time
import urllib.error
import urllib.request

from deploy_magnetra_auto_pause_once import (
    Stop, ROOT, UUID, NoRedirect, snapshot, current, stable, wait_for,
    _wrangler_deploy, uploaded_version_id,
)
from deploy_magnetra_zero_percent import _get_api
from inspect_companion_binding_readonly import (
    account_list, verify_account_scripts, Stop as AccountStop,
)
from stage_therarbag_iphone_20261024 import validate_source, verify_binding_payload
from release_therarbag_iphone_diagnostic_20261024 import (
    http as live_http, BASE, UA,
)

ACTIVE = "916d0671-b9c5-432d-8724-aed27bc22c4f"
ROLLBACK = "139d97f7-4048-4bbb-8e90-80585f1f4b26"
BASELINE = {ACTIVE:100, ROLLBACK:0}
ACTION = "CONFIRM_0MAGNET_OWNER_RELEASE_20261024"
ORIGINAL = "https://9mag.net/!lxbV"
TEMP_CONFIG = ROOT / "worker/.wrangler-0magnet-details-first-once.jsonc"
MAX_BYTES = 1200000
NEW = None

def source_guard():
    # Reuse full reviewed Cloudflare host/assets/services config validation.
    config = validate_source()
    code = (ROOT / "web/app.js").read_text(encoding="utf8")
    required = 'const preferDetails=item.provider==="oxtorrent"||item.provider==="torrent9"||item.provider==="therarbag"||item.provider==="0magnet";'
    baseline = 'const source=preferDetails ? item.details : item.magnetSource||item.details;'
    if code.count(required) != 1 or code.count(baseline) != 1:
        raise Stop("REVIEWED_0MAGNET_DETAILS_FIRST_SOURCE_MISMATCH")
    # Verify explicit on-device source preference without changing the other
    # 42 provider routes or back-end parsers.
    print("REVIEWED_0MAGNET_OWNER_DETAILS_FIRST_SOURCE: PASS", flush=True)
    return config

def split_guard():
    verify_account_scripts(account_list())
    before = current(BASELINE)
    for version in BASELINE:
        verify_binding_payload(version, _get_api("/versions/"+version))
    stable(before, BASELINE)
    print("CURRENT_BASELINE_916D100_139DZERO_FOUR_BINDINGS: PASS",flush=True)
    return before

def upload(config):
    if TEMP_CONFIG.exists():
        raise Stop("TEMP_CONFIG_ALREADY_EXISTS")
    cfg = dict(config)
    cfg["secrets"]={"required":["BTDIGG_GATEWAY_TOKEN","MAGNETRA_GATEWAY_TOKEN"]}
    TEMP_CONFIG.write_text(json.dumps(cfg,indent=2)+"\n",encoding="utf8")
    os.chmod(TEMP_CONFIG,0o600)
    try:
        try:
            result = subprocess.run(
                ["npx","--yes","wrangler@4.102.0","versions","upload",
                 "--config",str(TEMP_CONFIG),"--keep-vars","--message",
                 "Magnetra 0Magnet exact owner original details-first, reversible"],
                cwd=ROOT,text=True,capture_output=True,timeout=220,check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            raise Stop("UPLOAD_UNVERIFIED") from None
        if result.returncode:
            raise Stop("UPLOAD_FAILED") from None
        new=uploaded_version_id(result.stdout+"\n"+result.stderr)
        if new in BASELINE:
            raise Stop("IMMUTABLE_VERSION_COLLISION")
        print("FIX_IMMUTABLE_NEW_VERSION:",new,flush=True)
        return new
    finally:
        TEMP_CONFIG.unlink(missing_ok=True)

def candidate_http(path,version,body=None):
    if not UUID.fullmatch(version) or path not in ("/app.js","/api/health","/api/providers","/api/resolve"):
        raise Stop("UNAPPROVED_IMMUTABLE_HTTP_PATH")
    if body is not None and path!="/api/resolve":
        raise Stop("UNAPPROVED_POST_PATH")
    headers={
        "User-Agent":UA,"Cache-Control":"no-cache,no-store",
        "Accept-Encoding":"identity",
        "Accept":"application/json" if path.startswith("/api/") else "application/javascript",
        "Cloudflare-Workers-Version-Overrides":'alexlab-magnetra="'+version+'"',
    }
    data=None
    if body is not None:
        data=json.dumps(body,separators=(",",":")).encode()
        if len(data)>1200:raise Stop("FIX_PROBE_BODY_TOO_LARGE")
        headers.update({"Origin":BASE,"Content-Type":"application/json"})
    req=urllib.request.Request(BASE+path,method="POST" if body is not None else "GET",
                               data=data,headers=headers)
    try:
        with urllib.request.build_opener(NoRedirect()).open(req,timeout=30 if data else 18) as res:
            status,typ=res.status,res.headers.get("content-type","")
            raw=res.read(MAX_BYTES+1)
    except urllib.error.HTTPError as err:
        status,typ=err.code,err.headers.get("content-type","")
        raw=err.read(MAX_BYTES+1)
    except (urllib.error.URLError,TimeoutError,OSError):
        raise Stop("FIX_IMMUTABLE_EDGE_UNVERIFIED") from None
    if not raw or len(raw)>MAX_BYTES:raise Stop("FIX_IMMUTABLE_BODY_LIMIT_UNVERIFIED")
    if path=="/app.js":
        if status!=200 or "javascript" not in typ.lower():raise Stop("FIX_JS_ASSET_HTTP_UNVERIFIED")
        return raw
    if "application/json" not in typ.lower():raise Stop("FIX_API_NOT_JSON")
    try: body_json=json.loads(raw)
    except (UnicodeError,ValueError):raise Stop("FIX_API_JSON_MALFORMED") from None
    if not isinstance(body_json,dict):raise Stop("FIX_API_JSON_SHAPE")
    return status,body_json

def verify_candidate(version):
    reviewed=(ROOT/"web/app.js").read_bytes()
    live_js=candidate_http("/app.js",version)
    if hashlib.sha256(reviewed).digest()!=hashlib.sha256(live_js).digest():
        raise Stop("IMMUTABLE_FIX_JS_SHA_MISMATCH")
    status,health=candidate_http("/api/health",version)
    if status!=200 or health.get("ok") is not True or (health.get("total"),health.get("ported"))!=(46,46):
        raise Stop("IMMUTABLE_46_HEALTH_MISSING")
    status,p=candidate_http("/api/providers",version)
    names=p.get("providers")
    if status!=200 or not isinstance(names,list) or len(names)!=46:
        raise Stop("IMMUTABLE_46_PROVIDER_COUNT_MISMATCH")
    ids=[x.get("id") for x in names if isinstance(x,dict)]
    if len(ids)!=46 or len(set(ids))!=46 or "therarbag" not in ids or "0magnet" not in ids:
        raise Stop("IMMUTABLE_PROVIDER_IDENTITIES_UNVERIFIED")
    print("IMMUTABLE_JS_SHA_AND_HEALTH_CATALOG_46: PASS",flush=True)

def prove_real_owner_magnet(version):
    # Source-owned original exact owner URL was independently audited (GitHub
    # run 40133513283). The request below is read-only metadata extraction.
    # Never POST to Companion/Flud or log magnet/hash/source response body.
    status, payload = candidate_http("/api/resolve", version, body={
        "provider": "0magnet", "details": ORIGINAL
    })
    magnet = payload.get("magnet")
    if (status != 200 or not isinstance(magnet, str)
        or not re.fullmatch(
            r"magnet:\?xt=urn:btih:(?:[a-f0-9]{40}|[a-z2-7]{32})(?:&[^\s]{0,11900})?",
            magnet, re.I
        )):
        raise Stop("EXACT_0MAGNET_OWNER_SOURCE_NOT_VERIFIED")
    print("IMMUTABLE_0MAGNET_EXACT_OWNER_CANONICAL_MAGNET: PASS (value withheld)", flush=True)

def transition(first,source,target,label,version):
    stable(first,source)
    selector=[ACTIVE+"@"+str(target[ACTIVE])+"%",version+"@"+str(target[version])+"%"]
    if not _wrangler_deploy(selector,"Magnetra original 0Magnet details-first iPhone fix "+label):
        raise Stop("VERSION_ONLY_PERCENTAGE_COMMAND_FAILED_"+label)
    after=wait_for(first,source,target,True)
    stable(after,target)
    print("FIX_IMMUTABLE_TRAFFIC_"+label+": PASS",flush=True)
    return after

def public_postflight(version):
    full={ACTIVE:0,version:100}
    sha=hashlib.sha256((ROOT/"web/app.js").read_bytes()).digest()
    for attempt in range(8):
        js=live_http("/app.js")
        if hashlib.sha256(js).digest()==sha:
            break
        dep,shares=snapshot()
        if shares!=full or attempt==7:raise Stop("PRODUCTION_FIX_ASSET_NOT_CURRENT")
        time.sleep(5)
    status,health=live_http("/api/health")
    if status!=200 or (health.get("total"),health.get("ported"))!=(46,46):
        raise Stop("PRODUCTION_FIX_HEALTH_46_UNVERIFIED")
    status,catalog=live_http("/api/providers")
    if status!=200 or not isinstance(catalog.get("providers"),list) or len(catalog["providers"])!=46:
        raise Stop("PRODUCTION_FIX_PROVIDER_CATALOG_UNVERIFIED")
    print("PUBLIC_LIVE_CORRECTED_JS_SHA_AND_CATALOG_46: PASS",flush=True)

def rollback_if_safe(candidate):
    if not candidate or not UUID.fullmatch(candidate):
        return
    slot={ACTIVE:100,candidate:0}
    canary={ACTIVE:95,candidate:5}
    full={ACTIVE:0,candidate:100}
    try:
        deployment,shares=snapshot()
        if shares in (BASELINE,slot):
            print("SAFE_PRIOR_VERSION_STILL_AT_100",flush=True)
            return
        if shares not in (canary,full):
            print("UNKNOWN_SPLIT_ROLLBACK_REFUSED",flush=True)
            return
        verify_binding_payload(ACTIVE,_get_api("/versions/"+ACTIVE))
        verify_binding_payload(candidate,_get_api("/versions/"+candidate))
        stable(deployment,shares)
        if not _wrangler_deploy([ACTIVE+"@100%",candidate+"@0%"],
                "Magnetra 0Magnet safety rollback to proven active 916d"):
            print("ROLLBACK_COMMAND_UNVERIFIED",flush=True)
            return
        after=wait_for(deployment,shares,slot,True)
        stable(after,slot)
        print("KNOWN_SAFE_AUTOMATIC_ROLLBACK_ACTIVE100: PASS",flush=True)
    except (Stop,ValueError,TypeError,KeyError,OSError):
        print("ROLLBACK_NEEDS_MANUAL_AUDIT",flush=True)

def release():
    global NEW
    config=source_guard()
    first=split_guard()
    # Refuse a redundant release or a publicly changed asset before write.
    if hashlib.sha256(live_http("/app.js")).digest()==hashlib.sha256(
            (ROOT/"web/app.js").read_bytes()).digest():
        raise Stop("CORRECTED_PWA_ALREADY_LIVE")
    stable(first,BASELINE)
    NEW=upload(config)
    verify_binding_payload(NEW,_get_api("/versions/"+NEW))
    stable(first,BASELINE)
    print("NEW_VERSION_FOUR_IMMUTABLE_BINDINGS_NO_TRAFFIC_CHANGE: PASS",flush=True)

    slot={ACTIVE:100,NEW:0}
    canary={ACTIVE:95,NEW:5}
    full={ACTIVE:0,NEW:100}
    deployed_slot=transition(first,BASELINE,slot,"ZERO_SLOT",NEW)
    verify_candidate(NEW)
    prove_real_owner_magnet(NEW)
    stable(deployed_slot,slot)

    deployed_canary=transition(deployed_slot,slot,canary,"CANARY_5",NEW)
    verify_candidate(NEW)
    stable(deployed_canary,canary)

    deployed_full=transition(deployed_canary,canary,full,"FULL_100",NEW)
    public_postflight(NEW)
    stable(deployed_full,full)
    print("OWNER_0MAGNET_PRODUCTION_100_PASS: https://index.alexlab.media",flush=True)
    print("FIX_PREVIOUS_ACTIVE_PRESERVED_AT_ZERO:",ACTIVE,flush=True)
    print("OWNER_REAL_IPHONE_SAME_CARD_ACCEPTANCE_STILL_PENDING",flush=True)
    return 0

def main():
    if os.environ.get("MAGNETRA_0MAGNET_DETAILS_FIRST_ACTION")!=ACTION:
        print("EXPLICIT_0MAGNET_OWNER_PRODUCTION_ACTION_MISSING")
        return 2
    try:
        return release()
    except (Stop,AccountStop,ValueError,TypeError,KeyError,OSError):
        print("0MAGNET_RELEASE_STOP_NO_SUCCESS_ASSUMED",flush=True)
        rollback_if_safe(NEW)
        return 1
if __name__=="__main__":
    raise SystemExit(main())
