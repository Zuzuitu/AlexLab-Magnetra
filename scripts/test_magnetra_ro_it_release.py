#!/usr/bin/env python3
"""Offline tests for uniquely approved one-shot curated indexer UI release."""
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import release_magnetra_ro_it_12 as m

NEW = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
FIRST = {"id":"first"}
SLOT_DEP = {"id":"zero"}
CANARY_DEP = {"id":"canary"}
FULL_DEP = {"id":"full"}
SLOT = {m.ACTIVE:100,NEW:0}
CANARY = {m.ACTIVE:95,NEW:5}
FULL = {m.ACTIVE:0,NEW:100}


class CuratedReleaseSafety(unittest.TestCase):
    def test_without_unique_approval_no_mutation_or_cloudflare_read(self):
        with patch.dict(os.environ,{"MAGNETRA_RO_IT_12_ACTION":"CANCEL"}), \
             patch.object(m,"current") as read, \
             patch.object(m,"_wrangler_deploy") as write:
            self.assertEqual(m.main(),2)
            read.assert_not_called()
            write.assert_not_called()

    def test_reviewed_identity_config_and_visible_picker_are_present(self):
        config = m.identity_guard()
        self.assertEqual(config["name"],"alexlab-magnetra")
        self.assertEqual(config["assets"]["binding"],"ASSETS")
        self.assertIn("index.alexlab.media",str(config["routes"]))

    def test_unexpected_current_distribution_stops_before_upload(self):
        with patch.object(m,"current",side_effect=m.Stop("UNEXPECTED_LIVE_DEPLOYMENT_SPLIT")), \
             patch.object(m,"upload_version") as upload, \
             patch.object(m,"_wrangler_deploy") as write:
            self.assertEqual(m.main() if os.environ.get("MAGNETRA_RO_IT_12_ACTION")==m.ACTION else self._approved(),1)
            upload.assert_not_called()
            write.assert_not_called()

    @staticmethod
    def _approved():
        with patch.dict(os.environ,{"MAGNETRA_RO_IT_12_ACTION":m.ACTION}):
            return m.main()

    def test_full_flow_stage_and_canary_then_full_100(self):
        with patch.object(m,"current",return_value=FIRST) as current, \
             patch.object(m,"bindings") as bindings, \
             patch.object(m,"active_asset_guard") as old_hash, \
             patch.object(m,"stable"), \
             patch.object(m,"upload_version",return_value=NEW), \
             patch.object(m,"_wrangler_deploy",side_effect=[True,True,True]) as writes, \
             patch.object(m,"wait_for",side_effect=[SLOT_DEP,CANARY_DEP,FULL_DEP]), \
             patch.object(m,"verify_reviewed_assets") as assets, \
             patch.object(m,"catalog_guard") as catalog, \
             patch.object(m,"settle_public") as settled:
            self.assertEqual(self._approved(),0)
            current.assert_called_once_with(m.INITIAL)
            old_hash.assert_called_once()
            self.assertEqual(writes.call_count,3)
            self.assertEqual(
                [x.args[0] for x in writes.call_args_list],
                [
                    [m.ACTIVE+"@100%",NEW+"@0%"],
                    [m.ACTIVE+"@95%",NEW+"@5%"],
                    [m.ACTIVE+"@0%",NEW+"@100%"],
                ])
            self.assertEqual(assets.call_count,3)
            assets.assert_any_call(NEW,SLOT_DEP,SLOT)
            assets.assert_any_call(NEW,CANARY_DEP,CANARY)
            settled.assert_called_once_with(FULL_DEP,FULL)
            self.assertEqual([x.args[0] for x in catalog.call_args_list],[NEW,None])
            self.assertEqual(bindings.call_count,6)

    def test_zero_slot_failed_asset_verification_blocks_canary(self):
        with patch.object(m,"current",return_value=FIRST), \
             patch.object(m,"bindings"), \
             patch.object(m,"active_asset_guard"), \
             patch.object(m,"stable"), \
             patch.object(m,"upload_version",return_value=NEW), \
             patch.object(m,"_wrangler_deploy",return_value=True) as writes, \
             patch.object(m,"wait_for",return_value=SLOT_DEP), \
             patch.object(m,"verify_reviewed_assets",side_effect=m.Stop("STATIC_SHA_UNVERIFIED")), \
             patch.object(m,"rollback_if_safe") as rollback:
            self.assertEqual(self._approved(),1)
            writes.assert_called_once()
            rollback.assert_called_once_with(NEW)

    def test_failing_canary_can_rollback_only_to_exact_previous_100(self):
        with patch.object(m,"snapshot",return_value=(CANARY_DEP,CANARY)), \
             patch.object(m,"bindings"),patch.object(m,"stable"), \
             patch.object(m,"_wrangler_deploy",return_value=True) as write, \
             patch.object(m,"wait_for",return_value=SLOT_DEP) as wait:
            m.rollback_if_safe(NEW)
            write.assert_called_once()
            self.assertEqual(write.call_args.args[0],[m.ACTIVE+"@100%",NEW+"@0%"])
            wait.assert_called_once_with(CANARY_DEP,CANARY,SLOT,True)

    def test_unknown_concurrent_deployment_must_not_be_overwritten(self):
        with patch.object(m,"snapshot",return_value=(FULL_DEP,{m.ACTIVE:55,NEW:45})), \
             patch.object(m,"_wrangler_deploy") as write:
            m.rollback_if_safe(NEW)
            write.assert_not_called()

    def test_old_only_traffic_needs_no_rollback(self):
        with patch.object(m,"snapshot",return_value=(FIRST,m.INITIAL)), \
             patch.object(m,"_wrangler_deploy") as write:
            m.rollback_if_safe(NEW)
            write.assert_not_called()

    def test_catalog_restricts_versions_and_exact_46_id_contract(self):
        with patch.object(m.urllib.request,"build_opener") as client:
            with self.assertRaisesRegex(m.Stop,"INVALID_OVERRIDE_VERSION"):
                m.catalog_guard("injected")
            client.assert_not_called()


    def test_public_settle_waits_only_on_known_html_200_mismatch(self):
        with patch.object(m,"verify_reviewed_assets",side_effect=[m.Stop("HTML_NOT_REVIEWED_SOURCE_OR_KNOWN_CLOUDFLARE_BEACON"),None]) as assets, \
             patch.object(m,"stable") as stable, \
             patch.object(m.time,"sleep") as sleep:
            m.settle_public(FULL_DEP,FULL)
            self.assertEqual(assets.call_count,2)
            stable.assert_called_once_with(FULL_DEP,FULL)
            sleep.assert_called_once_with(8)

    def test_429_or_i18n_mismatch_never_retries(self):
        for code in ("I18N_SHA_MISMATCH","HTML_ROOT_TRANSPORT_NO_RETRY","STATIC_TRANSPORT_OR_HTTP_UNVERIFIED"):
            with self.subTest(code=code), \
                 patch.object(m,"verify_reviewed_assets",side_effect=m.Stop(code)) as assets, \
                 patch.object(m.time,"sleep") as sleep:
                with self.assertRaisesRegex(m.Stop,code):
                    m.settle_public(FULL_DEP,FULL)
                assets.assert_called_once()
                sleep.assert_not_called()

    def test_i18n_sha_guard_compares_local_dictionary_bytes(self):
        import hashlib
        expected=(m.ROOT/"web/i18n.js").read_bytes()
        with patch.object(m,"verify_assets") as old_assets, \
             patch.object(m,"static_get",return_value=expected) as get:
            m.verify_reviewed_assets(NEW,FIRST,SLOT)
            old_assets.assert_called_once_with(NEW,FIRST,SLOT)
            get.assert_called_once_with("/i18n.js",NEW)
        with patch.object(m,"verify_assets"), \
             patch.object(m,"static_get",return_value=b"unreviewed"):
            with self.assertRaisesRegex(m.Stop,"I18N_SHA_MISMATCH"):
                m.verify_reviewed_assets(NEW,FIRST,SLOT)

