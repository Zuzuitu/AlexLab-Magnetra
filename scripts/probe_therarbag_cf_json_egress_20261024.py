#!/usr/bin/env python3
"""Check the staged Cloudflare Worker's own original TheRarBg JSON egress.
No hash, magnet, source HTML, JSON, URL or user credential printed; no deploy.
"""
from __future__ import annotations
import json
import re
import sys
import urllib.request
import urllib.error
DETAIL="https://therarbg.com/post-detail/95bf8b/2026-10-20-cyberpunk-edgerunners-2-original-series-soundtrack-flac-44-1khz-24bit/"
VERSION=re.compile(r"^[a-f0-9]{8}-(?:[a-f0-9]{4}-){3}[a-f0-9]{12}$")
def main():
    if len(sys.argv)!=2 or not VERSION.fullmatch(sys.argv[1]):return 2
    request=urllib.request.Request("https://index.alexlab.media/api/resolve",
      data=json.dumps({"provider":"therarbag","details":DETAIL},separators=(",",":")).encode("utf-8"),
      headers={
       "content-type":"application/json",
       "accept":"application/json",
       "origin":"https://index.alexlab.media",
       "x-magnetra-source-json-diagnostic":"20261024-readonly-original",
       "Cloudflare-Workers-Version-Overrides":'alexlab-magnetra="'+sys.argv[1]+'"'
      },method="POST")
    try:
       with urllib.request.urlopen(request,timeout=20) as res:
           status=res.status
           raw=res.read(16000)
    except urllib.error.HTTPError as e:
       status=e.code
       raw=e.read(16000)
    except (urllib.error.URLError,TimeoutError,OSError):
       print("CF_JSON_EGRESS: NETWORK_UNVERIFIED")
       return 2
    try:
       data=json.loads(raw)
       if not isinstance(data,dict):raise ValueError()
    except (ValueError,UnicodeError):
       print("CF_JSON_EGRESS: NON_JSON_OR_EDGE_BLOCKED")
       return 2
    marker=data.get("probe")=="THERARBAG_CLOUDFLARE_SOURCE_JSON_V1"
    valid=data.get("originalSourceJsonValid") is True
    print("CF_OVERRIDE_PROBE_MARKER:", "VERIFIED" if marker else "NOT_VERIFIED")
    print("ORIGINAL_SOURCE_JSON_FROM_WORKER:", "VALID" if valid else "UNAVAILABLE")
    print("CF_PROBE_HTTP:",status if status in (200,502) else "OTHER")
    print("NO_TRAFFIC_PROMOTION_OR_USER_MAGNET:",True)
    return 0 if marker else 2
if __name__=="__main__":sys.exit(main())
