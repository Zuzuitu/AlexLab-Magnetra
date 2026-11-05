#!/usr/bin/env python3
"""Offline tests for one-shot BTDigg rate-limit PWA release. Zero Cloudflare."""
from __future__ import annotations
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import release_magnetra_btdigg_429_20261105 as release
from deploy_magnetra_auto_pause_once import Stop

class Guarded429ReleaseTests(unittest.TestCase):
    def test_requires_exact_action_before_calling_source_guard(self):
        with patch.dict(os.environ,{"MAGNETRA_BTDIGG_429_ACTION":"NO"},clear=False):
            with patch.object(release,"publish",side_effect=AssertionError("Must not publish")):
                self.assertEqual(release.main(),2)
        with patch.dict(os.environ,{"MAGNETRA_BTDIGG_429_ACTION":"NO"},clear=False):
            with patch.object(release,"source_guard",side_effect=AssertionError("Must not inspect remote")):
                self.assertEqual(release.main(),2)
    def test_base_sha_pinned_and_source_scope_minimal(self):
        self.assertEqual(release.REVIEWED,"7dfdd1bc8c84b83bdb5ea5ea06bfb030d4c8b457")
        self.assertEqual(release.REQUIRED_DIFF,{"web/app.js","web/i18n.js","web/sw.js"})
        self.assertTrue(release.REQUIRED_DIFF.issubset(release.ALLOWED_DIFF))
        self.assertTrue(all(not p.startswith("rock64/") for p in release.ALLOWED_DIFF))
        self.assertTrue(all(not p.startswith("app/") for p in release.ALLOWED_DIFF))
        self.assertFalse(any("token" in p for p in release.ALLOWED_DIFF))
    def test_existing_safe_version_rollback_reused(self):
        src=(HERE/"release_magnetra_btdigg_429_20261105.py").read_text()
        for guard in ("candidate_baseline(shares)","critical_binding_guard(old)",
                      "verify_all_assets(new,zero_dep,zero)",
                      "verify_public_with_html_settle(full_dep,full)",
                      "rollback_if_safe(old,new)",
                      "catalog_guard(new)","stable(full_dep,full)",
                      "--keep-vars","NO_BTDIGG_UPSTREAM_QUERIES_BY_RELEASE"):
            self.assertIn(guard,src)
        self.assertNotIn("audit-live-providers",src)
        self.assertNotIn("/api/search",src)
    def test_concurrent_unverified_split_rejected(self):
        with self.assertRaises(Stop):
            release.candidate_baseline({"invalid":50,"also-invalid":50})
    def test_workflow_release_marker_not_on_pr_or_generic_push(self):
        path=HERE.parent/".github/workflows/magnetra-btdigg-429-release-20261105.yml"
        text=path.read_text()
        self.assertIn("startsWith(github.event.head_commit.message, '[magnetra-btdigg-429-20261105] ')",text)
        self.assertIn("github.ref == 'refs/heads/main'",text)
        self.assertIn("cancel-in-progress: false",text)
        self.assertNotIn("workflow_dispatch",text)
        self.assertIn("fetch-depth: 0",text)
    def test_all_source_paths_still_available_for_rollback(self):
        s=(HERE.parent/"web/app.js").read_text()
        sw=(HERE.parent/"web/sw.js").read_text()
        self.assertIn("recordBTDigg429",s)
        self.assertIn("RATE_LIMIT_COOLDOWN",s)
        self.assertIn("alexlab-magnetra-v15",sw)

if __name__=="__main__": unittest.main()
