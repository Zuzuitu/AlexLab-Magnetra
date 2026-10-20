#!/usr/bin/env python3
"""One-shot read-only audit for newly uploaded Magnetra relevance fix.

Validates immutable version, secret names/types, unchanged production and source
asset SHA. If an override is not available until 0%-slot deployment, records
UNVERIFIED (never assumes user traffic changed). No retries or downloads.
"""
from __future__ import annotations
import hashlib
from pathlib import Path
import sys
import urllib.request
import urllib.error
from deploy_magnetra_zero_percent import _get_api, _current_deployment, _shares
from inspect_magnetra_fix_stage import STAGED as OLD, ACTIVE as ROLLBACK, EXPECTED, binding_pairs

NEW="136c1425-0070-48db-b995-5708bd35bb75"
URL="https://index.alexlab.media/app.js"
class Stop(Exception): pass
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl): return None

def read_asset(version):
    headers={"Cloudflare-Workers-Version-Overrides":'alexlab-magnetra="'+version+'"',
             "Accept-Encoding":"identity","Cache-Control":"no-store",
             "User-Agent":"MagnetraOneShot136cReadOnly/1.0"}
    try:
        req=urllib.request.Request(URL,headers=headers,method="GET")
        with urllib.request.build_opener(NoRedirect).open(req,timeout=18) as res:
            if res.status!=200 or "javascript" not in res.headers.get("content-type",""):
                raise Stop("OVERRIDE_ASSET_HTTP_UNVERIFIED")
            body=res.read(800001)
    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,OSError):
        raise Stop("OVERRIDE_ASSET_NOT_ROUTABLE")
    if not body or len(body)>800000: raise Stop("OVERRIDE_ASSET_LENGTH_UNVERIFIED")
    return body

def main():
    p=_get_api("/versions/"+NEW)
    if p.get("success") is not True or p.get("result",{}).get("id")!=NEW:
        raise Stop("NEW_IMMUTABLE_VERSION_MISSING")
    pairs=binding_pairs(p)
    for name,kinds in EXPECTED.items():
        if not any((name,kind) in pairs for kind in kinds):
            raise Stop("NEW_VERSION_BINDING_MISSING_"+name)
    print("NEW_VERSION_136C_BINDINGS: PASS (3 names/types, values withheld)")
    record=_current_deployment(_get_api("/deployments"))
    shares=_shares(record)
    print("LIVE_TRAFFIC_540B="+str(shares.get(OLD))+" 249D="+str(shares.get(ROLLBACK))+
          " NEW_136C="+str(shares.get(NEW,0))+" VERSIONS="+str(len(shares)))
    if shares!={OLD:100,ROLLBACK:0}: raise Stop("UNEXPECTED_PRODUCTION_VERSION_SPLIT")
    print("PRODUCTION_UNCHANGED: PASS (540b@100,249d@0; 136c not deployed)")
    try:
        new_asset=read_asset(NEW)
    except Stop as exc:
        print("NEW_VERSION_ASSET_OVERRIDE: UNVERIFIED ("+str(exc)+"); 0%-slot required for E2E")
        return 0
    expected=(Path(__file__).resolve().parent.parent/"web"/"app.js").read_bytes()
    if hashlib.sha256(new_asset).digest()!=hashlib.sha256(expected).digest():
        print("NEW_VERSION_ASSET_OVERRIDE: NOT_MATCHED_OR_NOT_ROUTABLE; no release")
        return 0
    print("NEW_VERSION_ASSET_OVERRIDE: PASS reviewed source SHA256="+hashlib.sha256(new_asset).hexdigest()[:16])
    print("AUDIT_NO_WRITE_NO_RETRIES_NO_TORRENT_NO_FLUD")
    return 0

if __name__=="__main__":
    try: sys.exit(main())
    except Stop as e:
        print("STAGED_AUDIT_STOP: "+str(e))
        sys.exit(1)
    except (OSError,ValueError,TypeError,KeyError,urllib.error.HTTPError):
        print("STAGED_AUDIT_STOP: SANITIZED_METADATA_OR_NETWORK_ERROR")
        sys.exit(1)