if __name__=="__main__":
    unittest.main()

    def test_public_settle_waits_only_on_known_html_200_mismatch(self):
        with patch.object(m,"verify_reviewed_assets",side_effect=[m.Stop("HTML_NOT_REVIEWED_SOURCE_OR_KNOWN_CLOUDFLARE_BEACON"),None]) as assets, \
             patch.object(m,"stable") as stable, \
             patch.object(m.time,"sleep") as sleep:
            m.settle_public(FULL_DEP,FULL)
            self.assertEqual(assets.call_count,2)
            stable.assert_called_once_with(FULL_DEP,FULL)
            sleep.assert_called_once_with(8)

    def test_429_or_i18n_mismatch_never_retries(self):
        for code in ("I18N_SHA_MISMATCH","HTML_ROOT_TRANSPORT_NO_RETRY","STATIC_TRANSPORT_OR_HTTP_UNVERIFIED"):
            with self.subTest(code=code), \
                 patch.object(m,"verify_reviewed_assets",side_effect=m.Stop(code)) as assets, \
                 patch.object(m.time,"sleep") as sleep:
                with self.assertRaisesRegex(m.Stop,code):
                    m.settle_public(FULL_DEP,FULL)
                assets.assert_called_once()
                sleep.assert_not_called()

    def test_i18n_sha_guard_compares_local_dictionary_bytes(self):
        import hashlib
        expected=(m.ROOT/"web/i18n.js").read_bytes()
        with patch.object(m,"verify_assets") as old_assets, \
             patch.object(m,"static_get",return_value=expected) as get:
            m.verify_reviewed_assets(NEW,FIRST,SLOT)
            old_assets.assert_called_once_with(NEW,FIRST,SLOT)
            get.assert_called_once_with("/i18n.js",NEW)
        with patch.object(m,"verify_assets"), \
             patch.object(m,"static_get",return_value=b"unreviewed"):
            with self.assertRaisesRegex(m.Stop,"I18N_SHA_MISMATCH"):
                m.verify_reviewed_assets(NEW,FIRST,SLOT)
