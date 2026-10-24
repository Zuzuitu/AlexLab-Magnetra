"""Offline fail-closed owner-approved TheRarBg production diagnostic release tests."""
import hashlib
import os
import unittest
from pathlib import Path
from unittest.mock import patch, call

import release_therarbag_iphone_diagnostic_20261024 as rel


class ReleaseTests(unittest.TestCase):
    def test_no_owner_activation_means_zero_network_or_deploy(self):
        with patch.dict(os.environ, {"MAGNETRA_IPHONE_DIAGNOSTIC_RELEASE_ACTION": ""}), \
             patch.object(rel, "release") as run, \
             patch.object(rel, "rollback_if_known") as rollback:
            self.assertEqual(rel.main(), 2)
            run.assert_not_called()
            rollback.assert_not_called()

    def test_versions_and_exact_percentage_math(self):
        self.assertEqual(rel.EXPECTED_SPLIT[rel.ACTIVE], 100)
        self.assertEqual(rel.EXPECTED_SPLIT[rel.PREVIOUS_ZERO], 0)
        self.assertEqual(rel.SLOT, {rel.ACTIVE: 100, rel.NEW: 0})
        self.assertEqual(rel.CANARY, {rel.ACTIVE: 95, rel.NEW: 5})
        self.assertEqual(rel.FULL, {rel.ACTIVE: 0, rel.NEW: 100})
        self.assertNotEqual(rel.NEW, rel.ACTIVE)

    def test_preflight_checks_all_four_bindings_for_three_versions(self):
        record = {"id": "baseline"}
        with patch.object(rel, "validated_source"), \
             patch.object(rel, "validate_source"), \
             patch.object(rel, "account_list", return_value={}), \
             patch.object(rel, "verify_account_scripts"), \
             patch.object(rel, "current", return_value=record) as current, \
             patch.object(rel, "_get_api", return_value={}), \
             patch.object(rel, "verify_binding_payload") as binding, \
             patch.object(rel, "stable") as stable:
            self.assertEqual(rel.before_any_write(), record)
            current.assert_called_once_with(rel.EXPECTED_SPLIT)
            self.assertEqual([c.args[0] for c in binding.call_args_list],
                             [rel.ACTIVE, rel.PREVIOUS_ZERO, rel.NEW])
            stable.assert_called_once_with(record, rel.EXPECTED_SPLIT)

    def test_transition_refuses_wrangle_failure_and_does_not_claim_success(self):
        old = {"id": "baseline"}
        with patch.object(rel, "stable") as stable, \
             patch.object(rel, "_wrangler_deploy", return_value=False) as deploy, \
             patch.object(rel, "wait_for") as postflight:
            with self.assertRaises(rel.Stop):
                rel.transition(old, rel.EXPECTED_SPLIT, rel.SLOT, "ZERO_SLOT")
            stable.assert_called_once_with(old, rel.EXPECTED_SPLIT)
            deploy.assert_called_once()
            self.assertEqual(deploy.call_args.args[0],
                             [rel.ACTIVE + "@100%", rel.NEW + "@0%"])
            postflight.assert_not_called()

    def test_exact_version_only_staged_canary_full_sequence(self):
        original = {"id": "orig"}
        zero = {"id": "zero"}
        canary = {"id": "canary"}
        full = {"id": "full"}
        with patch.object(rel, "before_any_write", return_value=original), \
             patch.object(rel, "http", return_value=b"old different JS"), \
             patch.object(rel, "stable") as stable, \
             patch.object(rel, "transition", side_effect=[zero, canary, full]) as transitions, \
             patch.object(rel, "version_checks") as version_check, \
             patch.object(rel, "diagnostic_checks") as diagnostic, \
             patch.object(rel, "public_checks") as public:
            self.assertEqual(rel.release(), 0)
            self.assertEqual(
                [(args.args[1], args.args[2]) for args in transitions.call_args_list],
                [(rel.EXPECTED_SPLIT, rel.SLOT),
                 (rel.SLOT, rel.CANARY),
                 (rel.CANARY, rel.FULL)],
            )
            version_check.assert_has_calls([call(rel.NEW), call(rel.NEW)])
            self.assertEqual(version_check.call_count, 2)
            diagnostic.assert_called_once_with(rel.NEW)
            public.assert_called_once_with()
            stable.assert_any_call(full, rel.FULL)

    def test_invalid_http_path_refuses_egress(self):
        with self.assertRaises(rel.Stop):
            rel.http("/api/companion/magnet")
        with self.assertRaises(rel.Stop):
            rel.http("/api/search?q=anything")
        with self.assertRaises(rel.Stop):
            rel.http("/api/resolve", body={"provider": "invalid"},
                     version="f"*36)
        with self.assertRaises(rel.Stop):
            rel.http("/api/health", body={})

    def test_probe_requires_exact_optin_diagnostic(self):
        good = {"build": "THERARBAG_IPHONE_DIAG_V1",
                "htmlStage": "HTML_NO_BTIH", "jsonStage": "JSON_HTTP_503",
                "elapsedMs": 100, "detailFingerprint": "abcdef012345"}
        with patch.object(rel, "http", return_value=(502, {
                "code": "DETAIL_NO_BTIH", "diagnostic": good})) as http:
            rel.diagnostic_checks(rel.NEW)
            self.assertEqual(http.call_args.kwargs["body"]["details"], rel.ORIGINAL)
            self.assertTrue(http.call_args.kwargs["diagnostic"])
        for bad in ({"diagnostic": {}},
                    {"diagnostic": dict(good, htmlStage="PRIVATE_DATA")},
                    {"diagnostic": dict(good, detailFingerprint="long-or-raw-source")},
                    {"diagnostic": dict(good, elapsedMs=50000)}):
            with self.subTest(bad=bad), patch.object(rel, "http", return_value=(502, bad)):
                with self.assertRaises(rel.Stop):
                    rel.diagnostic_checks(rel.NEW)

    def test_rollback_only_at_recognized_canary_or_full(self):
        for split in (rel.CANARY, rel.FULL):
            with self.subTest(split=split), \
                 patch.object(rel, "snapshot", return_value=({"id": "old"}, split)), \
                 patch.object(rel, "_get_api", return_value={}), \
                 patch.object(rel, "verify_binding_payload"), \
                 patch.object(rel, "stable"), \
                 patch.object(rel, "_wrangler_deploy", return_value=True) as deploy, \
                 patch.object(rel, "wait_for", return_value={"id": "new"}):
                rel.rollback_if_known()
                self.assertEqual(deploy.call_args.args[0],
                                 [rel.ACTIVE + "@100%", rel.NEW + "@0%"])
        for split in (rel.EXPECTED_SPLIT, rel.SLOT, {rel.ACTIVE: 70, rel.NEW: 30}):
            with self.subTest(split=split), \
                 patch.object(rel, "snapshot", return_value=({"id": "old"}, split)), \
                 patch.object(rel, "_wrangler_deploy") as deploy:
                rel.rollback_if_known()
                deploy.assert_not_called()

    def test_main_rolls_back_on_guarded_runtime_failure(self):
        with patch.dict(os.environ, {"MAGNETRA_IPHONE_DIAGNOSTIC_RELEASE_ACTION": rel.ACTION}), \
             patch.object(rel, "release", side_effect=rel.Stop("private")) as release, \
             patch.object(rel, "rollback_if_known") as rb:
            self.assertEqual(rel.main(), 1)
            release.assert_called_once_with()
            rb.assert_called_once_with()

    def test_source_has_no_version_upload_no_generic_deploy_no_secret_write(self):
        src = (Path(__file__).resolve().parent /
               "release_therarbag_iphone_diagnostic_20261024.py").read_text()
        self.assertIn("_wrangler_deploy", src)
        self.assertNotIn("subprocess.run(", src)
        self.assertNotIn("versions upload", src)
        self.assertNotIn("versions secrets", src)
        self.assertNotIn("--keep-vars", src)


if __name__ == "__main__":
    unittest.main()
