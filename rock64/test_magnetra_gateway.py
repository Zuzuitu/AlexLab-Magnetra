#!/usr/bin/env python3
"""Offline unit and ephemeral loopback socket tests; no external HTTP requests."""
import http.client
import importlib.util
import io
import json
import pathlib
import socket
import sys
import threading
import unittest
from email.message import Message
from urllib.error import HTTPError, URLError

FILE = pathlib.Path(__file__).with_name("magnetra_gateway.py")
spec = importlib.util.spec_from_file_location("magnetra_dispatcher", FILE)
hub = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = hub
spec.loader.exec_module(hub)
HUB_TOKEN = "H" * 64
EZTV_TOKEN = "E" * 64
ID = "460681"
MAGNET = "magnet:?xt=urn:btih:" + "a" * 40
OK = {"imdb_id": ID, "torrents_count": 1,
      "torrents": [{"imdb_id": ID, "magnet_url": MAGNET, "title": "fixture"}]}
ZERO = {"imdb_id": ID, "torrents_count": 0}


class FakeResponse:
    status = 200

    def __init__(self, data, status=200, content_type="application/json"):
        self.status = status
        self.data = data
        self.headers = Message()
        self.headers["content-type"] = content_type
        self.headers["content-length"] = str(len(data))

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, n):
        return self.data[:n]


class FixtureBackend:
    def __init__(self, result=None):
        self.calls = []
        self.result = result or (200, json.dumps(OK).encode())

    def fetch(self, imdb):
        self.calls.append(imdb)
        return self.result


