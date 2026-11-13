#!/usr/bin/env python3
"""Offline CI guards for opt-in isolated Chromium fixture integration.

This suite never launches Chromium, contacts BTDigg or reads the live profile.
The real browser/DOM smoke is separately owner-triggered with isolated venv.
"""
import ast
from http.server import BaseHTTPRequestHandler, HTTPServer
import importlib.util
from pathlib import Path
from unittest import TestCase, main

SCRIPT = Path(__file__).with_name("check-btdigg-offline-chromium-path.py")
SPEC = importlib.util.spec_from_file_location(
    "rock64.check_btdigg_offline_chromium_path", SCRIPT
)
MODULE = importlib.util.module_from_spec(SPEC)
MODULE.__package__ = "rock64"
SPEC.loader.exec_module(MODULE)


class LocalOnlyChromiumPathTests(TestCase):
    def test_source_syntax_and_no_network_fallback(self):
        source = SCRIPT.read_text(encoding="utf-8")
        ast.parse(source, filename=str(SCRIPT))
        self.assertIn('context.route("**/*", fulfill_fixture)', source)
        self.assertIn('route.abort("blockedbyclient")', source)
        self.assertIn("route.fulfill(status=429", source)
        self.assertIn("route.fulfill(status=200", source)
        self.assertIn('service_workers="block"', source)
        self.assertIn('"--disable-background-networking"', source)
        self.assertIn("tempfile.TemporaryDirectory", source)
        self.assertIn("headless=True", source)
        self.assertIn("chromium_sandbox=True", source)
        self.assertIn('("127.0.0.1", 0)', source)
        self.assertIn('TEST_TOKEN = "t" * 64', source)
        self.assertIn("server.handle_request()", source)
        self.assertIn("original_dom = validated_result_html(page)", source)
        for forbidden in [
            "route.continue_", "route.fallback", "connect_over_cdp",
            "connect_over_cdp(", "requests.get(", "urllib.request.urlopen(",
            "subprocess.run(", "browser.launch(", "os.system(",
            "sudo ", "--no-sandbox", "--remote-debugging-port",
            "MAGNETRA_BROWSER_PROFILE", "MAGNETRA_BTDIGG_TOKEN",
            "100.79.", "192.168.", ".X11-unix", "x11vnc",
            "cloudflared", "wrangler deploy",
        ]:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)

    def test_fixture_is_structural_only_not_claimed_as_live_search(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertEqual(len(MODULE.FAKE_HASH), 40)
        self.assertEqual(set(MODULE.FAKE_HASH), {"a"})
        self.assertIn("one_result", MODULE.FIXTURE_HTML)
        self.assertIn("torrent_name", MODULE.FIXTURE_HTML)
        self.assertIn("torrent_magnet", MODULE.FIXTURE_HTML)
        self.assertIn("fa-magnet", MODULE.FIXTURE_HTML)
        self.assertIn(MODULE.EXACT, MODULE.FIXTURE_HTML)
        self.assertIn("synthetic_fixture_not_source_availability", source)
        self.assertIn('"requests_to_btdigg_origin": 0', source)
        self.assertNotIn("I'm not a robot", source)

    def test_local_client_and_httpserver_are_same_thread_as_browser(self):
        class LocalHandler(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass
            def do_GET(self):
                if self.headers.get("Authorization") == "Bearer " + MODULE.TEST_TOKEN:
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"fixture-only")
                else:
                    self.send_response(401)
                    self.end_headers()

        server = HTTPServer(("127.0.0.1", 0), LocalHandler)
        server.timeout = 3
        try:
            status, body, retry, scope = MODULE.one_local_http_request(
                server, "/v1/search?q=test")
            self.assertEqual((status, body, retry, scope),
                             (200, b"fixture-only", None, None))
            status, body, _, _ = MODULE.one_local_http_request(
                server, "/v1/search?q=test", bearer="wrong")
            self.assertEqual(status, 401)
        finally:
            server.server_close()


if __name__ == "__main__":
    main()
