#!/usr/bin/env python3
"""Offline fail-closed tests of the exact owner-shared OxTorrent Resolve flow."""
import contextlib
import importlib.util
import io
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import call, patch

P = Path(__file__).with_name("diagnose_magnetra_exact_oxtorrent_resolve.py")
sys.path.insert(0, str(P.parent))
spec = importlib.util.spec_from_file_location("magnetra_exact_oxtorrent_diag", P)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)

BTIH = "magnet:?xt=urn:btih:" + "a" * 40
SAFE_RESULT = {"provider": "oxtorrent", "name": "Toy.Story.5.2026.MULTi",
               "details": m.OWNER_DETAIL, "magnetSource": None, "magnet": None}
WRONG_SOURCE = "https://www.oxtorrent.co/download/133995"


class ExactResolveTests(unittest.TestCase):
    def test_exact_public_owner_url_is_canonical(self):
        self.assertEqual(m.shape(m.OWNER_DETAIL), "CANONICAL_DETAIL")
        self.assertEqual(m.PROVIDER, "oxtorrent")

    def test_strict_shape_classifier_identifies_noncanonical_origin_or_path(self):
        examples = [
            ("https://evil.invalid/torrent/133995/x", "ORIGIN_REFUSED"),
            ("https://www.oxtorrent.co/torrent/133995/x?go=1", "QUERY"),
            ("https://www.oxtorrent.co/torrent/133995/x/", "TRAILING_SLASH"),
            ("https://www.oxtorrent.co/torrent/133995/x%20y", "ENCODED_PATH"),
            (WRONG_SOURCE, "OTHER_PATH"),
            (None, "ABSENT"),
        ]
        for url, code in examples:
            with self.subTest(code=code):
                self.assertEqual(m.shape(url), code)

    def test_no_explicit_consent_calls_no_sources(self):
        with patch.dict(os.environ, {"MAGNETRA_EXACT_RESOLVE_APPROVAL": "CANCEL"}):
            with patch.object(m, "gate") as cloudflare, \
                 patch.object(m, "request_json") as remote:
                with self.assertRaises(m.Stop):
                    m.execute()
                cloudflare.assert_not_called()
                remote.assert_not_called()

    def test_exact_result_only_must_match_correct_provider(self):
        self.assertEqual(m.select_search_record({"results": [SAFE_RESULT]}), SAFE_RESULT)
        self.assertIsNone(m.select_search_record({"results": [
            {"provider": "oxtorrent", "name": "different", "details": None}]}))
        with self.assertRaises(m.Stop):
            m.select_search_record({"results": [SAFE_RESULT, SAFE_RESULT]})
        with self.assertRaises(m.Stop):
            m.select_search_record({"results": [
                {"provider": "torrent9", "details": m.OWNER_DETAIL}]})

    def test_resolver_status_redacts_magnets_and_untrusted_errors(self):
        self.assertEqual(m.classify_resolve(200, {"magnet": BTIH}), "PASS_VALID_BTIH")
        self.assertEqual(m.classify_resolve(200, {"magnet": "https://fake.invalid"}),
                         "HTTP_200_INVALID_MAGNET")
        self.assertEqual(m.classify_resolve(502, {
            "error": "Provider could not resolve magnet: Noncanonical source HTML route refused."
        }), "HTTP_502_NONCANONICAL_WORKER_ROUTE")
        self.assertEqual(m.classify_resolve(502, {
            "error": "Provider could not resolve magnet: private-url TOKEN123"
        }), "HTTP_502_OTHER")

    def test_exact_same_field_probes_once_and_sanitizes(self):
        with patch.dict(os.environ, {"MAGNETRA_EXACT_RESOLVE_APPROVAL": m.ACTION}):
            with patch.object(m, "gate", side_effect=["d1", "d1"]), \
                 patch.object(m, "request_json", side_effect=[
                     (200, {"results": [SAFE_RESULT], "errors": []}),
                     (200, {"magnet": BTIH})]) as network:
                stream = io.StringIO()
                with contextlib.redirect_stdout(stream):
                    self.assertEqual(m.execute(), 0)
                text = stream.getvalue()
                self.assertIn("PWA_RESOLVE_URL_EQUALS_OWNER_LINK: YES", text)
                self.assertIn("OWNER_EXACT_RESOLVE: PASS_VALID_BTIH", text)
                self.assertNotIn(m.OWNER_DETAIL, text)
                self.assertNotIn(BTIH, text)
                self.assertEqual(network.call_count, 2)
                self.assertEqual(network.call_args_list[-1], call(
                    "/api/resolve", payload={
                        "provider": "oxtorrent", "details": m.OWNER_DETAIL
                    }))

    def test_preferred_magnet_source_mismatch_requires_distinct_probe(self):
        item = {**SAFE_RESULT, "magnetSource": WRONG_SOURCE}
        with patch.dict(os.environ, {"MAGNETRA_EXACT_RESOLVE_APPROVAL": m.ACTION}):
            with patch.object(m, "gate", side_effect=["d1", "d1"]), \
                 patch.object(m, "request_json", side_effect=[
                     (200, {"results": [item], "errors": []}),
                     (200, {"magnet": BTIH}),
                     (502, {"error": "Noncanonical source HTML route refused."})]) as network:
                stream = io.StringIO()
                with contextlib.redirect_stdout(stream):
                    self.assertEqual(m.execute(), 0)
                text = stream.getvalue()
                self.assertIn("PWA_RESOLVE_PREFERRED_FIELD: MAGNET_SOURCE", text)
                self.assertIn("PWA_RESOLVE_URL_EQUALS_OWNER_LINK: NO", text)
                self.assertIn("PWA_PREFERRED_RESOLVE: HTTP_502_NONCANONICAL_WORKER_ROUTE", text)
                self.assertEqual(network.call_count, 3)
                self.assertNotIn(WRONG_SOURCE, text)

    def test_owner_record_missing_still_probes_exact_one_detail(self):
        with patch.dict(os.environ, {"MAGNETRA_EXACT_RESOLVE_APPROVAL": m.ACTION}):
            with patch.object(m, "gate", side_effect=["d1", "d1"]), \
                 patch.object(m, "request_json", side_effect=[
                     (200, {"results": [], "errors": []}),
                     (502, {"error": "Noncanonical source HTML route refused."})]) as network:
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(m.execute(), 0)
                self.assertIn("OWNER_RECORD_IN_BOUNDED_SEARCH: NOT_PRESENT", output.getvalue())
                self.assertEqual(network.call_count, 2)

    def test_cloudflare_deployment_state_must_stay_identical(self):
        with patch.dict(os.environ, {"MAGNETRA_EXACT_RESOLVE_APPROVAL": m.ACTION}):
            with patch.object(m, "gate", side_effect=["d1", "d2"]), \
                 patch.object(m, "request_json", side_effect=[
                     (200, {"results": [], "errors": []}),
                     (200, {"magnet": BTIH})]):
                with self.assertRaisesRegex(m.Stop, "DEPLOYMENT_CHANGED"):
                    m.execute()


if __name__ == "__main__":
    unittest.main()
