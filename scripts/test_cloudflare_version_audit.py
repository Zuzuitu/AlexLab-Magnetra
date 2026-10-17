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
