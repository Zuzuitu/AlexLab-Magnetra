#!/usr/bin/env python3
"""Private, opt-in residential egress for Magnetra's ORIGINAL BTDigg adapter.

Only fetches the fixed https://btdig.com/search endpoint, never arbitrary URLs.
This service is NOT a DHT crawler or an anti-bot/CAPTCHA bypass. It binds
127.0.0.1 by default; expose only via a separately configured authenticated
Cloudflare Tunnel, with exactly the same high-entropy bearer token on both ends.

Python 3 stdlib only. No external dependencies or sensitive query logging.
"""
from __future__ import annotations

from collections import OrderedDict
import hmac
import http.client
import json
import math
import os
from pathlib import Path
import re
import socket
import ssl
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, quote, urlsplit

BIND = "127.0.0.1"
PORT = 8796
HOST = "https://btdig.com"
HOSTNAME = "btdig.com"
SIZE_LIMIT = 3_000_000
TIMEOUT_SECONDS = 12
# One IPv4 TLS connection for this gateway ONLY; not a system/network override.
# These are per-stage caps, all bounded by the original overall 12s budget.
TCP_CONNECT_SECONDS = 3
TLS_HANDSHAKE_SECONDS = 3
HTTP_IO_SECONDS = 6
# Fresh successful source HTML only. Small, bounded, in-memory LRU (no disk writes).
CACHE_SECONDS = 20 * 60
CACHE_MAX_ENTRIES = 4
CACHE_MAX_BYTES = 6_000_000
MIN_SEARCH_INTERVAL = 5
# A genuine source HTTP 429 pauses all uncached search terms in this single
# Rock64 gateway process; the existing 5-second pacing is not sufficient.
SOURCE_REFUSAL_COOLDOWN_SECONDS = 5 * 60
INFLIGHT_WAIT_SECONDS = TIMEOUT_SECONDS + 1
SOURCE_UA = (
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36"
)
QUERY_INVALID = re.compile(r"[\x00-\x1f\x7f]")


