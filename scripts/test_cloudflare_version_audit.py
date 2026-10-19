#!/usr/bin/env python3
"""Tests verify the audit refuses missing bindings and never leaks secret values."""
import importlib.util
import sys
import unittest
from pathlib import Path

p = Path(__file__).with_name("inspect_cloudflare_version.py")
spec = importlib.util.spec_from_file_location("magnetra_cf_audit", p)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

OLD = "a9df4429-1111-4111-8111-111111111111"
NEW = mod.VERSION
GOOD = [{"name": "BTDIGG_GATEWAY_TOKEN", "type": "secret_text", "text": "SECRET_DO_NOT_PRINT"},
        {"name": "MAGNETRA_GATEWAY_TOKEN", "type": "secret_text", "text": "OTHER_PRIVATE"},
        {"name": "ASSETS", "type": "assets"}]


def v(bindings=GOOD):
    return {"success": True, "result": {"id": NEW, "resources": {"bindings": bindings}}}


def dep(versions):
    return {"success": True, "result": {"deployments": [
        {"created_on": "2026-10-17T08:01:00Z", "versions": [{"version_id": OLD, "percentage": 100}]},
        {"created_on": "2026-10-17T08:15:00Z", "versions": versions}]}}


class AuditTest(unittest.TestCase):
    def test_success_no_leaks(self):
        lines, ok = mod.audit(v(), dep([{"version_id": OLD, "percentage": 100}]))
        self.assertTrue(ok)
        self.assertNotIn("SECRET_DO_NOT_PRINT", "\n".join(lines))
        self.assertNotIn("OTHER_PRIVATE", "\n".join(lines))

    def test_exact_two_version_zero_slot_passes(self):
        lines, ok = mod.audit(v(), dep([
            {"version_id": OLD, "percentage": 100},
            {"version_id": NEW, "percentage": 0},
        ]))
        self.assertTrue(ok)
        self.assertIn("ROLLBACK_ACTIVE_100_PERCENT: PASS", lines)
        self.assertIn("CANDIDATE_NO_TRAFFIC: PASS", lines)
        self.assertIn("ZERO_PERCENT_SLOT: PRESENT", lines)
        self.assertNotIn("SECRET_DO_NOT_PRINT", "\n".join(lines))
        self.assertNotIn("OTHER_PRIVATE", "\n".join(lines))

    def test_exact_slot_order_does_not_matter(self):
        lines, ok = mod.audit(v(), dep([
            {"version_id": NEW, "percentage": 0.0},
            {"version_id": OLD, "percentage": 100.0},
        ]))
        self.assertTrue(ok)
        self.assertIn("ZERO_PERCENT_SLOT: PRESENT", lines)

    def test_legacy_old_only_still_passes(self):
        lines, ok = mod.audit(v(), dep([
            {"version_id": OLD, "percentage": 100},
        ]))
        self.assertTrue(ok)
        self.assertIn("ZERO_PERCENT_SLOT: ABSENT", lines)

    def test_five_percent_canary_requires_different_gate(self):
        lines, ok = mod.audit(v(), dep([
            {"version_id": OLD, "percentage": 95},
            {"version_id": NEW, "percentage": 5},
        ]))
        self.assertFalse(ok)
        self.assertIn("CANDIDATE_NO_TRAFFIC: FAIL", lines)

    def test_reject_duplicate_version_or_unknown_slot(self):
        unknown = "bbbbbbbb-1111-4111-8111-111111111111"
        bad_shares = [
            [{"version_id": OLD, "percentage": 100},
             {"version_id": OLD, "percentage": 0}],
            [{"version_id": OLD, "percentage": 100},
             {"version_id": unknown, "percentage": 0}],
            [{"version_id": OLD, "percentage": 100},
             {"version_id": NEW, "percentage": 0},
             {"version_id": unknown, "percentage": 0}],
        ]
        for bad in bad_shares:
            with self.subTest(bad=bad):
                self.assertFalse(mod.audit(v(), dep(bad))[1])

    def test_reject_invalid_percentage_types_and_totals(self):
        for pct in (-1, 0.01, True, "0", None, 101):
            with self.subTest(pct=pct):
                self.assertFalse(mod.audit(v(), dep([
                    {"version_id": OLD, "percentage": 100},
                    {"version_id": NEW, "percentage": pct},
                ]))[1])

    def test_missing_secret(self):
        self.assertFalse(mod.audit(v(GOOD[1:]), dep([{"version_id": OLD, "percentage": 100}]))[1])

    def test_missing_assets(self):
        self.assertFalse(mod.audit(v(GOOD[:2]), dep([{"version_id": OLD, "percentage": 100}]))[1])

    def test_candidate_receives_one_percent(self):
        self.assertFalse(mod.audit(v(), dep([
            {"version_id": OLD, "percentage": 99}, {"version_id": NEW, "percentage": 1}]))[1])

    def test_fail_closed_on_unexpected_api(self):
        lines, ok = mod.audit({"success": False, "token": "PRIVATE_SECRET"}, {})
        self.assertFalse(ok)
        self.assertNotIn("PRIVATE_SECRET", "\n".join(lines))

    def test_keyed_bindings(self):
        item = {b["name"]: {"type": b["type"]} for b in GOOD}
        self.assertTrue(mod.audit(v(item), dep([{"version_id": OLD, "percentage": 100}]))[1])


if __name__ == "__main__":
    unittest.main()
