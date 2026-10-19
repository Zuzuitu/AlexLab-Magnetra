#!/usr/bin/env python3
"""Offline safety cases for exact Magnetra 249d 100 / 540b 0 manual slot."""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deploy_magnetra_fix_zero_slot as mod

PREVIOUS = "a9df4429-1111-4111-8111-111111111111"
UNEXPECTED = "bbbbbbbb-1111-4111-8111-111111111111"
GOOD_BINDINGS = [
    {"name": "BTDIGG_GATEWAY_TOKEN", "type": "secret_text"},
    {"name": "MAGNETRA_GATEWAY_TOKEN", "type": "secret_key"},
    {"name": "ASSETS", "type": "assets"},
]
VERSION = {"success": True, "result": {
    "id": mod.STAGED, "resources": {"bindings": GOOD_BINDINGS}
}}


def cloudflare_deploy(shares, ident="original"):
    return {"success": True, "result": {"deployments": [{
        "id": ident, "created_on": "2026-10-19T19:00:00Z",
        "versions": [{"version_id": k, "percentage": v} for k, v in shares.items()],
    }]}}


ORIGINAL = cloudflare_deploy({mod.CURRENT: 100, PREVIOUS: 0})
SLOT = cloudflare_deploy({mod.CURRENT: 100, mod.STAGED: 0}, "slot")
WRONG = cloudflare_deploy({mod.CURRENT: 96, mod.STAGED: 4}, "wrong")


