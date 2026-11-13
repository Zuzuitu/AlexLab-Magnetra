#!/usr/bin/env python3
"""Offline checks for Magnetra BTDigg #262 one-shot guarded release."""
from __future__ import annotations
import os
import re
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import release_magnetra_btdigg_pacing_20261113 as release
from deploy_magnetra_auto_pause_once import Stop

class GuardedPacingReleaseTests(unittest.TestCase):
    def test_no_action_does_not_call_cloudflare(self):
        with patch.dict(os.environ,{release.ACTION_ENV:"NO",release.INSPECT_ENV:"0"}):
            with patch.object(release,"publish",side_effect=AssertionError("publish")):
                with patch.object(release,"snapshot",side_effect=AssertionError("remote")):
                    self.assertEqual(release.main(),2)

    def test_readonly_inspect_does_not_upload_or_deploy(self):
        old="12345678-1234-4123-8123-123456789abc"
        with patch.dict(os.environ,{release.ACTION_ENV:"NO",release.INSPECT_ENV:"1"}):
            with patch.object(release,"snapshot",return_value=({"id":"d"},{old:100})):
                with patch.object(release,"critical_binding_guard") as bindings:
                    with patch.object(release,"upload",side_effect=AssertionError("write")):
                        with patch.object(release,"_wrangler_deploy",side_effect=AssertionError("write")):
                            self.assertEqual(release.main(),0)
                            bindings.assert_called_once_with(old)

    def test_source_scope_pinned_to_reviewed_merge(self):
        self.assertEqual(release.REVIEWED,"437d7fa370b5558e362e718fe042e289cb12d931")
        self.assertEqual(release.REQUIRED_DIFF,release.ALLOWED_DIFF)
        self.assertEqual(len(release.FROZEN),8)
        self.assertNotIn("web/app.js",release.ALLOWED_DIFF)
        self.assertNotIn("worker/src/index.mjs",release.ALLOWED_DIFF)
        self.assertTrue(all(not p.startswith("rock64/") for p in release.ALLOWED_DIFF))
        self.assertEqual(release.EVENT,"docs/release-events/magnetra-btdigg-pacing-20261113.md")

    def test_approval_requires_exact_single_file_activation(self):
        with patch.object(release,"_git",side_effect=[
            "[magnetra-btdigg-pacing-20261113] deploy",
            "web/app.js\n"+release.EVENT]):
            with self.assertRaises(Stop):
                release.approval_baseline()
        with patch.object(release,"_git",side_effect=[
            "[unapproved-commit] deploy",release.EVENT]):
            with self.assertRaises(Stop):
                release.approval_baseline()
        event=(HERE.parent/release.EVENT).read_text()
        self.assertTrue(
            event=="status: PENDING\nexpected_active_version: PENDING\n"
            or re.fullmatch(
                r"status: APPROVED\nexpected_active_version: ("+
                release.UUID.pattern+r")\n",event,re.I
            ) is not None,
            "Only pending or explicitly approved UUID event can pass offline CI"
        )

    def test_approved_baseline_mismatch_fails_before_upload(self):
        valid="12345678-1234-4123-8123-123456789abc"
        changed="99999999-9999-4999-8999-999999999999"
        with patch.object(release,"source_guard",return_value={}):
            with patch.object(release,"snapshot",return_value=({"id":"d"},{changed:100})):
                with patch.object(release,"approval_baseline",return_value=valid):
                    with patch.object(release,"upload",side_effect=AssertionError("write")):
                        with self.assertRaises(Stop):
                            release.publish()

    def test_guarded_script_retains_immutable_rollback_and_no_source_queries(self):
        code=(HERE/"release_magnetra_btdigg_pacing_20261113.py").read_text()
        for phrase in ("candidate_baseline(shares)","critical_binding_guard(old)",
                       "verify_all_assets(new,zero_dep,zero)",
                       "verify_public_with_html_settle(full_dep,full)",
                       "rollback_if_safe(old,new)","catalog_guard(new)",
                       "--keep-vars","APPROVED_CLOUDFLARE_BASELINE_CHANGED"):
            self.assertIn(phrase,code)
        self.assertNotIn("audit-live-providers.py",code)
        self.assertNotIn('"/api/search"',code)

    def test_workflow_only_owner_marker_can_deploy(self):
        y=(HERE.parent/".github/workflows/magnetra-btdigg-pacing-20261113.yml").read_text()
        self.assertIn("startsWith(github.event.head_commit.message, '[magnetra-btdigg-pacing-20261113] ')",y)
        self.assertIn("github.ref == 'refs/heads/main'",y)
        self.assertIn("cancel-in-progress: false",y)
        self.assertIn("fetch-depth: 0",y)
        self.assertNotIn("workflow_dispatch",y)
        self.assertIn("MAGNETRA_BTDIGG_PACING_READONLY_INSPECT: '1'",y)
        self.assertIn("MAGNETRA_BTDIGG_PACING_RELEASE_ACTION: CONFIRM_MAGNETRA_BTDIGG_PACING_20261113_RELEASE",y)

if __name__=="__main__":
    unittest.main()
