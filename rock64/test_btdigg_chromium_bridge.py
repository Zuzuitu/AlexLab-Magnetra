#!/usr/bin/env python3
"""Offline 8796 -> 18896 Chromium bridge tests; synthetic responses only."""
from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from rock64 import btdigg_gateway as gw

SECRET = "b" * 64
HTML = (
    '<html><div class="one_result"><div class="torrent_name">'
    '<a href="/torrent/source-fixture">The.Dog.Stars.2026.1080p.10bit.x265-PSA</a>'
    '</div><div class="torrent_magnet"><a href="magnet:?xt=urn:btih:'
    + "a"*40 + '">Magnet</a></div></div></html>'
).encode("ascii")

def good_state():
    return {
        "browser_connected": True,
        "open_tabs": 1,
        "verified_tabs": 1,
        "selected_tab_verified": True,
        "visible_source_rate_limited": False,
        "new_searches_paused": False,
        "last_navigation_status": None,
    }

class FakeBrowserHandler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        return
    def do_GET(self):
        self.server.visits.append(urlsplit(self.path).path)
        if self.headers.get("authorization") != "Bearer " + SECRET:
            self.send_response(401)
            self.end_headers()
            return
        path=urlsplit(self.path).path
        if path=="/v1/browser-state":
            status=200
            body=json.dumps(self.server.state).encode("utf8")
            mime="application/json"
        elif path=="/v1/search":
            self.server.searches.append(
                parse_qs(urlsplit(self.path).query).get("q", [None])[0]
            )
            status=self.server.search_status
            body=HTML if status==200 else b""
            mime="text/html" if status==200 else "application/json"
        else:
            status=404
            body=b""
            mime="application/json"
        self.send_response(status)
        self.send_header("content-type",mime)
        self.send_header("content-length",str(len(body)))
        if status==429:
            self.send_header("x-magnetra-btdigg-429-scope",
                             self.server.scope)
        self.end_headers()
        self.wfile.write(body)

class ChromiumBridgeContract(unittest.TestCase):
    def setUp(self):
        self.server=ThreadingHTTPServer(("127.0.0.1",0),FakeBrowserHandler)
        self.server.state=good_state()
        self.server.visits=[]
        self.server.searches=[]
        self.server.search_status=200
        self.server.scope="source"
        self.thread=threading.Thread(target=self.server.serve_forever,
                                     daemon=True)
        self.thread.start()
        self.port_patch=patch.object(gw,"BROWSER_PRIVATE_PORT",
                                     self.server.server_port)
        self.port_patch.start()
        self.bridge=gw.LocalChromiumBridge(SECRET)

    def tearDown(self):
        self.port_patch.stop()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(2)

    def test_no_unverified_browser_tab_may_trigger_a_source_search(self):
        for changes in (
            {"verified_tabs":0,"selected_tab_verified":False},
            {"visible_source_rate_limited":True,"new_searches_paused":True},
            {"new_searches_paused":True},
            {"browser_connected":False},
            {"verified_tabs":0},
        ):
            self.server.state={**good_state(),**changes}
            self.assertEqual(self.bridge.fetch("The Dog Stars 2026"),
                             (503,b""))
        self.assertEqual(self.server.searches, [])
        self.assertEqual(self.server.visits, ["/v1/browser-state"]*5)

    def test_legacy_browser_state_is_unknown_not_permission_to_navigate(self):
        self.server.state=good_state()
        self.server.state.pop("visible_source_rate_limited")
        self.server.state.pop("new_searches_paused")
        self.assertEqual(self.bridge.fetch("The Dog Stars 2026"),(503,b""))
        self.assertEqual(self.server.searches, [])

    def test_one_owner_request_reuses_existing_browser_gateway_contract(self):
        provider=gw.SearchProvider(fetcher=self.bridge.fetch,clock=lambda:100.0)
        status,body=provider.search("The Dog Stars 2026")
        self.assertEqual((status,body),(200,HTML))
        self.assertEqual(self.server.searches,["The Dog Stars 2026"])
        self.assertEqual(self.server.visits,
                         ["/v1/browser-state","/v1/search"])
        self.assertEqual(provider.search("The Dog Stars 2026")[0],200)
        self.assertEqual(self.server.searches,["The Dog Stars 2026"],
                         "one authentic fixture stays cached, never repeated")

    def test_real_source_429_gates_new_queries_without_retries(self):
        self.server.search_status=429
        self.server.scope="source"
        provider=gw.SearchProvider(fetcher=self.bridge.fetch,clock=lambda:100.0)
        self.assertEqual(provider.search("The Dog Stars 2026"),(429,b""))
        self.assertEqual(provider.search("Other title 2026"),(429,b""))
        self.assertEqual(self.server.searches,["The Dog Stars 2026"])
        self.assertEqual(provider.source_retry_after_seconds(),300)

    def test_local_pacing_does_not_forge_upstream_source_refusal(self):
        self.server.search_status=429
        self.server.scope="local-pacing"
        provider=gw.SearchProvider(fetcher=self.bridge.fetch,clock=lambda:100.0)
        self.assertEqual(provider.search("The Dog Stars 2026"),(503,b""))
        self.assertEqual(provider.source_retry_after_seconds(),0)
        self.assertEqual(self.server.searches,["The Dog Stars 2026"])

    def test_unexpected_unauthorized_browser_token_cannot_fallback_to_direct(self):
        bridge=gw.LocalChromiumBridge("z"*64)
        self.assertEqual(bridge.fetch("The Dog Stars 2026"),(503,b""))
        self.assertEqual(self.server.searches,[])
        with self.assertRaises(ValueError):
            gw.LocalChromiumBridge("short")

    def test_non_html_or_missing_result_is_not_fabricated_success(self):
        self.server.search_status=200
        with patch.object(gw.LocalChromiumBridge,"_read",
                          side_effect=[(200,json.dumps(good_state()).encode(),
                                        "application/json",""),
                                       (200,b"<html>Challenge</html>",
                                        "text/html","")]):
            self.assertEqual(self.bridge.fetch("The Dog Stars 2026"),(502,b""))

    def test_explicit_systemd_opt_in_and_private_token_required(self):
        with patch.dict("os.environ", {
            gw.BROWSER_BRIDGE_FLAG:"0",
            "CREDENTIALS_DIRECTORY":"/nonexistent",
        }):
            self.assertIsNone(gw.chromium_bridge_from_environment())
        with patch.dict("os.environ",{gw.BROWSER_BRIDGE_FLAG:"yes"}):
            with self.assertRaises(SystemExit):
                gw.chromium_bridge_from_environment()
        with patch.dict("os.environ",{gw.BROWSER_BRIDGE_FLAG:"1",
                                     "CREDENTIALS_DIRECTORY":"/nonexistent"}):
            with self.assertRaises(SystemExit):
                gw.chromium_bridge_from_environment()
        with tempfile.TemporaryDirectory() as directory:
            token=Path(directory)/gw.BROWSER_CREDENTIAL_NAME
            token.write_text(SECRET,encoding="ascii")
            with patch.dict("os.environ",{
                gw.BROWSER_BRIDGE_FLAG:"1",
                "CREDENTIALS_DIRECTORY":directory,
            }):
                self.assertIsInstance(gw.chromium_bridge_from_environment(),
                                      gw.LocalChromiumBridge)
                token.unlink()
                token.symlink_to("/etc/passwd")
                with self.assertRaises(SystemExit):
                    gw.chromium_bridge_from_environment()

if __name__=="__main__":
    unittest.main()
