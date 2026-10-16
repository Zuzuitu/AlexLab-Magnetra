#!/usr/bin/env python3
"""Explicit read-only local 8798 source HTML acceptance; never prints tokens/data.

Four authenticated *loopback* 8798 GETs at most, inducing at most four
bounded, fixed-origin HTTPS source GETs through the authenticated dispatcher.
No secrets, titles, full URLs, magnets, hashes, HTML or .torrent bytes logged.
"""
from __future__ import annotations

import http.client
import importlib.util
import json
import os
import pathlib
import re
from urllib.parse import urlencode, urlsplit

ROOT=pathlib.Path(__file__).resolve().parent
DIAGNOSTIC=ROOT / "probe-result-details.py"
TOKEN_FILE=pathlib.Path("/etc/magnetra-gateway/gateway.env")
IM=importlib.util
module_spec=IM.spec_from_file_location("magnetra_fixed_details_check",DIAGNOSTIC)
probe=IM.module_from_spec(module_spec)
import sys
sys.modules[module_spec.name]=probe
module_spec.loader.exec_module(probe)
MAX_BYTES=256_000
SECRET=re.compile(r"MAGNETRA_GATEWAY_TOKEN=([A-Za-z0-9_-]{48,256})\n")


def private_token():
    st=TOKEN_FILE.lstat()
    if st.st_uid != 0 or st.st_mode & 0o077 or not TOKEN_FILE.is_file():
        raise ValueError("secure hub credentials unavailable")
    fd=os.open(TOKEN_FILE,os.O_RDONLY|os.O_NOFOLLOW)
    try:
        text=os.read(fd,401).decode("ascii")
    finally:
        os.close(fd)
    m=SECRET.fullmatch(text)
    if not m:
        raise ValueError("invalid hub credential format")
    return m.group(1)


def local_html(path,token,connector=http.client.HTTPConnection):
    conn=connector("127.0.0.1",8798,timeout=12)
    try:
        conn.request("GET",path,headers={
            "Authorization":"Bearer "+token,"Accept":"text/html"
        })
        res=conn.getresponse()
        status=res.status
        ctype=res.getheader("content-type") or ""
        data=res.read(MAX_BYTES+1)
        if status != 200 or "text/html" not in ctype.lower() or len(data)>MAX_BYTES:
            return {"http":status,"state":"NOT_VERIFIED"},None
        return {"http":status,"state":"HTML_ACCEPTED"},data
    except (OSError,TimeoutError,http.client.HTTPException):
        return {"http":None,"state":"LOCAL_TRANSPORT_ERROR"},None
    finally:
        conn.close()


def check(source,token,connector=http.client.HTTPConnection):
    if source not in probe.SOURCES:
        raise ValueError("Source not in fixed allowlist")
    search_path="/v1/"+source.provider+"/html?"+urlencode({"mode":"search","q":"ubuntu"})
    status,body=local_html(search_path,token,connector)
    outcome={"provider":source.provider,"search":status,"query_matches":0,
             "details_checked":False,"details":None,"valid_magnet_anchor":False}
    if body is None:
        return outcome
    parser=probe.SearchRows()
    parser.feed(body.decode("utf-8",errors="replace"));parser.close()
    candidate=None
    for row in parser.rows:
        if row["cols"]<source.columns:
            continue
        for link in row["links"]:
            if "ubuntu" not in link["name"].casefold():
                continue
            target=probe.safe_detail(source,link["href"])
            if target:
                outcome["query_matches"]+=1
                if candidate is None:
                    candidate=urlsplit(target).path
            break
    if candidate is None:
        status["state"]="NO_SOURCE_ROW_MATCH"
        return outcome
    if not probe.safe_detail(source,candidate):
        return outcome
    detail_path="/v1/"+source.provider+"/html?"+urlencode({"mode":"detail","path":candidate})
    details,page=local_html(detail_path,token,connector)
    outcome["details_checked"]=True
    outcome["details"]=details
    if page is None:
        return outcome
    p=probe.MagnetAnchors(source.magnet_parent)
    p.feed(page.decode("utf-8",errors="replace"));p.close()
    outcome["valid_magnet_anchor"]=p.count>0
    details["state"]="FORMAT_VERIFIED" if p.count else "NO_VALID_MAGNET"
    return outcome


def main():
    try:
        token=private_token()
    except (OSError,ValueError,UnicodeError):
        print(json.dumps({"result":"STOP","reason":"SECURE_CREDENTIAL_UNAVAILABLE"}))
        return 1
    print(json.dumps({"check":"two_source_html_loopback","max_local_requests":4,
                      "source_urls_never_printed":True,"no_files_written":True}))
    results=[]
    for source in probe.SOURCES:
        result=check(source,token)
        print(json.dumps(result,separators=(",",":")))
        results.append(result)
    passed=all(x["search"].get("http")==200 and x["query_matches"]>=1
               and x["details"] and x["details"].get("http")==200
               and x["valid_magnet_anchor"] for x in results)
    print(json.dumps({"result":"PASS" if passed else "FAIL","checked_sources":2}))
    return 0 if passed else 1


if __name__=="__main__":
    raise SystemExit(main())
