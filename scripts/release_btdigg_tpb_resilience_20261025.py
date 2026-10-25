#!/usr/bin/env python3
"""Guarded immutable 11-source / 50-result PWA release: upload, 0, 5, 100.

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
from cloudflare_html_asset_guard import verify_reviewed_html
from release_therarbag_iphone_diagnostic_20261024 import (
    http as live_http, BASE, UA,
)

ACTIVE = "74754dac-1842-47b2-8e6f-92a10731f124"
ROLLBACK = "8d9c19f4-ca38-428b-888e-757ef578c829"
BASELINE = {ACTIVE:100,ROLLBACK:0}
# Independently observed in guarded source release #40216426537; live GETs repeat before write.
OLD_PUBLIC_GIT_BLOB = "98a5b25213126d8a0c402d21b558fb8c09c1ae2f"
ACTION = "CONFIRM_MAGNETRA_BTDIGG_TPB_RESILIENCE_20261025"
ORIGINAL = "https://nnmclub.to/forum/viewtopic.php?t=1896364"
SEARCH_PATH = "/api/search?q=Lupin&category=all&providers=nonameclub"
TEMP_CONFIG = ROOT / "worker/.wrangler-btdigg-tpb-once.jsonc"
MAX_BYTES = 1200000
APP_BLOB_SHA = "2d6735e0fc98f61820c746cfa34ec380cf497248"
PINNED_BLOBS={
 "worker/src/index.mjs":"7a3b1aeec415a623669159ddf5dfad57187df203",
 "worker/src/providers.mjs":"b80ab5ccb137dddb60a5f647cdbb2e6295f28a8b",
 "worker/src/legacy-adapters.mjs":"c34d77dfbc01a05e8172ac96b6e9875a4531fdd2",
 "worker/src/verified-source-cache.mjs":"f4481247dce12abff2723df8efebddf1275247c7"
}
POSITIVE_PATHS={
 "btdigg":"/api/search?q=ubuntu&category=all&providers=btdigg",
 "thepiratebay":"/api/search?q=ubuntu&category=all&providers=thepiratebay"
}
NEW = None

def source_guard():
    # Pin the already-reviewed 11-source application to prevent a future
    # unrelated main change from being silently included in this one-shot release.
    try:
        reviewed=subprocess.run(["git","hash-object","web/app.js"],cwd=ROOT,
            capture_output=True,text=True,timeout=8,check=False)
    except (OSError,subprocess.TimeoutExpired):
        raise Stop("REVIEWED_PWA_BLOB_CHECK_UNVERIFIED") from None
    if reviewed.returncode or reviewed.stdout.strip()!=APP_BLOB_SHA:
        raise Stop("REVIEWED_PWA_SOURCE_CHANGED")
    for path,sha in PINNED_BLOBS.items():
        try:
            result=subprocess.run(["git","hash-object",path],cwd=ROOT,
                capture_output=True,text=True,timeout=8,check=False)
        except (OSError,subprocess.TimeoutExpired):
            raise Stop("PINNED_SOURCE_HASH_CHECK_UNVERIFIED") from None
        if result.returncode or result.stdout.strip()!=sha:raise Stop("REVIEWED_SOURCE_CHANGED")
    config = validate_source()
    pwa=(ROOT/"web/app.js").read_text(encoding="utf8")
    adapter=(ROOT/"worker/src/legacy-adapters.mjs").read_text(encoding="utf8")
    specs=(ROOT/"worker/src/legacy-specs.mjs").read_text(encoding="utf8")
    select='const preferDetails=item.provider==="oxtorrent"||item.provider==="torrent9"||item.provider==="therarbag"||item.provider==="0magnet"||item.provider==="nonameclub";'
    source='const source=preferDetails ? item.details : item.magnetSource||item.details;'
    urlguard='if(typeof url!=="string"||!url.trim())return null;'
    if pwa.count(select)!=1 or pwa.count(source)!=1 or adapter.count(urlguard)!=1:
        raise Stop("REVIEWED_NONAMECLUB_SOURCE_GUARDS_MISMATCH")
    if 'function allowedExternal(url,host,base=host)' not in adapter or '"nonameclub": {' not in specs:
        raise Stop("ORIGINAL_FIXED_ORIGIN_PROVIDER_MISSING")
    # No change to original site parsing, no authentication, no relaxed SSRF guard.
    css=(ROOT/"web/styles.css").read_text(encoding="utf8")
    sw=(ROOT/"web/sw.js").read_text(encoding="utf8")
    html=(ROOT/"web/index.html").read_text(encoding="utf8")
    checks=(
        '@media (max-width:760px) and (display-mode:standalone)' in css,
        'html.ios-standalone .site-shell' in css,
        'padding-top:max(60px,env(safe-area-inset-top,0px))' in css,
        '#settingsButton{width:44px;height:44px;min-width:44px;min-height:44px}' in css,
        'navigator.standalone===true' in pwa,
        'document.documentElement.classList.add("ios-standalone")' in pwa,
        'const CACHE="alexlab-magnetra-v10"' in sw,
        'viewport-fit=cover' in html and 'black-translucent' in html,
        'const hiddenIndexerIds=new Set('+json.dumps(json.loads((ROOT/"config/project-invariants.json").read_text(encoding="utf8"))["pwa_indexer_curation"]["hidden_ids"],separators=(",",":"))+');' in pwa,
        'function toggleAllProviders()' in pwa,
        'function updateSelectAllButton()' in pwa,
        'stored.length===0' in pwa,
        'const RESULTS_PER_PAGE=50;' in pwa,
        'function renderPagination(total)' in pwa,
        'sorted.slice((state.resultsPage-1)*RESULTS_PER_PAGE,state.resultsPage*RESULTS_PER_PAGE)' in pwa,
        '$("selectWorking")' not in pwa,
        '$("selectAllProviders")' in pwa,
        'id="selectAllProviders">Selectează toate' in html,
        'id="selectWorking"' not in html,
        'id="resultsPagination"' in html,
        '"Previous page"' in (ROOT/"web/i18n.js").read_text(encoding="utf8"),
    )
    if not all(checks):
        raise Stop("REVIEWED_IOS_SAFE_AREA_SOURCE_GUARDS_MISMATCH")
    if ('cacheWarnings:[]' not in pwa or
        'CACHED_AFTER_SOURCE_FAILURE' not in pwa or
        'const BTDIGG_WORKER_TIMEOUT = 18_000;' not in adapter or
        'const TPB_API_TIMEOUT_MS = 16000;' not in (ROOT/"worker/src/providers.mjs").read_text(encoding="utf8")):
        raise Stop("REVIEWED_BTDIGG_TPB_SOURCE_GUARDS_MISMATCH")
    print("REVIEWED_BTDIGG_TPB_AND_11_CURATED_GUARDS: PASS",flush=True)
    return config

def split_guard():
    verify_account_scripts(account_list())
    before = current(BASELINE)
    for version in BASELINE:
        verify_binding_payload(version, _get_api("/versions/"+version))
    stable(before, BASELINE)
    print("EXACT_7475_100_8D9C_ZERO_FOUR_BINDINGS: PASS",flush=True)
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
                 "Magnetra PWA 11 curated sources and 50 result pages reversible"],
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
    allowed={"/app.js":"javascript","/styles.css":"text/css","/sw.js":"javascript",
             "/i18n.js":"javascript","/index.html":"text/html",
             "/api/health":"application/json","/api/providers":"application/json",
             "/api/resolve":"application/json",SEARCH_PATH:"application/json",
             "/":"text/html",**{p:"application/json" for p in POSITIVE_PATHS.values()}}
    if (version is not None and not UUID.fullmatch(version)) or path not in allowed:
        raise Stop("UNAPPROVED_IMMUTABLE_HTTP_PATH")
    if body is not None and path!="/api/resolve":raise Stop("UNAPPROVED_POST_PATH")
    headers={"User-Agent":UA,"Cache-Control":"no-cache,no-store",
             "Accept-Encoding":"identity","Accept":allowed[path]}
    if version is not None:
        headers["Cloudflare-Workers-Version-Overrides"]='alexlab-magnetra="'+version+'"'
    data=None
    if body is not None:
        data=json.dumps(body,separators=(",",":")).encode()
        if len(data)>1200:raise Stop("BODY_TOO_LARGE")
        headers.update({"Origin":BASE,"Content-Type":"application/json"})
    req=urllib.request.Request(BASE+path,method="POST" if body is not None else "GET",
                               data=data,headers=headers)
    try:
        with urllib.request.build_opener(NoRedirect()).open(req,timeout=30 if data else 28 if path in POSITIVE_PATHS.values() else 18) as response:
            status,typ=response.status,response.headers.get("content-type","")
            raw=response.read(MAX_BYTES+1)
    except urllib.error.HTTPError as e:
        status,typ=e.code,e.headers.get("content-type","")
        raw=e.read(MAX_BYTES+1)
    except (urllib.error.URLError,TimeoutError,OSError):
        raise Stop("IMMUTABLE_EDGE_UNVERIFIED") from None
    if not raw or len(raw)>MAX_BYTES:raise Stop("RESPONSE_SIZE_UNVERIFIED")
    if status!=200 or allowed[path] not in typ.lower():
        raise Stop("HTTP_OR_TYPE_UNVERIFIED")
    if path in ("/app.js","/styles.css","/sw.js","/i18n.js","/index.html","/"):
        return raw
    try:payload=json.loads(raw)
    except (UnicodeError,ValueError):raise Stop("API_JSON_INVALID") from None
    if not isinstance(payload,dict):raise Stop("API_SHAPE_INVALID")
    return status,payload

def verify_candidate(version):
    for path,file in (("/app.js","web/app.js"),("/styles.css","web/styles.css"),
                      ("/sw.js","web/sw.js"),("/i18n.js","web/i18n.js"),
                      ):
        expected=hashlib.sha256((ROOT/file).read_bytes()).digest()
        actual=hashlib.sha256(candidate_http(path,version)).digest()
        if expected!=actual:raise Stop("IMMUTABLE_ASSET_SHA_MISMATCH")
    verify_reviewed_html((ROOT/"web/index.html").read_bytes(),candidate_http("/",version))
    status,health=candidate_http("/api/health",version)
    if health.get("ok") is not True or (health.get("total"),health.get("ported"))!=(46,46):
        raise Stop("IMMUTABLE_HEALTH_NOT_46")
    status,catalog=candidate_http("/api/providers",version)
    providers=catalog.get("providers")
    if not isinstance(providers,list) or len(providers)!=46:
        raise Stop("IMMUTABLE_CATALOG_NOT_46")
    ids=[x.get("id") for x in providers if isinstance(x,dict)]
    if len(ids)!=46 or len(set(ids))!=46 or "subsplease" not in ids:
        raise Stop("IMMUTABLE_ORIGINAL_ADAPTERS_MISSING")
    print("IMMUTABLE_FIVE_ASSETS_AND_ORIGINAL_46_API_PASS",flush=True)

def prove_original_positive_searches(version):
    # A single bounded source-authenticated original query per provider.
    # Source outage is NOT a successful release gate; no retries or false hashes.
    for provider,path in POSITIVE_PATHS.items():
        status,payload=candidate_http(path,version)
        rows,stats,errors=payload.get("results"),payload.get("stats"),payload.get("errors")
        if (status!=200 or not isinstance(rows,list) or not 1<=len(rows)<=100
            or not isinstance(stats,list) or len(stats)!=1 or
            stats[0].get("provider")!=provider or stats[0].get("ok") is not True
            or stats[0].get("count")!=len(rows) or errors!=[] or
            stats[0].get("cacheMode")=="stale"):
            raise Stop("SOURCE_"+provider.upper()+"_GENUINE_POSITIVE_NOT_PROVEN")
        for row in rows:
            magnet=row.get("magnet") if isinstance(row,dict) else None
            if (not isinstance(row,dict) or row.get("provider")!=provider or
                not isinstance(row.get("name"),str) or not isinstance(magnet,str) or
                not re.fullmatch(r"magnet:\?xt=urn:btih:(?:[a-f0-9]{40}|[a-z2-7]{32})(?:&[^\s]{0,11900})?",magnet,re.I)):
                raise Stop("SOURCE_"+provider.upper()+"_MAGNET_IDENTITY_UNPROVEN")
        print("GENUINE_"+provider.upper()+"_POSITIVE_RESULT: PASS (redacted)",flush=True)

def prove_real_owner_magnet(version):
    # API extraction only: never log magnet, BTIH or response payload.
    status,payload=candidate_http("/api/resolve",version,body={
        "provider":"nonameclub","details":ORIGINAL
    })
    magnet=payload.get("magnet")
    if (status!=200 or not isinstance(magnet,str) or not re.fullmatch(
        r"magnet:\?xt=urn:btih:(?:[a-f0-9]{40}|[a-z2-7]{32})(?:&[^\s]{0,11900})?",
        magnet,re.I
    )):
        raise Stop("EXACT_NONAMECLUB_OWNER_MAGNET_UNVERIFIED")
    print("IMMUTABLE_NONAMECLUB_EXACT_ORIGINAL_MAGNET: PASS (redacted)",flush=True)


def prove_owner_search_card(version):
    # This GET confirms the NEW Worker adapter does not manufacture /undefined.
    # Strict exact owner match, no fuzzy title inference, and no torrent fetches.
    status,payload=candidate_http(SEARCH_PATH,version)
    rows=payload.get("results")
    if status!=200 or not isinstance(rows,list) or len(rows)>100:
        raise Stop("EXACT_NONAMECLUB_OWNER_SEARCH_UNVERIFIED")
    matches=[x for x in rows if isinstance(x,dict)
        and x.get("provider")=="nonameclub" and x.get("details")==ORIGINAL]
    if len(matches)!=1:
        raise Stop("EXACT_NONAMECLUB_OWNER_CARD_NOT_UNIQUE")
    if matches[0].get("magnetSource") is not None:
        raise Stop("NONAMECLUB_FALSE_AUXILIARY_STILL_PRESENT")
    print("IMMUTABLE_NONAMECLUB_SEARCH_CARD_DETAILS_ONLY: PASS",flush=True)

def transition(first,source,target,label,version):
    stable(first,source)
    selector=[ACTIVE+"@"+str(target[ACTIVE])+"%",version+"@"+str(target[version])+"%"]
    if not _wrangler_deploy(selector,"Magnetra BTDigg/TPB source reliability "+label):
        raise Stop("VERSION_ONLY_PERCENTAGE_COMMAND_FAILED_"+label)
    after=wait_for(first,source,target,True)
    stable(after,target)
    print("BTDIGG_TPB_TRAFFIC_"+label+": PASS",flush=True)
    return after

def public_postflight(version):
    full={ACTIVE:0,version:100}
    for path,file in (("/app.js","web/app.js"),("/styles.css","web/styles.css"),
                      ("/sw.js","web/sw.js"),("/i18n.js","web/i18n.js"),
                      ("/","web/index.html")):
        expected=(ROOT/file).read_bytes()
        for attempt in range(8):
            actual=candidate_http(path,None)
            try:
                if path=="/":verify_reviewed_html(expected,actual)
                elif hashlib.sha256(expected).digest()!=hashlib.sha256(actual).digest():
                    raise Stop("PUBLIC_ASSET_SHA_MISMATCH")
                break
            except (Stop,ValueError):
                dep,shares=snapshot()
                if shares!=full or attempt==7:raise Stop("PUBLIC_ASSET_SHA_MISMATCH")
                time.sleep(5)
    status,health=candidate_http("/api/health",None)
    if health.get("ok") is not True or (health.get("total"),health.get("ported"))!=(46,46):
        raise Stop("PUBLIC_HEALTH_NOT_46")
    status,catalog=candidate_http("/api/providers",None)
    if not isinstance(catalog.get("providers"),list) or len(catalog["providers"])!=46:
        raise Stop("PUBLIC_CATALOG_NOT_46")
    print("PUBLIC_FIVE_ASSETS_HASHES_46_CATALOG_PASS",flush=True)

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
                "Magnetra rollback to previous 7475 curated PWA"):
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
    old_bytes=live_http("/app.js")
    if hashlib.sha256(old_bytes).digest()==hashlib.sha256((ROOT/"web/app.js").read_bytes()).digest():
        raise Stop("NEW_PWA_ALREADY_LIVE")
    old_blob=hashlib.sha1(b"blob "+str(len(old_bytes)).encode()+bytes([0])+old_bytes).hexdigest()
    if old_blob!=OLD_PUBLIC_GIT_BLOB:raise Stop("PUBLIC_PREVIOUS_IMMUTABLE_BLOB_CHANGED")
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
    prove_original_positive_searches(NEW)
    prove_real_owner_magnet(NEW)
    prove_owner_search_card(NEW)
    stable(deployed_slot,slot)

    deployed_canary=transition(deployed_slot,slot,canary,"CANARY_5",NEW)
    verify_candidate(NEW)
    prove_owner_search_card(NEW)
    stable(deployed_canary,canary)

    deployed_full=transition(deployed_canary,canary,full,"FULL_100",NEW)
    public_postflight(NEW)
    stable(deployed_full,full)
    print("BTDIGG_TPB_RESILIENCE_PRODUCTION_100_PASS: https://index.alexlab.media",flush=True)
    print("PREVIOUS_IMMUTABLE_7475_ROLLBACK_AT_ZERO:",ACTIVE,flush=True)
    print("OWNER_REAL_IPHONE_SAME_CARD_ACCEPTANCE_STILL_PENDING",flush=True)
    return 0

def main():
    if os.environ.get("MAGNETRA_BTDIGG_TPB_RELEASE_ACTION")!=ACTION:
        print("EXPLICIT_CURATED_11_PAGING_50_OWNER_PRODUCTION_ACTION_MISSING")
        return 2
    try:
        return release()
    except (Stop,AccountStop,ValueError,TypeError,KeyError,OSError):
        print("BTDIGG_TPB_RELEASE_STOP_NO_SUCCESS_ASSUMED",flush=True)
        rollback_if_safe(NEW)
        return 1
if __name__=="__main__":
    raise SystemExit(main())