class SearchProvider:
    def __init__(self, fetcher=None, clock=None):
        self.fetcher = fetcher or self.fetch
        self.clock = clock or time.monotonic
        self._lock = threading.Lock()
        self._last = float("-inf")
        self._source_blocked_until = float("-inf")
        self._cache = OrderedDict()
        self._cache_bytes = 0
        # At most one upstream request at a time. An identical in-flight query
        # can reuse its outcome rather than causing a spurious local 429.
        self._inflight = None

    @staticmethod
    def fetch(query: str) -> tuple[int, bytes]:
        """Single genuine HTTPS request: IPv4 TCP, verified TLS, HTTP/1.1.

        The old urllib opener could spend ~12s before returning even response
        headers, reported only as 'transport'. Here every stage has a small
        ceiling AND shares the original 12s deadline. IPv6 is unreachable on
        this Rock64, but its observed immediate error alone did not prove the
        old timeout's cause; this is a narrowly-scoped transport improvement,
        not a claim that upstream reliability is guaranteed.

        No per-address retries, additional requests, challenge bypass, proxy,
        redirects, suppressed certificate checks or changes to global DNS.
        """
        started = time.monotonic()
        deadline = started + TIMEOUT_SECONDS
        phase = "dns"
        stages = {}
        status = 504
        failure = "none"

        def budget(max_seconds):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("original source deadline reached")
            return min(max_seconds, remaining)

        try:
            # Resolve *only* IPv4 for this one fixed BTDigg hostname.
            # Python's generic urllib/create_connection tries address families
            # using a per-address timeout. We explicitly use one socket and
            # NEVER iterate DNS answers to evade upstream blocks or limits.
            addresses = socket.getaddrinfo(
                HOSTNAME, 443, socket.AF_INET, socket.SOCK_STREAM,
                socket.IPPROTO_TCP)
            stages["dns_ms"] = round((time.monotonic() - started) * 1000)
            if not addresses:
                failure = "dns"
                return 504, b""

            phase = "tcp"
            family, kind, proto, _, address = addresses[0]
            with socket.socket(family, kind, proto) as plain:
                plain.settimeout(budget(TCP_CONNECT_SECONDS))
                plain.connect(address)
                stages["tcp_ms"] = round((time.monotonic() - started) * 1000)

                phase = "tls"
                context = ssl.create_default_context()  # verified CA + SNI
                context.set_alpn_protocols(["http/1.1"])
                plain.settimeout(budget(TLS_HANDSHAKE_SECONDS))
                with context.wrap_socket(plain, server_hostname=HOSTNAME) as secure:
                    stages["tls_ms"] = round((time.monotonic() - started) * 1000)

                    # http.client does not reconnect because the validated
                    # TLS socket is already attached; the origin stays fixed.
                    conn = http.client.HTTPConnection(HOSTNAME, 443)
                    conn.sock = secure
                    try:
                        phase = "headers"
                        secure.settimeout(budget(HTTP_IO_SECONDS))
                        conn.request(
                            "GET", "/search?q=" + quote(query, safe=""),
                            headers={
                                "User-Agent": SOURCE_UA,
                                "Accept": "text/html,application/xhtml+xml",
                                "Accept-Language": "en-US,en;q=0.9",
                                "Accept-Encoding": "identity",
                                "Connection": "close",
                            })
                        response = conn.getresponse()
                        stages["open_ms"] = round((time.monotonic() - started) * 1000)

                        if response.status != 200:
                            # The source's 429 is preserved; other upstream
                            # 3xx/4xx/5xx fail closed without redirect.
                            failure = ("http_429" if response.status == 429
                                       else "http_upstream")
                            return (429 if response.status == 429 else 503), b""
                        if int(response.headers.get("content-length") or 0) > SIZE_LIMIT:
                            failure = "body_size"
                            return 502, b""
                        if "text/html" not in response.headers.get("content-type", "").lower():
                            failure = "content_type"
                            return 502, b""

                        phase = "read"
                        secure.settimeout(budget(HTTP_IO_SECONDS))
                        raw = response.read(SIZE_LIMIT + 1)
                        stages["read_ms"] = round(
                            (time.monotonic() - started) * 1000) - stages["open_ms"]
                        if len(raw) > SIZE_LIMIT:
                            failure = "body_size"
                            return 502, b""
                        if any(x in raw[:2400].lower() for x in
                               (b"cf-mitigated", b"just a moment", b"checking your browser")):
                            failure = "source_challenge"
                            return 503, b""
                        status = 200
                        return status, raw
                    finally:
                        # Closing only a dedicated BTDigg connection; not any
                        # process-global networking facility or another service.
                        conn.close()
        except (TimeoutError, socket.timeout):
            failure = phase + "_timeout"
            return 504, b""
        except socket.gaierror:
            failure = "dns"
            return 504, b""
        except ssl.SSLError:
            failure = "tls"
            return 504, b""
        except (OSError, ValueError, http.client.HTTPException):
            failure = phase + "_transport"
            return 504, b""
        finally:
            # No query/URL/IP/token/certificate/exceptions in logs. Phase
            # timings are elapsed from start (except body read duration).
            # Used for read-only before/after diagnosis on the physical host.
            print(json.dumps({
                "event": "btdigg_upstream_timing",
                "total_ms": round((time.monotonic() - started) * 1000),
                "open_ms": stages.get("open_ms"),
                "read_ms": stages.get("read_ms"),
                "failure": failure,
                "dns_ms": stages.get("dns_ms"),
                "tcp_ms": stages.get("tcp_ms"),
                "tls_ms": stages.get("tls_ms"),
                "family": "IPv4",
            }), flush=True)

    def _prune(self, now):
        expired = [q for q, (_, timestamp) in self._cache.items()
                   if now - timestamp >= CACHE_SECONDS]
        for q in expired:
            html, _ = self._cache.pop(q)
            self._cache_bytes -= len(html)

    def _remember(self, query, html, now):
        # Never cache error bodies or apparent zero-result/challenge documents.
        if not html or b"one_result" not in html.lower():
            return
        if query in self._cache:
            old, _ = self._cache.pop(query)
            self._cache_bytes -= len(old)
        self._cache[query] = (html, now)
        self._cache_bytes += len(html)
        while (len(self._cache) > CACHE_MAX_ENTRIES or
               self._cache_bytes > CACHE_MAX_BYTES):
            _, (old, _) = self._cache.popitem(last=False)
            self._cache_bytes -= len(old)

    def source_retry_after_seconds(self) -> int:
        """Sanitized local deadline for HTTP Retry-After, never contacts origin."""
        with self._lock:
            remaining = self._source_blocked_until - self.clock()
            if not math.isfinite(remaining) or remaining <= 0:
                return 0
            return math.ceil(remaining)

    def search(self, query: str) -> tuple[int, bytes]:
        with self._lock:
            now = self.clock()
            self._prune(now)
            cached = self._cache.get(query)
            if cached is not None:
                self._cache.move_to_end(query)
                return 200, cached[0]
            # A source-confirmed refusal is independent of the per-query
            # five-second pacing. Previously authenticated positive HTML
            # remains available for the exact query without new navigation.
            if now < self._source_blocked_until:
                return 429, b""
            ongoing = self._inflight
            if ongoing is not None:
                if ongoing["query"] != query:
                    return 429, b""
                # The first request owns the upstream fetch; the waiter does
                # not consume another BTDigg request or bypass its rate limits.
                owner = False
            elif now - self._last < MIN_SEARCH_INTERVAL:
                return 429, b""
            else:
                owner = True
                ongoing = {"query": query, "event": threading.Event(),
                           "status": 504, "body": b""}
                self._inflight = ongoing
                self._last = now
        if not owner:
            if ongoing["event"].wait(INFLIGHT_WAIT_SECONDS):
                return ongoing["status"], ongoing["body"]
            return 504, b""

        status, html = 504, b""
        try:
            status, html = self.fetcher(query)
            if status != 200 or not html or len(html) > SIZE_LIMIT:
                html = b""
                if status == 200:
                    status = 502
        except Exception:
            # Keep secrets/queries out of errors. Always wake waiting threads.
            status, html = 504, b""
        finally:
            with self._lock:
                if status == 200:
                    self._prune(self.clock())
                    self._remember(query, html, self.clock())
                elif status == 429:
                    # Only the actual fetcher can establish a source block.
                    # Local 5-second pacing/inflight 429 exits before here.
                    self._source_blocked_until = max(
                        self._source_blocked_until,
                        self.clock() + SOURCE_REFUSAL_COOLDOWN_SECONDS,
                    )
                ongoing["status"] = status
                ongoing["body"] = html
                self._inflight = None
                ongoing["event"].set()
        return status, html

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
                # The gateway generates short local-pacing 429 responses as
                # well as genuine upstream refusals. Make the distinction
                # explicit for the authenticated Worker; never misstate a
                # five-second local pace as a source-wide refusal.
                source_remaining = provider.source_retry_after_seconds()
                self.send_header(
                    "retry-after",
                    str(max(MIN_SEARCH_INTERVAL, source_remaining)),
                )
                self.send_header(
                    "x-magnetra-btdigg-429-scope",
                    "source" if source_remaining else "local-pacing",
                )
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


