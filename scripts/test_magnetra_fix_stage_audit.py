#!/usr/bin/env python3
"""Synthetic no-network guard tests for staged Magnetra Resolve fix metadata."""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import inspect_magnetra_fix_stage as mod

OLD = "a9df4429-1111-4111-8111-111111111111"
OTHER = "bbbbbbbb-1111-4111-8111-111111111111"
GOOD_BINDINGS = [
    {"name": "BTDIGG_GATEWAY_TOKEN", "type": "secret_text", "value": "PRIVATE-BTDIGG"},
    {"name": "MAGNETRA_GATEWAY_TOKEN", "type": "secret_key", "value": "PRIVATE-MAGNETRA"},
    {"name": "ASSETS", "type": "assets", "value": "PRIVATE-ASSETS"},
]


def version(bindings=GOOD_BINDINGS, *, vid=mod.STAGED):
    return {"success": True, "result": {"id": vid, "resources": {"bindings": bindings}}}


def deployments(shares):
    return {"success": True, "result": {"deployments": [{
        "id": "deploy-20261019", "created_on": "2026-10-19T17:54:00Z",
        "versions": [{"version_id": vid, "percentage": pct}
                     for vid, pct in shares.items()],
    }]}}


class ReadOnlyStageGateTests(unittest.TestCase):
    def test_two_version_old_zero_production_is_safe(self):
        lines, passed = mod.audit(version(), deployments({mod.ACTIVE: 100, OLD: 0}))
        self.assertTrue(passed)
        self.assertIn("STAGE_GATE", "STAGE_GATE")
        self.assertIn("NEW_540B_VERSION_NOT_DEPLOYED: PASS", lines)
        self.assertIn("CURRENT_PRODUCTION_249D_100_PERCENT: PASS", lines)
        self.assertIn("BTDIGG_GATEWAY_TOKEN: PASS", lines)
        self.assertIn("MAGNETRA_GATEWAY_TOKEN: PASS", lines)
        self.assertIn("ASSETS: PASS", lines)
        self.assertNotIn("PRIVATE-BTDIGG", "\n".join(lines))
        self.assertNotIn("PRIVATE-MAGNETRA", "\n".join(lines))

    def test_active_only_100_production_is_also_safe(self):
        _, ok = mod.audit(version(), deployments({mod.ACTIVE: 100}))
        self.assertTrue(ok)

    def test_binding_dict_format_is_supported(self):
        bindings = {b["name"]: {"type": b["type"]} for b in GOOD_BINDINGS}
        self.assertTrue(mod.audit(version(bindings), deployments({mod.ACTIVE: 100}))[1])

    def test_missing_any_binding_fails_closed(self):
        for name in ("BTDIGG_GATEWAY_TOKEN", "MAGNETRA_GATEWAY_TOKEN", "ASSETS"):
            with self.subTest(name=name):
                items = [b for b in GOOD_BINDINGS if b["name"] != name]
                lines, ok = mod.audit(version(items), deployments({mod.ACTIVE: 100, OLD: 0}))
                self.assertFalse(ok)
                self.assertIn(name + ": UNVERIFIED", lines)

    def test_wrong_staged_version_never_passes(self):
        self.assertFalse(mod.audit(version(vid=OTHER), deployments({mod.ACTIVE: 100}))[1])

    def test_any_new_version_live_traffic_or_zero_slot_is_refused(self):
        for shares in (
            {mod.ACTIVE: 99, mod.STAGED: 1},
            {mod.ACTIVE: 100, mod.STAGED: 0},
            {mod.STAGED: 100, mod.ACTIVE: 0},
            {mod.ACTIVE: 90, OLD: 10},
            {OTHER: 100},
            {mod.ACTIVE: 100, OTHER: 0},
            {mod.ACTIVE: 100, OLD: 0, mod.STAGED: 0},
        ):
            with self.subTest(shares=shares):
                self.assertFalse(mod.audit(version(), deployments(shares))[1])

    def test_unverified_api_does_not_leak_payloads(self):
        secret = "DO_NOT_PRINT_PRIVATE"
        lines, ok = mod.audit({"success": False, "secret": secret},
                              deployments({mod.ACTIVE: 100}))
        self.assertFalse(ok)
        self.assertNotIn(secret, "\n".join(lines))
        lines, ok = mod.audit(version(), {"success": False, "body": secret})
        self.assertFalse(ok)
        self.assertNotIn(secret, "\n".join(lines))

    def test_main_performs_exactly_two_gets_and_no_writes(self):
        with patch.object(mod, "_get_api", side_effect=[
            version(), deployments({mod.ACTIVE: 100, OLD: 0})
        ]) as get:
            self.assertEqual(mod.main(), 0)
            self.assertEqual([call.args[0] for call in get.call_args_list], [
                "/versions/" + mod.STAGED, "/deployments",
            ])


if __name__ == "__main__":
    unittest.main()
