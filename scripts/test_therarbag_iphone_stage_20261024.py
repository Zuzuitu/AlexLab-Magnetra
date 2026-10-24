"""Offline fail-closed tests: TheRarBg iPhone immutable version-only stage."""
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import stage_therarbag_iphone_20261024 as stage


def payload(version, *, remove=None):
    bindings = [
        {"name": name, "type": next(iter(types))}
        for name, types in stage.EXPECTED_BINDINGS.items()
        if name != remove
    ]
    return {"success": True, "result": {"id": version,
            "resources": {"bindings": bindings}}}


class StageOnlyTests(unittest.TestCase):
    def test_exact_four_bindings_required_and_correct_version(self):
        version = stage.ACTIVE
        stage.verify_binding_payload(version, payload(version))
        for name in stage.EXPECTED_BINDINGS:
            with self.subTest(name=name), self.assertRaises(stage.Stop):
                stage.verify_binding_payload(version, payload(version, remove=name))
        with self.assertRaises(stage.Stop):
            stage.verify_binding_payload(version, payload(stage.PREVIOUS_ZERO))

    def test_invalid_and_competing_deployment_block_preflight(self):
        record = {"id": "one"}
        with patch.object(stage, "_get_api", return_value={"deployments": []}), \
             patch.object(stage, "_current_deployment", return_value=record), \
             patch.object(stage, "_shares", return_value={stage.ACTIVE: 95, stage.PREVIOUS_ZERO: 5}):
            with self.assertRaises(stage.Stop):
                stage.read_split()
        with patch.object(stage, "_get_api", return_value={"deployments": []}), \
             patch.object(stage, "_current_deployment", return_value={"id": ""}), \
             patch.object(stage, "_shares", return_value=stage.EXPECTED_SPLIT):
            with self.assertRaises(stage.Stop):
                stage.read_split()

    def test_no_activation_means_no_source_or_cloudflare_call(self):
        with patch.dict(os.environ, {"MAGNETRA_THERARBAG_IPHONE_STAGE_ACTION": ""}), \
             patch.object(stage, "validate_source") as source, \
             patch.object(stage, "guard_baseline") as cloudflare:
            self.assertEqual(stage.main(), 2)
            source.assert_not_called()
            cloudflare.assert_not_called()

    def test_upload_subcommand_is_versions_upload_only_and_config_is_ephemeral(self):
        fake = "12345678-1234-4234-8234-123456789abc"
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "stage.jsonc"
            calls = []
            def run(cmd, **opts):
                calls.append(cmd)
                self.assertEqual(cmd[3:5], ["versions", "upload"])
                self.assertIn("--keep-vars", cmd)
                self.assertNotIn("deploy", cmd)
                self.assertTrue(opts["capture_output"])
                self.assertTrue(opts["check"] is False)
                body = output.read_text()
                self.assertIn('"FLUD_RELAY"', body)
                self.assertIn('"BTDIGG_GATEWAY_TOKEN"', body)
                self.assertIn('"MAGNETRA_GATEWAY_TOKEN"', body)
                return SimpleNamespace(returncode=0,
                    stdout="Worker Version ID: " + fake, stderr="")
            with patch.object(stage, "STAGE_CONFIG", output), \
                 patch.object(stage.subprocess, "run", side_effect=run):
                got = stage.upload_only({"services": [{"binding": "FLUD_RELAY",
                    "service": "flud-remote-relay"}]})
            self.assertEqual(got, fake)
            self.assertEqual(len(calls), 1)
            self.assertFalse(output.exists())

    def test_run_does_not_change_deployment_record(self):
        ident = "12345678-1234-4234-8234-123456789abc"
        baseline = {"id": "unchanged", "versions": []}
        with patch.object(stage, "validate_source", return_value={"name": "alexlab-magnetra"}), \
             patch.object(stage, "guard_baseline", return_value=baseline), \
             patch.object(stage, "upload_only", return_value=ident) as uploader, \
             patch.object(stage, "verify_binding_payload") as verifier, \
             patch.object(stage, "_get_api", return_value=payload(ident)), \
             patch.object(stage, "read_split", return_value=baseline):
            self.assertEqual(stage.run(), 0)
            self.assertEqual(uploader.call_count, 1)
            self.assertEqual(verifier.call_count, 1)

    def test_post_upload_changed_deployment_cannot_report_success(self):
        ident = "12345678-1234-4234-8234-123456789abc"
        with patch.object(stage, "validate_source", return_value={}), \
             patch.object(stage, "guard_baseline", return_value={"id": "before"}), \
             patch.object(stage, "upload_only", return_value=ident), \
             patch.object(stage, "verify_binding_payload"), \
             patch.object(stage, "_get_api", return_value=payload(ident)), \
             patch.object(stage, "read_split", return_value={"id": "after"}):
            with self.assertRaises(stage.Stop):
                stage.run()


if __name__ == "__main__":
    unittest.main()
