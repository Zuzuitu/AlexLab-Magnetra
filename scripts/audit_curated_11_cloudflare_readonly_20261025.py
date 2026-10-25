#!/usr/bin/env python3
"""Non-mutating preflight for the corrected 11-indexer Magnetra PWA.

GET requests only. Never stage, upload, promote, send magnets or print secrets.
The active production version and remaining rollback slot are observed, not guessed.
"""
from __future__ import annotations
import hashlib
import json
import sys
import urllib.error
import urllib.request

from deploy_magnetra_auto_pause_once import ROOT, UUID, NoRedirect, Stop as ReleaseStop
from deploy_magnetra_zero_percent import _get_api, _current_deployment, _shares
from inspect_companion_binding_readonly import (
    account_list, verify_account_scripts, validated_source, Stop as AccountStop
)
from stage_therarbag_iphone_20261024 import verify_binding_payload

BASE = "https://index.alexlab.media"
EXPECTED_ACTIVE = "8d9c19f4-ca38-428b-888e-757ef578c829"
EXPECTED_PUBLIC_JS_PREFIX = "1160fa81597ce6ca"
READ_ALLOWLIST = frozenset({"/app.js", "/api/health", "/api/providers"})
MAX_BYTES = 3_000_000

class Stop(Exception):
    pass

def get_public(path):
    if path not in READ_ALLOWLIST:
        raise Stop("PUBLIC_GET_PATH_NOT_ALLOWED")
    req=urllib.request.Request(
        BASE + path, method="GET",
        headers={"User-Agent": "MagnetraCurated11ReadOnlyAudit/1.0",
                 "Accept-Encoding": "identity", "Cache-Control": "no-cache, no-store"})
    try:
        with urllib.request.build_opener(NoRedirect()).open(req, timeout=20) as response:
            if response.status != 200:
                raise Stop("PUBLIC_READ_STATUS_UNVERIFIED")
            if path == "/app.js" and "javascript" not in response.headers.get("content-type", "").lower():
                raise Stop("PUBLIC_APP_MIME_UNVERIFIED")
            if path.startswith("/api/") and "json" not in response.headers.get("content-type", "").lower():
                raise Stop("PUBLIC_API_MIME_UNVERIFIED")
            data=response.read(MAX_BYTES+1)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError):
        raise Stop("PUBLIC_GET_FAILED") from None
    if not data or len(data)>MAX_BYTES:
        raise Stop("PUBLIC_BODY_INVALID")
    return data

def source_check():
    validated_source()
    app=(ROOT/"web/app.js").read_text(encoding="utf8")
    inv=json.loads((ROOT/"config/project-invariants.json").read_text(encoding="utf8"))
    hidden=inv["pwa_indexer_curation"]["hidden_ids"]
    if len(hidden)!=35 or len(set(hidden))!=35 or "subsplease" not in hidden:
        raise Stop("CURATED_11_INVARIANT_MISMATCH")
    if ('const hiddenIndexerIds=new Set('+json.dumps(hidden,separators=(",",":"),ensure_ascii=False)+');') not in app:
        raise Stop("CURATED_11_APP_MISMATCH")
    if ("function toggleAllProviders()" not in app or
        "function updateSelectAllButton()" not in app or
        "const RESULTS_PER_PAGE=50;" not in app or
        "stored.length===0" not in app):
        raise Stop("REVIEWED_CURATED_PWA_MISSING")
    if 'const CACHE="alexlab-magnetra-v9";' not in (ROOT/"web/sw.js").read_text(encoding="utf8"):
        raise Stop("REVIEWED_PWA_CACHE_MISSING")

def live_public_check():
    js=get_public("/app.js")
    digest=hashlib.sha256(js).hexdigest()
    health=json.loads(get_public("/api/health"))
    catalog=json.loads(get_public("/api/providers"))
    ids=[x.get("id") for x in catalog.get("providers",[]) if isinstance(x,dict)]
    if health.get("ok") is not True or (health.get("total"),health.get("ported"))!=(46,46):
        raise Stop("PUBLIC_46_HEALTH_UNVERIFIED")
    if len(ids)!=46 or len(set(ids))!=46 or "subsplease" not in ids:
        raise Stop("PUBLIC_ORIGINAL_46_IDS_UNVERIFIED")
    if digest==hashlib.sha256((ROOT/"web/app.js").read_bytes()).hexdigest():
        print("PUBLIC_APP_STATUS: CORRECTED_11_ALREADY_LIVE",flush=True)
        return "corrected"
    if not digest.startswith(EXPECTED_PUBLIC_JS_PREFIX):
        raise Stop("PUBLIC_APP_UNKNOWN_OR_CHANGED")
    print("PUBLIC_APP_STATUS: PREVIOUS_45_STILL_LIVE",flush=True)
    return "old45"

def observe_split():
    deployment=_current_deployment(_get_api("/deployments"))
    shares=_shares(deployment)
    if not isinstance(deployment.get("id"),str) or not deployment["id"]:
        raise Stop("CLOUDFLARE_DEPLOYMENT_ID_UNVERIFIED")
    active=[v for v,p in shares.items() if p==100 and UUID.fullmatch(v)]
    inactive=[v for v,p in shares.items() if p==0 and UUID.fullmatch(v)]
    if len(active)!=1 or len(inactive)>1 or len(shares) not in (1,2):
        raise Stop("CLOUDFLARE_SPLIT_NOT_EXACT_100_WITH_OPTIONAL_0")
    for version in shares:
        verify_binding_payload(version,_get_api("/versions/"+version))
    again=_current_deployment(_get_api("/deployments"))
    if again.get("id")!=deployment["id"] or _shares(again)!=shares:
        raise Stop("CLOUDFLARE_DEPLOYMENT_CHANGED_DURING_GET")
    print("CLOUDFLARE_ACTIVE_VERSION: "+active[0],flush=True)
    print("CLOUDFLARE_ACTIVE_TRAFFIC: 100_PERCENT",flush=True)
    print("CLOUDFLARE_INACTIVE_VERSION: "+(inactive[0] if inactive else "NONE"),flush=True)
    print("CLOUDFLARE_INACTIVE_TRAFFIC: "+("0_PERCENT" if inactive else "NONE"),flush=True)
    print("CLOUDFLARE_FOUR_BINDINGS_ALL_DEPLOYED_VERSIONS: PASS",flush=True)
    return active[0],inactive

def run():
    source_check()
    verify_account_scripts(account_list())
    live=live_public_check()
    active,inactive=observe_split()
    if active!=EXPECTED_ACTIVE:
        raise Stop("ACTIVE_IS_NOT_LAST_VERIFIED_DIRECT_DEPLOYMENT")
    if live!="old45":
        raise Stop("PRODUCTION_NO_LONGER_EXPECTED_45_BASELINE")
    if live_public_check()!="old45":
        raise Stop("PUBLIC_CHANGED_DURING_READONLY_AUDIT")
    print("CURATED_11_BASELINE_PREFLIGHT: PASS_READONLY_NO_WRITES",flush=True)
    print("PUBLIC_46_BACKEND_ADAPTERS: PASS",flush=True)
    return 0

def main():
    try:
        return run()
    except (Stop, ReleaseStop, AccountStop, ValueError, TypeError, KeyError, UnicodeError, json.JSONDecodeError):
        print("CURATED_11_BASELINE_PREFLIGHT: STOP_UNVERIFIED_NO_WRITES",flush=True)
        return 1

if __name__=="__main__":
    sys.exit(main())
