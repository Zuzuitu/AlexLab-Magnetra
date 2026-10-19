#!/usr/bin/env python3
"""No-network tests for secure shape-only OxTorrent/Torrent9 diagnostics."""
import importlib.util
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
p = SCRIPTS / "diagnose_magnetra_detail_routes.py"
spec = importlib.util.spec_from_file_location("magnetra_detail_shapes_diag", p)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)


class ShapeTests(unittest.TestCase):
    def test_original_verified_ascii_routes_are_accepted(self):
        good = {
            "oxtorrent": "https://www.oxtorrent.co/torrent/135300/ubuntu-2026",
            "torrent9": "https://www7.torrent9.to/torrent/133873/ubuntu-title",
        }
        for source, url in good.items():
            self.assertEqual(m.route_shape(source, url), "CANONICAL_DETAIL")

    def test_identifies_safe_readonly_shape_categories(self):
        cases = [
            ("oxtorrent", "https://www.oxtorrent.co/torrent/3/a/", "TRAILING_SLASH"),
            ("oxtorrent", "https://www.oxtorrent.co/torrent/3/caf%C3%A9", "PERCENT_ENCODED_PATH"),
            ("torrent9", "https://www7.torrent9.to/torrent/3/abc?utm=bad", "QUERY_PARAMETERS"),
            ("torrent9", "https://www7.torrent9.to/torrent/3/abc#anchor", "FRAGMENT"),
            ("torrent9", "https://www7.torrent9.to/torrent/3/name(2026)", "UNEXPECTED_DETAIL_SLUG"),
            ("oxtorrent", "https://www.oxtorrent.co/torrent/3/café", "UNEXPECTED_DETAIL_SLUG"),
            ("oxtorrent", "https://www.oxtorrent.co/torrent/abc/slug", "DIFFERENT_TORRENT_ROUTE"),
            ("torrent9", "https://www7.torrent9.to/details/3/x", "OTHER_PATH_TEMPLATE"),
            ("oxtorrent", "https://evil.invalid/torrent/3/abc", "NONCANONICAL_ORIGIN"),
            ("torrent9", "http://www7.torrent9.to/torrent/3/abc", "NONCANONICAL_ORIGIN"),
            ("oxtorrent", "https://u:p@www.oxtorrent.co/torrent/3/abc", "NONCANONICAL_ORIGIN"),
            ("oxtorrent", "https://www.oxtorrent.co:8443/torrent/3/abc", "NONCANONICAL_ORIGIN"),
            ("oxtorrent", None, "MISSING_DETAIL"),
        ]
        for provider, url, expected in cases:
            with self.subTest(provider=provider, expected=expected):
                self.assertEqual(m.route_shape(provider, url), expected)

    def test_no_owner_approval_makes_no_network_request(self):
        with patch.dict(os.environ, {"MAGNETRA_DETAIL_DIAGNOSTIC_APPROVAL": "CANCEL"}):
            with patch.object(m, "_get_api") as cloudflare, \
                 patch.object(m, "get_production_search") as query:
                self.assertRaises(m.Stop, m.execute)
                cloudflare.assert_not_called()
                query.assert_not_called()

    def test_exact_production_100_0_metadata_gate(self):
        old = "a9df4429-1111-4111-8111-111111111111"
        new = m.VERSION
        def deployment(shares):
            return {"success": True, "result": {"deployments": [{
                "id": "some-deployment",
                "created_on": "2026-10-19T11:17:00Z",
                "versions": [
                    {"version_id": key, "percentage": pct}
                    for key, pct in shares.items()
                ],
            }]}}
        with patch.object(m, "_get_api", return_value=deployment({old: 0, new: 100})):
            self.assertEqual(m.confirm_current_release(), "some-deployment")
        for bad in (
            {old: 95, new: 5},
            {old: 100, new: 0},
            {"bbbbbbbb-1111-4111-8111-111111111111": 0, new: 100},
        ):
            with patch.object(m, "_get_api", return_value=deployment(bad)):
                with self.assertRaises(m.Stop):
                    m.confirm_current_release()

    def test_source_identity_and_screenshot_match_flags_no_raw_logging(self):
        rows = [
            {"provider": "oxtorrent", "name": "Toy.Story.5.2026.MULTi",
             "details": "https://www.oxtorrent.co/torrent/1234/abc%C3%A9"},
            {"provider": "torrent9", "name": "Hope.2026.MULTi",
             "details": "https://www7.torrent9.to/torrent/4321/abc/"},
        ]
        output = m.diagnose_results({"results": rows})
        self.assertEqual(output["summary"]["oxtorrent"]["PERCENT_ENCODED_PATH"], 1)
        self.assertEqual(output["matched"]["oxtorrent"]["PERCENT_ENCODED_PATH"], 1)
        self.assertEqual(output["matched"]["torrent9"]["TRAILING_SLASH"], 1)
        with self.assertRaises(m.Stop):
            m.diagnose_results({"results": [{"provider": "btdigg", "details": None}]})
        with self.assertRaises(m.Stop):
            m.diagnose_results({"results": "invalid"})


if __name__ == "__main__":
    unittest.main()