class GatewayTests(unittest.TestCase):
    def test_allowlist_and_loopback_only(self):
        self.assertEqual(hub.BIND, "127.0.0.1")
        self.assertEqual(hub.PORT, 8798)
        self.assertEqual(hub.ROUTES, frozenset({"/v1/eztvx/torrents"}))
        self.assertEqual(hub.EZTV_UPSTREAM, "http://127.0.0.1:8797/v1/torrents")
        self.assertLessEqual(hub.MAX_THREADS, 8)
        self.assertLessEqual(hub.MAX_BYTES, 1_000_000)
        self.assertLessEqual(hub.TIMEOUT, 12)

    def test_original_exact_imdb_and_magnet_validation(self):
        self.assertTrue(hub.valid_original_eztv(OK, ID))
        self.assertTrue(hub.valid_original_eztv(ZERO, ID))
        self.assertFalse(hub.valid_original_eztv({"imdb_id": ID, "torrents_count": 0,
                     "torrents": [OK["torrents"][0]]}, ID))
        self.assertFalse(hub.valid_original_eztv(
            {"imdb_id": ID, "torrents_count": 1,
             "torrents": [{"imdb_id": "460682", "magnet_url": MAGNET}]}, ID))
        self.assertFalse(hub.valid_original_eztv(
            {"imdb_id": ID, "torrents_count": 1,
             "torrents": [{"imdb_id": ID, "magnet_url": "https://fake.invalid"}]}, ID))
        self.assertFalse(hub.valid_original_eztv(
            {"imdb_id": ID, "torrents_count": 1,
             "torrents": [OK["torrents"][0]], "error": "unexpected"}, ID))
        self.assertFalse(hub.valid_original_eztv(
            {"imdb_id": "999999", "torrents_count": 1, "torrents": [OK["torrents"][0]]}, ID))
        self.assertFalse(hub.valid_original_eztv(
            {"imdb_id": ID, "torrents_count": 1, "torrents": "not-a-list"}, ID))

    def test_eztv_backend_only_calls_fixed_loopback_url(self):
        calls = []

        class Opener:
            def open(self, request, timeout):
                calls.append((request.full_url, timeout,
                              request.headers.get("Authorization"),
                              request.get_method()))
                return FakeResponse(json.dumps(OK).encode())

        status, body = hub.EZTVBackend(EZTV_TOKEN, opener=Opener()).fetch(ID)
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), OK)
        self.assertEqual(calls, [(hub.EZTV_UPSTREAM + "?imdb_id=460681",
                                  12, "Bearer " + EZTV_TOKEN, "GET")])
        self.assertEqual(hub.EZTVBackend(EZTV_TOKEN, opener=Opener()).fetch("bad"),
                         (400, b""))
        self.assertEqual(len(calls), 1)

    def test_backend_suppresses_errors_redirects_and_invalid_json(self):
        for response, expected in [
            (FakeResponse(b"<html>Challenge", content_type="text/html"), 502),
            (FakeResponse(b'{"incorrect": true}'), 502),
            (FakeResponse(json.dumps({"imdb_id": ID, "torrents_count": 0}).encode()), 200),
            (FakeResponse(b"{broken json"), 502),
            (FakeResponse(b"{}", status=302), 502),
        ]:
            class Opener:
                def open(self, request, timeout):
                    return response
            code, body = hub.EZTVBackend(EZTV_TOKEN, opener=Opener()).fetch(ID)
            self.assertEqual(code, expected)
            self.assertEqual(body, response.data if expected == 200 else b"")

        class Forbidden:
            def open(self, request, timeout):
                raise HTTPError(request.full_url, 429, "slow", {}, None)
        self.assertEqual(hub.EZTVBackend(EZTV_TOKEN, opener=Forbidden()).fetch(ID),
                         (429, b""))

        class Down:
            def open(self, request, timeout):
                raise URLError("secret URL never shown")
        self.assertEqual(hub.EZTVBackend(EZTV_TOKEN, opener=Down()).fetch(ID),
                         (504, b""))

    def test_token_validation_rejects_weak(self):
        with self.assertRaises(ValueError):
            hub.handler_class("short", FixtureBackend())
        with self.assertRaises(ValueError):
            hub.EZTVBackend("weak")

    def test_authenticated_loopback_handler_blocks_unknown_paths_and_methods(self):
        provider = FixtureBackend()
        handler = hub.handler_class(HUB_TOKEN, provider)
        server = hub.LimitedHTTPServer(("127.0.0.1", 0), handler)
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        try:
            def req(path, token=None, method="GET"):
                conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=3)
                headers = {} if token is None else {"Authorization": "Bearer " + token}
                conn.request(method, path, headers=headers)
                response = conn.getresponse()
                code = response.status
                data = response.read()
                conn.close()
                return code, data
            self.assertEqual(req("/healthz")[0], 401)
            self.assertEqual(req("/v1/eztvx/torrents?imdb_id=" + ID)[0], 401)
            self.assertEqual(req("/v1/eztvx/torrents?imdb_id=" + ID, "wrong")[0], 401)
            self.assertEqual(req("/healthz", HUB_TOKEN), (200, b'{"ok":true,"service":"magnetra-gateway"}'))
            bad_urls = [
                "/v1/eztvx/torrents?imdb_id=" + ID + "&url=https://evil.invalid",
                "/v1/eztvx/torrents?imdb_id=" + ID + "&imdb_id=123456",
                "/v1/eztvx/torrents?imdb_id=../path",
                "/v1/eztvx/torrents?imdb_id=",
                "/v1/eztvx/torrents?imdb_id=" + ID + "&token=bad",
            ]
            for path in bad_urls:
                self.assertEqual(req(path, HUB_TOKEN)[0], 400)
            self.assertEqual(req("/v1/another-provider/search?q=ubuntu", HUB_TOKEN)[0], 404)
            self.assertEqual(req("/proxy?url=https://example.com", HUB_TOKEN)[0], 404)
            self.assertEqual(req("/v1/eztvx/torrents?imdb_id=" + ID, HUB_TOKEN, "POST")[0], 405)
            self.assertEqual(req("/v1/eztvx/torrents?imdb_id=" + ID, HUB_TOKEN), (200, provider.result[1]))
            self.assertEqual(provider.calls, [ID])
        finally:
            server.shutdown()
            server.server_close()
            t.join(timeout=3)

    def test_rate_limit_and_zero_preserved_without_fallback(self):
        for code, body in [(429, b""), (504, b""), (200, json.dumps(ZERO).encode())]:
            provider = FixtureBackend((code, body))
            server = hub.LimitedHTTPServer(("127.0.0.1", 0),
                                           hub.handler_class(HUB_TOKEN, provider))
            t = threading.Thread(target=server.serve_forever, daemon=True)
            t.start()
            try:
                conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=3)
                conn.request("GET", "/v1/eztvx/torrents?imdb_id=" + ID,
                             headers={"Authorization": "Bearer " + HUB_TOKEN})
                response = conn.getresponse()
                self.assertEqual(response.status, code)
                self.assertEqual(response.read(), body)
                conn.close()
                self.assertEqual(provider.calls, [ID])
            finally:
                server.shutdown()
                server.server_close()
                t.join(timeout=3)


if __name__ == "__main__":
    unittest.main()
