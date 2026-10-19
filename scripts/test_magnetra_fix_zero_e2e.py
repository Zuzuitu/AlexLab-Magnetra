#!/usr/bin/env python3
"""No-network 540b zero-slot acceptance tests; never call actual providers."""
import hashlib
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import call, patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_magnetra_fix_zero_e2e as mod

MAGNET = "magnet:?xt=urn:btih:" + "a" * 40
OLD = mod.ACTIVE
NEW = mod.STAGED
BINDINGS = [
    {"name": "BTDIGG_GATEWAY_TOKEN", "type": "secret_text"},
    {"name": "MAGNETRA_GATEWAY_TOKEN", "type": "secret_text"},
    {"name": "ASSETS", "type": "assets"},
]


def deployed(shares, ident="slot"):
    return {"success": True, "result": {"deployments": [{
        "created_on": "2026-10-19T20:00:00Z", "id": ident,
        "versions": [{"version_id": v, "percentage": pct} for v, pct in shares.items()],
    }]}}


def stage(bindings=BINDINGS):
    return {"success": True, "result": {"id": NEW, "resources": {"bindings": bindings}}}


class StagedE2ETests(unittest.TestCase):
    def test_no_approval_zero_network_requests(self):
        with patch.dict(os.environ, {"MAGNETRA_FIX_E2E_ACTION": "CANCEL"}):
            with patch.object(mod, "_get_api") as cloudflare, \
                 patch.object(mod, "http_get") as source:
                with self.assertRaises(mod.Stop):
                    mod.execute()
                cloudflare.assert_not_called()
                source.assert_not_called()

    def test_only_exact_249d_100_540b_0_metadata_can_start(self):
        with patch.object(mod, "_get_api", side_effect=[
            stage(), deployed({OLD: 100, NEW: 0})
        ]):
            self.assertEqual(mod.deployment_gate(), "slot")
        for shares in (
            {OLD: 95, NEW: 5},
            {OLD: 100},
            {NEW: 100, OLD: 0},
            {OLD: 100, "bbbbbbbb-1111-4111-8111-111111111111": 0},
        ):
            with self.subTest(shares=shares):
                with patch.object(mod, "_get_api", side_effect=[stage(), deployed(shares)]):
                    with self.assertRaises(mod.Stop):
                        mod.deployment_gate()

    def test_missing_binding_refused(self):
        for name in ("BTDIGG_GATEWAY_TOKEN", "MAGNETRA_GATEWAY_TOKEN", "ASSETS"):
            with self.subTest(name=name):
                with patch.object(mod, "_get_api", side_effect=[
                    stage([b for b in BINDINGS if b["name"] != name]),
                    deployed({OLD: 100, NEW: 0})
                ]):
                    with self.assertRaisesRegex(mod.Stop, "STAGED_BINDING_UNVERIFIED"):
                        mod.deployment_gate()

    def test_exact_reviewed_asset_required_and_old_differs(self):
        reviewed = (Path(__file__).resolve().parent.parent / "web" / "app.js").read_bytes()
        with patch.object(mod, "http_get", side_effect=[reviewed, b"old bad source"]) as get:
            mod.verify_asset_override()
            self.assertEqual(get.call_args_list, [
                call("/app.js", staged=True),
                call("/app.js", staged=False),
            ])
        with patch.object(mod, "http_get", side_effect=[b"wrong worker", b"old"]):
            with self.assertRaisesRegex(mod.Stop, "STAGED_VERSION_ASSET_ATTRIBUTION_FAILED"):
                mod.verify_asset_override()
        with patch.object(mod, "http_get", side_effect=[reviewed, reviewed]):
            with self.assertRaisesRegex(mod.Stop, "OVERRIDE_IGNORED"):
                mod.verify_asset_override()

    def test_46_original_provider_ids_no_fabrication(self):
        good = {"providers": [{"id": "provider" + str(i)} for i in range(46)]}
        with patch.object(mod, "http_get", return_value=good):
            mod.verify_provider_catalog()
        with patch.object(mod, "http_get", return_value={"providers": good["providers"][:-1]}):
            with self.assertRaises(mod.Stop):
                mod.verify_provider_catalog()

    def test_exact_canonical_details_only_probed_and_magnets_redacted(self):
        rows = [
            {"provider": "oxtorrent",
             "details": "https://www.oxtorrent.co/torrent/133995/ubuntu-stable",
             "magnetSource": "https://www.oxtorrent.co/download/ad",
             "magnet": None},
            {"provider": "torrent9",
             "details": "https://www7.torrent9.to/torrent/133995/ubuntu-stable",
             "magnetSource": "https://www7.torrent9.to/download/ad",
             "magnet": None},
        ]
        with patch.object(mod, "http_get", side_effect=[
            {"results": rows, "errors": []},
            {"provider": "oxtorrent", "magnet": MAGNET},
            {"provider": "torrent9", "magnet": MAGNET},
        ]) as get:
            mod.verify_original_sources()
            self.assertEqual(get.call_count, 3)
            self.assertEqual(get.call_args_list[1], call("/api/resolve", staged=True, payload={
                "provider": "oxtorrent", "details": rows[0]["details"]
            }))
            self.assertEqual(get.call_args_list[2], call("/api/resolve", staged=True, payload={
                "provider": "torrent9", "details": rows[1]["details"]
            }))

    def test_reject_off_origin_and_ad_paths_before_resolve(self):
        rows = [
            {"provider": "oxtorrent", "details": "https://example.invalid/torrent/10/abc",
             "magnet": None},
            {"provider": "torrent9", "details": "https://www7.torrent9.to/torrent/20/valid",
             "magnet": None},
        ]
        with patch.object(mod, "http_get", return_value={"results": rows, "errors": []}) as get:
            with self.assertRaisesRegex(mod.Stop, "NONCANONICAL"):
                mod.verify_original_sources()
            get.assert_called_once()

    def test_any_source_error_stops_without_retry(self):
        with patch.object(mod, "http_get", return_value={"results": [], "errors": [
            {"provider": "oxtorrent", "code": "RATE_LIMIT"}]}) as get:
            with self.assertRaisesRegex(mod.Stop, "STAGED_SEARCH_SOURCE_ERROR"):
                mod.verify_original_sources()
            get.assert_called_once()

    def test_full_success_requires_unchanged_deployment(self):
        with patch.dict(os.environ, {"MAGNETRA_FIX_E2E_ACTION": mod.ACTION}):
            with patch.object(mod, "deployment_gate", side_effect=["slot", "slot"]), \
                 patch.object(mod, "verify_asset_override") as asset, \
                 patch.object(mod, "verify_provider_catalog") as catalog, \
                 patch.object(mod, "verify_original_sources") as sources:
                self.assertEqual(mod.execute(), 0)
                asset.assert_called_once()
                catalog.assert_called_once()
                sources.assert_called_once()

    def test_deployment_changed_at_end_is_failure(self):
        with patch.dict(os.environ, {"MAGNETRA_FIX_E2E_ACTION": mod.ACTION}):
            with patch.object(mod, "deployment_gate", side_effect=["slot", "changed"]), \
                 patch.object(mod, "verify_asset_override"), \
                 patch.object(mod, "verify_provider_catalog"), \
                 patch.object(mod, "verify_original_sources"):
                with self.assertRaisesRegex(mod.Stop, "DEPLOYMENT_CHANGED"):
                    mod.execute()


if __name__ == "__main__":
    unittest.main()
