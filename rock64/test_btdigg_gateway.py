#!/usr/bin/env python3
"""Standard-library tests; no real requests to BTDigg and no Rock64 access."""
import http.client
import importlib.util
import pathlib
import threading
import unittest
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
            return 200, b"<html>BTDigg genuine fixture</html>"
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

    def test_real_fetch_url_is_fixed(self):
        # A static contract check: arbitrary URLs cannot be influenced by request.
        self.assertEqual(gateway.HOST, "https://btdig.com")
        self.assertEqual(gateway.BIND, "127.0.0.1")
        self.assertGreaterEqual(gateway.MIN_SEARCH_INTERVAL, 5)
        self.assertEqual(gateway.LimitedHTTPServer.request_queue_size, 16)

if __name__ == "__main__":
    unittest.main()
