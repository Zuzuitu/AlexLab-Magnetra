#!/usr/bin/env python3
"""Offline authorization/rollback and exact baseline tests for bilingual release."""
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import release_magnetra_ro_it_12 as m

NEW="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
DEP0={"id":"baseline"}
DEP1={"id":"slot"}
DEP5={"id":"canary"}
DEP100={"id":"full"}
SLOT={m.ACTIVE:100, NEW:0}
CANARY={m.ACTIVE:95,NEW:5}
FULL={m.ACTIVE:0, NEW:100}

class ReleaseGuards(unittest.TestCase):
    def approved(self):
        with patch.dict(os.environ,{"MAGNETRA_RO_IT_12_RELEASE_ACTION":m.ACTION}):
            return m.main()

    def test_no_marker_makes_no_cloudflare_calls(self):
        with patch.dict(os.environ,{"MAGNETRA_RO_IT_12_RELEASE_ACTION":"CANCEL"}), \
             patch.object(m,"current") as current, \
             patch.object(m,"_wrangler_deploy") as deploy:
            self.assertEqual(m.main(),2)
            current.assert_not_called()
            deploy.assert_not_called()

    def test_historical_12_picker_release_must_refuse_current_45_picker(self):
        # Historical one-shot deployment must NEVER upload a new 45-indexer
        # UI under the obsolete 12-indexer activation marker.
        with self.assertRaisesRegex(m.Stop,"REVIEWED_RO_IT_12_PICKER_SOURCE_MISMATCH"):
            m.guard_source()

    def reviewed_historical_config(self):
        # Synthetic reviewed baseline for offline rollout/rollback simulations.
        # The actual guard_source above always remains fail-closed on current main.
        return {"name":"alexlab-magnetra","main":"src/index.mjs",
                "routes":[{"pattern":"index.alexlab.media","custom_domain":True}],
                "assets":{"directory":"../web","binding":"ASSETS"}}

    def test_unexpected_live_split_must_not_upload(self):
        with patch.object(m,"current",side_effect=m.Stop("UNKNOWN_LIVE_SPLIT")), \
             patch.object(m,"upload_version") as upload, \
             patch.object(m,"_wrangler_deploy") as write:
            self.assertEqual(self.approved(),1)
            upload.assert_not_called()
            write.assert_not_called()

    def test_positive_stage_canary_full_checks_i18n_and_46_catalog(self):
        with patch.object(m,"guard_source",return_value=self.reviewed_historical_config()), \
             patch.object(m,"current",return_value=DEP0) as current, \
             patch.object(m,"bindings"), patch.object(m,"old_js_guard") as sha, \
             patch.object(m,"stable"),patch.object(m,"upload_version",return_value=NEW), \
             patch.object(m,"_wrangler_deploy",side_effect=[True,True,True]) as writes, \
             patch.object(m,"wait_for",side_effect=[DEP1,DEP5,DEP100]), \
             patch.object(m,"verify_all_assets") as assets, \
             patch.object(m,"verify_public_with_html_settle") as settled, \
             patch.object(m,"catalog_guard") as catalog:
            self.assertEqual(self.approved(),0)
            current.assert_called_once_with(m.INITIAL)
            sha.assert_called_once()
            self.assertEqual([c.args[0] for c in writes.call_args_list],[
                [m.ACTIVE+"@100%", NEW+"@0%"],
                [m.ACTIVE+"@95%", NEW+"@5%"],
                [m.ACTIVE+"@0%", NEW+"@100%"]
            ])
            self.assertEqual([c.args for c in assets.call_args_list],[
                (NEW,DEP1,SLOT),(NEW,DEP5,CANARY)
            ])
            settled.assert_called_once_with(DEP100,FULL)
            self.assertEqual([c.args[0] for c in catalog.call_args_list],[NEW,None])

    def test_new_assets_mismatch_ends_before_canary(self):
        with patch.object(m,"guard_source",return_value=self.reviewed_historical_config()), \
             patch.object(m,"current",return_value=DEP0), \
             patch.object(m,"bindings"),patch.object(m,"old_js_guard"), \
             patch.object(m,"stable"),patch.object(m,"upload_version",return_value=NEW), \
             patch.object(m,"_wrangler_deploy",return_value=True) as writes, \
             patch.object(m,"wait_for",return_value=DEP1), \
             patch.object(m,"verify_all_assets",side_effect=m.Stop("TRANSLATION_ASSET_SHA_MISMATCH")), \
             patch.object(m,"rollback_if_safe") as rollback:
            self.assertEqual(self.approved(),1)
            writes.assert_called_once()
            rollback.assert_called_once_with(NEW)

    def test_canary_fail_rollback_requires_exact_split(self):
        with patch.object(m,"snapshot",return_value=(DEP5,CANARY)), \
             patch.object(m,"bindings"),patch.object(m,"stable"), \
             patch.object(m,"_wrangler_deploy",return_value=True) as write, \
             patch.object(m,"wait_for",return_value=DEP0) as wait:
            m.rollback_if_safe(NEW)
            write.assert_called_once()
            self.assertEqual(write.call_args.args[0],[m.ACTIVE+"@100%", NEW+"@0%"])
            wait.assert_called_once_with(DEP5,CANARY,SLOT,True)

    def test_unknown_or_concurrent_split_refuses_rollback(self):
        with patch.object(m,"snapshot",return_value=(DEP100,{m.ACTIVE:50,NEW:50})), \
             patch.object(m,"_wrangler_deploy") as write:
            m.rollback_if_safe(NEW)
            write.assert_not_called()

    def test_original_baseline_never_rewritten_by_rollback(self):
        with patch.object(m,"snapshot",return_value=(DEP0,m.INITIAL)), \
             patch.object(m,"_wrangler_deploy") as write:
            m.rollback_if_safe(NEW)
            write.assert_not_called()

    def test_http_200_html_settle_only_after_exact_mismatch(self):
        with patch.object(m,"verify_all_assets",side_effect=[m.Stop(m.HTML_200_MISMATCH),None]) as assets, \
             patch.object(m,"stable") as stable, \
             patch.object(m.time,"sleep") as sleep:
            m.verify_public_with_html_settle(DEP100,FULL)
            self.assertEqual(assets.call_count,2)
            stable.assert_called_once_with(DEP100,FULL)
            sleep.assert_called_once_with(8)

    def test_transport_error_never_retries(self):
        for reason in ("HTML_ROOT_TRANSPORT_NO_RETRY","TRANSLATION_ASSET_TRANSPORT_NO_RETRY","ASSET_SHA_MISMATCH_/app.js"):
            with self.subTest(reason=reason), \
                 patch.object(m,"verify_all_assets",side_effect=m.Stop(reason)) as assets, \
                 patch.object(m.time,"sleep") as sleep:
                with self.assertRaises(m.Stop):
                    m.verify_public_with_html_settle(DEP100,FULL)
                assets.assert_called_once()
                sleep.assert_not_called()

    def test_full_html_settle_has_five_waits_then_stops(self):
        with patch.object(m,"verify_all_assets",side_effect=m.Stop(m.HTML_200_MISMATCH)) as assets, \
             patch.object(m,"stable") as stable, \
             patch.object(m.time,"sleep") as sleep:
            with self.assertRaises(m.Stop):
                m.verify_public_with_html_settle(DEP100,FULL)
            self.assertEqual(assets.call_count,6)
            self.assertEqual(stable.call_count,5)
            self.assertEqual(sleep.call_count,5)

    def test_i18n_override_must_have_valid_immutable_version_id(self):
        with patch.object(m.urllib.request,"build_opener") as opener:
            with self.assertRaisesRegex(m.Stop,"UNVERIFIED_LANGUAGE_ASSET_OVERRIDE_VERSION"):
                m.read_i18n("not-a-uuid")
            opener.assert_not_called()

if __name__=="__main__":
    unittest.main()
