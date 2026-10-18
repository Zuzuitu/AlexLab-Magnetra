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


    def test_upstream_diagnostics_are_sanitized_and_classified(self):
        class FailingOpener:
            def open(self, request, timeout):
                raise URLError(socket.gaierror(-2, "sensitive DNS detail"))

        output = io.StringIO()
        with patch.object(gateway, "build_opener", return_value=FailingOpener()):
            with redirect_stdout(output):
                status, body = gateway.SearchProvider.fetch("private search phrase")
        self.assertEqual((status, body), (504, b""))
        log = output.getvalue()
        self.assertNotIn("private search phrase", log)
        self.assertNotIn("sensitive DNS detail", log)
        self.assertNotIn("btdig.com/search", log)
        record = json.loads(log)
        self.assertEqual(record["event"], "btdigg_upstream_timing")
        self.assertEqual(record["failure"], "dns")
        self.assertIsNone(record["open_ms"])
        self.assertIsNone(record["read_ms"])
        self.assertGreaterEqual(record["total_ms"], 0)

    def test_real_fetch_url_is_fixed(self):
        # A static contract check: arbitrary URLs cannot be influenced by request.
        self.assertEqual(gateway.HOST, "https://btdig.com")
        self.assertEqual(gateway.BIND, "127.0.0.1")
        self.assertGreaterEqual(gateway.MIN_SEARCH_INTERVAL, 5)
        self.assertEqual(gateway.LimitedHTTPServer.request_queue_size, 16)

if __name__ == "__main__":
    unittest.main()
