#!/usr/bin/env python3
"""Resume the EXISTING verified 0%-slot candidate; never reupload assets.

Exact 136c@100 / c86c@0 -> 136c@0 / c86c@100, with manual-only rollback.
The stage candidate, its 3 immutable binding names, reviewed JS/CSS bytes and
the entire reviewed HTML (modulo only strict Cloudflare Insights insertion)
must pass before the single version-only Wrangler traffic write.
"""
from __future__ import annotations
import hashlib
import os
from pathlib import Path
import sys
import time
import urllib.error
import urllib.request
from deploy_magnetra_auto_pause_once import (
    bindings, current, stable, static_get, wait_for, _wrangler_deploy, Stop,
    NoRedirect
)
from cloudflare_html_asset_guard import verify_reviewed_html, HTMLAssetMismatch

OLD="136c1425-0070-48db-b995-5708bd35bb75"
NEW="c86c9a32-31fd-4952-86ed-b35f1763b342"
SLOT={OLD:100,NEW:0}
FULL={OLD:0,NEW:100}
ROOT=Path(__file__).resolve().parent.parent
BASE="https://index.alexlab.media"
PROMOTE="CONFIRM_RESUME_VERIFIED_C86C_100"
RESTORE="CONFIRM_RESTORE_136C_FROM_C86C_100"

def html_root(version):
    # /index.html is deliberately NOT requested; Cloudflare redirects it to /.
    headers={
      "Accept-Encoding":"identity",
      "Cache-Control":"no-cache,no-store,max-age=0",
      "Pragma":"no-cache",
      "User-Agent":"MagnetraAutoPauseVerifiedResume/1.0",
    }
    if version:
        headers["Cloudflare-Workers-Version-Overrides"]='alexlab-magnetra="'+version+'"'
    req=urllib.request.Request(BASE+"/",headers=headers,method="GET")
    try:
        with urllib.request.build_opener(NoRedirect()).open(req,timeout=20) as resp:
            if resp.status!=200 or "text/html" not in resp.headers.get("content-type",""):
                raise Stop("HTML_ROOT_NON200_OR_TYPE")
            data=resp.read(1200001)
    except (urllib.error.HTTPError,urllib.error.URLError,OSError,TimeoutError):
        raise Stop("HTML_ROOT_TRANSPORT_NO_RETRY") from None
    if not data or len(data)>1200000:
        raise Stop("HTML_ROOT_BAD_SIZE")
    return data

def verify_assets(version,first,shares):
    """Never retry a non-200, 429 or 504; bounded polling ONLY HTTP-200 SHA lag."""
    for route,filename in (("/app.js","web/app.js"),("/styles.css","web/styles.css")):
        expected=(ROOT/filename).read_bytes()
        digest=hashlib.sha256(expected).digest()
        for attempt in range(12):
            got=static_get(route,version)
            if hashlib.sha256(got).digest()==digest:
                print("REVIEWED_ASSET_PASS: "+route+" sha="+hashlib.sha256(expected).hexdigest()[:16])
                break
            stable(first,shares)
            if attempt==11:raise Stop("ASSET_SHA_MISMATCH_"+route)
            time.sleep(8)
    raw=(ROOT/"web/index.html").read_bytes()
    # Re-run the proven strict staged HTML source check. It fails if even one
    # character of reviewed HTML differs outside the sole bounded CF beacon.
    try:
        identity=verify_reviewed_html(raw,html_root(version))
    except HTMLAssetMismatch:
        raise Stop("HTML_NOT_REVIEWED_SOURCE_OR_KNOWN_CLOUDFLARE_BEACON") from None
    print("REVIEWED_HTML_PASS: "+identity+" source_sha="+hashlib.sha256(raw).hexdigest()[:16])

def promote():
    first=current(SLOT)
    bindings(OLD)
    bindings(NEW)
    stable(first,SLOT)
    print("RESUME_PREFLIGHT: existing immutable c86c at 0%, 136c at 100%; NO VERSION UPLOAD")
    verify_assets(NEW,first,SLOT)
    stable(first,SLOT)
    print("RESUME_TRAFFIC_WRITE_ONCE: 136c0/c86c100; 136c immutable rollback stays")
    wrote=_wrangler_deploy(
        [OLD+"@0%",NEW+"@100%"],
        "Magnetra auto-pause c86c verified 0% stage resume; 136c retained at 0%")
    after=wait_for(first,SLOT,FULL,wrote)
    bindings(OLD)
    bindings(NEW)
    verify_assets(None,after,FULL)
    stable(after,FULL)
    print("RESUME_FULL_POSTFLIGHT_PASS: c86c100/136c0; iPhone acceptance pending")
    return 0

def restore():
    first=current(FULL)
    bindings(OLD)
    bindings(NEW)
    stable(first,FULL)
    print("MANUAL_RESTORE_WRITE_ONCE: 136c100/c86c0")
    wrote=_wrangler_deploy(
        [OLD+"@100%",NEW+"@0%"],
        "Magnetra manual known-state restore original 136c source relevance")
    wait_for(first,FULL,SLOT,wrote)
    print("MANUAL_RESTORE_POSTFLIGHT_PASS: 136c100/c86c0")
    return 0

def execute():
    action=os.environ.get("MAGNETRA_AUTO_PAUSE_RESUME_ACTION","")
    if action not in (PROMOTE,RESTORE):
        print("STOP: owner action must be explicitly chosen; no Cloudflare requests")
        return 2
    try:return promote() if action==PROMOTE else restore()
    except (Stop,ValueError,KeyError,TypeError,OSError):
        print("RESUME_STOP: immutable/source/routing/postflight gate; no automatic rewrite or rollback")
        return 1

if __name__=="__main__":sys.exit(execute())
