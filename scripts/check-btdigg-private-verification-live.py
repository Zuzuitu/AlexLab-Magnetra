#!/usr/bin/env python3
"""GET-only public PWA verification for private BTDigg CAPTCHA feature.

Never requests /api/search, source BTDigg, the Tailscale private hostname,
VNC, or any authenticated gateway.
"""
from urllib.request import Request,urlopen

ORIGIN="https://index.alexlab.media"
APP_MARKERS=(
    "BTDIGG_CAPTCHA_REQUIRED",
    "BTDIGG_VISIBLE_REFUSAL",
    "validatedBTDiggViewerOrigin",
    "btdiggViewerFrame",
    "btdiggPrivateViewerUrl",
)
HTML_MARKERS=(
    'id="btdiggVerificationDialog"',
    'id="btdiggViewerFrame"',
    'id="btdiggNovncOrigin"',
    'id="btdiggVerificationRetry"',
)
FRAME_DIRECTIVE="frame-src https://*.ts.net:8444"

def verify(app,html,csp):
    if not isinstance(app,str) or not isinstance(html,str):
        raise AssertionError("PWA assets not decoded")
    if any(term not in app for term in APP_MARKERS):
        raise AssertionError("PWA app.js is not the private CAPTCHA feature")
    if any(term not in html for term in HTML_MARKERS):
        raise AssertionError("PWA HTML missing private verification dialog")
    if FRAME_DIRECTIVE not in str(csp):
        raise AssertionError("PWA CSP disallows private tailnet iframe")
    if "script-src 'self'" not in csp or "frame-ancestors 'none'" not in csp:
        raise AssertionError("PWA baseline CSP isolation missing")
    return "PASS: private BTDigg CAPTCHA UI and CSP; NO_SOURCE_SEARCH"

def get(path):
    req=Request(ORIGIN+path,headers={
        "user-agent":"Magnetra-private-BTDigg-asset-smoke/1.0",
        "cache-control":"no-cache, no-store",
        "accept":"text/html,application/javascript,*/*",
    })
    with urlopen(req,timeout=12) as response:
        if response.status!=200: raise AssertionError("PWA static GET failed")
        raw=response.read(500_001)
        if len(raw)>500_000: raise AssertionError("PWA static response too large")
        return raw.decode("utf-8"),response.headers.get("content-security-policy","")

if __name__=="__main__":
    app,_=get("/app.js")
    html,csp=get("/")
    print(verify(app,html,csp))
