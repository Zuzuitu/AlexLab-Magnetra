#!/usr/bin/env python3
"""Manual-only 540b95/136c5 -> 540b0/136c100, guarded separate restore.

Fail closed on unknown versions, concurrent deployments and mismatch. Only one
version-only Wrangler write per explicit action; no automatic rollback, Worker
upload, provider retry, Flud transmission, torrent download or Rock64 changes.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urlencode

import deploy_magnetra_relevance_136c_slot as source
from deploy_magnetra_relevance_136c_canary import (
    CURRENT, NEW, FIVE, verify_source_asset, stable,
)
from deploy_magnetra_zero_percent import _wrangler_deploy

FULL={CURRENT:0,NEW:100}
RESTORED={CURRENT:100,NEW:0}
PROMOTE="CONFIRM_RELEVANCE_136C_FULL_100"
RESTORE="CONFIRM_RESTORE_540B_FROM_136C_FULL_100"

class Stop(Exception):pass
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        return None

def snapshot():
    return source.snapshot()

def verify_versions():
    source.verify_version(CURRENT)
    source.verify_version(NEW)

def screenshot_source_gate():
    """Single authentic source GET; no retry even for transient upstream 429."""
    path="/api/search?"+urlencode({
        "q":"the good dinosaur 2015",
        "providers":"torrent9,oxtorrent,ytsmx","category":"all"})
    data=source.request(path)
    rows,stats,errors=data.get("results"),data.get("stats"),data.get("errors")
    if not all(isinstance(v,list) for v in (rows,stats,errors)):
        raise Stop("SCREENSHOT_SOURCE_RESPONSE_SHAPE")
    ids={"torrent9","oxtorrent","ytsmx"}
    if len(stats)!=3 or len(rows)>300 or data.get("total")!=len(rows):
        raise Stop("SCREENSHOT_SOURCE_RESPONSE_COUNTS_UNVERIFIED")
    # Provider availability is a separate concern from title relevance. A
    # genuine TIMEOUT may be reported, but ONLY when the provider is correctly
    # attributed as unavailable and another original provider returns at
    # least one title with a verified query+year match. No retries of any kind.
    timed_out=set()
    for err in errors:
        if not isinstance(err,dict):
            raise Stop("SCREENSHOT_SOURCE_ERROR_SHAPE")
        provider=err.get("provider")
        if (provider not in ids or provider in timed_out or
                err.get("code")!="TIMEOUT"):
            raise Stop("SCREENSHOT_SOURCE_UNEXPECTED_ERROR")
        timed_out.add(provider)
    excluded=0
    counts={}
    for s in stats:
        if not isinstance(s,dict) or s.get("provider") not in ids:
            raise Stop("SCREENSHOT_SOURCE_STAT_INVALID")
        p=s["provider"]
        if p in counts:
            raise Stop("SCREENSHOT_DUPLICATE_SOURCE_STAT")
        count,raw,removed=s.get("count"),s.get("rawCount"),s.get("excludedOffTopic")
        if not all(type(v)==int and v>=0 for v in (count,raw,removed)) or raw!=count+removed:
            raise Stop("SCREENSHOT_SOURCE_RELEVANCE_COUNTS")
        if p in timed_out:
            if s.get("ok") is not False or any((count,raw,removed)):
                raise Stop("SCREENSHOT_TIMEOUT_NOT_TRUTHFULLY_REPORTED")
        elif s.get("ok") is not True:
            raise Stop("SCREENSHOT_HEALTHY_SOURCE_NOT_VERIFIED")
        counts[p]=count
        excluded+=removed
    if set(counts)!=ids or data.get("excludedOffTopic")!=excluded:
        raise Stop("SCREENSHOT_SOURCE_STAT_TOTALS")
    if sum(counts.values())!=len(rows):
        raise Stop("SCREENSHOT_SOURCE_RESULT_COUNT_MISMATCH")
    seen={key:0 for key in ids}
    for row in rows:
        if not isinstance(row,dict) or row.get("provider") not in ids:
            raise Stop("SCREENSHOT_SOURCE_WRONG_PROVIDER")
        provider=row["provider"]
        if provider in timed_out:
            raise Stop("SCREENSHOT_TIMEOUT_SOURCE_WITH_ROWS")
        actual=set(re.findall(r"[a-z0-9]+",str(row.get("name","")).lower()))
        if not {"good","dinosaur","2015"}.issubset(actual):
            raise Stop("SCREENSHOT_OFFTOPIC_LEAK")
        seen[provider]+=1
    if seen!=counts:
        raise Stop("SCREENSHOT_SOURCE_COUNT_PROVENANCE_MISMATCH")
    if not rows:
        raise Stop("SCREENSHOT_NO_POSITIVE_SAMPLE")
    print("SCREENSHOT_ORIGINAL_SOURCES: TITLE_GATE_PASS matches="+str(len(rows))+
          " excluded="+str(excluded)+" sourceTimeouts="+str(len(timed_out))+
          " (no source titles, magnets or URLs logged)")
    if timed_out:
        print("SOURCE_AVAILABILITY_DEGRADED: TIMEOUT providers="+
              ",".join(sorted(timed_out))+"; no retry; not counted as healthy")

def read_only_preflight():
    verify_versions()
    before,shares=snapshot()
    if shares!=FIVE:
        raise Stop("EXPECTED_EXACT_540B95_136C5_CANARY_MISSING")
    verify_source_asset()
    if not source.stage_e2e():
        raise Stop("KNABEN_TORRENTSCSV_SOURCE_NOT_VERIFIED")
    screenshot_source_gate()
    stable(before,FIVE)
    print("RELEVANCE_FULL_PREFLIGHT_PASS: five source IDs checked for title correctness; independent availability failures kept visible")
    return before

def await_version_split(before,target,previous,wrote):
    """Bounded metadata-only polling; never repeat a Wrangler write."""
    for n in range(4):
        record,shares=snapshot()
        if shares==target:
            if not wrote or record["id"]==before["id"]:
                raise Stop("TARGET_VISIBLE_BUT_WRITE_UNVERIFIED")
            return record
        if shares!=previous or not wrote:
            raise Stop("UNKNOWN_OR_CONCURRENT_DEPLOYMENT_NO_AUTO_ROLLBACK")
        if n<3:time.sleep(2)
    raise Stop("NEW_DISTRIBUTION_UNVERIFIED_NO_AUTO_RETRY")

def public_static_asset():
    """One GET of known origin, refuse redirects and all non-200 responses."""
    req=urllib.request.Request(
        "https://index.alexlab.media/app.js",
        headers={
            "Accept-Encoding":"identity",
            "Accept":"text/javascript,application/javascript",
            "Cache-Control":"no-cache,no-store,max-age=0",
            "User-Agent":"Magnetra136cFullOneShotPublicAsset/1.0",
        },method="GET")
    try:
        with urllib.request.build_opener(NoRedirect()).open(req,timeout=20) as response:
            if response.status!=200 or "javascript" not in response.headers.get("content-type",""):
                raise Stop("PUBLIC_ASSET_HTTP_OR_MIME_UNVERIFIED")
            data=response.read(800001)
    except (urllib.error.HTTPError,urllib.error.URLError,OSError,TimeoutError):
        raise Stop("PUBLIC_ASSET_TRANSPORT_UNVERIFIED") from None
    if not data or len(data)>800000:
        raise Stop("PUBLIC_ASSET_SIZE_UNVERIFIED")
    return data

def verify_public_assets(deployment):
    reviewed=(Path(__file__).resolve().parent.parent/"web"/"app.js").read_bytes()
    digest=hashlib.sha256(reviewed).digest()
    # Poll only 200 JS hash mismatches; NEVER retry HTTP errors/429/504 or provider calls.
    for attempt in range(12):
        data=public_static_asset()
        if hashlib.sha256(data).digest()==digest:
            print("RELEVANCE_FULL_PUBLIC_JS: PASS SHA256="+hashlib.sha256(reviewed).hexdigest()[:16])
            return
        observed,shares=snapshot()
        if observed["id"]!=deployment["id"] or shares!=FULL:
            raise Stop("POSTFLIGHT_DEPLOYMENT_CHANGED")
        if attempt<11:time.sleep(10)
    raise Stop("POSTFLIGHT_PUBLIC_ASSET_SHA_UNVERIFIED_CHECK_LATER_NO_REDEPLOY")

def promote():
    before=read_only_preflight()
    stable(before,FIVE)
    print("RELEVANCE_FULL_APPLY_ONCE: 540b0/136c100; restore 540b stored at 0")
    wrote=_wrangler_deploy(
        [CURRENT+"@0%",NEW+"@100%"],
        "Magnetra owner authorized relevance 136c 100%, 540b kept at 0% rollback")
    after=await_version_split(before,FULL,FIVE,wrote)
    verify_versions()
    verify_source_asset()
    verify_public_assets(after)
    final,shares=snapshot()
    if final["id"]!=after["id"] or shares!=FULL:
        raise Stop("FINAL_DEPLOYMENT_CHANGED")
    print("RELEVANCE_FULL_POSTFLIGHT_PASS: 136c100/540b0; no Flud, torrent, retries")
    print("IPHONE_SEARCH_UX: PENDING owner acceptance after actual full traffic release")
    return 0

def restore():
    verify_versions()
    before,shares=snapshot()
    if shares==RESTORED:
        print("RESTORE_ALREADY_SAFE: 540b100/136c0 no write")
        return 0
    if shares!=FULL:raise Stop("RESTORE_ONLY_FROM_EXACT_136C100_540B0")
    stable(before,FULL)
    print("RELEVANCE_RESTORE_APPLY_ONCE: 540b100/136c0")
    wrote=_wrangler_deploy(
        [CURRENT+"@100%",NEW+"@0%"],
        "Magnetra separately authorized restore 540b 100% from relevance 136c full")
    await_version_split(before,RESTORED,FULL,wrote)
    print("RELEVANCE_RESTORE_POSTFLIGHT_PASS: 540b100/136c0")
    return 0

def execute():
    action=os.environ.get("MAGNETRA_RELEVANCE_FULL_ACTION","")
    if action not in (PROMOTE,RESTORE):
        print("STOP: explicit owner manual action required before any Cloudflare requests")
        return 2
    try:
        return promote() if action==PROMOTE else restore()
    except (Stop,source.Stop,ValueError,TypeError,KeyError,OSError):
        print("RELEVANCE_FULL_STOP: CHECK_LOG_GATE_OR_CLOUDFLARE_METADATA; no automatic retry/rollback")
        return 1

if __name__=="__main__":sys.exit(execute())
