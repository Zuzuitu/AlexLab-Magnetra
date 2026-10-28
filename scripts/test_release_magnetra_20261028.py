#!/usr/bin/env python3
"""Offline, no-network safety gates for one-shot #226 controlled publication."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import release_magnetra_20261028 as mod

OLD = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
ZERO = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"

class Release226Tests(unittest.TestCase):
    def test_no_owner_approval_does_not_query_cloudflare(self):
        with patch.dict(mod.os.environ, {}, clear=True):
            with patch.object(mod, "snapshot") as cloud:
                self.assertEqual(mod.main(), 2)
                cloud.assert_not_called()

    def test_requires_single_100_percent_version(self):
        self.assertEqual(mod.candidate_baseline({OLD:100}), OLD)
        self.assertEqual(mod.candidate_baseline({OLD:100, ZERO:0}), OLD)
        for bad in ({OLD:95,ZERO:5},{OLD:0,ZERO:100, "extra":0},
                    {OLD:99.9,ZERO:0.1},{OLD:50,ZERO:50},{}):
            with self.subTest(bad=bad):
                with self.assertRaises(mod.Stop):
                    mod.candidate_baseline(bad)

    def test_rollback_does_not_touch_unknown_external_deployment(self):
        with patch.object(mod, "snapshot", return_value=({"id":"snap"},{OLD:90,ZERO:10})):
            with patch.object(mod, "_wrangler_deploy") as write:
                mod.rollback_if_safe(OLD,ZERO)
                write.assert_not_called()

    def test_zero_stage_does_not_write_rollback(self):
        with patch.object(mod, "snapshot", return_value=({"id":"snap"},{OLD:100,ZERO:0})):
            with patch.object(mod, "_wrangler_deploy") as write:
                mod.rollback_if_safe(OLD,ZERO)
                write.assert_not_called()

    def test_fail_closed_missing_service_binding(self):
        with patch.object(mod, "bindings"):
            with patch.object(mod, "_get_api", return_value={"result":{"resources":{"bindings":[]}}}):
                with self.assertRaises(mod.Stop):
                    mod.critical_binding_guard(OLD)

    def test_repo_allowlist_and_old_sha_pinned(self):
        self.assertEqual(len(mod.REVIEWED),40)
        self.assertIn("worker/test/indexer-curation.test.mjs",mod.EXPECTED_DIFF)
        self.assertIn("web/app.js",mod.EXPECTED_DIFF)
        self.assertEqual(len(mod.REQUIRED_SECRETS),2)

if __name__ == "__main__":
    unittest.main()
