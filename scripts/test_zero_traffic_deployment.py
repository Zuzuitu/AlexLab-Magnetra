#!/usr/bin/env python3
"""Fail-closed tests for owner-approved 100%/0% Cloudflare version slot."""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deploy_magnetra_zero_percent as m

OLD = "a9df4429-1111-4111-8111-111111111111"
NEW = m.VERSION
SECRETS = [{"name": n, "type": t} for n,t in
           (("BTDIGG_GATEWAY_TOKEN", "secret_text"),
            ("MAGNETRA_GATEWAY_TOKEN", "secret_text"),
            ("ASSETS", "assets"))]
VERSION_JSON = {"success": True, "result": {"id": NEW, "resources": {"bindings": SECRETS}}}


def deploy(shares, stamp="2026-10-17T16:10:00Z", identifier="d1"):
    return {"success": True, "result": {"deployments": [
        {"id": identifier, "created_on": stamp, "versions":
            [{"version_id": i, "percentage": p} for i,p in shares.items()]}]}}


OLD_DEP = deploy({OLD: 100})
NEW_DEP = deploy({OLD: 100, NEW: 0}, identifier="d2")
BAD_DEP = deploy({OLD: 99.99, NEW: 0.01}, identifier="d3")


class GateTests(unittest.TestCase):
    def test_explicit_exact_zero_slot(self):
        self.assertTrue(m._is_target({OLD: 100, NEW: 0}, OLD))
        self.assertFalse(m._is_target({OLD: 99.99, NEW: 0.01}, OLD))
        self.assertFalse(m._is_target({OLD: 100}, OLD))

    def test_percentage_schema_accept_zero_only_for_target(self):
        self.assertEqual(m._shares(m._current_deployment(NEW_DEP)), {OLD: 100, NEW: 0})
        with self.assertRaises(ValueError):
            m._shares({"versions": [{"version_id": OLD, "percentage": 99}]})

    def test_mutation_requires_manual_confirmation(self):
        with patch.dict(os.environ, {"MAGNETRA_EXPLICIT_ZERO_PERCENT_APPROVAL": "CANCEL"}):
            with patch.object(m, "_get_api") as getter:
                self.assertEqual(m.execute(), 2)
                getter.assert_not_called()

    def test_preflight_blocked_without_binding(self):
        wrong = {"success": True, "result": {"id": NEW, "resources": {"bindings": SECRETS[:1]}}}
        with patch.dict(os.environ, {"MAGNETRA_EXPLICIT_ZERO_PERCENT_APPROVAL": "CONFIRM_OLD_100_NEW_0"}):
            with patch.object(m, "_get_api", side_effect=[wrong, OLD_DEP]):
                with patch.object(m, "_wrangler_deploy") as deployer:
                    self.assertEqual(m.execute(), 2)
                    deployer.assert_not_called()

    def test_success_exact_old100_new0(self):
        with patch.dict(os.environ, {"MAGNETRA_EXPLICIT_ZERO_PERCENT_APPROVAL": "CONFIRM_OLD_100_NEW_0"}):
            with patch.object(m, "_get_api", side_effect=[VERSION_JSON, OLD_DEP, OLD_DEP, NEW_DEP]):
                with patch.object(m, "_wrangler_deploy", return_value=True) as d:
                    self.assertEqual(m.execute(), 0)
                    self.assertEqual(d.call_count, 1)
                    self.assertEqual(d.call_args.args[0], [OLD + "@100%", NEW + "@0%"])

    def test_unsupported_zero_never_falls_back(self):
        with patch.dict(os.environ, {"MAGNETRA_EXPLICIT_ZERO_PERCENT_APPROVAL": "CONFIRM_OLD_100_NEW_0"}):
            with patch.object(m, "_get_api", side_effect=[VERSION_JSON, OLD_DEP, OLD_DEP, OLD_DEP, OLD_DEP]):
                with patch.object(m, "_wrangler_deploy", return_value=False) as d:
                    self.assertEqual(m.execute(), 1)
                    self.assertEqual(d.call_count, 1)
                    self.assertNotIn("@0.01%", str(d.call_args_list))

    def test_invalid_split_triggers_rollback(self):
        with patch.dict(os.environ, {"MAGNETRA_EXPLICIT_ZERO_PERCENT_APPROVAL": "CONFIRM_OLD_100_NEW_0"}):
            with patch.object(m, "_get_api", side_effect=[
                VERSION_JSON, OLD_DEP, OLD_DEP, BAD_DEP, BAD_DEP, OLD_DEP]):
                with patch.object(m, "_wrangler_deploy", side_effect=[True, True]) as d:
                    self.assertEqual(m.execute(), 1)
                    self.assertEqual(d.call_count, 2)
                    self.assertEqual(d.call_args_list[1].args[0], [OLD + "@100%"])

    def test_unknown_concurrent_version_not_force_reverted(self):
        unknown = "bbbbbbbb-1111-4111-8111-111111111111"
        with patch.object(m, "_get_api", return_value=deploy({unknown: 100})):
            with patch.object(m, "_wrangler_deploy") as d:
                self.assertFalse(m._recover(OLD))
                d.assert_not_called()


if __name__ == "__main__":
    unittest.main()
