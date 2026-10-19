#!/usr/bin/env python3
"""Offline fail-closed unit cases for manual exact-version 5% Resolve canary."""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deploy_magnetra_fix_canary_5 as mod

OTHER = "bbbbbbbb-1111-4111-8111-111111111111"
VERSION = {"success": True, "result": {"id": mod.STAGED, "resources": {"bindings": [
    {"name": "BTDIGG_GATEWAY_TOKEN", "type": "secret_text"},
    {"name": "MAGNETRA_GATEWAY_TOKEN", "type": "secret_key"},
    {"name": "ASSETS", "type": "assets"},
]}}}


def record(shares, id="zero"):
    return {"success": True, "result": {"deployments": [{
        "id": id, "created_on": "2026-10-19T19:32:00Z",
        "versions": [{"version_id": k, "percentage": v} for k, v in shares.items()],
    }]}}


ZERO = record(mod.ZERO)
FIVE = record(mod.FIVE, id="five")


class CanaryTests(unittest.TestCase):
    def test_no_explicit_approval_no_cloudflare_calls(self):
        with patch.dict(os.environ, {"MAGNETRA_FIX_CANARY_ACTION": "CANCEL"}):
            with patch.object(mod, "_get_api") as api, \
                 patch.object(mod, "_wrangler_deploy") as deploy:
                self.assertEqual(mod.execute(), 2)
                api.assert_not_called()
                deploy.assert_not_called()

    def test_exact_owner_5percent_with_three_bindings(self):
        with patch.dict(os.environ, {"MAGNETRA_FIX_CANARY_ACTION": mod.CANARY}):
            with patch.object(mod, "_get_api", side_effect=[
                VERSION, ZERO, ZERO, FIVE
            ]):
                with patch.object(mod, "_wrangler_deploy", return_value=True) as deploy:
                    self.assertEqual(mod.execute(), 0)
                    deploy.assert_called_once()
                    self.assertEqual(deploy.call_args.args[0], [
                        mod.ACTIVE + "@95%", mod.STAGED + "@5%"
                    ])

    def test_cloudflare_postflight_eventual_consistency_without_second_write(self):
        with patch.object(mod, "_get_api", side_effect=[
            VERSION, ZERO, ZERO, ZERO, FIVE,
        ]), patch.object(mod, "_wrangler_deploy", return_value=True) as deploy, \
             patch.object(mod.time, "sleep") as sleep:
            self.assertEqual(mod.activate_canary(), 0)
            sleep.assert_called_once_with(2)
            deploy.assert_called_once()

    def test_bad_binding_aborts_without_write(self):
        for omitted in ("BTDIGG_GATEWAY_TOKEN", "MAGNETRA_GATEWAY_TOKEN", "ASSETS"):
            bad = {"success": True, "result": {"id": mod.STAGED, "resources": {
                "bindings": [b for b in VERSION["result"]["resources"]["bindings"]
                             if b["name"] != omitted],
            }}}
            with self.subTest(omitted=omitted):
                with patch.object(mod, "_get_api", return_value=bad), \
                     patch.object(mod, "_wrangler_deploy") as deploy:
                    self.assertEqual(mod.activate_canary(), 2)
                    deploy.assert_not_called()

    def test_bad_slot_or_unrecognized_version_aborts_without_write(self):
        for shares in (
            {mod.ACTIVE: 95, mod.STAGED: 5},
            {mod.ACTIVE: 100},
            {mod.STAGED: 100, mod.ACTIVE: 0},
            {mod.ACTIVE: 100, OTHER: 0},
        ):
            with self.subTest(shares=shares):
                with patch.object(mod, "_get_api", side_effect=[
                    VERSION, record(shares)
                ]), patch.object(mod, "_wrangler_deploy") as deploy:
                    self.assertEqual(mod.activate_canary(), 2)
                    deploy.assert_not_called()

    def test_concurrent_deployment_before_write_fails_closed(self):
        changed = record(mod.ZERO, id="changed")
        with patch.object(mod, "_get_api", side_effect=[
            VERSION, ZERO, changed,
        ]), patch.object(mod, "_wrangler_deploy") as deploy:
            self.assertEqual(mod.activate_canary(), 2)
            deploy.assert_not_called()

    def test_metadata_still_zero_cannot_claim_canary(self):
        with patch.object(mod, "_get_api", side_effect=[
            VERSION, ZERO, ZERO, ZERO, ZERO, ZERO, ZERO
        ]), patch.object(mod, "_wrangler_deploy", return_value=True) as deploy, \
             patch.object(mod.time, "sleep") as sleep:
            self.assertEqual(mod.activate_canary(), 1)
            self.assertEqual(sleep.call_count, 3)
            deploy.assert_called_once()

    def test_failed_cli_but_canary_visible_cannot_claim_verified(self):
        with patch.object(mod, "_get_api", side_effect=[
            VERSION, ZERO, ZERO, FIVE
        ]), patch.object(mod, "_wrangler_deploy", return_value=False) as deploy, \
             patch.object(mod, "safe_restore") as restore:
            self.assertEqual(mod.activate_canary(), 1)
            deploy.assert_called_once()
            restore.assert_not_called()

    def test_unsafe_known_split_auto_restores(self):
        bad = record({mod.ACTIVE: 89, mod.STAGED: 11}, id="bad")
        with patch.object(mod, "_get_api", side_effect=[
            VERSION, ZERO, ZERO, bad
        ]), patch.object(mod, "_wrangler_deploy", return_value=True), \
             patch.object(mod, "safe_restore", return_value=True) as restore:
            self.assertEqual(mod.activate_canary(), 1)
            restore.assert_called_once()

    def test_unknown_split_does_not_automatically_restore(self):
        weird = record({mod.ACTIVE: 95, OTHER: 5}, id="unknown")
        with patch.object(mod, "_get_api", side_effect=[
            VERSION, ZERO, ZERO, weird
        ]), patch.object(mod, "_wrangler_deploy", return_value=True), \
             patch.object(mod, "safe_restore") as restore:
            self.assertEqual(mod.activate_canary(), 1)
            restore.assert_not_called()

    def test_owner_manual_rollback_only_from_known_canary(self):
        with patch.dict(os.environ, {"MAGNETRA_FIX_CANARY_ACTION": mod.RESTORE}):
            with patch.object(mod, "_get_api", return_value=FIVE), \
                 patch.object(mod, "safe_restore", return_value=True) as restore:
                self.assertEqual(mod.execute(), 0)
                restore.assert_called_once()
            with patch.object(mod, "_get_api", return_value=ZERO), \
                 patch.object(mod, "safe_restore") as restore:
                self.assertEqual(mod.execute(), 0)
                restore.assert_not_called()
            with patch.object(mod, "_get_api", return_value=record({
                mod.ACTIVE: 90, mod.STAGED: 10,
            })), patch.object(mod, "safe_restore") as restore:
                self.assertEqual(mod.execute(), 2)
                restore.assert_not_called()

    def test_safe_restore_exact_known_ids(self):
        with patch.object(mod, "_get_api", side_effect=[
            FIVE, FIVE, ZERO
        ]), patch.object(mod, "_wrangler_deploy", return_value=True) as deploy:
            self.assertTrue(mod.safe_restore())
            self.assertEqual(deploy.call_args.args[0], [
                mod.ACTIVE + "@100%", mod.STAGED + "@0%"
            ])

    def test_safe_restore_unknown_id_not_modified(self):
        bad = record({mod.ACTIVE: 95, OTHER: 5})
        with patch.object(mod, "_get_api", return_value=bad), \
             patch.object(mod, "_wrangler_deploy") as deploy:
            self.assertFalse(mod.safe_restore())
            deploy.assert_not_called()


if __name__ == "__main__":
    unittest.main()
