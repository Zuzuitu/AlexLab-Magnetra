#!/usr/bin/env python3
"""No-write differential of immutable 0Magnet candidate in Cloudflare zero slot."""
import hashlib,json,os,sys,urllib.request,urllib.error
from deploy_magnetra_auto_pause_once import ROOT,Stop,NoRedirect,snapshot,stable
from deploy_magnetra_zero_percent import _get_api
from inspect_companion_binding_readonly import account_list,verify_account_scripts,validated_source
from stage_therarbag_iphone_20261024 import verify_binding_payload

ACTIVE="916d0671-b9c5-432d-8724-aed27bc22c4f"
NEW="763defbe-38aa-4299-acf1-1639a59e7be6"
EXPECTED={ACTIVE:100,NEW:0}
ACTION="OWNER_READONLY_0MAGNET_ZERO_SLOT_20261024"
ROOT_URL="https://index.alexlab.media"
LIMIT=1100000

def fetch(path,version):
    if path not in ("/app.js","/api/health","/api/providers") or version not in (ACTIVE,NEW,None):
        raise Stop("FIXED_ROUTE_GUARD")
    headers={"Cache-Control":"no-store","Accept-Encoding":"identity","User-Agent":"MagnetraOwnerZeroSlotAudit/1.0"}
    if version:
        headers["Cloudflare-Workers-Version-Overrides"]='alexlab-magnetra="'+version+'"'
    req=urllib.request.Request(ROOT_URL+path,headers=headers,method="GET")
    try:
        with urllib.request.build_opener(NoRedirect()).open(req,timeout=20) as res:
            return res.status,res.headers.get("content-type","").lower(),res.read(LIMIT+1)
    except urllib.error.HTTPError as err:
        return err.code,err.headers.get("content-type","").lower(),b""
    except (urllib.error.URLError,OSError,TimeoutError):
        return 0,"",b""

def asset_state(status,mime,body,expected):
    if status!=200:return "HTTP_"+str(status) if status in (0,301,302,403,404,429,500,502,503,504) else "HTTP_OTHER"
    if "javascript" not in mime:return "MIME_MISMATCH"
    if not body or len(body)>LIMIT:return "SIZE_MISMATCH"
    return "SHA_MATCH" if hashlib.sha256(body).digest()==hashlib.sha256(expected).digest() else "SHA_MISMATCH"

def api_state(status,mime,body,path):
    if status!=200:return "HTTP_"+str(status) if status in (0,301,302,403,404,429,500,502,503,504) else "HTTP_OTHER"
    if "application/json" not in mime:return "MIME_MISMATCH"
    if not body or len(body)>LIMIT:return "SIZE_MISMATCH"
    try:x=json.loads(body)
    except (ValueError,UnicodeError):return "INVALID_JSON"
    if not isinstance(x,dict):return "INVALID_SCHEMA"
    if path=="/api/health":
        return "HEALTH_46_PASS" if x.get("ok") is True and (x.get("total"),x.get("ported"))==(46,46) else "HEALTH_MISMATCH"
    items=x.get("providers")
    if not isinstance(items,list) or len(items)!=46:return "CATALOG_46_MISMATCH"
    ids=[i.get("id") for i in items if isinstance(i,dict)]
    return "CATALOG_46_PASS" if len(ids)==len(set(ids))==46 and "0magnet" in ids and "therarbag" in ids else "CATALOG_IDENTITIES_MISMATCH"

def run():
    if os.environ.get("MAGNETRA_0MAGNET_ZERO_READONLY")!=ACTION:raise Stop("NOT_AUTHORIZED")
    validated_source()
    verify_account_scripts(account_list())
    dep,shares=snapshot()
    if shares!=EXPECTED:raise Stop("LIVE_SPLIT_CHANGED")
    for v in (ACTIVE,NEW):
        verify_binding_payload(v,_get_api("/versions/"+v))
    stable(dep,EXPECTED)
    print("IMMUTABLE_ZERO_SLOT_SPLIT_916D100_NEW0: PASS",flush=True)
    print("CLOUDFLARE_FOUR_BINDINGS_ACCOUNT: PASS",flush=True)
    reviewed=(ROOT/"web/app.js").read_bytes()
    for label,v in (("OLD",ACTIVE),("NEW",NEW),("PUBLIC",None)):
        code,mime,body=fetch("/app.js",v)
        print("APP_JS_"+label+": "+asset_state(code,mime,body,reviewed),flush=True)
        stable(dep,EXPECTED)
    for label,path in (("HEALTH","/api/health"),("CATALOG","/api/providers")):
        code,mime,body=fetch(path,NEW)
        print("CANDIDATE_"+label+": "+api_state(code,mime,body,path),flush=True)
        stable(dep,EXPECTED)
    print("READONLY_DONE_NO_WRITES_NO_TORRENT_NO_SECRETS",flush=True)
    return 0

def main():
    if sys.argv[1:]!=["--approved-readonly"] or os.environ.get("MAGNETRA_0MAGNET_ZERO_READONLY")!=ACTION:
        print("STOP_NOT_APPROVED_NO_OUTBOUND",flush=True);return 2
    try:return run()
    except Exception:
        print("STOP_UNVERIFIED_SAFE_NO_WRITES",flush=True);return 1

if __name__=="__main__":raise SystemExit(main())
