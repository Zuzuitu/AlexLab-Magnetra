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
        "visible_captcha_required": False,
        "new_searches_paused": False,
        "last_navigation_status": None,
        "last_upstream_http_status": None,
        "selected_tab_index": 0,
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
            {"new_searches_paused":True},
            {"browser_connected":False},
            {"verified_tabs":0},
        ):
            self.server.state={**good_state(),**changes}
            self.assertEqual(self.bridge.fetch("The Dog Stars 2026"),
                             (503,b""))
        self.assertEqual(self.server.searches, [])
        self.assertEqual(self.server.visits, ["/v1/browser-state"]*4)

    def test_visible_human_challenge_enters_one_private_attempt_then_428(self):
        # Private 428 is not upstream 429, and never stores source results.
        self.server.state={**good_state(),"verified_tabs":0,
                           "selected_tab_verified":False,
                           "visible_captcha_required":True,
                           "new_searches_paused":True}
        self.server.search_status=428
        self.assertEqual(self.bridge.fetch("The dog stars 720p"),(428,b""))
        self.assertEqual(self.server.searches,["The dog stars 720p"])
        self.assertEqual(self.server.visits,
                         ["/v1/browser-state","/v1/search"])
        provider=gw.SearchProvider(fetcher=self.bridge.fetch,clock=lambda:100.0)
        self.assertEqual(provider.search("The dog stars 720p"),(428,b""))
        self.assertEqual(provider.source_retry_after_seconds(),0)
        self.assertEqual(self.server.searches,["The dog stars 720p"]*2)

    def test_one_request_can_return_verified_html_after_checkbox(self):
        self.server.state={**good_state(),"verified_tabs":0,
                           "selected_tab_verified":False,
                           "visible_captcha_required":True,
                           "new_searches_paused":True}
        self.assertEqual(self.bridge.fetch("Owner query"),(200,HTML))
        self.assertEqual(self.server.searches,["Owner query"])
        self.assertEqual(self.server.visits,
                         ["/v1/browser-state","/v1/search"])

    def test_ambiguous_captcha_never_enters_private_search_endpoint(self):
        for key,value in (
            ("open_tabs",2),("visible_source_rate_limited",True),
            ("last_upstream_http_status",429),("selected_tab_index",1)):
            with self.subTest(key=key):
                self.server.state={**good_state(),"verified_tabs":0,
                                   "selected_tab_verified":False,
                                   "visible_captcha_required":True,
                                   "new_searches_paused":True,key:value}
                before=len(self.server.searches)
                self.assertEqual(self.bridge.fetch("Owner query"),(428,b""))
                self.assertEqual(len(self.server.searches),before)


    def test_visible_source_refusal_is_soft_425_without_new_navigation(self):
        # HTTP 200 can show a Too Many Requests *page* without network 429.
        # Private 425 is NOT a real 429 and must not start a 5-min lock.
        # No source navigation is performed until a later approved PWA action.
        self.server.state={
            **good_state(), "verified_tabs":0,
            "selected_tab_verified":False,
            "visible_source_rate_limited":True,
            "new_searches_paused":True,
        }
        self.assertEqual(self.bridge.fetch("The Dog Stars 2026"),(425,b""))
        self.assertEqual(self.server.searches,[])
        provider=gw.SearchProvider(fetcher=self.bridge.fetch,clock=lambda:100.0)
        self.assertEqual(provider.search("The Dog Stars 2026"),(425,b""))
        self.assertEqual(provider.source_retry_after_seconds(),0)
        # The local five-second gateway pacing applies to immediate distinct
        # queries, but this does not create an upstream refusal latch.
        self.assertEqual(provider.search("Different query"),(429,b""))
        self.assertEqual(self.server.searches,[])
        self.assertEqual(self.server.visits,["/v1/browser-state"]*2)

    def test_manual_verified_second_tab_may_pass_gateway_without_source_probe(self):
        state={
            **good_state(),
            "open_tabs": 2,
            "verified_tabs": 1,
            "selected_tab_verified": False,
            "visible_source_rate_limited": True,
            "visible_captcha_required": False,
            "new_searches_paused": True,
            "selected_tab_index": 0,
            "last_upstream_http_status": None,
            "tab_diagnostics": [
                {"page_kind":"canonical_search","validation":"no_paired_rows",
                 "paired_rows":0,"title_rows":0,"magnet_rows":0},
                {"page_kind":"canonical_search","validation":"valid",
                 "paired_rows":10,"title_rows":10,"magnet_rows":10},
            ],
        }
        self.server.state=state
        self.assertFalse(gw.browser_state_ready(state))
        self.assertTrue(gw.browser_state_owner_verified_adoption_ready(state))
        self.assertEqual(self.bridge.fetch("The dog stars 720p"),(200,HTML))
        self.assertEqual(self.server.searches,["The dog stars 720p"])
        self.assertEqual(self.server.visits,
                         ["/v1/browser-state","/v1/search"])

    def test_manual_verified_third_tab_passes_local_bridge_without_source_probe(self):
        refused = {
            "page_kind": "canonical_search", "validation": "no_paired_rows",
            "paired_rows": 0, "title_rows": 0, "magnet_rows": 0,
        }
        valid = {
            "page_kind": "canonical_search", "validation": "valid",
            "paired_rows": 10, "title_rows": 10, "magnet_rows": 10,
        }
        state = {
            **good_state(), "open_tabs": 3, "verified_tabs": 1,
            "selected_tab_verified": False,
            "visible_source_rate_limited": True,
            "visible_captcha_required": False,
            "new_searches_paused": True,
            "selected_tab_index": 1,
            "pwa_tab_recovery_attempts": 2,
            "pwa_tab_recovery_last_outcome": "visible_refusal",
            "last_upstream_http_status": None,
            "tab_diagnostics": [dict(refused), dict(refused), dict(valid)],
        }
        self.server.state = state
        self.assertFalse(gw.browser_state_ready(state))
        self.assertTrue(gw.browser_state_owner_verified_adoption_ready(state))
        self.assertEqual(self.bridge.fetch("The Dog Stars 2026"), (200, HTML))
        self.assertEqual(self.server.visits,
                         ["/v1/browser-state", "/v1/search"])
        self.assertEqual(self.server.searches, ["The Dog Stars 2026"])

    def test_third_tab_adoption_rejects_ambiguous_states_before_private_search(self):
        refused = {
            "page_kind": "canonical_search", "validation": "no_paired_rows",
            "paired_rows": 0, "title_rows": 0, "magnet_rows": 0,
        }
        valid = {
            "page_kind": "canonical_search", "validation": "valid",
            "paired_rows": 10, "title_rows": 10, "magnet_rows": 10,
        }
        baseline = {
            **good_state(), "open_tabs": 3, "verified_tabs": 1,
            "selected_tab_verified": False,
            "visible_source_rate_limited": True,
            "visible_captcha_required": False,
            "new_searches_paused": True,
            "selected_tab_index": 1,
            "tab_diagnostics": [dict(refused), dict(refused), dict(valid)],
        }
        alternatives = (
            {"tab_diagnostics": [{"page_kind": "blank"}, dict(refused), dict(valid)]},
            {"tab_diagnostics": [dict(valid), dict(refused), dict(valid)]},
            {"selected_tab_index": 2},
            {"verified_tabs": 2},
            {"visible_captcha_required": True},
            {"last_navigation_status": 429},
            {"last_upstream_http_status": 429},
            {"new_searches_paused": False},
            {"open_tabs": 4},
            {"tab_diagnostics": [dict(refused), dict(refused)]},
            {"tab_diagnostics": [dict(refused), dict(refused),
                                 {**valid, "magnet_rows": 0}]},
            {"tab_diagnostics": [dict(refused),
                                 {**refused, "title_rows": 1}, dict(valid)]},
        )
        for override in alternatives:
            with self.subTest(override=override):
                state = {**baseline, **override}
                self.server.state = state
                self.assertFalse(
                    gw.browser_state_owner_verified_adoption_ready(state))
                self.assertNotEqual(
                    self.bridge.fetch("The Dog Stars 2026")[0], 200)
        self.assertEqual(self.server.searches, [])
        self.assertEqual(self.server.visits,
                         ["/v1/browser-state"] * len(alternatives))

    def test_manual_adoption_gateway_rejects_unsafe_or_unverified_pair(self):
        base={
            **good_state(),
            "open_tabs": 2, "verified_tabs": 1,
            "selected_tab_verified": False,
            "visible_source_rate_limited": True,
            "visible_captcha_required": False,
            "new_searches_paused": True,
            "last_navigation_status": None,
            "last_upstream_http_status": None,
            "selected_tab_index": 0,
            "tab_diagnostics": [
                {"page_kind":"canonical_search","validation":"no_paired_rows",
                 "paired_rows":0,"title_rows":0,"magnet_rows":0},
                {"page_kind":"canonical_search","validation":"valid",
                 "paired_rows":10,"title_rows":10,"magnet_rows":10},
            ],
        }
        failures=(
            {"visible_captcha_required":True},
            {"visible_source_rate_limited":False},
            {"last_navigation_status":429},
            {"last_upstream_http_status":429},
            {"open_tabs":3},
            {"verified_tabs":2},
            {"selected_tab_verified":True},
            {"selected_tab_index":2},
            {"new_searches_paused":False},
            {"tab_diagnostics":[
                base["tab_diagnostics"][0],
                {"page_kind":"canonical_search","validation":"no_paired_rows",
                 "paired_rows":0,"title_rows":0,"magnet_rows":0}]},
            {"tab_diagnostics":[
                base["tab_diagnostics"][0],
                {"page_kind":"canonical_search","validation":"valid",
                 "paired_rows":10,"title_rows":10,"magnet_rows":0}]},
            {"tab_diagnostics":[
                base["tab_diagnostics"][0],
                {"page_kind":"other","validation":"valid",
                 "paired_rows":10,"title_rows":10,"magnet_rows":10}]},
        )
        for override in failures:
            with self.subTest(override=override):
                self.server.state={**base,**override}
                self.assertFalse(
                    gw.browser_state_owner_verified_adoption_ready(
                        self.server.state))
                self.assertNotEqual(
                    self.bridge.fetch("The dog stars 720p")[0],200)
        self.assertEqual(self.server.searches,[])
        self.assertEqual(self.server.visits,
                         ["/v1/browser-state"]*len(failures))

    def test_manual_adoption_accepts_safely_reversed_selected_tab_index(self):
        old={"page_kind":"canonical_search","validation":"no_paired_rows",
             "paired_rows":0,"title_rows":0,"magnet_rows":0}
        verified={"page_kind":"canonical_search","validation":"valid",
                  "paired_rows":10,"title_rows":10,"magnet_rows":10}
        state={
            **good_state(), "open_tabs":2,"verified_tabs":1,
            "selected_tab_verified":False,"visible_source_rate_limited":True,
            "new_searches_paused":True,"selected_tab_index":1,
            "tab_diagnostics":[verified,old],
        }
        self.assertTrue(gw.browser_state_owner_verified_adoption_ready(state))

    def test_one_explicit_pwa_query_can_reach_ready_new_tab_recovery(self):
        self.server.state={
            **good_state(),
            "verified_tabs":0, "selected_tab_verified":False,
            "visible_source_rate_limited":True,
            "new_searches_paused":True,
            "pwa_tab_recovery_ready":True,
            "pwa_tab_recovery_reason":"visible_refusal",
            "pwa_tab_recovery_wait_seconds":0,
        }
        self.assertTrue(gw.browser_state_tab_recovery_ready(self.server.state))
        self.assertEqual(self.bridge.fetch("One owner search 2026"),(200,HTML))
        self.assertEqual(self.server.searches,["One owner search 2026"])
        self.assertEqual(self.server.visits,[
            "/v1/browser-state","/v1/search"])

    def test_recovery_refuses_early_legacy_challenge_and_multi_tab(self):
        base={
            **good_state(), "verified_tabs":0,"selected_tab_verified":False,
            "visible_source_rate_limited":True,"new_searches_paused":True,
            "pwa_tab_recovery_ready":True,
            "pwa_tab_recovery_reason":"visible_refusal",
            "pwa_tab_recovery_wait_seconds":0,
        }
        cases=(
            {"pwa_tab_recovery_wait_seconds":1},
            {"pwa_tab_recovery_ready":False},
            {"pwa_tab_recovery_reason":"unknown"},
            {"open_tabs":2},
            {"verified_tabs":1},
            {"visible_source_rate_limited":False},
            {"pwa_tab_recovery_wait_seconds":False},
            {"visible_captcha_required":True},
            {"visible_captcha_required":None},
        )
        for changed in cases:
            self.server.state={**base,**changed}
            self.assertFalse(gw.browser_state_tab_recovery_ready(self.server.state))
            self.assertNotEqual(self.bridge.fetch("One owner search 2026")[0],200)
        self.assertEqual(self.server.searches,[],
                         "unready PWA requests never reach the browser search route")

    def test_guarded_boot_blank_single_tab_can_recover_but_challenge_cannot(self):
        self.server.state={
            **good_state(), "verified_tabs":0,
            "selected_tab_verified":False,
            "visible_source_rate_limited":False,
            "pwa_tab_recovery_ready":True,
            "pwa_tab_recovery_reason":"blank_after_boot",
            "pwa_tab_recovery_wait_seconds":0,
            "tab_diagnostics":[{"page_kind":"blank"}],
        }
        self.assertTrue(gw.browser_state_tab_recovery_ready(self.server.state))
        self.assertEqual(self.bridge.fetch("Owner 2026")[0],200)
        self.server.state["tab_diagnostics"]=[{"page_kind":"canonical_search"}]
        self.assertFalse(gw.browser_state_tab_recovery_ready(self.server.state))
        self.assertEqual(self.bridge.fetch("Other owner 2026")[0],503)
        self.assertEqual(self.server.searches,["Owner 2026"])

    def test_legacy_unverified_or_ambiguous_browser_must_not_navigate(self):
        self.server.state=good_state()
        self.server.state.pop("visible_source_rate_limited")
        self.server.state["selected_tab_verified"]=False
        self.assertEqual(self.bridge.fetch("The Dog Stars 2026"),(503,b""))
        self.server.state=good_state()
        self.server.state.pop("visible_source_rate_limited")
        self.server.state["open_tabs"]=2
        self.assertEqual(self.bridge.fetch("The Dog Stars 2026"),(503,b""))
        self.server.state["open_tabs"]=1
        self.server.state["last_navigation_status"]=429
        self.assertEqual(self.bridge.fetch("The Dog Stars 2026"),(503,b""))
        self.assertEqual(self.server.searches, [])

    def test_legacy_single_owner_verified_tab_allows_one_explicit_search(self):
        self.server.state=good_state()
        self.server.state.pop("visible_source_rate_limited")
        self.assertTrue(gw.browser_state_ready(self.server.state))
        self.assertEqual(self.bridge.fetch("The Dog Stars 2026"),(200,HTML))
        self.assertEqual(self.server.searches,["The Dog Stars 2026"])

    def test_absent_legacy_pacing_flag_is_never_approved(self):
        self.server.state=good_state()
        self.server.state.pop("visible_source_rate_limited")
        self.server.state.pop("new_searches_paused")
        self.assertFalse(gw.browser_state_ready(self.server.state))
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
        self.assertEqual(provider.source_retry_after_seconds(),30)

    def test_browser_visible_soft_refusal_from_search_keeps_429_unlockable(self):
        self.server.search_status=425
        provider=gw.SearchProvider(fetcher=self.bridge.fetch,clock=lambda:100.0)
        self.assertEqual(provider.search("One user query"),(425,b""))
        self.assertEqual(provider.source_retry_after_seconds(),0)
        self.assertEqual(self.server.searches,["One user query"])
        self.assertEqual(provider.search("Immediate different query")[0],429)
        self.assertEqual(self.server.searches,["One user query"])

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
