#!/usr/bin/env python3
"""Read-only, fixed-origin HTTP classification of Cloudflare 403.
Every POST intentionally has a non-allowlisted detail URL so that reaching
the Worker returns a harmless 400 *before* any provider/network fetch.
No retries, log of IP, body, headers, secrets, hashes, or magnets.
"""
from __future__ import annotations
import json
import urllib.request
import urllib.error

BASE="https://index.alexlab.media"
VERSION="8d3f9813-e30f-417b-b9a7-a1247f994e9d"
OWNER_ORIGIN=BASE
BODY=json.dumps({"provider":"therarbag","details":"https://invalid.example.invalid/not-allowlisted"},
                separators=(",",":")).encode("utf-8")
UA_BROWSER=("Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36")
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args):return None

def classify(body,ctype,status,expect_health):
    if len(body)>12000:return "OVERSIZED_NON_DIAGNOSTIC"
    if "application/json" not in ctype.lower():
        return ("EDGE_OR_PROXY_NON_JSON_403" if status==403
                else "NON_JSON_RESPONSE")
    try:
        obj=json.loads(body)
    except (ValueError,UnicodeDecodeError):
        return "INVALID_JSON_RESPONSE"
    if not isinstance(obj,dict):return "NONOBJECT_JSON"
    if expect_health and status==200 and obj.get("ok") is True and obj.get("ported")==46:
        return "WORKER_HEALTH_CONFIRMED"
    if not expect_health and status==400 and obj.get("error")=="Details URL is not in the provider allowlist.":
        return "WORKER_RESOLVE_ROUTE_CONFIRMED_NO_UPSTREAM"
    if not expect_health and status==403 and obj.get("error")=="Cross-origin submission not permitted.":
        return "WORKER_ORIGIN_403"
    if status==403:return "JSON_403_OTHER"
    return "UNEXPECTED_JSON_RESPONSE"

def probe(label,method,path,*,browser,override):
    hdr={"Accept":"application/json","Cache-Control":"no-store",
         "User-Agent": UA_BROWSER if browser else "Python-urllib/3.13"}
    if method=="POST":
        hdr["Content-Type"]="application/json"
        hdr["Origin"]=OWNER_ORIGIN
    if override:
        hdr["Cloudflare-Workers-Version-Overrides"]='alexlab-magnetra="'+VERSION+'"'
    req=urllib.request.Request(BASE+path,data=BODY if method=="POST" else None,
                               headers=hdr,method=method)
    status=0
    try:
        with urllib.request.build_opener(NoRedirect()).open(req,timeout=12) as r:
            status=r.status
            ctype=r.headers.get("Content-Type","")
            mitigated=r.headers.get("cf-mitigated","").lower()=="challenge"
            body=r.read(12001)
    except urllib.error.HTTPError as e:
        status=e.code
        ctype=e.headers.get("Content-Type","")
        mitigated=e.headers.get("cf-mitigated","").lower()=="challenge"
        body=e.read(12001)
    except (urllib.error.URLError,TimeoutError,OSError):
        print(label+": NETWORK_UNAVAILABLE")
        return
    kind=classify(body,ctype,status,method=="GET")
    print(f"{label}: HTTP_{status} {kind}"+
          (" CF_CHALLENGE" if mitigated else ""))

def main():
    print("TEST_MODE: ZERO_PROVIDER_REQUESTS_NO_USER_MAGNET")
    probe("HEALTH_PYTHON", "GET","/api/health",browser=False,override=False)
    probe("HEALTH_BROWSER", "GET","/api/health",browser=True,override=False)
    probe("HEALTH_BROWSER_OVERRIDE","GET","/api/health",browser=True,override=True)
    probe("RESOLVE_INVALID_BROWSER","POST","/api/resolve",browser=True,override=False)
    probe("RESOLVE_INVALID_BROWSER_OVERRIDE","POST","/api/resolve",browser=True,override=True)
    probe("RESOLVE_INVALID_PYTHON_OVERRIDE","POST","/api/resolve",browser=False,override=True)

if __name__=="__main__":main()
