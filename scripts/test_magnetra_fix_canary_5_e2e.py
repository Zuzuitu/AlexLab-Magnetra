#!/usr/bin/env python3
"""No-network immutable version and source-check tests for the 5% canary."""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_magnetra_fix_canary_5_e2e as mod
from deploy_magnetra_fix_canary_5 import FIVE

GOOD = {"success": True, "result": {"id": mod.STAGED, "resources": {"bindings": [
    {"name": "BTDIGG_GATEWAY_TOKEN", "type": "secret_text"},
    {"name": "MAGNETRA_GATEWAY_TOKEN", "type": "secret_text"},
    {"name": "ASSETS", "type": "assets"},
]}}}


def deployment(shares=FIVE, ident="canary"):
    return {"success": True, "result": {"deployments": [{
        "id": ident,
        "created_on": "2026-10-19T20:15:00Z",
        "versions": [{"version_id": k, "percentage": v} for k, v in shares.items()],
    }]}}


class CanaryAcceptanceTests(unittest.TestCase):
    def test_cancel_before_any_requests(self):
        with patch.dict(os.environ, {"MAGNETRA_FIX_CANARY_E2E_ACTION": "CANCEL"}):
            with patch.object(mod, "_get_api") as cloudflare, \
                 patch.object(mod.source, "http_get") as source:
                with self.assertRaises(mod.Stop):
                    mod.execute()
                cloudflare.assert_not_called()
                source.assert_not_called()

    def test_only_95_5_metadata_and_all_bindings_allow_source_probe(self):
        with patch.object(mod, "_get_api", side_effect=[GOOD, deployment()]):
            self.assertEqual(mod.metadata_gate(), "canary")
        for shares in (
            {mod.ACTIVE: 100, mod.STAGED: 0},
            {mod.ACTIVE: 100},
            {mod.ACTIVE: 90, mod.STAGED: 10},
            {mod.ACTIVE: 0, mod.STAGED: 100},
        ):
            with self.subTest(shares=shares):
                with patch.object(mod, "_get_api",
                                  side_effect=[GOOD, deployment(shares)]):
                    with self.assertRaises(mod.Stop):
                        mod.metadata_gate()

    def test_missing_secrets_fail_closed(self):
        for missing in ("BTDIGG_GATEWAY_TOKEN", "MAGNETRA_GATEWAY_TOKEN", "ASSETS"):
            bad = {"success": True, "result": {"id": mod.STAGED, "resources": {
                "bindings": [b for b in GOOD["result"]["resources"]["bindings"]
                             if b["name"] != missing],
            }}}
            with self.subTest(missing=missing):
                with patch.object(mod, "_get_api", side_effect=[bad, deployment()]):
                    with self.assertRaises(mod.Stop):
                        mod.metadata_gate()

    def test_explicit_old_and_new_asset_digests_are_distinct(self):
        real = (Path(__file__).resolve().parent.parent / "web" / "app.js").read_bytes()
        with patch.object(mod.source, "http_get", return_value=real) as new, \
             patch.object(mod, "get_explicit_old_asset", return_value=b"old version"):
            mod.verify_versions_immutable_assets()
            new.assert_called_once_with("/app.js", staged=True)
        with patch.object(mod.source, "http_get", return_value=b"wrong fix"), \
             patch.object(mod, "get_explicit_old_asset", return_value=b"old"):
            with self.assertRaisesRegex(mod.Stop, "DOES_NOT_MATCH_REVIEWED_CODE"):
                mod.verify_versions_immutable_assets()
        with patch.object(mod.source, "http_get", return_value=real), \
             patch.object(mod, "get_explicit_old_asset", return_value=real):
            with self.assertRaisesRegex(mod.Stop, "OVERRIDE_UNVERIFIED"):
                mod.verify_versions_immutable_assets()

    def test_canary_check_limits_to_two_original_html_sources_only(self):
        with patch.dict(os.environ, {"MAGNETRA_FIX_CANARY_E2E_ACTION": mod.ACTION}):
            with patch.object(mod, "metadata_gate", side_effect=["id1", "id1"]), \
                 patch.object(mod, "verify_versions_immutable_assets") as asset, \
                 patch.object(mod.source, "verify_provider_catalog") as catalog, \
                 patch.object(mod.source, "verify_original_sources") as originals:
                self.assertEqual(mod.execute(), 0)
                asset.assert_called_once()
                catalog.assert_called_once()
                originals.assert_called_once()

    def test_source_checks_not_attempted_if_deployment_changes(self):
        with patch.dict(os.environ, {"MAGNETRA_FIX_CANARY_E2E_ACTION": mod.ACTION}):
            with patch.object(mod, "metadata_gate", side_effect=["id1", "id2"]), \
                 patch.object(mod, "verify_versions_immutable_assets"), \
                 patch.object(mod.source, "verify_provider_catalog"), \
                 patch.object(mod.source, "verify_original_sources"):
                with self.assertRaisesRegex(mod.Stop, "DEPLOYMENT_CHANGED"):
                    mod.execute()

    def test_old_asset_override_header_pinned_to_249d(self):
        self.assertIn(mod.ACTIVE, mod.OLD_OVERRIDE)
        self.assertNotIn(mod.STAGED, mod.OLD_OVERRIDE)
        self.assertEqual(mod.OLD_OVERRIDE, 'alexlab-magnetra="' + mod.ACTIVE + '"')


if __name__ == "__main__":
    unittest.main()
