#!/usr/bin/env python3
"""Read-only BTDigg PWA asset smoke: never calls /api/search or BTDigg origin."""
from __future__ import annotations
from urllib.request import Request, urlopen

ORIGIN="https://index.alexlab.media"
EXPECTED=(
    "const BTDIGG_MIN_GAP_MS=30_000;",
    "const BTDIGG_429_DELAYS_MS=[60_000,120_000,300_000];",
    "function btdiggCooldownRemainingMs(",
    "async function waitForBTDigg(",
)

def verify(fetch=None):
    if fetch is None:
        def fetch(url):
            req=Request(url,headers={
                "User-Agent":"Magnetra-BTDigg-PWA-AssetSmoke/1.0",
                "Cache-Control":"no-cache, no-store",
                "Accept":"application/javascript,text/javascript,*/*",
            })
            with urlopen(req,timeout=12) as response:
                if response.status!=200:
                    raise AssertionError("PWA app.js not HTTP 200")
                return response.read(250_001)
    data=fetch(ORIGIN+"/app.js")
    if not isinstance(data,bytes) or not 10_000<=len(data)<=250_000:
        raise AssertionError("PWA JS response absent or malformed")
    source=data.decode("utf-8")
    if any(fragment not in source for fragment in EXPECTED):
        raise AssertionError("PWA JS is not the reviewed BTDigg 30s version")
    return "PASS: deployed BTDigg PWA JS; NO_SOURCE_SEARCH"

if __name__=="__main__":
    print(verify())
