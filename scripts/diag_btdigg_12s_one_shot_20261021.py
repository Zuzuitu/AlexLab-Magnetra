#!/usr/bin/env python3
"""One and only one benign BTDigg query; no gateway changes or retries."""
import json
import sys
import time
import urllib.request
import urllib.error
from deploy_magnetra_relevance_136c_slot import snapshot
OLD="136c1425-0070-48db-b995-5708bd35bb75"
NEW="c86c9a32-31fd-4952-86ed-b35f1763b342"
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):return None
def run():
 dep,shares=snapshot()
 print("CLOUDFLARE_SHARES: c86c="+str(shares.get(NEW))+" 136c="+str(shares.get(OLD)))
 if shares!={NEW:100,OLD:0}:
  print("STOP_NOT_VERIFIED_PRODUCTION_SLOT");return 2
 url="https://index.alexlab.media/api/search?q=ubuntu&providers=btdigg&category=all"
 req=urllib.request.Request(url,headers={"accept":"application/json","cache-control":"no-store",
 "user-agent":"MagnetraOneShotBTDiggOriginTimeoutDiagnostic/1.0"},method="GET")
 started=time.monotonic()
 try:
  with urllib.request.build_opener(NoRedirect()).open(req,timeout=23) as rsp:
   code=rsp.status
   body=rsp.read(250001)
 except urllib.error.HTTPError as e:
  code=e.code;body=b""
 except (urllib.error.URLError,OSError,TimeoutError):
  print("BTDIGG_PUBLIC_TRANSPORT_ERROR: elapsed_ms="+str(round((time.monotonic()-started)*1000)))
  print("NO_SOURCE_RETRY");return 1
 elapsed=round((time.monotonic()-started)*1000)
 print("PUBLIC_HTTP="+str(code)+" elapsed_ms="+str(elapsed))
 if code!=200 or not body or len(body)>250000:
  print("BTDIGG_HTTP_OR_BODY_INVALID; NO_RETRY");return 1
 try:obj=json.loads(body)
 except (ValueError,UnicodeError):
  print("BTDIGG_INVALID_JSON; NO_RETRY");return 1
 if not isinstance(obj,dict):
  print("BTDIGG_SCHEMA_INVALID");return 1
 rows,stats,errs=obj.get("results"),obj.get("stats"),obj.get("errors")
 if not all(isinstance(v,list) for v in (rows,stats,errs)):
  print("BTDIGG_SCHEMA_INVALID");return 1
 safe={"RATE_LIMIT","TIMEOUT","BTDIGG_SOURCE_TIMEOUT","BTDIGG_TUNNEL_TIMEOUT",
       "BTDIGG_TUNNEL_ERROR","BTDIGG_TUNNEL_1042","UPSTREAM_ERROR","ACCESS_DENIED"}
 for e in errs:
  if not isinstance(e,dict) or e.get("provider")!="btdigg":
   print("BTDIGG_UNATTRIBUTED_FAILURE");return 1
  code=e.get("code")
  print("BTDIGG_ERROR_CODE="+str(code if code in safe else "OTHER_OR_UNKNOWN"))
 print("BTDIGG_STATS="+json.dumps([
  {"provider":s.get("provider"),"ok":s.get("ok"),
   "matched":s.get("count"),"raw":s.get("rawCount")}
  for s in stats if isinstance(s,dict)],separators=(",",":")))
 valid=(len(rows)>0 and all(isinstance(r,dict) and r.get("provider")=="btdigg"
  and isinstance(r.get("magnet"),str) and r["magnet"].startswith("magnet:?xt=urn:btih:")
  for r in rows))
 print("BTDIGG_POSITIVE_ORIGINAL_ROWS="+str(len(rows))+
       " valid_magnets="+str(valid)+" source_errors="+str(len(errs)))
 print("READONLY_ONE_REQUEST_NO_RETRY_NO_DOWNLOAD")
 return 0 if valid and not errs else 1
if __name__=="__main__":
 try:sys.exit(run())
 except Exception:
  print("STOP_UNEXPECTED_DIAGNOSTIC_EXCEPTION (no payload logged)");sys.exit(2)
