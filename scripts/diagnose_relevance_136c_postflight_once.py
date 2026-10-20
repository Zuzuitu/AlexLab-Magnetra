#!/usr/bin/env python3
"""Read-only one-shot 136c@0% attribution and original query diagnostics.

No Cloudflare write, no source retry, no redirects, no magnet/download/Flud.
Output only aggregate results and truncated hashes (never source titles or URLs).
"""
from __future__ import annotations
import hashlib, json, re, sys
from pathlib import Path
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from urllib.request import Request, HTTPRedirectHandler, build_opener

from deploy_magnetra_zero_percent import _get_api, _current_deployment, _shares
from inspect_magnetra_fix_stage import STAGED as CURRENT, binding_pairs, EXPECTED

NEW="136c1425-0070-48db-b995-5708bd35bb75"
BASE="https://index.alexlab.media"
LIMIT=1000000
TITLE="the good dinosaur 2015"
SOURCE_IDS=("torrent9","oxtorrent","ytsmx")
ALLOW={"app.js","api/search"}
class Stop(Exception): pass
class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def get(kind,version=None,bust=False):
    if kind not in ALLOW: raise Stop("UNAPPROVED_ROUTE")
    route="/"+kind
    if kind=="app.js" and bust:
        route+="?magnetra_136c_asset_audit=20261020"
    if kind=="api/search":
        route+="?"+urlencode({"q":TITLE,"providers":",".join(SOURCE_IDS),"category":"all"})
    headers={"Accept-Encoding":"identity", "Cache-Control":"no-cache,no-store,max-age=0",
             "Pragma":"no-cache", "User-Agent":"MagnetraReadOnly136cPostflight/1.0",
             "Accept":"application/json" if kind=="api/search" else "text/javascript"}
    if version is not None:
        if version not in (NEW,CURRENT): raise Stop("UNKNOWN_OVERRIDE_VERSION")
        headers["Cloudflare-Workers-Version-Overrides"]='alexlab-magnetra="'+version+'"'
    req=Request(BASE+route,headers=headers,method="GET")
    try:
        with build_opener(NoRedirect()).open(req, timeout=26) as response:
            mimetype=response.headers.get("content-type","")
            if response.status!=200 or ("application/json" if kind=="api/search" else "javascript") not in mimetype:
                raise Stop("HTTP_OR_MIME_UNVERIFIED")
            data=response.read(LIMIT+1)
            age=response.headers.get("age","?")[:20]
            edge=response.headers.get("cf-cache-status","?")[:30]
    except HTTPError as e:
        raise Stop("HTTP_"+str(e.code)) from None
    except (URLError,TimeoutError,OSError):
        raise Stop("TRANSPORT_UNVERIFIED") from None
    if not data or len(data)>LIMIT: raise Stop("RESPONSE_SIZE_UNVERIFIED")
    return data,edge,age

def asset_probe(label,version=None,bust=False):
    try:
        data,edge,age=get("app.js",version,bust)
    except Stop as e:
        print(label+": UNVERIFIED "+str(e))
        return None
    h=hashlib.sha256(data).hexdigest()
    print(label+": SHA256_PREFIX="+h[:16]+" BYTES="+str(len(data))+
          " CF_CACHE="+edge+" AGE="+age)
    return data

