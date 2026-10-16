#!/usr/bin/env python3
"""Magnetra ONE-tunnel authenticated dispatcher, opt-in provider expansion.

Only hardcoded provider paths; the first allowlisted backend is the original
authenticated EZTV gateway on 127.0.0.1:8797. The BTDigg tunnel/8796 and
existing BTDigg route are deliberately not referenced or modified here.
No arbitrary upstream URLs, redirects, external proxy, caching, downloads or
logging of search terms, IMDb IDs, magnet URLs, hashes, bearer tokens or bodies.
"""
from __future__ import annotations

import hmac
import json
import os
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener
# Python -I intentionally excludes the script directory. Import only the pinned
# administrator-owned sibling module; do not load ambient user/site packages.
import sys
from pathlib import Path
PINNED_ROOT = Path(__file__).resolve().parent
if str(PINNED_ROOT) not in sys.path:
    sys.path.insert(0, str(PINNED_ROOT))
from magnetra_html_egress import HtmlEgress

BIND = "127.0.0.1"
PORT = 8798
EZTV_ORIGIN = "http://127.0.0.1:8797"
EZTV_UPSTREAM = EZTV_ORIGIN + "/v1/torrents"
MAX_BYTES = 1_000_000
MAX_THREADS = 8
TIMEOUT = 12
TOKEN = re.compile(r"^[A-Za-z0-9_-]{48,256}$")
IMDB = re.compile(r"^[0-9]{5,12}$")
MAGNET = re.compile(r"^magnet:\?xt=urn:btih:(?:[a-f0-9]{40}|[a-z2-7]{32})(?:&|$)", re.I)

# Fixed route registry: adding an indexer means code review + real provider
# search/detail evidence, never a client-specified URL or host.
ROUTES = frozenset({"/v1/eztvx/torrents", "/v1/oxtorrent/html", "/v1/torrent9/html"})


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def valid_original_eztv(payload: object, imdb: str) -> bool:
    """Preserve exactly the source record identity; reject fabricated results."""
    if not isinstance(payload, dict) or "error" in payload or "errors" in payload:
        return False
    echo = str(payload.get("imdb_id", "")).removeprefix("tt")
    if not echo.isdigit() or int(echo) != int(imdb):
        return False
    total = payload.get("torrents_count")
    if type(total) not in (int, str) or not str(total).isdigit():
        return False
    rows = payload.get("torrents")
    if rows is None:
        return "torrents" not in payload and int(total) == 0
    if not isinstance(rows, list) or len(rows) > 100:
        return False
    if int(total) == 0 and len(rows) > 0:
        return False
    for row in rows:
        if not isinstance(row, dict):
            return False
        row_imdb = str(row.get("imdb_id", "")).removeprefix("tt")
        if not row_imdb.isdigit() or int(row_imdb) != int(imdb):
            return False
        magnet = row.get("magnet_url")
        if not isinstance(magnet, str) or not MAGNET.match(magnet):
            return False
    return True


class EZTVBackend:
    """Allowlisted loopback transport. Never follows HTTP redirects or env proxies."""
    def __init__(self, eztv_token: str, opener=None):
        if not TOKEN.fullmatch(eztv_token):
            raise ValueError("invalid private EZTV gateway credential")
        self._token = eztv_token
        self._opener = opener or build_opener(ProxyHandler({}), NoRedirect())

    def fetch(self, imdb: str) -> tuple[int, bytes]:
        if not IMDB.fullmatch(imdb):
            return 400, b""
        url = EZTV_UPSTREAM + "?" + urlencode({"imdb_id": imdb})
        request = Request(url, method="GET", headers={
            "Authorization": "Bearer " + self._token,
            "Accept": "application/json", "Accept-Encoding": "identity"
        })
        try:
            with self._opener.open(request, timeout=TIMEOUT) as result:
                if result.status != 200:
                    return 502, b""
                if "application/json" not in result.headers.get("content-type", "").lower():
                    return 502, b""
                if int(result.headers.get("content-length") or 0) > MAX_BYTES:
                    return 502, b""
                body = result.read(MAX_BYTES + 1)
                if len(body) > MAX_BYTES:
                    return 502, b""
                try:
                    payload = json.loads(body)
                except (ValueError, UnicodeError):
                    return 502, b""
                if not valid_original_eztv(payload, imdb):
                    return 502, b""
                return 200, body
        except HTTPError as exc:
            try:
                return (exc.code if exc.code in (401, 403, 429, 504) else 502), b""
            finally:
                exc.close()
        except (URLError, OSError, TimeoutError):
            return 504, b""


