#!/usr/bin/env python3
"""One-shot read-only public EZTV query semantics check, no source retries.

Never print names, links, hashes, magnets, HTTP bodies, gateway tokens or user data.
GETs only public Magnetra API, uses real deployed Worker routing without overrides.
"""
from __future__ import annotations
import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

BASE="https://index.alexlab.media/api/search"
MAX_BYTES=1_000_000
QUERIES=(("GENERIC_YEAR_2026","2026"),("EXACT_SERIES_IMDB_SAMPLE","tt0413573"))

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def probe(label,query):
    url=BASE+"?"+urlencode({"q":query,"providers":"eztvx","category":"series"})
    req=Request(url,method="GET",headers={
        "User-Agent":"AlexLab-EZTV-OneShot-Readonly/1.0",
        "Accept":"application/json","Cache-Control":"no-store",
        "Accept-Encoding":"identity",
    })
    try:
        with build_opener(NoRedirect()).open(req,timeout=35) as res:
            if res.status!=200 or "application/json" not in res.headers.get("content-type",""):
                print(label+": HTTP_OR_MIME_UNVERIFIED")
                return
            raw=res.read(MAX_BYTES+1)
    except HTTPError as err:
        print(label+": HTTP_"+str(err.code))
        return
    except (URLError,TimeoutError,OSError):
        print(label+": TRANSPORT_UNVERIFIED")
        return
    if not raw or len(raw)>MAX_BYTES:
        print(label+": SIZE_UNVERIFIED")
        return
    try:
        obj=json.loads(raw)
    except (ValueError,UnicodeError):
        print(label+": NON_JSON")
        return
    if not isinstance(obj,dict):
        print(label+": BAD_JSON_SHAPE")
        return
    items=obj.get("results")
    errors=obj.get("errors")
    stats=obj.get("stats")
    if not isinstance(items,list) or not isinstance(errors,list) or not isinstance(stats,list):
        print(label+": BAD_RESULT_SHAPE")
        return
    if any(not isinstance(x,dict) or x.get("provider")!="eztvx" for x in items):
        print(label+": SOURCE_PROVENANCE_ERROR")
        return
    safe_codes=[]
    for err in errors:
        c=err.get("code") if isinstance(err,dict) else None
        if isinstance(c,str) and re.fullmatch(r"[A-Z_]{2,48}",c):
            safe_codes.append(c)
        else:
            safe_codes.append("UNRECOGNIZED")
    summaries=[(bool(s.get("ok")),s.get("count")) for s in stats
               if isinstance(s,dict) and s.get("provider")=="eztvx"]
    print(label+": RESULT_COUNT="+str(len(items))+
          " ERROR_COUNT="+str(len(errors))+" ERROR_CODES="+",".join(safe_codes)+
          " STATS="+str(summaries[:1]))

def main():
    for label,query in QUERIES:
        probe(label,query)
    print("EZTV_READONLY_DIAG_COMPLETE: two single GETs, no retries or mutations")

if __name__=="__main__":
    main()
