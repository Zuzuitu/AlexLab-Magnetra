#!/usr/bin/env python3
"""Read-only Cloudflare Worker original JSON stage fingerprint, no hash/magnet."""
import json
import re
import sys
import urllib.request
import urllib.error

DETAIL="https://therarbg.com/post-detail/95bf8b/2026-10-20-cyberpunk-edgerunners-2-original-series-soundtrack-flac-44-1khz-24bit/"
UUID=re.compile(r"^[a-f0-9]{8}-(?:[a-f0-9]{4}-){3}[a-f0-9]{12}$")
STAGES={
 "FETCH_TIMEOUT","FETCH_NETWORK","HTTP_REDIRECT","SOURCE_HTTP_401","SOURCE_HTTP_403",
 "SOURCE_HTTP_404","SOURCE_HTTP_429","SOURCE_HTTP_500","SOURCE_HTTP_502",
 "SOURCE_HTTP_503","SOURCE_HTTP_504","SOURCE_HTTP_OTHER","SOURCE_CHALLENGE",
 "HTML_NOT_JSON","UNEXPECTED_CONTENT_TYPE","OVERSIZE","BODY_READ_FAILED",
 "INVALID_JSON","MISSING_DATA_OBJECT","MISSING_OR_INVALID_INFO_HASH","SOURCE_JSON_VALID"
}
def main():
 if len(sys.argv)!=2 or not UUID.fullmatch(sys.argv[1]):
  print("TEST_STOP: NO_STAGED_CANDIDATE")
  return 2
 req=urllib.request.Request("https://index.alexlab.media/api/resolve",
  data=json.dumps({"provider":"therarbag","details":DETAIL},separators=(",",":")).encode(),
  headers={
   "User-Agent":"Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36",
   "Accept-Language":"en-US,en;q=0.9",
   "Content-Type":"application/json","Accept":"application/json",
   "Origin":"https://index.alexlab.media",
   "x-magnetra-source-json-diagnostic":"20261024-source-stage-v2",
   "Cloudflare-Workers-Version-Overrides":'alexlab-magnetra="'+sys.argv[1]+'"'
  },method="POST")
 try:
  with urllib.request.urlopen(req,timeout=22) as response:
   status=response.status
   raw=response.read(6000)
 except urllib.error.HTTPError as e:
  status=e.code
  raw=e.read(6000)
 except (urllib.error.URLError,TimeoutError,OSError):
  print("EDGE_TRANSPORT: UNVERIFIED")
  return 2
 try:
  obj=json.loads(raw)
  if not isinstance(obj,dict):raise ValueError()
 except (ValueError,UnicodeDecodeError):
  print("EDGE_RESPONSE: NON_JSON_OR_BLOCKED")
  print("EDGE_HTTP:",status if status in (200,400,403,502) else "OTHER")
  return 2
 marker=obj.get("probe")=="THERARBAG_SOURCE_JSON_STAGE_V2"
 stage=obj.get("stage") if obj.get("stage") in STAGES else "UNCLASSIFIED"
 print("STAGED_WORKER_MARKER:", "VERIFIED" if marker else "NOT_VERIFIED")
 print("ORIGINAL_JSON_SOURCE_STAGE:", stage if marker else "NO_WORKER_EVIDENCE")
 print("EDGE_HTTP:", status if status in (200,400,403,502) else "OTHER")
 print("NO_MAGNET_NO_SOURCE_CONTENT_NO_PROMOTION:",True)
 return 0 if marker else 2
if __name__=="__main__":sys.exit(main())