def handler_class(hub_token: str, eztv: EZTVBackend, html=None):
    if not TOKEN.fullmatch(hub_token):
        raise ValueError("invalid central gateway credential")

    class Handler(BaseHTTPRequestHandler):
        server_version = "MagnetraGateway/1.0"
        sys_version = ""

        def log_message(self, fmt, *args):
            return  # no request URL, IMDb, tokens, response details in journald

        def reply(self, code: int, body: bytes = b"", content_type="application/json"):
            self.send_response(code)
            self.send_header("content-type", content_type)
            self.send_header("cache-control", "private, no-store")
            self.send_header("x-content-type-options", "nosniff")
            self.send_header("content-length", str(len(body)))
            self.end_headers()
            if body:
                self.wfile.write(body)

        def do_GET(self):
            if not hmac.compare_digest(self.headers.get("Authorization", ""),
                                       "Bearer " + hub_token):
                return self.reply(401)
            if len(self.path) > 350:
                return self.reply(404)
            parts = urlsplit(self.path)
            if parts.fragment or parts.scheme or parts.netloc:
                return self.reply(404)
            if parts.path == "/healthz" and not parts.query:
                return self.reply(200, b'{"ok":true,"service":"magnetra-gateway"}')
            if parts.path not in ROUTES:
                return self.reply(404)
            try:
                args = parse_qs(parts.query, strict_parsing=True, keep_blank_values=True)
            except ValueError:
                return self.reply(400)
            if parts.path != "/v1/eztvx/torrents":
                if html is None:
                    return self.reply(503)
                if set(args) not in ({"mode", "q"}, {"mode", "path"}):
                    return self.reply(400)
                if any(len(values) != 1 for values in args.values()):
                    return self.reply(400)
                mode = args["mode"][0]
                key = "q" if mode == "search" else "path" if mode == "detail" else None
                if key is None or set(args) != {"mode", key}:
                    return self.reply(400)
                provider = parts.path.split("/")[2]
                status, body = html.fetch(provider, mode, args[key][0])
                return self.reply(status, body if status == 200 else b"",
                                  "text/html; charset=utf-8" if status == 200 else "application/json")
            if len(self.path) > 180 or set(args) != {"imdb_id"} or len(args["imdb_id"]) != 1:
                return self.reply(400)
            imdb = args["imdb_id"][0]
            if not IMDB.fullmatch(imdb):
                return self.reply(400)
            status, body = eztv.fetch(imdb)
            return self.reply(status, body if status == 200 else b"")

        def do_POST(self):
            return self.reply(405)

        def do_HEAD(self):
            return self.reply(405)

    return Handler


class LimitedHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    request_queue_size = 8

    def __init__(self, address, handler):
        self._slots = threading.BoundedSemaphore(MAX_THREADS)
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
    hub_token = os.environ.get("MAGNETRA_GATEWAY_TOKEN", "")
    eztv_token = os.environ.get("MAGNETRA_EZTV_TOKEN", "")
    if not TOKEN.fullmatch(hub_token) or not TOKEN.fullmatch(eztv_token):
        raise SystemExit("Required isolated hub and EZTV gateway credentials absent/invalid")
    if hmac.compare_digest(hub_token, eztv_token):
        raise SystemExit("Central gateway token must differ from existing EZTV token")
    server = LimitedHTTPServer((BIND, PORT),
                               handler_class(hub_token, EZTVBackend(eztv_token), HtmlEgress()))
    try:
        server.serve_forever(poll_interval=0.5)
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
