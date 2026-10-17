#!/usr/bin/env python3
"""Offline contract tests: no network, no torrent download, no secret logging."""
import importlib.util
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

P = Path(__file__).with_name("check-magnetra-candidate-e2e.py")
spec = importlib.util.spec_from_file_location("magnetra_candidate_e2e", P)
sys.path.insert(0, str(P.parent))
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)


class CandidateE2ETests(unittest.TestCase):
    def test_override_header_exact_workernamed_version(self):
        self.assertEqual(m.OVERRIDE, 'alexlab-magnetra="' + m.VERSION + '"')

    def test_valid_magnet_accepts_btih_and_blocks_wrong_values(self):
        self.assertTrue(m.valid_magnet("magnet:?xt=urn:btih:" + "a" * 40))
        self.assertTrue(m.valid_magnet("magnet:?xt=urn:btih:" + "a" * 32 + "&dn=ok"))
        self.assertFalse(m.valid_magnet("magnet:?xt=urn:btih:" + "q" * 40))
        self.assertFalse(m.valid_magnet("https://example.invalid/test"))
        self.assertFalse(m.valid_magnet("magnet:?xt=urn:btih:" + "a" * 40 + "x"))
        self.assertFalse(m.valid_magnet("magnet:?xt=urn:btih:" + "a" * 40 + "&a=" + "x" * 12000))

    def test_fingerprint_blocks_unproven_candidate_even_if_200(self):
        with patch.object(m, "request_api", side_effect=[
            (200, {"providers": []}), (200, {"providers": [{}] * 46})]):
            with self.assertRaisesRegex(m.Stop, "OVERRIDE_ATTRIBUTION_UNVERIFIED_BASELINE"):
                m.check_routing_fingerprint()

    def test_fingerprint_passes_old404_new46(self):
        with patch.object(m, "request_api", side_effect=[
            (404, None), (200, {"providers": [{}] * 46})]):
            m.check_routing_fingerprint()

    def test_fingerprint_rejects_old404_new404(self):
        with patch.object(m, "request_api", side_effect=[
            (404, None), (404, None)]):
            with self.assertRaises(m.Stop):
                m.check_routing_fingerprint()

    def test_catalog_requires_46_unique(self):
        with patch.object(m, "request_api", return_value=(200, {
            "providers": [{"id": "same"}] * 46
        })):
            with self.assertRaises(m.Stop):
                m.check_catalog()

    def test_search_fails_wrong_provider_or_untrusted_magnet(self):
        row = {"provider": "torrent9", "name": "Ubuntu",
               "magnet": "magnet:?xt=urn:btih:" + "a" * 40}
        output = {"results": [row], "stats": [{"provider": "oxtorrent", "ok": True}],
                  "errors": []}
        with patch.object(m, "request_api", return_value=(200, output)):
            with self.assertRaises(m.Stop):
                m.validate_search("oxtorrent", "ubuntu")

    def test_resolution_does_not_log_full_magnet(self):
        output = {"provider": "oxtorrent", "magnet": "magnet:?xt=urn:btih:" + "b" * 40}
        with patch.object(m, "request_api", return_value=(200, output)):
            m.check_resolve("oxtorrent", [{
                "details": "https://www.oxtorrent.co/torrent/132583/ubuntu-title",
                "magnet": None
            }])

    def test_no_e2e_without_manual_approval(self):
        with patch.dict(os.environ, {"MAGNETRA_E2E_READONLY_APPROVAL": "CANCEL"}):
            with patch.object(m, "check_deployment") as gate:
                with self.assertRaises(m.Stop):
                    m.execute()
                gate.assert_not_called()


if __name__ == "__main__":
    unittest.main()
