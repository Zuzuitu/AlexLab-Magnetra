#!/usr/bin/env python3
"""Single-pass read-only debug of failed zero-share HTML hash gate."""
from __future__ import annotations
import hashlib
from pathlib import Path
import urllib.request
import urllib.error
from deploy_magnetra_relevance_136c_slot import snapshot, verify_version

OLD="136c1425-0070-48db-b995-5708bd35bb75"
NEW="c86c9a32-31fd-4952-86ed-b35f1763b342"
EXPECTED={OLD:100,NEW:0}
ROOT=Path(__file__).resolve().parent.parent
BASE="https://index.alexlab.media"
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):return None
def digest(data):return hashlib.sha256(data).hexdigest()[:20]
def read(path,version):
 headers={"Accept-Encoding":"identity","Cache-Control":"no-cache,no-store,max-age=0",
          "Pragma":"no-cache","User-Agent":"MagnetraAutoPauseHtmlZeroShareReadOnly/1.0"}
 if version:headers["Cloudflare-Workers-Version-Overrides"]='alexlab-magnetra="'+version+'"'
 req=urllib.request.Request(BASE+path,headers=headers,method="GET")
 try:
  with urllib.request.build_opener(NoRedirect()).open(req,timeout=20) as res:
   data=res.read(1300000)
   return res.status,res.headers.get("content-type",""),data
 except urllib.error.HTTPError as e:
  return e.code,"HTTP_ERROR",b""
 except (urllib.error.URLError,OSError,TimeoutError):
  return -1,"NETWORK_ERROR",b""
def main():
 d,shares=snapshot()
 print("CLOUDFLARE_SHARES: 136c="+str(shares.get(OLD))+
       " new="+str(shares.get(NEW))+" count="+str(len(shares)))
 if shares!=EXPECTED:
  print("STOP_UNEXPECTED_SPLIT");return 2
 verify_version(OLD);verify_version(NEW)
 print("VERSION_BINDINGS_VERIFIED")
 reviewed=(ROOT/"web/index.html").read_bytes()
 print("SOURCE_INDEX: size="+str(len(reviewed))+" sha="+digest(reviewed))
 for version,label in [(NEW,"new-c86"),(OLD,"old-136c"),(None,"public-default")]:
  for path in ("/index.html","/"):
   status,ctype,data=read(path,version)
   if status!=200 or "html" not in ctype.lower() or len(data)>1200000:
    print(label+" "+path+" STATUS="+str(status)+" TYPE="+("HTML" if "html" in ctype.lower() else "NONHTML"))
    continue
   common=0
   for a,b in zip(reviewed,data):
    if a!=b:break
    common+=1
   print(label+" "+path+" STATUS=200 size="+str(len(data))+" sha="+digest(data)+
         " match="+str(data==reviewed)+
         " prefix_equal="+str(common)+
         " has_new_summary="+str(b'sourceHealthSummary' in data)+
         " has_new_auto_pause_copy="+str(b'failed indexer' in data))
 final,now=snapshot()
 if final["id"]!=d["id"] or now!=EXPECTED:print("CONCURRENT_DEPLOYMENT_STOP");return 2
 print("READ_ONLY_COMPLETE: no upload, traffic write, provider search or retries")
 return 0
if __name__=="__main__":
 try:raise SystemExit(main())
 except (KeyError,ValueError,TypeError,OSError):
  print("DIAGNOSTIC_STOP: SANITIZED");raise SystemExit(1)
