#!/usr/bin/env python3
"""One-shot safe NoNameClub original-page vs. production-resolver differential.

Only GET exact owner-provided original page and metadata-only POST to the
production /api/resolve endpoint; no magnets/torrents/BTIH/passkeys logged,
no login or challenge bypass, no repeated requests, no Flud/Shield.
"""
from __future__ import annotations
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs
from urllib.request import Request, HTTPRedirectHandler, build_opener
import json,os,re,sys

ORIGINAL="https://nnmclub.to/forum/viewtopic.php?t=1896364"
PRODUCTION="https://index.alexlab.media/api/resolve"
ACTION="OWNER_NONAMECLUB_EXACT_READONLY_20261025"
MAX_BYTES=1100000
UA="Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36"

class Stop(Exception):pass
class NoRedirect(HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):return None

def request_exact(url, payload=None):
 if (url,payload is not None) not in ((ORIGINAL,False),(PRODUCTION,True)):
  raise Stop("UNAPPROVED_URL_OR_METHOD")
 data=json.dumps(payload,separators=(",",":")).encode() if payload is not None else None
 if data is not None and (payload!={"provider":"nonameclub","details":ORIGINAL} or len(data)>450):
  raise Stop("UNAPPROVED_RESOLVE_BODY")
 headers={"User-Agent":UA,"Accept-Encoding":"identity","Cache-Control":"no-store,no-cache",
          "Accept":"application/json" if data else "text/html,application/xhtml+xml"}
 if data:headers.update({"Content-Type":"application/json","Origin":"https://index.alexlab.media"})
 req=Request(url,headers=headers,method="POST" if data else "GET",data=data)
 try:
  with build_opener(NoRedirect).open(req,timeout=20) as res:
   return res.status,res.headers.get("Content-Type",""),res.read(MAX_BYTES+1)
 except HTTPError as e:
  body=e.read(MAX_BYTES+1) if data else b""
  return e.code,e.headers.get("Content-Type",""),body
 except (URLError,OSError,TimeoutError):
  return 0,"",b""

def btih(value):
 if not isinstance(value,str) or not value.lower().startswith("magnet:?") or len(value)>12000:return None
 try:
  q=parse_qs(value.split("?",1)[1])
  xt=q.get("xt",[])
  if len(xt)!=1:return None
  m=re.fullmatch(r"urn:btih:([a-f0-9]{40}|[a-z2-7]{32})",xt[0],re.I)
  return m[1].lower() if m else None
 except (ValueError,IndexError,TypeError):
  return None

class Inspect(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True)
  self.anchors=[]
  self.images=[]
  self.onclick_magnet=0
  self._anchor_stack=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if isinstance(a.get("onclick"),str) and "magnet:?" in a["onclick"].lower():self.onclick_magnet+=1
  if tag.lower()=="a":
   self.anchors.append(a.get("href") or "")
   self._anchor_stack.append(len(self.anchors)-1)
  elif tag.lower()=="img":
   alt=" ".join(str(a.get(x) or "") for x in ("alt","title"))
   if "примагнит" in alt.lower() or "magnet" in alt.lower():
    self.images.append(self._anchor_stack[-1] if self._anchor_stack else None)
 def handle_endtag(self,tag):
  if tag.lower()=="a" and self._anchor_stack:self._anchor_stack.pop()

def source_summary(status,mime,body):
 if status!=200:return ("HTTP_"+str(status),None)
 if len(body)>MAX_BYTES:return ("OVERSIZED",None)
 if "html" not in mime.lower():return ("NON_HTML",None)
 sample=body[:2000].decode("utf8","replace").lower()
 if "just a moment" in sample or "checking your browser" in sample:return ("CHALLENGE",None)
 parser=Inspect()
 try:parser.feed(body.decode("utf8","replace"))
 except (ValueError,AssertionError):return ("MALFORMED_HTML",None)
 # Source-owned exact selector as worker: a[href^='magnet:']
 matches=[v for v in parser.anchors if v.startswith("magnet:")]
 hashes=[v for v in (btih(link) for link in matches) if v]
 if len(hashes)>0:return ("HTML_MAGNET_ANCHOR_VALID",hashes[0])
 if len(matches)>0:return ("HTML_MAGNET_ANCHOR_UNUSABLE",None)
 if parser.onclick_magnet>0:return ("JS_ONCLICK_MAGNET_ONLY",None)
 if parser.images and any(i is not None for i in parser.images):return ("MAGNET_ICON_ANCHOR_WITHOUT_MAGNET_HREF",None)
 if parser.images:return ("MAGNET_ICON_NO_LINK",None)
 return ("NO_MAGNET_INDICATOR_IN_SERVER_HTML",None)

def worker_summary(status,mime,body):
 if len(body)>MAX_BYTES:return ("RESPONSE_OVERSIZED",None)
 if "application/json" not in mime.lower():return ("NON_JSON",None)
 try:r=json.loads(body)
 except (ValueError,UnicodeError):return ("INVALID_JSON",None)
 if not isinstance(r,dict):return ("INVALID_SCHEMA",None)
 if status==200:
  h=btih(r.get("magnet"))
  return ("RESOLVED_VALID_BTIH",h) if h else ("HTTP200_WITHOUT_MAGNET",None)
 # Error text never printed; only fixed category from server error message.
 err=str(r.get("error","")).lower()[:420]
 for code in ("401","403","404","429","500","502","503","504"):
  if "provider http "+code in err:return ("ORIGINAL_HTTP_"+code,None)
 if "no supported magnet" in err:return ("NO_SUPPORTED_MAGNET_IN_HTML",None)
 if "challenge" in err or "browser session" in err:return ("SOURCE_CHALLENGE",None)
 if "redirect" in err:return ("SOURCE_REDIRECT",None)
 if "timeout" in err:return ("SOURCE_TIMEOUT",None)
 if "details url" in err or "not allowed" in err:return ("DETAILS_URL_REJECTED",None)
 return ("RESOLVE_ERROR_OTHER",None)

def run():
 status,mime,html=request_exact(ORIGINAL)
 print("ORIGINAL_PUBLIC_PAGE_HTTP:",status,flush=True)
 stage,h=source_summary(status,mime,html)
 print("ORIGINAL_HTML_MAGNET_STAGE:",stage,flush=True)
 if status!=200 or stage in ("CHALLENGE","OVERSIZED"):
  print("READONLY_STOP_SOURCE_UNAVAILABLE_NO_RETRY",flush=True)
  return 0
 # One existing production resolver call, no torrent or Flud.
 status,mime,body=request_exact(PRODUCTION,{"provider":"nonameclub","details":ORIGINAL})
 print("PRODUCTION_RESOLVE_HTTP:",status,flush=True)
 outcome,worker_hash=worker_summary(status,mime,body)
 print("PRODUCTION_RESOLVE_STAGE:",outcome,flush=True)
 if h and worker_hash:
  print("SOURCE_AND_WORKER_BTIH_EQUAL:","YES" if h==worker_hash else "NO",flush=True)
 print("READONLY_DONE_NO_MAGNET_HASH_HTML_TORRENT_COOKIE_OR_FLUD_LOGGED",flush=True)
 return 0

def main():
 if sys.argv[1:]!=["--owner-readonly"] or os.environ.get("MAGNETRA_NONAMECLUB_OWNER_READONLY")!=ACTION:
  print("STOP_NOT_AUTHORIZED_NO_REQUEST",flush=True);return 2
 try:return run()
 except Exception:
  print("READONLY_STOP_UNEXPECTED_REDACTED",flush=True);return 1

if __name__=="__main__":raise SystemExit(main())
