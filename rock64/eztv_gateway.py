#!/usr/bin/env python3
"""Single-origin, read-only EZTV API egress for AlexLab Magnetra.

Runs independently from BTDigg, binds loopback, and does not change network
configuration. Never logs torrent names, magnets, hashes, tokens or queries.
No redirects, third-party libraries, torrent downloads or public open proxy.
"""
from __future__ import annotations

import hmac
import json
import os
import re
import threading
import time
from collections import OrderedDict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit, urlencode
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

BIND = "127.0.0.1"
PORT = 8797
SOURCE = "https://eztvx.to/api/get-torrents"
MAX_BYTES = 1_000_000
TIMEOUT = 10
CACHE_TTL = 60
CACHE_ITEMS = 4
MIN_GAP = 3
UA = ("Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36")
IMDB = re.compile(r"^[0-9]{5,12}$")
TOKEN = re.compile(r"^[A-Za-z0-9_-]{48,256}$")


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def validate_payload(data, imdb: str) -> bool:
    """Only authenticated, relevant EZTV JSON reaches the Cloudflare Worker."""
    if not isinstance(data, dict) or "error" in data or "errors" in data:
        return False
    echo = str(data.get("imdb_id", "")).removeprefix("tt")
    if not echo.isdigit() or int(echo) != int(imdb):
        return False
    count = data.get("torrents_count")
    if type(count) not in (str, int) or not str(count).isdigit():
        return False
    torrents = data.get("torrents")
    if torrents is None:
        return "torrents" not in data and int(count) == 0
    if not isinstance(torrents, list) or len(torrents) > 100:
        return False
    return all(isinstance(row, dict) and
               ("imdb_id" not in row or
                (str(row["imdb_id"]).removeprefix("tt").isdigit() and
                 int(str(row["imdb_id"]).removeprefix("tt")) == int(imdb)))
               for row in torrents)


def fetch_upstream(imdb: str) -> tuple[int, bytes]:
    url = SOURCE + "?" + urlencode({"imdb_id": imdb, "limit": 100, "page": 1})
    req = Request(url, method="GET", headers={
        "User-Agent": UA, "Accept": "application/json", "Accept-Encoding": "identity"
    })
    try:
        # Disable ambient HTTP_PROXY, HTTPS_PROXY and redirects for this process.
        with build_opener(ProxyHandler({}), NoRedirect()).open(req, timeout=TIMEOUT) as res:
            if res.status != 200:
                return 502, b""
            if "application/json" not in res.headers.get("content-type", "").lower():
                return 502, b""
            if int(res.headers.get("content-length") or 0) > MAX_BYTES:
                return 502, b""
            body = res.read(MAX_BYTES + 1)
            if len(body) > MAX_BYTES:
                return 502, b""
            try:
                data = json.loads(body)
            except (ValueError, UnicodeError):
                return 502, b""
            if not validate_payload(data, imdb):
                return 502, b""
            return 200, body
    except HTTPError as exc:
        return (exc.code if exc.code in (403, 429) else 502), b""
    except (URLError, OSError, TimeoutError):
        return 504, b""


class Provider:
    """Small RAM-only successful response cache; never retry failed upstream calls."""
    def __init__(self, fetcher=fetch_upstream, clock=time.monotonic):
        self.fetcher = fetcher
        self.clock = clock
        self.lock = threading.Lock()
        self.last = float("-inf")
        self.cache = OrderedDict()
        self.inflight = set()

    def search(self, imdb: str) -> tuple[int, bytes]:
        with self.lock:
            now = self.clock()
            for key, (_, expiry) in list(self.cache.items()):
                if expiry <= now:
                    self.cache.pop(key)
            if imdb in self.cache:
                self.cache.move_to_end(imdb)
                return 200, self.cache[imdb][0]
            if imdb in self.inflight or now - self.last < MIN_GAP:
                return 429, b""
            self.inflight.add(imdb)
            self.last = now
        try:
            status, body = self.fetcher(imdb)
        except Exception:
            status, body = 504, b""
        with self.lock:
            self.inflight.discard(imdb)
            if status == 200 and body and len(body) <= MAX_BYTES:
                self.cache[imdb] = (body, self.clock() + CACHE_TTL)
                self.cache.move_to_end(imdb)
                while len(self.cache) > CACHE_ITEMS:
                    self.cache.popitem(last=False)
        return status, body if status == 200 else b""


def handler_class(secret: str, provider: Provider):
    class Handler(BaseHTTPRequestHandler):
        server_version = "MagnetraEZTV/1.0"
        sys_version = ""

        def log_message(self, fmt, *args):
            return  # no paths, tokens or source details in journald

        def reply(self, status: int, body: bytes = b""):
            self.send_response(status)
            self.send_header("content-type", "application/json")
            self.send_header("cache-control", "private, no-store")
            self.send_header("x-content-type-options", "nosniff")
            self.send_header("content-length", str(len(body)))
            self.end_headers()
            if body:
                self.wfile.write(body)

        def do_GET(self):
            if not hmac.compare_digest(self.headers.get("Authorization", ""),
                                       "Bearer " + secret):
                return self.reply(401)
            parsed = urlsplit(self.path)
            if parsed.path == "/healthz" and not parsed.query and not parsed.fragment:
                return self.reply(200, b'{"ok":true}')
            if parsed.path != "/v1/torrents" or parsed.fragment or len(self.path) > 160:
                return self.reply(404)
            try:
                args = parse_qs(parsed.query, keep_blank_values=True, strict_parsing=True)
            except ValueError:
                return self.reply(400)
            if set(args) != {"imdb_id"} or len(args["imdb_id"]) != 1:
                return self.reply(400)
            imdb = args["imdb_id"][0]
            if not IMDB.fullmatch(imdb):
                return self.reply(400)
            status, body = provider.search(imdb)
            return self.reply(status, body)

        def do_POST(self):
            return self.reply(405)

        def do_HEAD(self):
            return self.reply(405)

    return Handler


class LimitedHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    request_queue_size = 8


def main():
    secret = os.environ.get("MAGNETRA_EZTV_TOKEN", "")
    if not TOKEN.fullmatch(secret):
        raise SystemExit("Missing/invalid MAGNETRA_EZTV_TOKEN (set privately).")
    server = LimitedHTTPServer((BIND, PORT), handler_class(secret, Provider()))
    try:
        server.serve_forever(poll_interval=0.5)
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
