#!/usr/bin/env python3
"""Offline contract tests of bounded, no-secret-log 2026 production card diagnosis."""
import contextlib
import importlib.util
import io
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import call, patch

P = Path(__file__).with_name("diagnose_magnetra_2026_card_resolve.py")
sys.path.insert(0, str(P.parent))
spec = importlib.util.spec_from_file_location("magnetra_2026_cards", P)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)
OXT = "https://www.oxtorrent.co/torrent/133995/toy-story-5-2026-multi-ca-1080p-web-h264-supply"
T9 = "https://www7.torrent9.to/torrent/133873/ubuntu-title"
BTIH = "magnet:?xt=urn:btih:" + "a" * 40


class CardTests(unittest.TestCase):
    def test_canonical_source_routes_for_both_sources(self):
        self.assertEqual(m.shape("oxtorrent", OXT), "CANONICAL_DETAIL")
        self.assertEqual(m.shape("torrent9", T9), "CANONICAL_DETAIL")
        self.assertEqual(m.shape("torrent9", "https://evil.invalid/torrent/1/x"),
                         "NONCANONICAL_ORIGIN")

    def test_reject_cross_source_misattribution(self):
        with self.assertRaises(m.Stop):
            m.records({"results": [{"provider": "btdigg", "details": OXT}]})
        with self.assertRaises(m.Stop):
            m.records({"results": [None]})
        with self.assertRaises(m.Stop):
            m.records({"results": "bad"})
        with self.assertRaises(m.Stop):
            m.records({"results": [{}]})

    def test_report_catches_noncanonical_preferred_magnet_source(self):
        items = [{"provider": "oxtorrent", "name": "Toy.Story.5.2026",
                  "details": OXT,
                  "magnetSource": "https://www.oxtorrent.co/sponsored/123",
                  "torrentFile": "https://www.oxtorrent.co/download/123"}]
        report = m.report("oxtorrent", items)
        self.assertEqual(report["total"], 1)
        self.assertEqual(report["detail_CANONICAL_DETAIL"], 1)
        self.assertEqual(report["magnetSource_present"], 1)
        self.assertEqual(report["magnetSource_overrides_details"], 1)
        self.assertEqual(report["pwa_preferred_noncanonical"], 1)
        self.assertEqual(report["torrentFile_present"], 1)

    def test_sample_prefers_screenshot_title_without_logging_title(self):
        rows = [
            {"name": "Generic Ubuntu", "details": OXT, "magnet": None},
            {"name": "Toy.Story.5.2026.MULTi", "details": OXT, "magnet": None},
        ]
        row, name = m.choose_sample("oxtorrent", rows)
        self.assertEqual(name, "SCREENSHOT_TITLE")
        self.assertIs(row, rows[1])

    def test_probe_comparison_is_one_call_for_canonical_detail(self):
        item = {"details": OXT, "magnetSource": None}
        with patch.object(m._exact, "request_json", return_value=(200, {"magnet": BTIH})) as remote:
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                m.probe("oxtorrent", item)
            self.assertEqual(remote.call_count, 1)
            self.assertIn("CANONICAL_DETAIL_RESOLVE_oxtorrent: PASS_VALID_BTIH", stream.getvalue())
            self.assertIn("PWA_PREFERRED_RESOLVE_oxtorrent: SAME_AS_DETAILS", stream.getvalue())
            self.assertNotIn(BTIH, stream.getvalue())
            self.assertNotIn(OXT, stream.getvalue())

    def test_noncanonical_preferred_link_is_classified_not_fetched(self):
        ad = "https://www.oxtorrent.co/advertisements/open"
        item = {"details": OXT, "magnetSource": ad}
        with patch.object(m._exact, "request_json", return_value=(200, {"magnet": BTIH})) as remote:
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                m.probe("oxtorrent", item)
            self.assertEqual(remote.call_count, 1)
            self.assertIn("SKIPPED_NONCANONICAL_PREFERRED_LINK", stream.getvalue())
            self.assertNotIn(ad, stream.getvalue())

    def test_distinct_canonical_preferred_link_gets_second_only(self):
        source = "https://www.oxtorrent.co/torrent/123/other"
        item = {"details": OXT, "magnetSource": source}
        with patch.object(m._exact, "request_json", return_value=(502, {
                "error": "Noncanonical source HTML route refused."})) as remote:
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                m.probe("oxtorrent", item)
            self.assertEqual(remote.call_count, 2)
            self.assertIn("PWA_PREFERRED_RESOLVE_oxtorrent: HTTP_502_NONCANONICAL_WORKER_ROUTE", stream.getvalue())

    def test_public_js_version_compare_is_hash_only(self):
        data = (m.DIRECTORY.parent / "web" / "app.js").read_bytes()
        class Resp:
            status = 200
            def __init__(self, body):
                self.body = body
            def __enter__(self):
                return self
            def __exit__(self, *_):
                return False
            def read(self, _n):
                return self.body
        class Opener:
            def __init__(self, body):
                self.body = body
            def open(self, request, timeout):
                self._last_request = request
                self._last_timeout = timeout
                return Resp(self.body)
        good = Opener(data)
        bad = Opener(data + b"// stale asset")
        self.assertEqual(m.compare_live_pwa_asset(good), "MATCH_REVIEWED_MAIN")
        self.assertEqual(m.compare_live_pwa_asset(bad), "DIFFERS_FROM_REVIEWED_MAIN")
        self.assertEqual(good._last_timeout, 15)
        self.assertEqual(good._last_request.full_url, "https://index.alexlab.media/app.js")

    def test_no_approval_no_network_calls(self):
        with patch.dict(os.environ, {"MAGNETRA_2026_CARD_DIAGNOSTIC_APPROVAL": "CANCEL"}):
            with patch.object(m._exact, "gate") as cloudflare, \
                 patch.object(m._exact, "request_json") as source:
                with self.assertRaises(m.Stop):
                    m.execute()
                cloudflare.assert_not_called()
                source.assert_not_called()

    def test_exact_two_source_request_and_postflight(self):
        results = [
            {"provider": "oxtorrent", "name": "Toy.Story.5.2026", "details": OXT},
            {"provider": "torrent9", "name": "Ubuntu", "details": T9},
        ]
        with patch.dict(os.environ, {"MAGNETRA_2026_CARD_DIAGNOSTIC_APPROVAL": m.ACTION}):
            with patch.object(m._exact, "gate", side_effect=["id1", "id1"]), \
                 patch.object(m._exact, "request_json", side_effect=[
                    (200, {"results": results, "errors": []}),
                    (200, {"magnet": BTIH}),
                    (200, {"magnet": BTIH})
                 ]) as remote:
                stream = io.StringIO()
                with contextlib.redirect_stdout(stream):
                    self.assertEqual(m.execute(), 0)
                self.assertEqual(remote.call_count, 3)
                search_path = remote.call_args_list[0].args[0]
                self.assertIn("providers=oxtorrent%2Ctorrent9", search_path)
                self.assertNotIn("btdigg", search_path)
                self.assertNotIn("eztvx", search_path)
                output=stream.getvalue()
                self.assertNotIn(BTIH, output)
                self.assertNotIn(OXT, output)
                self.assertNotIn(T9, output)
                self.assertIn("DIAGNOSTIC_PASS", output)


if __name__ == "__main__":
    unittest.main()
