"""Fail-closed offline tests for the 27 October TPB 429 manual-only release."""
import inspect
import os
import unittest
from unittest.mock import patch
import release_tpb_429_guarded_20261027 as release

ACTIVE="40bfd647-2b8a-4643-94f2-577e723aba97"
ROLLBACK="74754dac-1842-47b2-8e6f-92a10731f124"

class TPB429ReleaseGuards(unittest.TestCase):
    def test_current_known_immutable_baseline(self):
        self.assertEqual(release.BASELINE,{ACTIVE:100,ROLLBACK:0})
        self.assertEqual(release.ACTIVE,ACTIVE)
        self.assertEqual(release.ROLLBACK,ROLLBACK)
        self.assertEqual(release.OLD_PUBLIC_GIT_BLOB,"2d6735e0fc98f61820c746cfa34ec380cf497248")

    def test_requires_explicit_manual_approval(self):
        with patch.dict(os.environ,{"MAGNETRA_TPB_429_RELEASE_ACTION":""}):
            with patch.object(release,"release") as do_release:
                self.assertEqual(release.main(),2)
                do_release.assert_not_called()
        self.assertEqual(release.ACTION,"CONFIRM_MAGNETRA_TPB_429_GUARDED_20261027")

    def test_disallowed_api_and_external_origin_are_rejected_without_network(self):
        for path in ("/api/search", "/api/companion/status", "//evil.example","/api/search?q=ubuntu&providers=thepiratebay"):
            with self.assertRaises(release.Stop):
                release.candidate_http(path,"11111111-1111-4111-8111-111111111111")

    def test_release_has_no_automatic_tpb_or_btdigg_searches(self):
        code=inspect.getsource(release.release)
        self.assertNotIn("prove_original_positive_searches",code)
        self.assertNotIn("thepiratebay",code)
        self.assertNotIn("POSITIVE_PATHS",inspect.getsource(release.candidate_http))
        self.assertIn("verify_candidate(NEW)",code)
        self.assertIn("public_postflight(NEW)",code)

    def test_read_only_preflight_stops_before_upload_when_baseline_differs(self):
        with patch.object(release,"source_guard",return_value={}), \
             patch.object(release,"split_guard",side_effect=release.Stop("UNKNOWN_SPLIT")), \
             patch.object(release,"upload") as upload:
            with self.assertRaises(release.Stop):
                release.release()
            upload.assert_not_called()

    def test_preview_error_does_not_override_unknown_split(self):
        with patch.object(release,"snapshot",return_value=(object(),{ACTIVE:88,ROLLBACK:12})), \
             patch.object(release,"_wrangler_deploy") as change, \
             patch.object(release,"verify_binding_payload") as verify:
            release.rollback_if_safe("11111111-1111-4111-8111-111111111111")
            change.assert_not_called()
            verify.assert_not_called()

    def test_both_source_and_immutable_binding_guard_in_script(self):
        text=inspect.getsource(release)
        self.assertIn("verify_binding_payload(NEW,_get_api",text)
        self.assertIn("stable(first,BASELINE)",text)
        self.assertIn("TPB_429_SOURCE_GUARDS_MISMATCH",text)
        self.assertIn("TPB_DEFAULT_COOLDOWN_MS=60_000",text)
        self.assertIn("cloudflare_html_asset_guard",text)
        self.assertIn("_wrangler_deploy",text)

if __name__=="__main__":
    unittest.main()
