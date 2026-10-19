#!/usr/bin/env python3
"""No-network, fail-closed tests for manually approved Magnetra 5% canary."""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deploy_magnetra_canary as m

OLD = "a9df4429-1111-4111-8111-111111111111"
NEW = m.VERSION
OTHER = "bbbbbbbb-1111-4111-8111-111111111111"
VERSION = {"success": True, "result": {"id": NEW, "resources": {
    "bindings": [
        {"name": "BTDIGG_GATEWAY_TOKEN", "type": "secret_text"},
        {"name": "MAGNETRA_GATEWAY_TOKEN", "type": "secret_key"},
        {"name": "ASSETS", "type": "assets"},
    ]
}}}


def deployment(shares, ident="d1"):
    return {"success": True, "result": {"deployments": [{
        "id": ident, "created_on": "2026-10-19T10:30:00Z",
        "versions": [{"version_id": k, "percentage": v} for k, v in shares.items()],
    }]}}


ZERO = deployment({OLD: 100, NEW: 0})
CANARY = deployment({OLD: 95, NEW: 5}, ident="d2")
OLD_ONLY = deployment({OLD: 100}, ident="d3")


class CanaryTests(unittest.TestCase):
    def test_missing_approval_makes_no_network_requests(self):
        with patch.dict(os.environ, {"MAGNETRA_CANARY_ACTION": "CANCEL"}):
            with patch.object(m, "_get_api") as api:
                self.assertEqual(m.execute(), 2)
                api.assert_not_called()

    def test_canary_exact_95_5(self):
        with patch.dict(os.environ, {"MAGNETRA_CANARY_ACTION": m.START}):
            with patch.object(m, "_get_api", side_effect=[VERSION, ZERO, ZERO, CANARY]):
                with patch.object(m, "_wrangler_deploy", return_value=True) as deployer:
                    self.assertEqual(m.execute(), 0)
                    deployer.assert_called_once()
                    self.assertEqual(deployer.call_args.args[0], [OLD + "@95%", NEW + "@5%"])

    def test_canary_waits_boundedly_for_cloudflare_metadata(self):
        with patch.object(m, "_get_api", side_effect=[
            VERSION, ZERO, ZERO, ZERO, CANARY,
        ]):
            with patch.object(m, "_wrangler_deploy", return_value=True):
                with patch.object(m.time, "sleep") as sleeper:
                    self.assertEqual(m.start_canary(), 0)
                    sleeper.assert_called_once_with(2)

    def test_canary_never_claims_success_from_stale_postflight(self):
        with patch.object(m, "_get_api", side_effect=[
            VERSION, ZERO, ZERO, ZERO, ZERO, ZERO, ZERO,
        ]):
            with patch.object(m, "_wrangler_deploy", return_value=True):
                with patch.object(m.time, "sleep") as sleeper:
                    self.assertEqual(m.start_canary(), 1)
                    self.assertEqual(sleeper.call_count, 3)

    def test_canary_only_starts_at_exact_100_0(self):
        with patch.object(m, "_get_api", side_effect=[VERSION, OLD_ONLY]):
            with patch.object(m, "_wrangler_deploy") as deployer:
                self.assertEqual(m.start_canary(), 2)
                deployer.assert_not_called()

    def test_missing_binding_blocks_canary(self):
        bad = {"success": True, "result": {"id": NEW, "resources": {
            "bindings": [{"name": "ASSETS", "type": "assets"}]}}}
        with patch.object(m, "_get_api", side_effect=[bad, ZERO]):
            with patch.object(m, "_wrangler_deploy") as deployer:
                self.assertEqual(m.start_canary(), 2)
                deployer.assert_not_called()

    def test_race_before_write_blocks_canary(self):
        with patch.object(m, "_get_api", side_effect=[VERSION, ZERO, CANARY]):
            with patch.object(m, "_wrangler_deploy") as deployer:
                self.assertEqual(m.start_canary(), 2)
                deployer.assert_not_called()

    def test_canary_bad_postflight_rolls_back_known_ids(self):
        split = deployment({OLD: 90, NEW: 10}, ident="d2")
        with patch.object(m, "_get_api", side_effect=[VERSION, ZERO, ZERO, split]):
            with patch.object(m, "_wrangler_deploy", return_value=True):
                with patch.object(m, "_recover", return_value=True) as recover:
                    self.assertEqual(m.start_canary(), 1)
                    recover.assert_called_once_with(OLD)

    def test_canary_does_not_rollback_unknown_concurrent_version(self):
        alien = deployment({OLD: 95, OTHER: 5}, ident="d2")
        with patch.object(m, "_get_api", side_effect=[VERSION, ZERO, ZERO, alien]):
            with patch.object(m, "_wrangler_deploy", return_value=True):
                with patch.object(m, "_recover") as recover:
                    self.assertEqual(m.start_canary(), 1)
                    recover.assert_not_called()

    def test_manual_rollback_from_canary_only(self):
        with patch.dict(os.environ, {"MAGNETRA_CANARY_ACTION": m.ROLLBACK_ACTION}):
            with patch.object(m, "_get_api", side_effect=[CANARY, CANARY]):
                with patch.object(m, "_recover", return_value=True) as recover:
                    self.assertEqual(m.execute(), 0)
                    recover.assert_called_once_with(OLD)

    def test_manual_rollback_refuses_unknown_share(self):
        alien = deployment({OLD: 85, NEW: 15})
        with patch.object(m, "_get_api", return_value=alien):
            with patch.object(m, "_recover") as recover:
                self.assertEqual(m.rollback(), 2)
                recover.assert_not_called()

    def test_manual_rollback_is_idempotent(self):
        with patch.object(m, "_get_api", return_value=OLD_ONLY):
            with patch.object(m, "_recover") as recover:
                self.assertEqual(m.rollback(), 0)
                recover.assert_not_called()

    def test_manual_rollback_from_zero_slot(self):
        with patch.object(m, "_get_api", side_effect=[ZERO, ZERO]):
            with patch.object(m, "_recover", return_value=True) as recover:
                self.assertEqual(m.rollback(), 0)
                recover.assert_called_once_with(OLD)

    def test_cannot_use_deployment_with_missing_id(self):
        missing_id = deployment({OLD: 100, NEW: 0}, ident="")
        with patch.object(m, "_get_api", side_effect=[VERSION, missing_id, missing_id]):
            with patch.object(m, "_wrangler_deploy") as deployer:
                self.assertEqual(m.start_canary(), 2)
                deployer.assert_not_called()


if __name__ == "__main__":
    unittest.main()
