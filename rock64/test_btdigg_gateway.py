#!/usr/bin/env python3
"""Standard-library tests; no real requests to BTDigg and no Rock64 access."""
import http.client
import io
import json
import socket
import importlib.util
import pathlib
import threading
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch
from urllib.error import URLError
from http.server import ThreadingHTTPServer
from urllib.parse import quote

PATH = pathlib.Path(__file__).with_name("btdigg_gateway.py")
SPEC = importlib.util.spec_from_file_location("btdigg_gateway", PATH)
gateway = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gateway)
TOKEN = "t" * 64

class GatewayTests(unittest.TestCase):
    def setUp(self):
        self.now = [100.0]
        self.requests = []
        def upstream(query):
            self.requests.append(query)
            return 200, b"<html><div class=\"one_result\">BTDigg genuine fixture</div></html>"
        self.provider = gateway.SearchProvider(fetcher=upstream, clock=lambda: self.now[0])
        self.server = gateway.LimitedHTTPServer(
            ("127.0.0.1", 0),
            gateway.handler_class(TOKEN, self.provider),
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def call(self, url, token=TOKEN, method="GET"):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        headers = {"Authorization": "Bearer " + token} if token else {}
        connection.request(method, url, headers=headers)
        response = connection.getresponse()
        status, body = response.status, response.read()
        content_type = response.headers.get("content-type")
        connection.close()
        return status, body, content_type

    def test_health_and_reject_unauthorized(self):
        self.assertEqual(self.call("/healthz")[0], 200)
        self.assertEqual(self.call("/healthz", token="")[0], 401)
        self.assertEqual(self.call("/v1/search?q=ubuntu", token="invalid")[0], 401)
        self.assertEqual(self.call("/v1/search?q=ubuntu", method="POST")[0], 405)
        self.assertEqual(self.requests, [])

    def test_allowlist_input_and_cache(self):
        for uri in ["/v1/search", "/v1/search?q=x",
                    "/v1/search?q=a&q=b", "/v1/search?q=x&url=host",
                    "/other?q=ubuntu", "/v1/search?q=%00oops"]:
            self.assertNotEqual(self.call(uri)[0], 200, uri)
        self.assertEqual(self.requests, [])
        first = self.call("/v1/search?q=ubuntu")
        self.assertEqual(first[0], 200)
        self.assertIn(b"BTDigg", first[1])
        self.assertIn("text/html", first[2])
        self.assertEqual(self.call("/v1/search?q=ubuntu")[0], 200)
        self.assertEqual(self.requests, ["ubuntu"], "cached request must not refetch")
        self.assertEqual(self.call("/v1/search?q=debian")[0], 429, "bounded rate")
        self.now[0] += 6
        self.assertEqual(self.call("/v1/search?q=debian")[0], 200)
        self.assertEqual(self.requests, ["ubuntu", "debian"])
        self.now[0] += 6
        romanian = "ț" * 180
        self.assertEqual(self.call("/v1/search?q=" + quote(romanian))[0], 200)
        self.assertEqual(self.requests[-1], romanian)

    def test_upstream_statuses_are_not_disguised(self):
        for status in [429, 503, 504]:
            provider = gateway.SearchProvider(fetcher=lambda q: (status, b""), clock=lambda: 1.0)
            code, content = provider.search("ubuntu")
            self.assertEqual(code, status)
            self.assertEqual(content, b"")

    def test_true_upstream_429_pauses_uncached_requests_without_retry(self):
        calls = []
        def source(query):
            calls.append(query)
            return (429, b"") if len(calls) == 1 else (
                200, b'<div class="one_result">authentic</div>')
        provider = gateway.SearchProvider(fetcher=source, clock=lambda: self.now[0])
        self.assertEqual(provider.search("first"), (429, b""))
        self.assertEqual(provider.rate_limit_remaining_seconds(),
                         gateway.UPSTREAM_429_BACKOFF_SECONDS)
        self.now[0] += gateway.MIN_SEARCH_INTERVAL + 1
        self.assertEqual(provider.search("second"), (429, b""))
        self.assertEqual(calls, ["first"], "no new origin request under rate limit")
        self.now[0] += gateway.UPSTREAM_429_BACKOFF_SECONDS - gateway.MIN_SEARCH_INTERVAL - 2
        self.assertEqual(provider.search("third"), (429, b""))
        self.assertEqual(calls, ["first"])
        self.now[0] += 2
        self.assertEqual(provider.search("second")[0], 200)
        self.assertEqual(calls, ["first", "second"])

    def test_cached_genuine_html_remains_available_during_remote_429(self):
        calls = []
        def source(q):
            calls.append(q)
            if q == "good":
                return (200, b'<div class="one_result">genuine result</div>')
            return (429, b"")
        provider = gateway.SearchProvider(fetcher=source, clock=lambda: self.now[0])
        self.assertEqual(provider.search("good")[0], 200)
        self.now[0] += 6
        self.assertEqual(provider.search("limited"), (429, b""))
        self.assertEqual(provider.search("good")[0], 200)
        self.assertEqual(calls, ["good", "limited"],
                         "only genuine positive response can be served from cache")
        self.assertEqual(provider.search("uncached"), (429, b""))
        self.assertEqual(len(calls), 2)

    def test_local_five_second_limit_does_not_invent_upstream_429_cooldown(self):
        provider = gateway.SearchProvider(
            fetcher=lambda q: (200, b'<div class="one_result">ok</div>'),
            clock=lambda: self.now[0])
        self.assertEqual(provider.search("good")[0], 200)
        self.assertEqual(provider.search("other"), (429, b""))
        self.assertEqual(provider.rate_limit_remaining_seconds(),
                         gateway.MIN_SEARCH_INTERVAL)
        self.now[0] += gateway.MIN_SEARCH_INTERVAL + 1
        self.assertEqual(provider.search("other")[0], 200)

    def test_multiple_queries_bounded_lru_and_expiration(self):
        self.assertEqual(self.provider.search("ubuntu")[0], 200)
        self.now[0] += 6
        self.assertEqual(self.provider.search("debian")[0], 200)
        self.assertEqual(self.provider.search("ubuntu")[0], 200)
        self.assertEqual(self.requests, ["ubuntu", "debian"],
                         "cached hit must not use another upstream request")
        for i in range(gateway.CACHE_MAX_ENTRIES):
            self.now[0] += 6
            self.assertEqual(self.provider.search("extra"+str(i))[0], 200)
        self.assertLessEqual(len(self.provider._cache), gateway.CACHE_MAX_ENTRIES)
        self.assertLessEqual(self.provider._cache_bytes, gateway.CACHE_MAX_BYTES)
        # ubuntu must have been evicted by the LRU bound.
        self.now[0] += 6
        self.assertEqual(self.provider.search("ubuntu")[0], 200)
        self.assertEqual(self.requests.count("ubuntu"), 2)
        self.now[0] += gateway.CACHE_SECONDS + 1
        self.assertEqual(self.provider.search("ubuntu")[0], 200)
        self.assertEqual(self.requests.count("ubuntu"), 3,
                         "expired HTML must not be represented as fresh")

    def test_same_query_inflight_shares_one_real_request(self):
        started = threading.Event()
        release = threading.Event()
        calls = []
        def slow_fetch(query):
            calls.append(query)
            started.set()
            self.assertTrue(release.wait(2), "test upstream was not released")
            return 200, b'<div class="one_result"><div>Ubuntu</div></div>'
        provider = gateway.SearchProvider(fetcher=slow_fetch, clock=lambda: 100.0)
        results = []
        first = threading.Thread(target=lambda: results.append(provider.search("ubuntu")))
        second = threading.Thread(target=lambda: results.append(provider.search("ubuntu")))
        first.start()
        self.assertTrue(started.wait(1))
        second.start()
        self.assertEqual(provider.search("different")[0], 429,
                         "other queries must not enter the active upstream fetch")
        release.set()
        first.join(2)
        second.join(2)
        self.assertFalse(first.is_alive())
        self.assertFalse(second.is_alive())
        self.assertEqual(calls, ["ubuntu"])
        self.assertEqual([s for s, _ in results], [200, 200])

    def test_no_cache_for_rate_limit_or_empty_rows_and_no_retry(self):
        statuses = [429, 200, 200]
        calls = []
        def upstream(query):
            status = statuses[len(calls)]
            calls.append(query)
            return (status, b'<div class="one_result">genuine</div>' if status == 200
                    else b"")
        provider = gateway.SearchProvider(fetcher=upstream, clock=lambda: self.now[0])
        self.assertEqual(provider.search("ubuntu")[0], 429)
        self.assertEqual(calls, ["ubuntu"], "429 cannot trigger automatic retries")
        self.now[0] += 6
        self.assertEqual(provider.search("ubuntu")[0], 200)
        self.assertEqual(provider.search("ubuntu")[0], 200)
        self.assertEqual(calls, ["ubuntu", "ubuntu"])
        empty = gateway.SearchProvider(fetcher=lambda q:(200,b"<html>No results</html>"),
                                       clock=lambda: self.now[0])
        self.assertEqual(empty.search("ubuntu")[0], 200)
        self.assertFalse(empty._cache, "empty or challenge-like HTML cannot be cached")


    @staticmethod
    def _simulated_connection(status=200, body=b'<div class="one_result">ok</div>',
                              tcp_error=None, tls_error=None, header_error=None):
        """All tests remain offline; no real source/DNS/network use."""
        actions = []
        class Socket:
            def __enter__(self): return self
            def __exit__(self, *_): self.close()
            def close(self): actions.append(("close",))
            def settimeout(self, seconds):
                actions.append(("timeout", round(seconds, 3)))
            def connect(self, address):
                actions.append(("tcp_connect", address))
                if tcp_error: raise tcp_error
        sock = Socket()
        class Context:
            def set_alpn_protocols(self, values):
                actions.append(("alpn", tuple(values)))
            def wrap_socket(self, raw, server_hostname):
                actions.append(("tls", server_hostname))
                assert raw is sock
                if tls_error: raise tls_error
                return sock
        class Reply:
            def __init__(self):
                self.status = status
                self.headers = {"content-type": "text/html"}
            def read(self, length):
                actions.append(("read", length))
                return body
        class Connection:
            sock = None
            def request(self, method, path, headers):
                actions.append(("request", method, path, dict(headers)))
            def getresponse(self):
                actions.append(("headers",))
                if header_error: raise header_error
                return Reply()
            def close(self): actions.append(("http_close",))
        patches = [
            patch.object(gateway.socket, "getaddrinfo",
                return_value=[
                    (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP,
                     "", ("192.0.2.15", 443)),
                    (socket.AF_INET6, socket.SOCK_STREAM, socket.IPPROTO_TCP,
                     "", ("2001:db8::5", 443, 0, 0))]),
            patch.object(gateway.socket, "socket", return_value=sock),
            patch.object(gateway.ssl, "create_default_context", return_value=Context()),
            patch.object(gateway.http.client, "HTTPConnection", return_value=Connection()),
        ]
        return patches, actions

    def _one_upstream(self, query="ubuntu", **kwargs):
        patches, actions = self._simulated_connection(**kwargs)
        output = io.StringIO()
        with patches[0], patches[1], patches[2], patches[3]:
            with redirect_stdout(output):
                status, body = gateway.SearchProvider.fetch(query)
        return status, body, actions, json.loads(output.getvalue())

    def test_single_ipv4_tls_verified_http_request_bounded_and_private(self):
        status, body, events, record = self._one_upstream(
            "private search phrase")
        self.assertEqual((status, body),
                         (200, b'<div class="one_result">ok</div>'))
        tcp = [x for x in events if x[0] == "tcp_connect"]
        self.assertEqual(tcp, [("tcp_connect", ("192.0.2.15", 443))],
                         "one TCP connection only, IPv4 only, no IP hopping")
        self.assertIn(("tls", "btdig.com"), events, "SNI/hostname must stay fixed")
        self.assertIn(("alpn", ("http/1.1",)), events)
        requests = [x for x in events if x[0] == "request"]
        self.assertEqual(len(requests), 1, "never retry upstream search")
        self.assertEqual(requests[0][:2], ("request", "GET"))
        self.assertEqual(requests[0][2], "/search?q=private%20search%20phrase")
        self.assertEqual(requests[0][3]["Accept-Encoding"], "identity")
        self.assertIn(("read", gateway.SIZE_LIMIT + 1), events)
        self.assertTrue(all(0 < x[1] <= gateway.TIMEOUT_SECONDS
                            for x in events if x[0] == "timeout"))
        self.assertEqual(record["family"], "IPv4")
        self.assertEqual(record["failure"], "none")
        self.assertIsInstance(record["dns_ms"], int)
        self.assertIsInstance(record["tcp_ms"], int)
        self.assertIsInstance(record["tls_ms"], int)
        self.assertIsInstance(record["open_ms"], int)
        serialized = json.dumps(record)
        for secret in ("private search phrase", "192.0.2.15",
                       "btdig.com", "2001:db8::5", "magnet"):
            self.assertNotIn(secret, serialized)

    def test_dns_failure_remains_sanitized_and_never_connects(self):
        actions = []
        out = io.StringIO()
        with (patch.object(gateway.socket, "getaddrinfo",
                           side_effect=socket.gaierror(-2, "sensitive DNS detail")),
              patch.object(gateway.socket, "socket",
                           side_effect=lambda *a: actions.append(a))):
            with redirect_stdout(out):
                status, body = gateway.SearchProvider.fetch("private search phrase")
        self.assertEqual((status, body), (504, b""))
        record = json.loads(out.getvalue())
        self.assertEqual(record["failure"], "dns")
        self.assertIsNone(record["open_ms"])
        self.assertIsNone(record["read_ms"])
        self.assertEqual(actions, [])
        self.assertNotIn("private search phrase", out.getvalue())
        self.assertNotIn("sensitive DNS detail", out.getvalue())

    def test_tcp_timeout_stops_before_tls_and_http(self):
        status, body, events, rec = self._one_upstream(
            tcp_error=socket.timeout("TCP secret address error"))
        self.assertEqual((status, body), (504, b""))
        self.assertEqual(rec["failure"], "tcp_timeout")
        self.assertFalse(any(x[0] in ("tls", "request", "headers") for x in events))
        self.assertIsNone(rec["open_ms"])

    def test_tls_verification_failure_stops_before_http(self):
        status, body, events, rec = self._one_upstream(
            tls_error=gateway.ssl.SSLCertVerificationError(
                "invalid CA; sensitive details"))
        self.assertEqual((status, body), (504, b""))
        self.assertEqual(rec["failure"], "tls")
        self.assertFalse(any(x[0] == "request" for x in events))
        self.assertIsNone(rec["open_ms"])

    def test_response_header_timeout_is_bounded_and_classified(self):
        status, body, events, rec = self._one_upstream(
            header_error=socket.timeout("no response headers"))
        self.assertEqual((status, body), (504, b""))
        self.assertEqual(rec["failure"], "headers_timeout")
        self.assertEqual(sum(x[0] == "request" for x in events), 1)
        self.assertIsNone(rec["open_ms"])

    def test_http_429_and_redirect_are_never_followed_or_hidden(self):
        for source_status, expected in ((429,429), (302,503), (403,503)):
            with self.subTest(status=source_status):
                code, body, events, rec = self._one_upstream(
                    status=source_status)
                self.assertEqual((code, body), (expected, b""))
                self.assertEqual(sum(x[0] == "request" for x in events), 1)
                self.assertEqual(sum(x[0] == "read" for x in events), 0)
                self.assertEqual(rec["failure"],
                                 "http_429" if source_status == 429
                                 else "http_upstream")

    def test_challenge_and_oversized_html_never_enter_success_cache(self):
        for body, expected in (
            (b"<html>Just a moment</html>", 503),
            (b"x" * (gateway.SIZE_LIMIT + 1), 502),
        ):
            with self.subTest(length=len(body)):
                status, content, events, record = self._one_upstream(body=body)
                self.assertEqual((status, content), (expected, b""))
                self.assertNotEqual(record["failure"], "none")

    def test_real_fetch_url_is_fixed(self):
        # A static contract check: arbitrary URLs cannot be influenced by request.
        self.assertEqual(gateway.HOST, "https://btdig.com")
        self.assertEqual(gateway.BIND, "127.0.0.1")
        self.assertGreaterEqual(gateway.MIN_SEARCH_INTERVAL, 5)
        self.assertEqual(gateway.LimitedHTTPServer.request_queue_size, 16)

if __name__ == "__main__":
    unittest.main()
