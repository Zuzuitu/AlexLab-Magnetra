#!/usr/bin/env python3
"""Read-only post-100% production acceptance. No retry, deploy, torrent or Flud.
Compares unoverridden PUBLIC assets and original source responses to immutable
reviewed repository code after owner-triggered 136c full release.
"""
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlencode

from deploy_magnetra_relevance_136c_slot import (
    CURRENT, NEW, snapshot, verify_version
)

BASE="https://index.alexlab.media"
PROVIDERS=("knaben","torrentscsv","torrent9","oxtorrent","ytsmx")
EXPECTED={CURRENT:0,NEW:100}
LIMIT=1000000

class Stop(Exception): pass
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):return None

def get_public(path,mime):
 if not path.startswith("/") or path.startswith("//") or len(path)>440:
  raise Stop("PUBLIC_ROUTE_INVALID")
 req=urllib.request.Request(
  BASE+path,method="GET",
  headers={"Accept-Encoding":"identity","Cache-Control":"no-cache,no-store,max-age=0",
           "Pragma":"no-cache","User-Agent":"MagnetraReadonly136cFullPostflight/1.0",
           "Accept":mime})
 try:
  with urllib.request.build_opener(NoRedirect()).open(req,timeout=38) as res:
   expected_type="json" if mime=="application/json" else "javascript"
   if res.status!=200 or expected_type not in res.headers.get("content-type",""):
    raise Stop("PUBLIC_CONTENT_OR_STATUS_UNVERIFIED")
   body=res.read(LIMIT+1)
 except urllib.error.HTTPError as e:raise Stop("PUBLIC_HTTP_"+str(e.code)) from None
 except (urllib.error.URLError,OSError,TimeoutError):raise Stop("PUBLIC_TRANSPORT_UNVERIFIED") from None
 if not body or len(body)>LIMIT:raise Stop("PUBLIC_SIZE_UNVERIFIED")
 return body

def public_json(route):
 data=get_public(route,"application/json")
 try: value=json.loads(data)
 except (ValueError,UnicodeError):raise Stop("PUBLIC_INVALID_JSON") from None
 if not isinstance(value,dict):raise Stop("PUBLIC_JSON_NOT_OBJECT")
 return value

def main():
 first,shares=snapshot()
 print("CLOUDFLARE_LIVE: 540b="+str(shares.get(CURRENT))+
       " 136c="+str(shares.get(NEW))+" versions="+str(len(shares)))
 if shares!=EXPECTED:raise Stop("NOT_136C100_540B0")
 verify_version(CURRENT)
 verify_version(NEW)
 print("IMMUTABLE_VERSIONS: PASS required bindings")
 reviewed=(Path(__file__).resolve().parent.parent/"web/app.js").read_bytes()
 public=get_public("/app.js","text/javascript,application/javascript")
 if hashlib.sha256(reviewed).digest()!=hashlib.sha256(public).digest():
  raise Stop("PUBLIC_APP_JS_SHA_NOT_YET_VERIFIED")
 print("PUBLIC_APP_JS: PASS sha256prefix="+hashlib.sha256(public).hexdigest()[:16]+
       " bytes="+str(len(public)))
 catalog=public_json("/api/providers").get("providers")
 if not isinstance(catalog,list) or len(catalog)!=46 or len({
  p.get("id") for p in catalog if isinstance(p,dict)})!=46:
  raise Stop("PUBLIC_46_PROVIDER_CATALOG_MISMATCH")
 print("PUBLIC_CATALOG: PASS 46 original provider IDs (not 46 healthy sources)")
 query=urlencode({"q":"the good dinosaur 2015","providers":",".join(PROVIDERS),"category":"all"})
 resp=public_json("/api/search?"+query)
 rows,stats,errors=resp.get("results"),resp.get("stats"),resp.get("errors")
 if not all(isinstance(x,list) for x in (rows,stats,errors)):
  raise Stop("PUBLIC_SEARCH_SCHEMA_INVALID")
 if len(rows)>350 or len(stats)!=len(PROVIDERS) or resp.get("total")!=len(rows):
  raise Stop("PUBLIC_SEARCH_COUNTS_INVALID")
 source_counts={}
 off_topic=0
 for s in stats:
  if not isinstance(s,dict) or s.get("provider") not in PROVIDERS or s["provider"] in source_counts:
   raise Stop("PUBLIC_STATS_PROVENANCE_INVALID")
  p=s["provider"]
  n,raw,excluded=s.get("count"),s.get("rawCount"),s.get("excludedOffTopic")
  if not all(type(x)==int and x>=0 for x in (n,raw,excluded)) or n+excluded!=raw:
   raise Stop("PUBLIC_STATS_INTERNAL_COUNTS_INVALID")
  source_counts[p]=n
  off_topic+=excluded
 if set(source_counts)!=set(PROVIDERS) or resp.get("excludedOffTopic")!=off_topic:
  raise Stop("PUBLIC_STATS_MISSING_OR_BAD_TOTALS")
 seen=dict.fromkeys(PROVIDERS,0)
 for row in rows:
  if not isinstance(row,dict) or row.get("provider") not in PROVIDERS:
   raise Stop("PUBLIC_RESULT_SOURCE_UNKNOWN")
  expected={"good","dinosaur","2015"}
  actual=set(re.findall(r"[a-z0-9]+",str(row.get("name","")).lower()))
  if not expected.issubset(actual):raise Stop("PUBLIC_IRRELEVANT_TITLE_LEAK")
  seen[row["provider"]]+=1
 if seen!=source_counts:raise Stop("PUBLIC_PER_SOURCE_COUNTS_DISAGREE")
 failures=set()
 for err in errors:
  if not isinstance(err,dict) or err.get("provider") not in PROVIDERS:
   raise Stop("PUBLIC_ERROR_UNATTRIBUTED")
  p=err["provider"]
  if p in failures or source_counts[p]!=0:raise Stop("PUBLIC_SOURCE_ERROR_CONTRADICTION")
  failures.add(p)
 for stat in stats:
  if stat["provider"] in failures and stat.get("ok") is not False:
   raise Stop("PUBLIC_SOURCE_ERROR_HIDDEN")
 print("PUBLIC_5_SOURCE_QUERY: rows_matching="+str(len(rows))+
       " off_topic_excluded="+str(off_topic)+
       " genuine_source_errors="+str(len(errors))+
       " title_gate=PASS")
 for p in PROVIDERS:
  print("SOURCE_"+p+": matches="+str(source_counts[p])+
        " status="+("ERROR" if p in failures else "RESPONDED"))
 if not rows:raise Stop("PUBLIC_NO_POSITIVE_EXAMPLE")
 last,actual=snapshot()
 if first["id"]!=last["id"] or actual!=EXPECTED:
  raise Stop("CONCURRENT_CLOUDFLARE_CHANGE")
 print("READ_ONLY_FULL_POSTFLIGHT: PASS 136c100/540b0, public app.js and relevant titles")
 print("PROVIDER_AVAILABILITY: "+("DEGRADED" if errors else "NO_ERRORS_OBSERVED")+
       " (does not claim 46/46 provider uptime)")
 return 0

if __name__=="__main__":
 try:sys.exit(main())
 except Stop as e:
  print("READ_ONLY_POSTFLIGHT_STOP: "+str(e));sys.exit(1)
 except (KeyError,ValueError,TypeError):
  print("READ_ONLY_POSTFLIGHT_STOP: SANITIZED_METADATA_OR_TYPE");sys.exit(1)
