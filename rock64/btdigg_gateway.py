#!/usr/bin/env python3
"""Private, opt-in residential egress for Magnetra's ORIGINAL BTDigg adapter.

Only fetches the fixed https://btdig.com/search endpoint, never arbitrary URLs.
This service is NOT a DHT crawler or an anti-bot/CAPTCHA bypass. It binds
127.0.0.1 by default; expose only via a separately configured authenticated
Cloudflare Tunnel, with exactly the same high-entropy bearer token on both ends.

Python 3 stdlib only. No external dependencies or sensitive query logging.
"""
from __future__ import annotations

import hmac
import json
import os
import re
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

BIND = "127.0.0.1"
PORT = 8796
HOST = "https://btdig.com"
SIZE_LIMIT = 3_000_000
TIMEOUT_SECONDS = 8
CACHE_SECONDS = 30
MIN_SEARCH_INTERVAL = 5
SOURCE_UA = (
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36"
)
QUERY_INVALID = re.compile(r"[\x00-\x1f\x7f]")


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class SearchProvider:
    def __init__(self, fetcher=None, clock=None):
        self.fetcher = fetcher or self.fetch
        self.clock = clock or time.monotonic
        self._mutex = threading.Lock()
        self._last = float("-inf")
        self._cached_query = None
        self._cached_content = b""
        self._cached_at = float("-inf")

    @staticmethod
    def fetch(query: str) -> tuple[int, bytes]:
        url = HOST + "/search?q=" + quote(query, safe="")
        request = Request(
            url,
            headers={
                "User-Agent": SOURCE_UA,
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "identity",
            },
            method="GET",
        )
        try:
            # Explicitly stop redirects: not an open proxy, no off-origin hops.
            with build_opener(ProxyHandler({}), NoRedirect()).open(request, timeout=TIMEOUT_SECONDS) as res:
                if res.status != 200:
                    return res.status, b""
                if int(res.headers.get("content-length") or 0) > SIZE_LIMIT:
                    return 502, b""
                if "text/html" not in res.headers.get("content-type", "").lower():
                    return 502, b""
                raw = res.read(SIZE_LIMIT + 1)
                if len(raw) > SIZE_LIMIT:
                    return 502, b""
                if any(x in raw[:2400].lower() for x in
                       (b"cf-mitigated", b"just a moment", b"checking your browser")):
                    return 503, b""
                return 200, raw
        except HTTPError as e:
            # No retries on 429 / CAPTCHA; respect provider controls.
            return (429 if e.code == 429 else 503), b""
        except (OSError, URLError, TimeoutError):
            return 504, b""

    def search(self, query: str) -> tuple[int, bytes]:
        if not self._mutex.acquire(blocking=False):
            return 429, b""
        try:
            now = self.clock()
            if self._cached_query == query and now - self._cached_at < CACHE_SECONDS:
                return 200, self._cached_content
            if now - self._last < MIN_SEARCH_INTERVAL:
                return 429, b""
            self._last = now
            status, html = self.fetcher(query)
            if status == 200 and html and len(html) <= SIZE_LIMIT:
                self._cached_query = query
                self._cached_content = html
                self._cached_at = self.clock()
                return 200, html
            return status, b""
        finally:
            self._mutex.release()


def handler_class(secret: str, provider: SearchProvider):
    class Handler(BaseHTTPRequestHandler):
        server_version = "MagnetraBTDigg/1.0"
        sys_version = ""

        def log_message(self, format, *args):
            # Requests contain queries; intentionally do not log them or auth headers.
            return

        def reply(self, status: int, body: bytes = b"", mime="application/json"):
            self.send_response(status)
            self.send_header("content-type", mime)
            self.send_header("cache-control", "no-store")
            self.send_header("x-content-type-options", "nosniff")
            self.send_header("content-length", str(len(body)))
            if status == 429:
                self.send_header("retry-after", str(MIN_SEARCH_INTERVAL))
            self.end_headers()
            if body:
                self.wfile.write(body)

        def do_GET(self):
            authorization = self.headers.get("authorization", "")
            if not hmac.compare_digest(authorization, "Bearer " + secret):
                self.reply(401, b'{"error":"unauthorized"}')
                return
            parsed = urlsplit(self.path)
            if parsed.path == "/healthz" and not parsed.query:
                self.reply(200, b'{"ok":true}', "application/json")
                return
            if parsed.path != "/v1/search" or parsed.fragment or len(self.path) > 2600:
                self.reply(404, b'{"error":"not found"}')
                return
            params = parse_qs(parsed.query, keep_blank_values=True)
            if set(params) != {"q"} or len(params["q"]) != 1:
                self.reply(400, b'{"error":"invalid query"}')
                return
            query = params["q"][0].strip()
            if not 2 <= len(query) <= 180 or QUERY_INVALID.search(query):
                self.reply(400, b'{"error":"invalid query"}')
                return
            status, body = provider.search(query)
            if status == 200:
                self.reply(200, body, "text/html; charset=utf-8")
            else:
                reason = {
                    429: "rate limited",
                    503: "BTDigg challenge or upstream unavailable",
                    504: "BTDigg request timed out",
                }.get(status, "BTDigg upstream error")
                self.reply(status, json.dumps({"error": reason}).encode())

        def do_POST(self):
            self.reply(405, b'{"error":"method not allowed"}')

    return Handler



class LimitedHTTPServer(ThreadingHTTPServer):
    """Bound per-request threads, including rejected/unauthenticated requests."""
    daemon_threads = True
    request_queue_size = 16

    def __init__(self, address, handler):
        self._slots = threading.BoundedSemaphore(16)
        super().__init__(address, handler)

    def process_request(self, request, client_address):
        if not self._slots.acquire(blocking=False):
            request.close()
            return
        try:
            super().process_request(request, client_address)
        except BaseException:
            self._slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self._slots.release()


def main():
    token = os.environ.get("MAGNETRA_BTDIGG_TOKEN", "")
    if len(token) < 48 or len(token) > 256 or not re.fullmatch(r"[A-Za-z0-9_-]+", token):
        raise SystemExit("Set a strong MAGNETRA_BTDIGG_TOKEN (48-256 URL-safe characters).")
    # Explicit no-port-forward and no LAN listener. Use Cloudflare Tunnel -> localhost.
    server = LimitedHTTPServer((BIND, PORT), handler_class(token, SearchProvider()))
    print("Magnetra BTDigg gateway bound to 127.0.0.1:%d (private); no public listener." % PORT, flush=True)
    try:
        server.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
