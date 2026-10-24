import os
import unittest
from unittest.mock import patch
import diagnose_0magnet_owner_readonly_20261024 as d

HASH = "0123456789abcdef0123456789abcdef01234567"
MAGNET = "magnet:?xt=urn:btih:" + HASH
DETAIL = "https://9mag.net/test/owner-sample"
CARD = {"provider": "0magnet", "name": "Little.House.on.the.Prairie.2026.S01.720p.10bit.WEBRip.2CH.x265.HEVC-PSA",
        "size": "2.26GB", "details": DETAIL, "magnet": None}

class Tests(unittest.TestCase):
    def test_host_guards(self):
        self.assertTrue(d.same_source_detail(DETAIL))
        for url in ["https://evil.com/", "http://9mag.net/test", "https://9mag.net.evil.com/test",
                    "https://a@9mag.net/test", "https://9mag.net/#x", "https://9mag.net/",
                    "https://9mag.net:443/private", "https://9mag.net/x" + "y"*1700]:
            self.assertFalse(d.same_source_detail(url), url)

    def test_unique_same_card_no_guess(self):
        self.assertEqual(d.choose_owner({"results": [CARD]}), CARD)
        self.assertIsNone(d.choose_owner({"results": []}))
        self.assertIsNone(d.choose_owner({"results": [{**CARD, "provider": "therarbag"}]}))
        self.assertIsNone(d.choose_owner({"results": [CARD, CARD]}))
        self.assertIsNone(d.choose_owner({"results": [{**CARD, "name": "Another Film 2026"}]}))

    def test_input_value_from_server_html_only(self):
        html = ('<input id="input-magnet" value="' + MAGNET + '&amp;dn=Example">').encode()
        shape, magnet = d.page_magnet_shape(html)
        self.assertEqual(shape, "MAGNET_VALID")
        self.assertEqual(d.btih(magnet), HASH)
        self.assertEqual(d.page_magnet_shape(b'<input id="input-magnet">')[0], "VALUE_ATTR_MISSING")
        self.assertEqual(d.page_magnet_shape(b'<div id="input-magnet"></div>')[0], "INPUT_MISSING")
        self.assertEqual(d.page_magnet_shape(b'<input id="input-magnet" value="not-a-magnet">')[0],
                         "VALUE_NOT_VALID_BTIH")
        self.assertEqual(d.page_magnet_shape(html + html)[0], "INPUT_DUPLICATED")

    def test_error_categories_no_raw_response(self):
        self.assertEqual(d.safe_error_class({"error": "Provider could not resolve magnet: provider HTTP 403"}),
                         "SOURCE_HTTP_403_OR_401")
        self.assertEqual(d.safe_error_class({"error": "Provider could not resolve magnet: provider details page contains no supported magnet link"}),
                         "SOURCE_NO_SUPPORTED_MAGNET")
        self.assertEqual(d.safe_error_class({"error": "private token " + HASH}), "OTHER_RESOLVE_FAILURE")

    def test_missing_approval_makes_no_outbound_calls(self):
        with patch.object(d.sys, "argv", ["script"]), patch.object(d, "request_once") as req:
            self.assertEqual(d.main(), 2)
            req.assert_not_called()

    def test_one_real_source_detail_and_one_resolver_no_leaks(self):
        import json
        search_json = json.dumps({"results": [CARD], "errors": []}).encode()
        source_html = ('<input id="input-magnet" value="' + MAGNET + '">').encode()
        reply_json = json.dumps({"provider":"0magnet", "magnet": MAGNET}).encode()
        calls = []
        def fake(url, *, payload=None, accept="application/json"):
            calls.append((url, payload))
            if "/api/search" in url:
                return (200, "application/json", search_json)
            if url == DETAIL:
                return (200, "text/html", source_html)
            if url.endswith("/api/resolve"):
                self.assertEqual(payload, {"provider":"0magnet", "details":DETAIL})
                return (200, "application/json", reply_json)
            self.fail("unexpected outbound request")
        with patch.dict(os.environ, {"MAGNETRA_0MAGNET_DIAGNOSTIC_APPROVAL": d.APPROVAL}), \
             patch.object(d, "request_once", fake), patch("builtins.print") as printer:
            self.assertEqual(d.execute(), 0)
        log = " ".join(" ".join(str(z) for z in a.args) for a in printer.call_args_list)
        self.assertEqual(len(calls), 3)
        self.assertIn("SAME_SOURCE_BTih_MATCH: YES", log)
        self.assertNotIn(MAGNET, log)
        self.assertNotIn(HASH, log)
        self.assertNotIn(DETAIL, log)
        self.assertNotIn(CARD["name"], log)

    def test_error_stops_no_second_source_call(self):
        import json
        body = json.dumps({"results":[], "errors":[{"provider":"0magnet","code":"RATE_LIMIT"}]}).encode()
        with patch.dict(os.environ, {"MAGNETRA_0MAGNET_DIAGNOSTIC_APPROVAL":d.APPROVAL}), \
             patch.object(d, "request_once", return_value=(200, "application/json", body)) as req, \
             patch("builtins.print"):
            with self.assertRaisesRegex(d.Stop, "PROVIDER_SEARCH_FAILED_NO_RETRY"):
                d.execute()
            self.assertEqual(req.call_count, 1)

if __name__=="__main__":
    unittest.main()
