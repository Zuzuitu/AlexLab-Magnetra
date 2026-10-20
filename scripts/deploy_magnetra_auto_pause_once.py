#!/usr/bin/env python3
"""Manual one-action release for PWA failure-only indexer auto-pause.

Stage/upload a new immutable Cloudflare version, verify three static assets in an
actual zero-percent version slot, promote to 100 with old 136c kept at 0%.
No source probes/retries, paid services, Flud sends, DNS, secret changes or Rock64.
Fail closed on unexpected versions, deployment races and non-200 static requests.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

from deploy_magnetra_zero_percent import _get_api, _wrangler_deploy
from deploy_magnetra_relevance_136c_slot import snapshot
from inspect_magnetra_fix_stage import EXPECTED, binding_pairs

OLD="136c1425-0070-48db-b995-5708bd35bb75"
OLD_ROLLBACK="540b3417-f845-47e8-96bd-856ccc9f1350"
ACTION="CONFIRM_AUTO_PAUSE_SINGLE_ACTION_RELEASE"
RESTORE="CONFIRM_AUTO_PAUSE_MANUAL_RESTORE"
BASE="https://index.alexlab.media"
ROOT=Path(__file__).resolve().parent.parent
UUID=re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}",re.I)
ASSETS=(("/app.js","web/app.js","javascript"),
        ("/styles.css","web/styles.css","text/css"),
        ("/index.html","web/index.html","text/html"))

class Stop(Exception):pass
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  return None

def bindings(version):
 if not isinstance(version,str) or not UUID.fullmatch(version):
  raise Stop("INVALID_VERSION_ID")
 data=_get_api("/versions/"+version)
 if not isinstance(data,dict) or data.get("success") is not True or data.get("result",{}).get("id")!=version:
  raise Stop("IMMUTABLE_VERSION_NOT_FOUND")
 pairs=binding_pairs(data)
 for name,kinds in EXPECTED.items():
  if not any((name,kind) in pairs for kind in kinds):
   raise Stop("IMMUTABLE_VERSION_BINDING_UNVERIFIED_"+name)
 print("IMMUTABLE_BINDINGS_PASS: "+version[:8]+" (3 names/types only)")

def current(expected):
 dep,shares=snapshot()
 if shares!=expected or not dep.get("id"):
  raise Stop("UNEXPECTED_LIVE_DEPLOYMENT_SPLIT")
 return dep

def stable(first,expected):
 second=current(expected)
 if first["id"]!=second["id"]:
  raise Stop("CONCURRENT_CLOUDFLARE_DEPLOYMENT")
 return second

def uploaded_version_id(output):
 values=re.findall(r"Worker Version ID:\s*("+UUID.pattern+r")",output,re.I)
 if len(values)!=1:
  raise Stop("UNIQUE_UPLOADED_VERSION_ID_UNVERIFIED")
 return values[0].lower()

def upload_version():
 config=json.loads((ROOT/"worker/wrangler.jsonc").read_text(encoding="utf8"))
 if (config.get("name")!="alexlab-magnetra" or config.get("main")!="src/index.mjs"
  or config.get("routes")!=[{"pattern":"index.alexlab.media","custom_domain":True}]
  or config.get("assets")!={"directory":"../web","binding":"ASSETS"}):
  raise Stop("PRODUCTION_ORIGIN_ASSETS_UNVERIFIED")
 config["secrets"]={"required":["BTDIGG_GATEWAY_TOKEN","MAGNETRA_GATEWAY_TOKEN"]}
 tmp=ROOT/"worker/.wrangler-auto-pause-once.jsonc"
 tmp.write_text(json.dumps(config),encoding="utf8")
 os.chmod(tmp,0o600)
 try:
  try:
   process=subprocess.run(
    ["npx","--yes","wrangler@4.102.0","versions","upload",
     "--config",str(tmp),"--keep-vars",
     "--message","Magnetra automatic reversible source failure pause - verified PWA release"],
    cwd=ROOT,capture_output=True,text=True,timeout=220,check=False)
  except (OSError,subprocess.TimeoutExpired):
   raise Stop("WRANGLER_UPLOAD_NOT_VERIFIED") from None
  if process.returncode:
   raise Stop("WRANGLER_UPLOAD_FAILED")
  version=uploaded_version_id(process.stdout+"\n"+process.stderr)
  if version in (OLD,OLD_ROLLBACK):
   raise Stop("UPLOADED_IMMUTABLE_VERSION_COLLISION")
  print("NEW_VERSION_UPLOADED:"+version)
  return version
 finally:
  tmp.unlink(missing_ok=True)

def static_get(path,version=None):
 if path not in (a[0] for a in ASSETS):
  raise Stop("UNAPPROVED_STATIC_ASSET_ROUTE")
 headers={"Accept-Encoding":"identity","Cache-Control":"no-cache,no-store,max-age=0",
          "Pragma":"no-cache","User-Agent":"MagnetraAutoPauseOneActionReadonly/1.0"}
 if version is not None:
  if not UUID.fullmatch(version):raise Stop("UNKNOWN_OVERRIDE_VERSION")
  headers["Cloudflare-Workers-Version-Overrides"]='alexlab-magnetra="'+version+'"'
 req=urllib.request.Request(BASE+path,headers=headers,method="GET")
 try:
  with urllib.request.build_opener(NoRedirect()).open(req,timeout=18) as resp:
   expected=next(x[2] for x in ASSETS if x[0]==path)
   if resp.status!=200 or expected not in resp.headers.get("content-type",""):
    raise Stop("STATIC_HTTP_OR_MIME_UNVERIFIED")
   data=resp.read(1_200_001)
 except (urllib.error.HTTPError,urllib.error.URLError,OSError,TimeoutError):
  raise Stop("STATIC_TRANSPORT_OR_HTTP_UNVERIFIED") from None
 if not data or len(data)>1_200_000:
  raise Stop("STATIC_ASSET_LENGTH_INVALID")
 return data

def verify_assets(version,deployment,shares):
 # Reads from Cloudflare CDN must be bounded. Only successful, valid HTTP-200
 # but old-hash responses are polled; NEVER retry 429/504/other HTTP errors.
 for route,filename,_ in ASSETS:
  reviewed=(ROOT/filename).read_bytes()
  sha=hashlib.sha256(reviewed).digest()
  for attempt in range(12):
   got=static_get(route,version)
   if hashlib.sha256(got).digest()==sha:
    print("STATIC_PASS:"+route+" hash="+hashlib.sha256(reviewed).hexdigest()[:16])
    break
   stable(deployment,shares)
   if attempt==11:raise Stop("STATIC_SHA_UNVERIFIED_"+route)
   time.sleep(8)

def wait_for(first,old,target,wrote):
 for n in range(4):
  dep,share=snapshot()
  if share==target:
   if not wrote or dep["id"]==first["id"]:
    raise Stop("TARGET_VISIBLE_BUT_WRITE_UNVERIFIED")
   return dep
  if share!=old or not wrote:
   raise Stop("UNKNOWN_POSTWRITE_DEPLOYMENT_NO_AUTORETRY")
  if n<3:time.sleep(2)
 raise Stop("DEPLOYMENT_POSTFLIGHT_UNVERIFIED")

def release():
 original={OLD:100,OLD_ROLLBACK:0}
 before=current(original)
 bindings(OLD)
 bindings(OLD_ROLLBACK)
 stable(before,original)
 print("PREFLIGHT_PASS: live 136c100/540b0; immutable verified")
 new=upload_version()
 bindings(new)
 stable(before,original)
 slot={OLD:100,new:0}
 print("SLOT_WRITE_ONCE: 136c100/new0")
 wrote=_wrangler_deploy([OLD+"@100%",new+"@0%"],
                        "Magnetra reversible source selection candidate at 0 percent")
 deployed_slot=wait_for(before,original,slot,wrote)
 verify_assets(new,deployed_slot,slot)
 stable(deployed_slot,slot)
 full={OLD:0,new:100}
 print("FULL_WRITE_ONCE: 136c0/new100; 136c remains rollback")
 wrote2=_wrangler_deploy([OLD+"@0%",new+"@100%"],
                         "Magnetra reversible automatic pause PWA to 100 percent")
 deployed_full=wait_for(deployed_slot,slot,full,wrote2)
 verify_assets(None,deployed_full,full)
 stable(deployed_full,full)
 print("FULL_POSTFLIGHT_PASS: NEW100 136C0 new_version="+new)
 print("IPHONE_AUTO_PAUSE: owner acceptance pending a completed user search")
 return 0

def restore():
 new=os.environ.get("MAGNETRA_AUTO_PAUSE_RESTORE_ID","").strip().lower()
 if not UUID.fullmatch(new) or new in (OLD,OLD_ROLLBACK):
  raise Stop("RESTORE_REQUIRES_EXACT_CANDIDATE_VERSION_ID")
 full={OLD:0,new:100}
 before=current(full)
 bindings(OLD)
 bindings(new)
 stable(before,full)
 destination={OLD:100,new:0}
 print("RESTORE_WRITE_ONCE: 136c100/new0")
 wrote=_wrangler_deploy([OLD+"@100%",new+"@0%"],
                        "Magnetra manual restore 136c stable relevance release")
 wait_for(before,full,destination,wrote)
 print("RESTORE_POSTFLIGHT_PASS: 136c100")
 return 0

def main():
 action=os.environ.get("MAGNETRA_AUTO_PAUSE_ACTION","")
 if action not in (ACTION,RESTORE):
  print("STOP: exact owner GitHub manual action required before any Cloudflare request")
  return 2
 try:return release() if action==ACTION else restore()
 except (Stop,ValueError,TypeError,KeyError,OSError):
  print("AUTO_PAUSE_RELEASE_STOP: check immutable/deployment/statics gates, no auto rollback, never rerun blindly")
  return 1

if __name__=="__main__":
 sys.exit(main())
