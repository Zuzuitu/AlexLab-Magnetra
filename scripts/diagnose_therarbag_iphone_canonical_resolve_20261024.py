#!/usr/bin/env python3
"""One GET exact owner card and one bounded POST canonical original detail.
Never print source title, URL, hashes, magnet, body, or credentials.
"""
import re,sys
from diagnose_therarbag_iphone_exact_size_20261024 import PUBLIC_URL,SEARCH,exact_title_and_size
from diagnose_therarbag_iphone_linkshape_20261024 import api_search,fingerprint,Stop
from release_therarbag_iphone_diagnostic_20261024 import http
SAFE=re.compile(r"^[A-Z0-9_]{3,40}$")
def verify_source(payload):
    rows=payload.get("results")
    if not isinstance(rows,list) or len(rows)>250:raise Stop("BAD_SEARCH_RESULT_SCHEMA")
    selected=[x for x in rows if exact_title_and_size(x)]
    if len(selected)!=1 or selected[0].get("details")!=PUBLIC_URL:raise Stop("EXACT_OWNER_CARD_NOT_VERIFIED")
    alternate=selected[0].get("magnetSource")
    label=("ABSENT" if alternate in (None,"") else "SAME" if alternate==PUBLIC_URL
           else "DIFFERENT" if isinstance(alternate,str) and len(alternate)<=1500 else "INVALID")
    print("OWNER_SEARCH_352MB_CANONICAL_DETAILS: PASS",flush=True)
    print("OWNER_SEARCH_MAGNETSOURCE:",label,flush=True)
    if isinstance(alternate,str) and alternate:
        print("MAGNETSOURCE_EQUALS_PREVIOUS_IPHONE_TRACE:",fingerprint(alternate)=="b12d9fd36aa0",flush=True)

def verify_resolver(fn=http):
    status,body=fn("/api/resolve",body={"provider":"therarbag","details":PUBLIC_URL},diagnostic=True)
    diag=body.get("diagnostic")
    if status not in (200,502) or not isinstance(diag,dict) or diag.get("build")!="THERARBAG_IPHONE_DIAG_V1" or diag.get("detailFingerprint")!=fingerprint(PUBLIC_URL):
        raise Stop("CANONICAL_PROBE_NOT_VERIFIED")
    a,b=diag.get("htmlStage"),diag.get("jsonStage")
    if not isinstance(a,str) or not SAFE.fullmatch(a) or not isinstance(b,str) or not SAFE.fullmatch(b):
        raise Stop("INVALID_DIAGNOSTIC_ENUM")
    code=body.get("code")
    if status==502 and (not isinstance(code,str) or not SAFE.fullmatch(code)):
        raise Stop("UNSAFE_ERROR_CLASS")
    if status==200 and not re.match(r"^magnet:\?xt=urn:btih:(?:[0-9a-f]{40}|[a-z2-7]{32})(?:&|$)",str(body.get("magnet","")),re.I):
        raise Stop("MAGNET_SHAPE_INVALID")
    print("DIRECT_CANONICAL_PROBE_CLASS:","VALID_MAGNET" if status==200 else "SOURCE_ERROR",flush=True)
    print("DIRECT_CANONICAL_HTML_STAGE:",a,flush=True)
    print("DIRECT_CANONICAL_JSON_STAGE:",b,flush=True)
    if code:print("DIRECT_CANONICAL_ERROR_CODE:",code,flush=True)
    print("NO_REAL_MAGNET_HASH_URL_TITLE_LOGGED: PASS",flush=True)

def main():
    if sys.argv[1:]!=["--approved-readonly"]:
        print("MANUAL_APPROVAL_REQUIRED");return 2
    try:
        verify_source(api_search(SEARCH))
        verify_resolver()
    except Stop as e:
        print("OWNER_CANONICAL_AUDIT_STOP:",str(e));return 1
    return 0
if __name__=="__main__":raise SystemExit(main())
