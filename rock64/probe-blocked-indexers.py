#!/usr/bin/env python3
"""Read-only, direct residential egress diagnosis for four original Magnetra indexers.

Run as unprivileged 'runner' on the physical Rock64, not from a Cloudflare
Worker or VPN browser session. Exactly five GETs, fixed HTTPS allowlist,
max 256 KB inspected from each, up to 9 seconds per request.
No torrents/magnets downloaded, no credentials, HTML or query titles printed.
Never changes DNS, Tailscale, VPN, routes, systemd or the BTDigg gateway.
"""
from __future__ import annotations

import socket
import time
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36"
)
MAX_PREVIEW = 256 * 1024
TIMEOUT_SECONDS = 9

@dataclass(frozen=True)
class Target:
    name: str
    url: str
    marker: bytes
    cookie: str = ""

# The exact existing Magnetra source domains and URL templates.
# The EZTV API is an EXTRA probe, not a drop-in arbitrary-keyword search:
# the official API supports recent releases and IMDb-ID queries.
TARGETS = (
    Target("1337x", "https://1337x.to/search/ubuntu/1/", b"table-list"),
    Target("BT4G", "https://bt4gprx.com/search?q=ubuntu&category=all&orderby=seeders&p=1", b"notion-list-item"),
    Target("Ext", "https://ext.to/browse/?q=ubuntu", b"search-table"),
    Target("EZTV web", "https://eztvx.to/search/ubuntu", b"epinfo", "layout=def_wlinks"),
    Target("EZTV API", "https://eztvx.to/api/get-torrents?limit=2&page=1", b'"torrents"'),
)

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def request_for(target: Target) -> Request:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json" if target.name == "EZTV API"
            else "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "identity",
    }
    if target.cookie:
        headers["Cookie"] = target.cookie
    return Request(target.url, headers=headers, method="GET")

def describe(status: int, headers, body: bytes, marker: bytes) -> str:
    if status in (301, 302, 303, 307, 308):
        return "REDIRECT (not followed)"
    if status in (401, 403):
        return "ACCESS_DENIED"
    if status == 429:
        return "RATE_LIMIT"
    if status != 200:
        return "HTTP_ERROR"
    head = body[:8192].lower()
    if (headers.get("cf-mitigated", "").lower() == "challenge"
        or b"just a moment" in head or b"checking your browser" in head
        or b"captcha" in head):
        return "CHALLENGE"
    if marker in body.lower():
        return "HTTP_OK + expected page/API marker"
    return "HTTP_OK, source format not verified"

def run_one(target: Target, opener=None):
    # Explicitly ignores proxy environment variables; no browser/Tailscale
    # routing assumptions. Never redirects to unexpected origins.
    opener = opener or build_opener(ProxyHandler({}), NoRedirect())
    began = time.monotonic()
    try:
        with opener.open(request_for(target), timeout=TIMEOUT_SECONDS) as response:
            status = response.status
            headers = response.headers
            body = response.read(MAX_PREVIEW)
    except HTTPError as exc:
        status, headers, body = exc.code, exc.headers, b""
        exc.close()
    except (socket.timeout, TimeoutError, URLError, OSError):
        return "TRANSPORT_OR_TIMEOUT", time.monotonic() - began
    return f"HTTP {status}: {describe(status, headers, body, target.marker)}", time.monotonic() - began

def main():
    print("Magnetra · residential source probe (Rock64, read-only)")
    print("Five fixed search/API requests; no torrents, magnets, credentials or VPN changes.")
    for target in TARGETS:
        result, elapsed = run_one(target)
        print(f"{target.name:9s} | {result:46s} | {elapsed:.2f}s")
    print("Complete. Statuses show reachability from Rock64 only, not Cloudflare.")

if __name__ == "__main__":
    main()
