#!/usr/bin/env python3
"""GET-only live Magnetra PWA smoke for owner-scoped BTDigg refusal recovery.

This verifies Cloudflare static assets. It never fetches /api/search,
contacts BTDigg/Rock64/noVNC/Tailscale, or calls other provider APIs.
"""
from urllib.request import Request,urlopen

ORIGIN="https://index.alexlab.media"
ASSET_LIMIT=600_000
APP_MARKERS=(
    "fetchBTDiggWithOneGuardedNewTab",
    "btdiggVisibleRefusalOnly",
    "BTDIGG_VISIBLE_REFUSAL",
    "await pause(query,signal,true)",
    "document.visibilityState",
    'btdiggVerificationMode==="refusal"',
    'btdiggVerificationRetry").hidden',
    "BTDigg: attempting one new browser tab",
)
I18N_MARKERS=(
    '"Inspect BTDigg refusal in Magnetra"',
    '"BTDigg source refusal"',
    "BTDigg shows Too Many Requests; waiting 30 seconds",
    '"ro": "BTDigg: încercăm o singură căutare într-un tab nou…"',
    '"it": "BTDigg: un solo tentativo di ricerca in una nuova scheda…"',
)
STYLE_MARKERS=(
    "#btdiggVerificationRetry[hidden]{display:none!important}",
)
HTML_MARKERS=(
    'id="btdiggVerificationDialog"',
    'id="btdiggVerificationRetry"',
    'id="btdiggViewerFrame"',
)

def verify(app,html,i18n,styles,headers):
    for name,asset,terms in (
        ("app",app,APP_MARKERS),
        ("html",html,HTML_MARKERS),
        ("i18n",i18n,I18N_MARKERS),
        ("styles",styles,STYLE_MARKERS),
    ):
        if not isinstance(asset,str) or any(term not in asset for term in terms):
            raise AssertionError("Missing reviewed BTDigg one-shot asset: "+name)
    csp=str(headers)
    if ("frame-src https://*.ts.net:8444" not in csp
            or "script-src 'self'" not in csp
            or "frame-ancestors 'none'" not in csp):
        raise AssertionError("Private noVNC CSP boundary was modified")
    return "PASS: scoped one-shot BTDigg recovery UI; NO_PROVIDER_SEARCH"

def get_static(path):
    req=Request(ORIGIN+path,headers={
        "user-agent":"Magnetra-BTDigg-one-shot-static-smoke/1",
        "cache-control":"no-cache, no-store",
        "accept":"text/html,text/css,application/javascript,*/*",
    })
    with urlopen(req,timeout=12) as response:
        if response.status!=200:
            raise AssertionError("Unexpected static response status")
        body=response.read(ASSET_LIMIT+1)
        if len(body)>ASSET_LIMIT:
            raise AssertionError("Static asset oversized")
        return body.decode("utf-8"),response.headers.get(
            "content-security-policy","")

if __name__=="__main__":
    app,_=get_static("/app.js")
    html,headers=get_static("/")
    i18n,_=get_static("/i18n.js")
    styles,_=get_static("/styles.css")
    print(verify(app,html,i18n,styles,headers))