class GuardedZeroSlotTests(unittest.TestCase):
    def test_cancel_never_calls_cloudflare(self):
        with patch.dict(os.environ, {"MAGNETRA_FIX_ZERO_ACTION": "CANCEL"}):
            with patch.object(mod, "_get_api") as get:
                with patch.object(mod, "_wrangler_deploy") as write:
                    self.assertEqual(mod.execute(), 2)
                    get.assert_not_called()
                    write.assert_not_called()

    def test_exact_original_100_0_applies_exact_two_versions_only(self):
        with patch.dict(os.environ, {"MAGNETRA_FIX_ZERO_ACTION": mod.APPROVAL}):
            with patch.object(mod, "_get_api",
                              side_effect=[VERSION, ORIGINAL, ORIGINAL, SLOT]):
                with patch.object(mod, "_wrangler_deploy", return_value=True) as write:
                    self.assertEqual(mod.execute(), 0)
                    write.assert_called_once()
                    self.assertEqual(write.call_args.args[0],
                                     [mod.CURRENT + "@100%", mod.STAGED + "@0%"])

    def test_old_active_only_100_is_allowed_without_fake_previous_version(self):
        start = cloudflare_deploy({mod.CURRENT: 100})
        with patch.dict(os.environ, {"MAGNETRA_FIX_ZERO_ACTION": mod.APPROVAL}):
            with patch.object(mod, "_get_api",
                              side_effect=[VERSION, start, start, SLOT]):
                with patch.object(mod, "_wrangler_deploy", return_value=True) as write:
                    self.assertEqual(mod.execute(), 0)
                    self.assertEqual(write.call_args.args[0],
                                     [mod.CURRENT + "@100%", mod.STAGED + "@0%"])

    def test_missing_secret_fails_before_write(self):
        for missing in ("BTDIGG_GATEWAY_TOKEN", "MAGNETRA_GATEWAY_TOKEN", "ASSETS"):
            with self.subTest(missing=missing):
                version = {"success": True, "result": {"id": mod.STAGED,
                    "resources": {"bindings": [
                        x for x in GOOD_BINDINGS if x["name"] != missing
                    ]}}}
                with patch.dict(os.environ, {"MAGNETRA_FIX_ZERO_ACTION": mod.APPROVAL}):
                    with patch.object(mod, "_get_api", side_effect=[version, ORIGINAL]):
                        with patch.object(mod, "_wrangler_deploy") as write:
                            self.assertEqual(mod.execute(), 2)
                            write.assert_not_called()

    def test_wrong_current_split_and_unknown_version_refused(self):
        for shares in (
            {mod.CURRENT: 95, PREVIOUS: 5},
            {mod.CURRENT: 90, mod.STAGED: 10},
            {UNEXPECTED: 100},
            {mod.CURRENT: 100, UNEXPECTED: 0},
        ):
            with self.subTest(shares=shares):
                deployment = cloudflare_deploy(shares)
                with patch.dict(os.environ, {"MAGNETRA_FIX_ZERO_ACTION": mod.APPROVAL}):
                    with patch.object(mod, "_get_api",
                                      side_effect=[VERSION, deployment]):
                        with patch.object(mod, "_wrangler_deploy") as write:
                            self.assertEqual(mod.execute(), 2)
                            write.assert_not_called()

    def test_race_before_write_refuses_mutation(self):
        changed = cloudflare_deploy({mod.CURRENT: 100, PREVIOUS: 0}, "changed")
        with patch.dict(os.environ, {"MAGNETRA_FIX_ZERO_ACTION": mod.APPROVAL}):
            with patch.object(mod, "_get_api",
                              side_effect=[VERSION, ORIGINAL, changed]):
                with patch.object(mod, "_wrangler_deploy") as write:
                    self.assertEqual(mod.execute(), 2)
                    write.assert_not_called()

    def test_postflight_metadata_propagation_is_bounded(self):
        with patch.dict(os.environ, {"MAGNETRA_FIX_ZERO_ACTION": mod.APPROVAL}):
            with patch.object(mod, "_get_api",
                              side_effect=[VERSION, ORIGINAL, ORIGINAL, ORIGINAL, SLOT]):
                with patch.object(mod, "_wrangler_deploy", return_value=True):
                    with patch.object(mod.time, "sleep") as sleep:
                        self.assertEqual(mod.execute(), 0)
                        sleep.assert_called_once_with(2)

    def test_no_false_success_if_cli_did_not_confirm(self):
        with patch.dict(os.environ, {"MAGNETRA_FIX_ZERO_ACTION": mod.APPROVAL}):
            with patch.object(mod, "_get_api",
                              side_effect=[VERSION, ORIGINAL, ORIGINAL, SLOT]):
                with patch.object(mod, "_wrangler_deploy", return_value=False):
                    self.assertEqual(mod.execute(), 1)

    def test_wrong_known_shares_attempt_guarded_rollback(self):
        with patch.dict(os.environ, {"MAGNETRA_FIX_ZERO_ACTION": mod.APPROVAL}):
            with patch.object(mod, "_get_api",
                              side_effect=[VERSION, ORIGINAL, ORIGINAL, WRONG]):
                with patch.object(mod, "_wrangler_deploy", return_value=True):
                    with patch.object(mod, "guarded_restore") as rollback:
                        self.assertEqual(mod.execute(), 1)
                        rollback.assert_called_once()

    def test_unknown_concurrent_state_never_force_rolls_back(self):
        weird = cloudflare_deploy({UNEXPECTED: 100}, "unknown")
        with patch.dict(os.environ, {"MAGNETRA_FIX_ZERO_ACTION": mod.APPROVAL}):
            with patch.object(mod, "_get_api",
                              side_effect=[VERSION, ORIGINAL, ORIGINAL, weird]):
                with patch.object(mod, "_wrangler_deploy", return_value=True):
                    with patch.object(mod, "guarded_restore") as rollback:
                        self.assertEqual(mod.execute(), 1)
                        rollback.assert_not_called()

    def test_guarded_restore_of_wrong_known_version_split(self):
        safe = cloudflare_deploy({mod.CURRENT: 100, mod.STAGED: 0}, "new-slot")
        with patch.object(mod, "_get_api", side_effect=[WRONG, WRONG, safe]):
            with patch.object(mod, "_wrangler_deploy", return_value=True) as write:
                self.assertTrue(mod.guarded_restore())
                self.assertEqual(write.call_args.args[0],
                                 [mod.CURRENT + "@100%", mod.STAGED + "@0%"])

    def test_guarded_restore_refuses_unknown_version(self):
        rogue = cloudflare_deploy({mod.CURRENT: 60, UNEXPECTED: 40}, "rogue")
        with patch.object(mod, "_get_api", return_value=rogue):
            with patch.object(mod, "_wrangler_deploy") as write:
                self.assertFalse(mod.guarded_restore())
                write.assert_not_called()


if __name__ == "__main__":
    unittest.main()
