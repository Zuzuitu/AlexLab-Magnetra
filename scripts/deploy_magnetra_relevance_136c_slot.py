#!/usr/bin/env python3
"""Owner-gated 540b100/249d0 -> 540b100/136c0, then stage-only relevance E2E.

Version-only 0%-slot write happens ONCE and never changes normal user traffic.
No upload, API retries, source substitution, Flud, magnet disclosure or Rock64.
Previous version 249d remains stored in Cloudflare, outside deployment split.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.parse import urlencode
import urllib.request
import urllib.error

from deploy_magnetra_zero_percent import _get_api, _current_deployment, _shares, _wrangler_deploy
from inspect_magnetra_fix_stage import ACTIVE as PREVIOUS, STAGED as CURRENT, EXPECTED, binding_pairs

NEW="136c1425-0070-48db-b995-5708bd35bb75"
ACTION="CONFIRM_540B100_136C0_SLOT_AND_READONLY_E2E"
BEFORE={CURRENT:100,PREVIOUS:0}
SLOT={CURRENT:100,NEW:0}
BASE="https://index.alexlab.media"
OVERRIDE='alexlab-magnetra="'+NEW+'"'
TITLE="the good dinosaur 2015"
SOURCE_IDS=("knaben","torrentscsv")

class Stop(Exception):
    pass
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        return None

def verify_version(version_id):
    if version_id not in (NEW,CURRENT):
        raise Stop("UNRECOGNIZED_VERSION_ID")
    p=_get_api("/versions/"+version_id)
    if not isinstance(p,dict) or p.get("success") is not True or not isinstance(p.get("result"),dict) or p["result"].get("id")!=version_id:
        raise Stop("VERSION_ID_NOT_VERIFIED")
    b=binding_pairs(p)
    for name,kinds in EXPECTED.items():
        if not any((name,kind) in b for kind in kinds):
            raise Stop("VERSION_BINDING_UNVERIFIED_"+name)

def snapshot():
    r=_current_deployment(_get_api("/deployments"))
    if not isinstance(r.get("id"),str) or not r["id"]:
        raise Stop("DEPLOYMENT_ID_UNVERIFIED")
    return r,_shares(r)

def request(path,as_json=True):
    if not path.startswith("/") or path.startswith("//") or "\\" in path or len(path)>400:
        raise Stop("UNSAFE_FIXED_PUBLIC_PATH")
    headers={"Cloudflare-Workers-Version-Overrides":OVERRIDE,
      "User-Agent":"Magnetra136cSlotReadOnlyE2E/1.0",
      "Accept-Encoding":"identity","Cache-Control":"no-store",
      "Accept":"application/json" if as_json else "text/javascript,application/javascript"}
    req=urllib.request.Request(BASE+path,headers=headers,method="GET")
    try:
        with urllib.request.build_opener(NoRedirect()).open(req,timeout=25) as res:
            mime=res.headers.get("content-type","")
            if res.status!=200 or ("application/json" if as_json else "javascript") not in mime:
                raise Stop("OVERRIDE_HTTP_OR_CONTENT_TYPE_UNVERIFIED")
            body=res.read(1_000_001)
    except (urllib.error.URLError,TimeoutError,OSError):
        raise Stop("OVERRIDE_TRANSPORT_UNVERIFIED") from None
    if not body or len(body)>1_000_000: raise Stop("OVERRIDE_SIZE_UNVERIFIED")
    if not as_json: return body
    try:
        data=json.loads(body)
    except (ValueError,UnicodeError):
        raise Stop("OVERRIDE_JSON_INVALID") from None
    if not isinstance(data,dict): raise Stop("OVERRIDE_JSON_SHAPE")
    return data

def stage_e2e():
    local=(Path(__file__).resolve().parent.parent/"web"/"app.js").read_bytes()
    from_net=request("/app.js",as_json=False)
    if hashlib.sha256(local).digest()!=hashlib.sha256(from_net).digest():
        raise Stop("NEW_IMMUTABLE_PWA_ASSETS_DONT_MATCH_REVIEWED_SOURCE")
    print("STAGED_136C_APP_JS: PASS SHA256="+hashlib.sha256(local).hexdigest()[:16])
    catalog=request("/api/providers").get("providers")
    if not isinstance(catalog,list) or len(catalog)!=46 or len({x.get("id") for x in catalog if isinstance(x,dict)})!=46:
        raise Stop("STAGED_PROVIDER_CATALOG_NOT_46")
    print("STAGED_CATALOG: PASS 46 original IDs")
    query=urlencode({"q":TITLE,"providers":",".join(SOURCE_IDS),"category":"all"})
    response=request("/api/search?"+query)
    rows,stats,errors=response.get("results"),response.get("stats"),response.get("errors")
    if not isinstance(rows,list) or not isinstance(stats,list) or not isinstance(errors,list):
        raise Stop("STAGED_RELEVANCE_JSON_SCHEMA_UNVERIFIED")
    if len(stats)!=len(SOURCE_IDS) or len(rows)>200 or len(errors)>len(SOURCE_IDS):
        raise Stop("STAGED_RELEVANCE_SOURCE_SCHEMA_UNVERIFIED")
    if response.get("total")!=len(rows):
        raise Stop("STAGED_RELEVANCE_TOTAL_MISMATCH")
    expected={"good","dinosaur","2015"}
    for item in rows:
        if not isinstance(item,dict) or item.get("provider") not in SOURCE_IDS:
            raise Stop("STAGED_RELEVANCE_SOURCE_IDENTITY_MISMATCH")
        actual=set(re.findall(r"[a-z0-9]+",str(item.get("name","")).lower()))
        if not expected.issubset(actual):
            raise Stop("STAGED_UNRELATED_RESULT_LEAKED")
    excluded=0
    names=[]
    for stat in stats:
        if not isinstance(stat,dict) or stat.get("provider") not in SOURCE_IDS:
            raise Stop("STAGED_STATS_PROVIDER_INVALID")
        n,raw,removed=stat.get("count"),stat.get("rawCount"),stat.get("excludedOffTopic")
        if not all(type(x)==int and x>=0 for x in (n,raw,removed)) or raw!=n+removed:
            raise Stop("STAGED_RELEVANCE_COUNTS_INCONSISTENT")
        excluded+=removed
        names.append(stat["provider"])
    if set(names)!=set(SOURCE_IDS) or response.get("excludedOffTopic")!=excluded:
        raise Stop("STAGED_RELEVANCE_AGGREGATE_INVALID")
    print("STAGED_TITLE_QUERY: PASS matched="+str(len(rows))+
          " excludedOffTopic="+str(excluded)+
          " providerErrors="+str(len(errors))+" (redacted)")
    # Provider 403s/timeouts are not coded as excluded off-topic rows.
    if errors: print("STAGED_SOURCE_LIVE_AVAILABILITY: INCONCLUSIVE (genuine source errors)")
    if not rows: print("STAGED_SOURCE_TITLE_MATCHES: NO_POSITIVE_SAMPLE (do not claim discovery success)")
    else: print("STAGED_SOURCE_TITLE_MATCHES: PASS authentic source titles (names/magnets withheld)")
    return len(rows)>0 and not errors

def execute():
    if os.environ.get("MAGNETRA_RELEVANCE_ZERO_ACTION")!=ACTION:
        print("STOP: exact manual approval absent; no network or write")
        return 2
    verify_version(CURRENT)
    verify_version(NEW)
    before,shares=snapshot()
    if shares!=BEFORE:
        raise Stop("EXPECTED_540B100_249D0_DEPLOYMENT_MISSING")
    same,split=snapshot()
    if before["id"]!=same["id"] or split!=BEFORE:
        raise Stop("CONCURRENT_DEPLOYMENT_NO_WRITE")
    print("PREFLIGHT_PASS: immutable 540b & 136c with three bindings each; 540b100/249d0")
    print("ZERO_SLOT_WRITE_ONCE: 540b100 / 136c0; no user traffic change")
    wrote=_wrangler_deploy([CURRENT+"@100%",NEW+"@0%"],
       "Magnetra relevance fix 136c at 0%, prior 540b retains 100%")
    after=None
    for attempt in range(4):
        after,split=snapshot()
        if split==SLOT:
            if not wrote or after["id"]==before["id"]:
                raise Stop("ZERO_SLOT_VISIBLE_BUT_WRITE_UNVERIFIED")
            break
        if split!=BEFORE or not wrote:
            raise Stop("ZERO_SLOT_UNEXPECTED_STATE_MANUAL_REVIEW")
        if attempt==3:
            raise Stop("ZERO_SLOT_NOT_CONFIRMED_MANUAL_REVIEW")
        time.sleep(2)
    print("ZERO_SLOT_POSTFLIGHT: PASS (540b100, 136c0)")
    verify_version(NEW)
    # No second write/retries of provider requests, only read-only staged E2E.
    positive=stage_e2e()
    end,split=snapshot()
    if split!=SLOT or end["id"]!=after["id"]:
        raise Stop("CONCURRENT_DEPLOYMENT_DURING_E2E")
    print("NEW_VERSION_136C_E2E:", "PASS" if positive else "PARTIAL_OR_SOURCE_UNAVAILABLE")
    print("PRODUCTION_REMAINS_540B_100: no provider/asset deploy")
    return 0 if positive else 1

if __name__=="__main__":
    try:
        sys.exit(execute())
    except (Stop,ValueError,TypeError,KeyError) as e:
        print("ZERO_SLOT_E2E_STOP:",str(e) if isinstance(e,Stop) else "SANITIZED_METADATA_OR_TYPE")
        sys.exit(1)
