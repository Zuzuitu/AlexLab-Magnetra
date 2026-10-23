"""Offline smoke tests for the GET-only Cloudflare binding inspection."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inspect_companion_binding_readonly import (Stop, audit_version_and_deployment,
                                                  verify_account_scripts)


def versions(version, bindings):
    return {"success": True, "result": {
        "id": version, "resources": {"bindings": [
            {"name": name, "type": kind} for name, kind in bindings
        ]}
    }}


class CompanionBindingInspectionTests(unittest.TestCase):
    A = "a088fa41-233d-48d3-bd4c-52be6194fda8"
    B = "056d8394-79b0-459a-b93e-b5f5a8a7295d"
    OLD = [
        ("ASSETS", "assets"),
        ("BTDIGG_GATEWAY_TOKEN", "secret_text"),
        ("MAGNETRA_GATEWAY_TOKEN", "secret_text"),
    ]

    def deployment(self):
        return {"success": True, "result": {"deployments": [{
            "id": "safe-deployment", "created_on": "2026-10-23T10:00:00Z",
            "versions": [
                {"version_id": self.A, "percentage": 100},
                {"version_id": self.B, "percentage": 0},
            ]
        }]}}

    def test_confirms_both_script_names_under_single_account(self):
        verify_account_scripts({"success": True, "result": [
            {"id": "alexlab-magnetra"}, {"id": "flud-remote-relay"}, {"id": "another"}
        ]})

    def test_rejects_missing_relay_script(self):
        with self.assertRaises(Stop):
            verify_account_scripts({"success": True, "result": [{"id": "alexlab-magnetra"}]})

    def test_old_three_binding_baseline_is_safe_and_not_misrepresented(self):
        ident, dep, bound = audit_version_and_deployment(
            versions(self.A, self.OLD), self.deployment())
        self.assertEqual(ident, self.A)
        self.assertEqual(dep, "safe-deployment")
        self.assertFalse(bound)

    def test_fourth_service_binding_is_recognized_without_losing_old_bindings(self):
        _, _, bound = audit_version_and_deployment(
            versions(self.A, self.OLD + [("FLUD_RELAY", "service")]), self.deployment())
        self.assertTrue(bound)

    def test_fails_closed_on_missing_original_gateway_secret_binding(self):
        with self.assertRaises(Stop):
            audit_version_and_deployment(versions(self.A, self.OLD[:-1]), self.deployment())

    def test_fails_closed_when_version_response_does_not_match_active(self):
        with self.assertRaises(Stop):
            audit_version_and_deployment(versions(self.B, self.OLD), self.deployment())


if __name__ == "__main__":
    unittest.main()
