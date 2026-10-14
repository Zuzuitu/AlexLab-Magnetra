#!/usr/bin/env python3
"""EZTV gateway tests: local loopback only; fake upstream, no torrents downloaded."""
import http.client
import importlib.util
import json
import pathlib
import threading
import unittest

P = pathlib.Path(__file__).with_name("eztv_gateway.py")
spec = importlib.util.spec_from_file_location("eztv_gateway", P)
gateway = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gateway)
SECRET = "s" * 64


def data(imdb="460681", count=0):
    return json.dumps({"imdb_id": imdb, "torrents_count": count, "limit": 100,
                       "page": 1}).encode()


class ValidationTests(unittest.TestCase):
    def test_live_observed_absent_torrents_zero_count(self):
        payload = json.loads(data())
        self.assertTrue(gateway.validate_payload(payload, "460681"))
        self.assertFalse(gateway.validate_payload(payload, "460682"))
        for broken in [
            {"imdb_id": "460681", "torrents_count": 3},
            {"imdb_id": "460681", "torrents_count": 0, "torrents": None},
            {"imdb_id": "460681", "torrents_count": 0, "error": "upstream error"},
            {"imdb_id": "460681", "torrents_count": 0, "torrents": "bad"},
            {"imdb_id": "460681", "torrents_count": 0, "torrents": [] , "errors":[]},
            {"imdb_id": "460681", "torrents_count": 1,
             "torrents": [{"imdb_id": "999999", "title": "unrelated"}]},
            {"imdb_id": "460681", "torrents_count": 0, "torrents": [{}] * 101},
        ]:
            self.assertFalse(gateway.validate_payload(broken, "460681"), broken)

    def test_verified_row_imdb_and_unchanged_magnet_metadata(self):
        h = "a" * 40
        fixture = {"imdb_id": "460681", "torrents_count": 15, "limit": 100,
                   "page": 1,
                   "torrents": [{"imdb_id": "460681", "title": "fixture",
                                "hash": h, "magnet_url": "magnet:?xt=urn:btih:" + h}]}
        self.assertTrue(gateway.validate_payload(fixture, "460681"))
        self.assertEqual(len(fixture["torrents"]), 1)
        self.assertEqual(gateway.SOURCE, "https://eztvx.to/api/get-torrents")
        self.assertEqual(gateway.BIND, "127.0.0.1")

    def test_success_cache_bound_no_retry_on_source_error(self):
        clock = [100.]
        calls = []
        def upstream(imdb):
            calls.append(imdb)
            return (200, data(imdb, 0)) if imdb != "999999" else (429, b"")
        p = gateway.Provider(fetcher=upstream, clock=lambda: clock[0])
        self.assertEqual(p.search("460681")[0], 200)
        self.assertEqual(p.search("460681")[0], 200)
        self.assertEqual(calls, ["460681"])
        self.assertEqual(p.search("460682")[0], 429)
        clock[0] += 4
        self.assertEqual(p.search("999999")[0], 429)
        self.assertEqual(p.search("999999")[0], 429)
        self.assertEqual(calls, ["460681", "999999"])
        self.assertNotIn("999999", p.cache)
        clock[0] += 4
        self.assertEqual(p.search("460682")[0], 200)
        clock[0] += gateway.CACHE_TTL + 1
        self.assertEqual(p.search("460681")[0], 200)
        self.assertEqual(calls.count("460681"), 2)


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.lookups = []
        def upstream(imdb):
            self.lookups.append(imdb)
            return 200, data(imdb, 0)
        self.provider = gateway.Provider(fetcher=upstream)
        self.server = gateway.LimitedHTTPServer(
            ("127.0.0.1", 0), gateway.handler_class(SECRET, self.provider))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)

    def get(self, path, token=SECRET, method="GET"):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        headers = {"Authorization": "Bearer " + token} if token else {}
        conn.request(method, path, headers=headers)
        resp = conn.getresponse()
        result = (resp.status, resp.read(), resp.getheader("cache-control"))
        conn.close()
        return result

    def test_auth_and_fixed_route(self):
        self.assertEqual(self.get("/healthz")[0], 200)
        self.assertEqual(self.get("/healthz", token="")[0], 401)
        self.assertEqual(self.get("/v1/torrents?imdb_id=460681", token="bad")[0], 401)
        for path in [
            "/v1/torrents", "/v1/torrents?imdb_id=",
            "/v1/torrents?imdb_id=460681&url=https://evil.example",
            "/v1/torrents?imdb_id=460681&imdb_id=999999",
            "/v1/torrents?imdb_id=tt0460681",
            "/v1/torrents?imdb_id=1",
            "/v1/torrents?imdb_id=%00bad",
            "/v1/torrents?imdb_id=460681#fragment",
            "/wrong?imdb_id=460681",
        ]:
            self.assertNotEqual(self.get(path)[0], 200, path)
        self.assertEqual(self.get("/v1/torrents?imdb_id=460681", method="POST")[0], 405)
        self.assertEqual(self.lookups, [])

    def test_valid_authenticated_query_no_unrelated_proxying(self):
        status, body, cache = self.get("/v1/torrents?imdb_id=460681")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["torrents_count"], 0)
        self.assertIn("no-store", cache)
        self.assertEqual(self.lookups, ["460681"])


if __name__ == "__main__":
    unittest.main()