# Optional owner-authorized hop from the EXISTING production loopback gateway
# to the separate, human-verified persistent Chromium session. OFF by default.
# The browser is not launched, refreshed, restarted, verified, or modified here.
BROWSER_PRIVATE_PORT = 18896
BROWSER_CREDENTIAL_NAME = "browser_token"
BROWSER_BRIDGE_FLAG = "MAGNETRA_BTDIGG_CHROMIUM_BRIDGE"
BROWSER_STATE_LIMIT = 4096

def browser_state_ready(state):
    """Require one safely verified tab. Older single-tab browser is accepted
    only if no in-process navigation refusal was recorded; never allow legacy
    multi-tab sessions because their visible 429 detection is unavailable.
    """
    if not isinstance(state, dict) or (
        state.get("browser_connected") is not True
        or type(state.get("verified_tabs")) is not int
        or state["verified_tabs"] < 1
        or state.get("selected_tab_verified") is not True
    ):
        return False
    if (state.get("visible_source_rate_limited") is False
            and state.get("new_searches_paused") is False):
        return True
    return (
        "visible_source_rate_limited" not in state
        and type(state.get("open_tabs")) is int
        and state["open_tabs"] == 1
        and state["verified_tabs"] == 1
        and state.get("new_searches_paused") is False
        and state.get("last_navigation_status") is None
    )


