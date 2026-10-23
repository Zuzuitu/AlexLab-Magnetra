#!/usr/bin/env python3
"""Read-only staged-version override probe; does NOT activate candidate traffic.
One source-owned JSON read, baseline Resolve and candidate Resolve.
Only finite status/boolean emitted: no hash, magnet, HTML, token or title.
"""
import json
import re
import sys
import urllib.request
import urllib.error

ACTIVE="36019925-2308-4f99-8223-13854012d372"
TARGET="https://index.alexlab.media/api/resolve"
DETAIL="https://therarbg.com/post-detail/95bf8b/2026-10-20-cyberpunk-edgerunners-2-original-series-soundtrack-flac-44-1khz-24bit/"
HASH=re.compile(r"^[0-9a-f]{40}$")
UUID=re.compile(r"^[a-f0-9]{8}-(?:[a-f0-9]{4}-){3}[a-f0-9]{12}$")
HEADERS={"user-agent":"Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36","accept":"application/json"}
SAFE_ERRORS={"DETAIL_NO_BTIH","SOURCE_HTTP_403","SOURCE_HTTP_404","SOURCE_HTTP_429","SOURCE_HTTP_500","SOURCE_HTTP_502","SOURCE_HTTP_503","SOURCE_HTTP_504","SOURCE_HTTP_OTHER","SOURCE_TIMEOUT","SOURCE_REDIRECT","SOURCE_CHALLENGE","SOURCE_NETWORK","RESOLVE_UNKNOWN","WORKER_RUNTIME"}

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args):return None
OPENER=urllib.request.build_opener(NoRedirect())

def read(req,max_bytes=300000):
    try:
        with OPENER.open(req,timeout=16) as r:
            return r.status,r.read(max_bytes+1)
    except urllib.error.HTTPError as e:
        return e.code,e.read(max_bytes+1)
    except (urllib.error.URLError,TimeoutError,OSError):
        return 0,b""

def source_hash():
    url=DETAIL+"?format=json"
    req=urllib.request.Request(url,headers=HEADERS)
    status,payload=read(req)
    if status!=200 or len(payload)>300000:return None
    try:
        doc=json.loads(payload)
        h=doc["data"]["info_hash"]
        return h.lower() if isinstance(h,str) and HASH.fullmatch(h.lower()) else None
    except (ValueError,KeyError,TypeError):return None

def resolve(version):
    header=dict(HEADERS)
    header.update({
       "content-type":"application/json",
       "origin":"https://index.alexlab.media",
       "Cloudflare-Workers-Version-Overrides":'alexlab-magnetra="'+version+'"'
    })
    request=urllib.request.Request(TARGET,
       data=json.dumps({"provider":"therarbag","details":DETAIL},separators=(",",":")).encode(),
       headers=header,method="POST")
    code,payload=read(request)
    if len(payload)>300000:return "TOO_LARGE",None,None
    try:
        d=json.loads(payload)
        if not isinstance(d,dict):raise ValueError("not object")
    except (ValueError,UnicodeError):
        return "EDGE_BLOCKED" if code==403 else "NON_JSON",None,None
    magnet=d.get("magnet")
    valid=bool(isinstance(magnet,str) and re.fullmatch(
       r"magnet:\?xt=urn:btih:([a-f0-9]{40})(?:&.*)?",magnet,re.I))
    hashpart=magnet[20:60].lower() if valid else None
    error=d.get("code")
    return ("OK" if code==200 and valid else
       error if isinstance(error,str) and error in SAFE_ERRORS else
       "EDGE_BLOCKED" if code==403 else "UNCLASSIFIED"),hashpart,code

def main():
    if len(sys.argv)!=2 or not UUID.fullmatch(sys.argv[1]) or sys.argv[1]==ACTIVE:
        print("OVERRIDE_STOP: CANDIDATE_ID_INVALID")
        return 2
    expected=source_hash()
    if expected is None:
        print("SOURCE_JSON_REFERENCE: UNVERIFIED")
        return 2
    print("SOURCE_JSON_REFERENCE: VERIFIED")
    base,base_hash,base_http=resolve(ACTIVE)
    candidate,candidate_hash,candidate_http=resolve(sys.argv[1])
    print("BASELINE_RESOLVE_STAGE:",base)
    print("CANDIDATE_RESOLVE_STAGE:",candidate)
    print("CANDIDATE_BTih_VALID_AND_MATCHES_SOURCE:",candidate=="OK" and candidate_hash==expected)
    if candidate=="EDGE_BLOCKED" or base=="EDGE_BLOCKED":
        print("OVERRIDE_RESULT: GITHUB_PUBLIC_EDGE_BLOCKED; NO_RELEASE_APPROVAL")
        return 0
    if candidate=="OK" and candidate_hash==expected and base!="OK":
        print("OVERRIDE_RESULT: CANDIDATE_SOURCE_RESOLVE_PASS_BASELINE_DIFFERENTIAL")
        return 0
    print("OVERRIDE_RESULT: NOT_YET_PROVEN; KEEP_CANDIDATE_AT_ZERO")
    return 0
if __name__=="__main__":sys.exit(main())
