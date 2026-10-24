#!/usr/bin/env python3
"""Read-only exact owner NoNameClub PWA search-card identity differential.

Search the exact provider with the same ordinary PWA API and compare the card's
source fields to owner-provided 1896364. One same-origin metadata-only resolver
POST only for an exact matched card; never log magnet, hashes, raw JSON,
individual result names, cookies, passkeys or source URLs.
"""
from __future__ import annotations
from urllib.parse import urlencode,urlsplit
from urllib.request import Request,build_opener,HTTPRedirectHandler
from urllib.error import HTTPError,URLError
import json,os,re,sys

PROD="https://index.alexlab.media"
EXACT="https://nnmclub.to/forum/viewtopic.php?t=1896364"
P="nonameclub"
ACTION="OWNER_NONAMECLUB_EXACT_CARD_MATCH_READONLY_20261025"
MAX=1200000

class Stop(Exception): pass
class NoRedirect(HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):return None

def request(url,payload=None):
 allowed={PROD+"/api/search?"+urlencode({"q":q,"category":"all","providers":P}) for q in ("Lupin","Lupin 2026")}
 allowed.add(PROD+"/api/resolve")
 if url not in allowed or (payload is not None and (url!=PROD+"/api/resolve" or payload!={"provider":P,"details":EXACT})):
  raise Stop("UNAPPROVED_URL_OR_PAYLOAD")
 if payload is None and url.endswith("/api/resolve"):raise Stop("MISSING_METHOD")
 data=json.dumps(payload,separators=(",",":")).encode() if payload is not None else None
 headers={"User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile Safari/604.1",
  "Accept":"application/json","Accept-Encoding":"identity","Cache-Control":"no-store"}
 if data:headers.update({"Content-Type":"application/json","Origin":PROD})
 try:
  with build_opener(NoRedirect()).open(Request(url,method="POST" if data else "GET",headers=headers,data=data),timeout=24) as r:
   return r.status,r.headers.get("content-type",""),r.read(MAX+1)
 except HTTPError as e:return e.code,e.headers.get("content-type",""),e.read(MAX+1)
 except (URLError,OSError,TimeoutError):return 0,"",b""

def extract(status,mime,body):
 if status!=200:raise Stop("SEARCH_HTTP_"+str(status) if status in (0,403,404,429,500,502,503,504) else "SEARCH_HTTP_OTHER")
 if len(body)>MAX or "application/json" not in mime.lower():raise Stop("SEARCH_NOT_BOUNDED_JSON")
 try:v=json.loads(body)
 except (ValueError,UnicodeError):raise Stop("SEARCH_INVALID_JSON") from None
 records=v.get("results") if isinstance(v,dict) else None
 if not isinstance(records,list) or len(records)>100:raise Stop("SEARCH_INVALID_RESULT_SHAPE")
 if not all(isinstance(r,dict) for r in records):raise Stop("SEARCH_INVALID_ITEM")
 matches=[x for x in records if x.get("provider")==P and x.get("details")==EXACT]
 if len(matches)>1:raise Stop("AMBIGUOUS_DUPLICATE_OWNER_CARD")
 return len(matches),matches[0] if matches else None, len(records)

def row_stage(row):
 if row is None:return "NOT_FOUND"
 if isinstance(row.get("magnet"),str) and row["magnet"].startswith("magnet:?"):return "PRE_RESOLVED_MAGNET"
 if row.get("magnetSource") is not None:return "AUXILIARY_MAGNET_SOURCE_PRESENT"
 if row.get("details")==EXACT:return "CANONICAL_DETAILS_ONLY"
 return "UNEXPECTED_DETAILS"

def hash_valid(magnet):
 if not isinstance(magnet,str) or not magnet.startswith("magnet:?") or len(magnet)>12000:return False
 from urllib.parse import parse_qs
 xt=parse_qs(magnet.split("?",1)[1]).get("xt",[])
 return len(xt)==1 and bool(re.fullmatch(r"urn:btih:(?:[a-f0-9]{40}|[a-z2-7]{32})",xt[0],re.I))

def classify_resolve(status,mime,body):
 if len(body)>MAX or "application/json" not in mime.lower():return "NON_JSON_OR_OVERSIZED"
 try:v=json.loads(body)
 except (ValueError,UnicodeError):return "INVALID_JSON"
 if not isinstance(v,dict):return "INVALID_JSON_SCHEMA"
 if status==200:return "VALID_BTIH" if hash_valid(v.get("magnet")) else "SUCCESS_WITHOUT_VALID_BTIH"
 err=str(v.get("error",""))[:300].lower()
 if "no supported magnet" in err:return "NO_SUPPORTED_MAGNET_IN_HTML"
 for code in ("401","403","404","429","502","503","504"):
  if "provider http "+code in err:return "UPSTREAM_HTTP_"+code
 if "not allowed" in err:return "DETAIL_URL_REJECTED"
 if "timeout" in err:return "UPSTREAM_TIMEOUT"
 if "challenge" in err:return "UPSTREAM_CHALLENGE"
 return "HTTP_ERROR_OTHER"

def run():
 if os.environ.get("MAGNETRA_NONAMECLUB_CARD_READONLY")!=ACTION:raise Stop("UNAUTHORIZED")
 rows=None
 for query in ("Lupin","Lupin 2026"):
  url=PROD+"/api/search?"+urlencode({"q":query,"category":"all","providers":P})
  status,mime,body=request(url)
  n,row,num=extract(status,mime,body)
  print("SEARCH_"+("GENERAL" if query=="Lupin" else "SPECIFIC")+"_HTTP:",status,flush=True)
  print("OWNER_EXACT_DETAILS_CARD:", "FOUND" if n==1 else "NOT_IN_SAMPLE",flush=True)
  print("SOURCE_RECORD_COUNT_CLASS:", "NONEMPTY" if num else "EMPTY",flush=True)
  if n:
   rows=row
   break
 if rows is None:
  print("NO_EXACT_CARD_PROVEN_NO_RESOLVE_REQUEST",flush=True)
  return 0
 print("OWNER_CARD_MAGNET_PRECEDENCE_CLASS:",row_stage(rows),flush=True)
 if rows.get("provider")!=P or rows.get("details")!=EXACT:raise Stop("DETAIL_CARD_MUTATED")
 if row_stage(rows)=="PRE_RESOLVED_MAGNET":
  print("CARD_HAS_IMMEDIATE_MAGNET_NO_NEED_TO_RESOLVE",flush=True)
  return 0
 code,mime,body=request(PROD+"/api/resolve",{"provider":P,"details":EXACT})
 print("OWNER_CARD_EXACT_RESOLVE_HTTP:",code,flush=True)
 print("OWNER_CARD_EXACT_RESOLVE_CLASS:",classify_resolve(code,mime,body),flush=True)
 print("NO_MAGNET_HASH_FILENAME_RAW_JSON_TORRENT_LOGGED",flush=True)
 return 0

def main():
 if sys.argv[1:]!=["--owner-readonly"] or os.environ.get("MAGNETRA_NONAMECLUB_CARD_READONLY")!=ACTION:
  print("STOP_NOT_AUTHORIZED_NO_REQUESTS",flush=True);return 2
 try:return run()
 except Stop as e:
  print("SAFE_STOP:",str(e),flush=True)
  return 1
 except Exception:
  print("SAFE_STOP:UNEXPECTED_REDACTED",flush=True)
  return 1
if __name__=="__main__":raise SystemExit(main())