class LocalChromiumBridge:
    """Fixed localhost HTTP transport; independent browser bearer credential."""

    def __init__(self, browser_token):
        if not re.fullmatch(r"[A-Za-z0-9_-]{48,256}", browser_token or ""):
            raise ValueError("invalid isolated browser credential")
        self._token = browser_token

    def _read(self, path, accept, limit, timeout):
        conn = http.client.HTTPConnection("127.0.0.1", BROWSER_PRIVATE_PORT, timeout=timeout)
        try:
            conn.request("GET", path, headers={
                "authorization": "Bearer " + self._token,
                "accept": accept,
                "connection": "close",
            })
            response = conn.getresponse()
            status = response.status
            mime = response.getheader("content-type") or ""
            scope = response.getheader("x-magnetra-btdigg-429-scope") or ""
            size = response.getheader("content-length")
            if size is not None and (not size.isdecimal() or int(size) > limit):
                return 502, b"", mime, scope
            body = response.read(limit + 1)
            if len(body) > limit:
                return 502, b"", mime, scope
            return status, body, mime, scope
        finally:
            conn.close()

    def fetch(self, query):
        # Each actual PWA search requires an already verified BTDigg tab.
        # This first call is local and read-only; never creates source traffic.
        try:
            status, body, mime, _ = self._read(
                "/v1/browser-state", "application/json", BROWSER_STATE_LIMIT, 3
            )
            if status != 200 or "application/json" not in mime:
                return 503, b""
            state = json.loads(body)
            if not browser_state_ready(state):
                # A stale 429 page, unverified tab, refused navigation or
                # ambiguous legacy multi-tab session cannot reach the source.
                return 503, b""
            path = "/v1/search?q=" + quote(query, safe="")
            status, html, mime, scope = self._read(
                path, "text/html", SIZE_LIMIT, 11
            )
            if status == 429:
                # A 5-second *local* denial by the browser process must not
                # create the production gateway's five-minute source lock.
                return (503 if scope == "local-pacing" else 429), b""
            if status != 200:
                return (504 if status == 504 else 503), b""
            if "text/html" not in mime.lower():
                return 502, b""
            if b"one_result" not in html.lower() or (
                b"magnet:?xt=urn:btih:" not in html.lower()
            ):
                return 502, b""
            return 200, html
        except (OSError, ValueError, TypeError, http.client.HTTPException,
                UnicodeError):
            # Never expose local credentials or source URLs in logs/errors.
            return 504, b""


def chromium_bridge_from_environment():
    mode = os.environ.get(BROWSER_BRIDGE_FLAG, "")
    if mode in ("", "0"):
        return None
    if mode != "1":
        raise SystemExit("STOP: invalid explicit Chromium bridge flag")
    credentials_directory = os.environ.get("CREDENTIALS_DIRECTORY", "")
    if not credentials_directory or not os.path.isabs(credentials_directory):
        raise SystemExit("STOP: missing private systemd credential directory")
    base = Path(credentials_directory)
    token_path = base / BROWSER_CREDENTIAL_NAME
    try:
        if base.is_symlink() or token_path.is_symlink():
            raise ValueError("credential symlink")
        if not token_path.is_file() or token_path.stat().st_size > 300:
            raise ValueError("invalid credential size")
        token = token_path.read_text(encoding="ascii").strip()
        return LocalChromiumBridge(token)
    except (OSError, ValueError, UnicodeError):
        raise SystemExit("STOP: private browser credential unavailable") from None


def main():
    token = os.environ.get("MAGNETRA_BTDIGG_TOKEN", "")
    if len(token) < 48 or len(token) > 256 or not re.fullmatch(r"[A-Za-z0-9_-]+", token):
        raise SystemExit("Set a strong MAGNETRA_BTDIGG_TOKEN (48-256 URL-safe characters).")
    # Explicit no-port-forward and no LAN listener. Use Cloudflare Tunnel -> localhost.
    browser_bridge = chromium_bridge_from_environment()
    provider = SearchProvider(fetcher=browser_bridge.fetch) if browser_bridge else SearchProvider()
    server = LimitedHTTPServer((BIND, PORT), handler_class(token, provider))
    print("Magnetra BTDigg gateway bound to 127.0.0.1:%d (private); no public listener." % PORT, flush=True)
    try:
        server.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
