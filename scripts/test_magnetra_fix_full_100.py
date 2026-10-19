#!/usr/bin/env python3
"""No-network regression safety for 249d95/540b5 -> 249d0/540b100."""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deploy_magnetra_fix_full_100 as mod

OTHER = "bbbbbbbb-1111-4111-8111-111111111111"
BINDINGS = [
    {"name": "BTDIGG_GATEWAY_TOKEN", "type": "secret_text"},
    {"name": "MAGNETRA_GATEWAY_TOKEN", "type": "secret_key"},
    {"name": "ASSETS", "type": "assets"},
]


def version(ident, bindings=BINDINGS):
    return {"success": True, "result": {"id": ident, "resources": {"bindings": bindings}}}


def deployment(shares, ident="five"):
    return {"success": True, "result": {"deployments": [{
        "id": ident, "created_on": "2026-10-19T21:03:00Z",
        "versions": [{"version_id": key, "percentage": value}
                     for key, value in shares.items()],
    }]}}


class FixFullReleaseTests(unittest.TestCase):
    def test_cancel_does_not_read_cloudflare_or_write(self):
        with patch.dict(os.environ, {"MAGNETRA_FIX_FULL_ACTION": "CANCEL"}), \
             patch.object(mod, "_get_api") as api, \
             patch.object(mod, "_wrangler_deploy") as wrangler:
            self.assertEqual(mod.execute(), 2)
            api.assert_not_called()
            wrangler.assert_not_called()

    def test_both_immutable_versions_require_all_three_binding_types(self):
        for ident in (mod.ACTIVE, mod.STAGED):
            with patch.object(mod, "_get_api", return_value=version(ident)):
                mod.verify_bindings(ident)
            for omitted in ("ASSETS", "BTDIGG_GATEWAY_TOKEN", "MAGNETRA_GATEWAY_TOKEN"):
                bad = [v for v in BINDINGS if v["name"] != omitted]
                with self.subTest(version=ident, omitted=omitted):
                    with patch.object(mod, "_get_api", return_value=version(ident, bad)):
                        with self.assertRaises(mod.Stop):
                            mod.verify_bindings(ident)
        with patch.object(mod, "_get_api") as api:
            with self.assertRaises(mod.Stop):
                mod.verify_bindings(OTHER)
            api.assert_not_called()

    def test_preflight_checks_real_sources_and_unchanged_deployment(self):
        with patch.object(mod, "_get_api", side_effect=[
            version(mod.ACTIVE), version(mod.STAGED),
            deployment(mod.FIVE), deployment(mod.FIVE),
        ]), patch.object(mod.canary, "verify_versions_immutable_assets") as assets, \
             patch.object(mod.canary.source, "verify_provider_catalog") as catalog, \
             patch.object(mod.canary.source, "verify_original_sources") as sources, \
             patch.object(mod, "_wrangler_deploy") as wrangler:
            self.assertEqual(mod.read_only_preflight()["id"], "five")
            assets.assert_called_once()
            catalog.assert_called_once()
            sources.assert_called_once()
            wrangler.assert_not_called()

    def test_missing_canary_or_third_version_is_refused(self):
        for shares in ({mod.ACTIVE: 100, mod.STAGED: 0},
                       {mod.ACTIVE: 90, mod.STAGED: 10},
                       {mod.ACTIVE: 95, OTHER: 5},
                       {mod.ACTIVE: 0, mod.STAGED: 100}):
            with self.subTest(shares=shares):
                with patch.object(mod, "_get_api", side_effect=[
                    version(mod.ACTIVE), version(mod.STAGED), deployment(shares),
                ]), patch.object(mod.canary, "verify_versions_immutable_assets") as assets, \
                     patch.object(mod, "_wrangler_deploy") as wrangler:
                    with self.assertRaises(mod.Stop):
                        mod.read_only_preflight()
                    assets.assert_not_called()
                    wrangler.assert_not_called()

    def test_new_deployment_id_race_refused(self):
        with patch.object(mod, "snapshot", return_value=({"id": "changed"}, mod.FIVE)):
            with self.assertRaisesRegex(mod.Stop, "CONCURRENT"):
                mod.verify_stable({"id": "old"}, mod.FIVE)

    def test_source_failure_aborts_before_write(self):
        with patch.object(mod, "read_only_preflight", side_effect=mod.Stop("SOURCE_ERROR")), \
             patch.object(mod, "_wrangler_deploy") as wrangler, \
             patch.dict(os.environ, {"MAGNETRA_FIX_FULL_ACTION": mod.PROMOTE}):
            self.assertEqual(mod.execute(), 1)
            wrangler.assert_not_called()

    def test_release_exact_two_versions_and_public_100_percent_js(self):
        real = (Path(__file__).resolve().parent.parent / "web" / "app.js").read_bytes()
        with patch.dict(os.environ, {"MAGNETRA_FIX_FULL_ACTION": mod.PROMOTE}), \
             patch.object(mod, "read_only_preflight", return_value={"id": "five"}), \
             patch.object(mod, "verify_stable"), \
             patch.object(mod, "_wrangler_deploy", return_value=True) as wrangler, \
             patch.object(mod, "confirm_postflight", return_value=True) as post, \
             patch.object(mod, "verify_bindings"), \
             patch.object(mod.canary, "verify_versions_immutable_assets"), \
             patch.object(mod.canary.source, "verify_provider_catalog"), \
             patch.object(mod.canary.source, "http_get", return_value=real):
            self.assertEqual(mod.execute(), 0)
            self.assertEqual(wrangler.call_args.args[0], [
                mod.ACTIVE + "@0%", mod.STAGED + "@100%",
            ])
            post.assert_called_once_with("five", mod.FIVE, mod.FULL, True)

    def test_public_asset_mismatch_cannot_claim_success(self):
        with patch.object(mod, "read_only_preflight", return_value={"id": "five"}), \
             patch.object(mod, "verify_stable"), \
             patch.object(mod, "_wrangler_deploy", return_value=True), \
             patch.object(mod, "confirm_postflight", return_value=True), \
             patch.object(mod, "verify_bindings"), \
             patch.object(mod.canary, "verify_versions_immutable_assets"), \
             patch.object(mod.canary.source, "verify_provider_catalog"), \
             patch.object(mod.canary.source, "http_get", return_value=b"old"), \
             patch.object(mod, "snapshot", return_value=({"id": "full"}, mod.FULL)), \
             patch.object(mod.time, "sleep") as sleep:
            with self.assertRaisesRegex(mod.Stop, "PUBLIC_ASSET_UNVERIFIED"):
                mod.promote()
            self.assertEqual(sleep.call_count, 3)

    def test_public_asset_converges_after_two_read_only_checks(self):
        reviewed = (Path(__file__).resolve().parent.parent / "web" / "app.js").read_bytes()
        with patch.object(mod, "read_only_preflight", return_value={"id": "five"}), \
             patch.object(mod, "verify_stable"), \
             patch.object(mod, "_wrangler_deploy", return_value=True) as wrangler, \
             patch.object(mod, "confirm_postflight", return_value=True), \
             patch.object(mod, "verify_bindings"), \
             patch.object(mod.canary, "verify_versions_immutable_assets"), \
             patch.object(mod.canary.source, "verify_provider_catalog"), \
             patch.object(mod.canary.source, "http_get", side_effect=[b"old", reviewed]) as http, \
             patch.object(mod, "snapshot", return_value=({"id": "full"}, mod.FULL)), \
             patch.object(mod.time, "sleep") as sleep:
            self.assertEqual(mod.promote(), 0)
            self.assertEqual(http.call_count, 2)
            sleep.assert_called_once_with(2)
            wrangler.assert_called_once()

    def test_post_deployment_id_changes_during_asset_poll_refused(self):
        with patch.object(mod, "read_only_preflight", return_value={"id": "five"}), \
             patch.object(mod, "verify_stable"), \
             patch.object(mod, "_wrangler_deploy", return_value=True) as wrangler, \
             patch.object(mod, "confirm_postflight", return_value=True), \
             patch.object(mod, "verify_bindings"), \
             patch.object(mod.canary, "verify_versions_immutable_assets"), \
             patch.object(mod.canary.source, "verify_provider_catalog"), \
             patch.object(mod.canary.source, "http_get", return_value=b"old"), \
             patch.object(mod, "snapshot", side_effect=[
                 ({"id": "first"}, mod.FULL), ({"id": "other"}, mod.FULL),
             ]), patch.object(mod.time, "sleep"):
            with self.assertRaisesRegex(mod.Stop, "DEPLOYMENT_CHANGED"):
                mod.promote()
            wrangler.assert_called_once()

    def test_postflight_proves_new_deployment_not_just_existing_target(self):
        with patch.object(mod, "snapshot", return_value=({"id": "new"}, mod.FULL)):
            self.assertTrue(mod.confirm_postflight("old", mod.FIVE, mod.FULL, True))
            with self.assertRaisesRegex(mod.Stop, "WRITE_UNVERIFIED"):
                mod.confirm_postflight("old", mod.FIVE, mod.FULL, False)
        with patch.object(mod, "snapshot", return_value=({"id": "old"}, mod.FULL)):
            with self.assertRaises(mod.Stop):
                mod.confirm_postflight("old", mod.FIVE, mod.FULL, True)

    def test_bounded_get_wait_without_second_write(self):
        with patch.object(mod, "snapshot", side_effect=[
            ({"id": "old"}, mod.FIVE), ({"id": "new"}, mod.FULL),
        ]), patch.object(mod.time, "sleep") as sleep, \
             patch.object(mod, "_wrangler_deploy") as wrangler:
            self.assertTrue(mod.confirm_postflight("old", mod.FIVE, mod.FULL, True))
            sleep.assert_called_once_with(2)
            wrangler.assert_not_called()

    def test_unknown_split_after_write_refuses_speculative_rollback(self):
        with patch.object(mod, "snapshot", return_value=(
                {"id": "unknown"}, {mod.ACTIVE: 90, mod.STAGED: 10})), \
             patch.object(mod, "_wrangler_deploy") as wrangler:
            with self.assertRaisesRegex(mod.Stop, "UNEXPECTED_TRAFFIC_SPLIT"):
                mod.confirm_postflight("old", mod.FIVE, mod.FULL, True)
            wrangler.assert_not_called()

    def test_manual_rollback_only_from_exact_full_promotion(self):
        with patch.dict(os.environ, {"MAGNETRA_FIX_FULL_ACTION": mod.RESTORE}), \
             patch.object(mod, "verify_bindings"), \
             patch.object(mod, "snapshot", return_value=({"id": "full"}, mod.FULL)), \
             patch.object(mod, "verify_stable"), \
             patch.object(mod, "_wrangler_deploy", return_value=True) as wrangler, \
             patch.object(mod, "confirm_postflight", return_value=True):
            self.assertEqual(mod.execute(), 0)
            self.assertEqual(wrangler.call_args.args[0], [
                mod.ACTIVE + "@100%", mod.STAGED + "@0%",
            ])
        with patch.object(mod, "verify_bindings"), \
             patch.object(mod, "snapshot", return_value=({"id": "five"}, mod.FIVE)), \
             patch.object(mod, "_wrangler_deploy") as wrangler:
            with self.assertRaises(mod.Stop):
                mod.rollback()
            wrangler.assert_not_called()

    def test_rollback_already_safe_makes_zero_writes(self):
        with patch.object(mod, "verify_bindings"), \
             patch.object(mod, "snapshot", return_value=({"id": "zero"}, mod.ZERO)), \
             patch.object(mod, "_wrangler_deploy") as wrangler:
            self.assertEqual(mod.rollback(), 0)
            wrangler.assert_not_called()


if __name__ == "__main__":
    unittest.main()
