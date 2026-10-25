#!/usr/bin/env python3
"""Read-only exact public PWA hash and Cloudflare binding/deployment audit.

Never deploy, stage, mutate, send magnets, disclose secrets or follow redirects.
Checks the already-merged 45-source/50-result app against the actual live
responses, without assuming that a generic deployment preserved a rollback slot.
"""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request

from deploy_magnetra_auto_pause_once import ROOT, Stop, NoRedirect, UUID, snapshot
from deploy_magnetra_zero_percent import _get_api
from inspect_companion_binding_readonly import account_list, verify_account_scripts
from stage_therarbag_iphone_20261024 import validate_source, verify_binding_payload

BASE="https://index.alexlab.media"
APP_BLOB="eb98cfe79e1a9edb48b6e3d650d7eed81ed7c3a4"
ASSETS=(("/app.js","web/app.js","javascript"),
        ("/i18n.js","web/i18n.js","javascript"),
        ("/styles.css","web/styles.css","text/css"),
        ("/sw.js","web/sw.js","javascript"),
        ("/index.html","web/index.html","text/html"))
MAX_BODY=1_200_000

def read_public(path,expected_mime):
    if path not in [a[0] for a in ASSETS]+["/api/health","/api/providers"]:
        raise Stop("UNAPPROVED_READONLY_ROUTE")
    req=urllib.request.Request(BASE+path,method="GET",headers={
        "User-Agent":"MagnetraReadOnlyPostreleaseAudit/1.0",
        "Accept-Encoding":"identity",
        "Cache-Control":"no-cache, no-store",
        "Pragma":"no-cache"})
    try:
        with urllib.request.build_opener(NoRedirect()).open(req,timeout=18) as response:
            if response.status!=200 or expected_mime not in response.headers.get("content-type","").lower():
                raise Stop("PUBLIC_HTTP_OR_MIME_INVALID")
            data=response.read(MAX_BODY+1)
    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,OSError):
        raise Stop("PUBLIC_READ_FAILED") from None
    if not data or len(data)>MAX_BODY:raise Stop("PUBLIC_BODY_INVALID")
    return data

def source_guard():
    validate_source()
    try:
        p=subprocess.run(["git","hash-object","web/app.js"],cwd=ROOT,text=True,
                         capture_output=True,timeout=8,check=False)
    except (OSError,subprocess.TimeoutExpired):
        raise Stop("SOURCE_HASH_CHECK_FAILED") from None
    if p.returncode or p.stdout.strip()!=APP_BLOB:
        raise Stop("REVIEWED_APP_SOURCE_CHANGED")
    source=(ROOT/"web/app.js").read_text(encoding="utf8")
    html=(ROOT/"web/index.html").read_text(encoding="utf8")
    if not all((
        'const hiddenIndexerIds=new Set(["subsplease"]);' in source,
        'const RESULTS_PER_PAGE=50;' in source,
        'function renderPagination(total)' in source,
        'id="selectAllProviders">Selectează toate' in html,
        'id="selectWorking"' not in html,
        'id="resultsPagination"' in html,
        '"subsplease"' in source,
    )):raise Stop("REVIEWED_OWNER_PWA_FEATURES_MISSING")

def verify_assets():
    for path,local,mime in ASSETS:
        reviewed=hashlib.sha256((ROOT/local).read_bytes()).digest()
        public=hashlib.sha256(read_public(path,mime)).digest()
        if public!=reviewed:raise Stop("PUBLIC_ASSET_SHA_MISMATCH_"+path.strip("/").replace(".","_"))
        print("PUBLIC_ASSET_EXACT_SHA_PASS:"+path,flush=True)
    health=json.loads(read_public("/api/health","application/json"))
    catalog=json.loads(read_public("/api/providers","application/json"))
    if (health.get("ok") is not True
            or (health.get("total"),health.get("ported"))!=(46,46)):
        raise Stop("LIVE_46_HEALTH_UNVERIFIED")
    providers=catalog.get("providers")
    if not isinstance(providers,list) or len(providers)!=46:
        raise Stop("LIVE_46_CATALOG_UNVERIFIED")
    ids=[p.get("id") for p in providers if isinstance(p,dict)]
    if len(ids)!=46 or len(set(ids))!=46 or "subsplease" not in ids:
        raise Stop("LIVE_46_IDENTITY_UNVERIFIED")
    print("PUBLIC_45_PICKER_50_RESULTS_STATIC_AND_46_API_PASS",flush=True)

def verify_deployment():
    verify_account_scripts(account_list())
    dep,split=snapshot()
    if not isinstance(dep.get("id"),str) or not dep["id"]:
        raise Stop("LIVE_DEPLOYMENT_METADATA_UNVERIFIED")
    active=[v for v,p in split.items() if p==100 and UUID.fullmatch(v)]
    if len(active)!=1 or len(split)>2 or any(p not in (0,100) for p in split.values()):
        raise Stop("LIVE_SPLIT_NOT_SINGLE_ACTIVE")
    for version in split:
        verify_binding_payload(version,_get_api("/versions/"+version))
    if snapshot()[0].get("id")!=dep["id"] or snapshot()[1]!=split:
        raise Stop("CONCURRENT_DEPLOYMENT_CHANGED")
    print("CLOUDFLARE_ACTIVE_IMMUTABLE_VERSION:"+active[0],flush=True)
    print("CLOUDFLARE_ACTIVE_FOUR_BINDINGS:PASS",flush=True)
    previous="76a15eae-5c8c-41a2-bace-adb9b2460933"
    if split.get(previous)==0:
        print("PREVIOUS_IOS_STABLE_VERSION_0_PERCENT_SLOT:VERIFIED",flush=True)
    else:
        print("PREVIOUS_IOS_STABLE_VERSION_0_PERCENT_SLOT:NOT_PRESENT_UNVERIFIED",flush=True)
    print("CLOUDFLARE_TRAFFIC_DISTINCT_VERSION_COUNT:"+str(len(split)),flush=True)
    return active[0],split

def main():
    try:
        source_guard()
        verify_assets()
        active,split=verify_deployment()
        verify_assets() # fail on changes or stale CDN after read-only account check
        print("POSTRELEASE_READONLY_AUDIT_PASS_NO_WRITES",flush=True)
        return 0
    except (Stop,ValueError,KeyError,TypeError,UnicodeError,json.JSONDecodeError):
        print("POSTRELEASE_READONLY_AUDIT_STOP_UNVERIFIED",flush=True)
        return 1

if __name__=="__main__":
    sys.exit(main())
