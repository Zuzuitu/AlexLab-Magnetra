#!/usr/bin/env python3
"""One read-only exact Cloudflare V3 original JSON schema classification.
No HTML, hashes, torrent links or sensitive source data may be printed.
"""
import json
import re
import sys
import urllib.request
import urllib.error

DETAIL="https://therarbg.com/post-detail/95bf8b/2026-10-20-cyberpunk-edgerunners-2-original-series-soundtrack-flac-44-1khz-24bit/"
UUID=re.compile(r"^[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}$")
ENUM=frozenset({
"FETCH_TIMEOUT","FETCH_NETWORK","HTTP_REDIRECT",
"SOURCE_HTTP_401","SOURCE_HTTP_403","SOURCE_HTTP_404","SOURCE_HTTP_429",
"SOURCE_HTTP_500","SOURCE_HTTP_502","SOURCE_HTTP_503","SOURCE_HTTP_504",
"SOURCE_HTTP_OTHER","SOURCE_CHALLENGE","HTML_NOT_JSON","UNEXPECTED_CONTENT_TYPE",
"OVERSIZE","BODY_READ_FAILED","INVALID_JSON","JSON_ROOT_PRIMITIVE",
"JSON_ROOT_ARRAY","JSON_ERROR_ENVELOPE","JSON_HASH_CONFLICT",
"JSON_ROOT_BTIH_VALID","JSON_WRAPPED_BTIH_VALID","JSON_ROOT_BTIH_INVALID",
"JSON_WRAPPED_BTIH_INVALID","JSON_RESULTS_RESPONSE","JSON_OBJECT_NO_INFO_HASH"
})
def main():
 if len(sys.argv)!=2 or not UUID.fullmatch(sys.argv[1]):
  print("DIAGNOSTIC_STOP: INVALID_CANDIDATE_ID")
  return 2
 req=urllib.request.Request("https://index.alexlab.media/api/resolve",
  method="POST",
  data=json.dumps({"provider":"therarbag","details":DETAIL}).encode("utf-8"),
  headers={
   "User-Agent":"Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36",
   "Accept-Language":"en-US,en;q=0.9",
   "Accept":"application/json","Content-Type":"application/json",
   "Origin":"https://index.alexlab.media",
   "x-magnetra-source-json-diagnostic":"20261024-source-stage-v3",
   "Cloudflare-Workers-Version-Overrides":'alexlab-magnetra="'+sys.argv[1]+'"'
  })
 try:
  with urllib.request.urlopen(req,timeout=20) as response:
   status=response.status
   raw=response.read(8193)
 except urllib.error.HTTPError as e:
  status=e.code
  raw=e.read(8193)
 except (urllib.error.URLError,TimeoutError,OSError):
  print("DIAGNOSTIC_STOP: TRANSPORT_UNAVAILABLE")
  return 2
 if len(raw)>8192:
  print("DIAGNOSTIC_STOP: RESPONSE_TOO_LARGE")
  return 2
 try:
  body=json.loads(raw)
 except (ValueError,UnicodeDecodeError):
  print("DIAGNOSTIC_STOP: NON_JSON_EDGE_RESPONSE")
  return 2
 if not isinstance(body,dict) or body.get("probe")!="THERARBAG_SOURCE_JSON_STAGE_V3":
  # Finite classification only. Never show body, error, hash, URL or headers.
  print("DIAGNOSTIC_STOP: VERSION_ATTRIBUTION_NOT_PROVEN")
  print("EDGE_HTTP:",status if status in (200,400,401,403,404,429,500,502,503,530) else "OTHER")
  print("RESPONSE_SHAPE:",
    "WORKER_JSON_OTHER" if isinstance(body,dict) and status in (200,400,502)
    else "OTHER_JSON_RESPONSE")
  return 2
 stage=body.get("stage")
 if stage not in ENUM:
  print("DIAGNOSTIC_STOP: UNKNOWN_SOURCE_STAGE")
  return 2
 print("IMMUTABLE_V3_PROBE: VERIFIED")
 print("SOURCE_JSON_SCHEMA:",stage)
 print("HTTP:",status)
 print("TRAFFIC_0_PERCENT_UNCHANGED: VERIFY_WITH_API")
 return 0
if __name__=="__main__":
 raise SystemExit(main())