def main():
    current=_shares(_current_deployment(_get_api("/deployments")))
    print("DEPLOYED_VERSION_SHARES: 540b="+str(current.get(CURRENT))+
          " 136c="+str(current.get(NEW))+" num="+str(len(current)))
    if current != {CURRENT:100,NEW:0}:
        raise Stop("NOT_EXACT_540B100_136C0_NO_TEST")
    stage=_get_api("/versions/"+NEW)
    if stage.get("success") is not True or stage.get("result",{}).get("id")!=NEW:
        raise Stop("136C_IMMUTABLE_VERSION_UNVERIFIED")
    bindings=binding_pairs(stage)
    if not all(any((name,kind) in bindings for kind in kinds) for name,kinds in EXPECTED.items()):
        raise Stop("136C_BINDINGS_UNVERIFIED")
    print("136C_IMMUTABLE_METADATA: PASS 3 required binding names/types")
    local=(Path(__file__).resolve().parent.parent/"web/app.js").read_bytes()
    print("REVIEWED_SOURCE_APP_JS: SHA256_PREFIX="+hashlib.sha256(local).hexdigest()[:16]+
          " BYTES="+str(len(local)))
    stage_asset=asset_probe("STAGE_136C_OVERRIDE",NEW)
    active_asset=asset_probe("PROD_540B_OVERRIDE",CURRENT)
    public_asset=asset_probe("PUBLIC_DEFAULT")
    bust_asset=asset_probe("STAGE_136C_CACHE_BUSTED",NEW,True)
    for label,item in (("STAGE_136C_OVERRIDE",stage_asset),("PROD_540B_OVERRIDE",active_asset),
                       ("PUBLIC_DEFAULT",public_asset),("STAGE_136C_CACHE_BUSTED",bust_asset)):
        cat="MATCH_NEW_REVIEWED" if item==local else "MATCH_PROD_540B" if item==active_asset else "UNKNOWN_OR_UNVERIFIED"
        print("ASSET_ATTRIBUTION_"+label+": "+cat)
    try:
        payload,edge,age=get("api/search",NEW)
        d=json.loads(payload)
        rows,stats,errors=d.get("results"),d.get("stats"),d.get("errors")
        if not all(isinstance(a,list) for a in (rows,stats,errors)):raise Stop("API_SEARCH_JSON_SCHEMA_UNVERIFIED")
        print("STAGED_API_SCHEMA: fields rawCount="+str(all(isinstance(s,dict) and isinstance(s.get("rawCount"),int) for s in stats))+
              " excludedOffTopic="+str(isinstance(d.get("excludedOffTopic"),int))+
              " providerStats="+str(len(stats))+" returned="+str(len(rows))+" errors="+str(len(errors)))
        if len(stats)!=len(SOURCE_IDS) or len(rows)>300:raise Stop("SOURCE_STATS_COUNT_UNVERIFIED")
        for item in rows:
            if not isinstance(item,dict) or item.get("provider") not in SOURCE_IDS:
                raise Stop("ROW_PROVENANCE_UNVERIFIED")
            if not {"good","dinosaur","2015"}.issubset(set(re.findall(r"[a-z0-9]+",str(item.get("name","")).lower()))):
                raise Stop("UNRELATED_RESULT_STILL_SHOWN")
        if d.get("total")!=len(rows):raise Stop("COUNT_INCONSISTENT")
        print("STAGED_TITLE_RELEVANCE: PASS rows_verified="+str(len(rows))+
              " exclusions="+str(d.get("excludedOffTopic","UNVERIFIED")))
        if errors or not rows:print("LIVE_POSITIVE_SOURCE_ACCEPTANCE: NOT_PROVEN")
        else:print("LIVE_POSITIVE_SOURCE_ACCEPTANCE: PASS")
    except Stop as e:
        print("STAGED_QUERY: INCONCLUSIVE "+str(e))
    except (ValueError,KeyError,TypeError):
        print("STAGED_QUERY: INCONCLUSIVE BAD_RESPONSE")
    print("DIAGNOSTIC_COMPLETE: READ_ONLY_NO_DEPLOY_NO_RETRIES_NO_FLUD")
    return 0

if __name__=="__main__":
    try:sys.exit(main())
    except Stop as e:
        print("DIAGNOSTIC_STOP: "+str(e))
        sys.exit(1)
    except (ValueError,TypeError,KeyError):
        print("DIAGNOSTIC_STOP: SANITIZED_CLOUDFLARE_METADATA")
        sys.exit(1)
