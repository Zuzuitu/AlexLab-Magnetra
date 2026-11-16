#!/usr/bin/env python3
"""GET-only Cloudflare PWA smoke for request-dispatch BTDigg pacing.

No provider API calls, no BTDigg navigation, no private tailnet requests,
no noVNC connections and no request containing torrent search terms.
"""
import re
from urllib.request import Request,urlopen

ORIGIN="https://index.alexlab.media"
LIMIT=600_000
SOURCE_MARKERS=(
    "function recordBTDiggRequestDispatch(at=Date.now())",
    "btdiggPacing.nextAllowedAt=Math.max(",
    "btdiggPacing.nextAllowedAt,at+BTDIGG_MIN_GAP_MS",
    "await waitForBTDigg(query,controller.signal);",
    "recordBTDiggRequestDispatch();",
    "await pause(query,signal,true);",
    "btdiggCooldownRemainingMs()>0",
    "recordBTDigg429();",
)

def verify(app,html,csp):
    if not isinstance(app,str) or not isinstance(html,str):
        raise AssertionError("Invalid PWA asset")
    if any(marker not in app for marker in SOURCE_MARKERS):
        raise AssertionError("Missing dispatch-anchored BTDigg pacing markers")
    search=app.split("async function search(){",1)
    if len(search)!=2:
        raise AssertionError("PWA search dispatcher missing")
    search=search[1].split("async function status(){",1)[0]
    if "recordBTDiggRequestDispatch();" not in search:
        raise AssertionError("Missing BTDigg initial source dispatch timestamp")
    if "btdiggPacing.nextAllowedAt=Date.now()+BTDIGG_MIN_GAP_MS" in search:
        raise AssertionError("Old 30-second post-response timer regression")
    if "recordBTDiggRequestDispatch();" not in app.split(
        "async function fetchBTDiggWithOneGuardedNewTab(",1)[1].split(
        "async function search(){",1)[0]:
        raise AssertionError("Guarded new-tab source request timestamp missing")
    if len(re.findall(r"recordBTDiggRequestDispatch\(\);",app))!=2:
        raise AssertionError("Unexpected number of source-dispatch timestamps")
    if 'id="btdiggVerificationDialog"' not in html:
        raise AssertionError("Manual private CAPTCHA dialog not present")
    if "frame-src https://*.ts.net:8444" not in csp:
        raise AssertionError("Private noVNC CSP boundary changed")
    return "PASS: BTDigg spacing from dispatch, not response; NO_SOURCE_SEARCH"

def get(path):
    req=Request(ORIGIN+path,headers={
        "user-agent":"Magnetra-BTDigg-Pacing-Static-Smoke/1",
        "cache-control":"no-cache,no-store",
        "accept":"text/html,application/javascript,*/*",
    })
    with urlopen(req,timeout=12) as response:
        if response.status!=200:
            raise AssertionError("Unexpected static asset status")
        raw=response.read(LIMIT+1)
        if len(raw)>LIMIT:
            raise AssertionError("Static asset exceeds safe size")
        return raw.decode("utf-8"),response.headers.get(
            "content-security-policy","")

if __name__=="__main__":
    app,_=get("/app.js")
    html,csp=get("/")
    print(verify(app,html,csp))
