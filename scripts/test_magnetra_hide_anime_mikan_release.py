#!/usr/bin/env python3
"""Offline tests for uniquely approved one-shot curated indexer UI release."""
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import release_magnetra_hide_anime_mikan as m

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
        with patch.dict(os.environ,{"MAGNETRA_CURATED_RELEASE_ACTION":"CANCEL"}), \
             patch.object(m,"current") as read, \
             patch.object(m,"_wrangler_deploy") as write:
            self.assertEqual(m.main(),2)
            read.assert_not_called()
            write.assert_not_called()

    def test_old_27_picker_release_guard_rejects_new_bilingual_source(self):
        # Immutable one-shot releases must not silently accept a later
        # different picker or localization. Assert the gate stays closed.
        with self.assertRaisesRegex(m.Stop,"REVIEWED_CURATED_SOURCE_NOT_PRESENT"):
            m.identity_guard()

    def test_unexpected_current_distribution_stops_before_upload(self):
        with patch.object(m,"current",side_effect=m.Stop("UNEXPECTED_LIVE_DEPLOYMENT_SPLIT")), \
             patch.object(m,"upload_version") as upload, \
             patch.object(m,"_wrangler_deploy") as write:
            self.assertEqual(m.main() if os.environ.get("MAGNETRA_CURATED_RELEASE_ACTION")==m.ACTION else self._approved(),1)
            upload.assert_not_called()
            write.assert_not_called()

    @staticmethod
    def _approved():
        with patch.dict(os.environ,{"MAGNETRA_CURATED_RELEASE_ACTION":m.ACTION}):
            return m.main()

    def test_full_flow_stage_and_canary_then_full_100(self):
        with patch.object(m,"identity_guard"), \
             patch.object(m,"current",return_value=FIRST) as current, \
             patch.object(m,"bindings") as bindings, \
             patch.object(m,"active_asset_guard") as old_hash, \
             patch.object(m,"stable"), \
             patch.object(m,"upload_version",return_value=NEW), \
             patch.object(m,"_wrangler_deploy",side_effect=[True,True,True]) as writes, \
             patch.object(m,"wait_for",side_effect=[SLOT_DEP,CANARY_DEP,FULL_DEP]), \
             patch.object(m,"verify_assets") as assets, \
             patch.object(m,"catalog_guard") as catalog:
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
            assets.assert_any_call(None,FULL_DEP,FULL)
            self.assertEqual([x.args[0] for x in catalog.call_args_list],[NEW,None])
            self.assertEqual(bindings.call_count,6)

    def test_zero_slot_failed_asset_verification_blocks_canary(self):
        with patch.object(m,"identity_guard"), \
             patch.object(m,"current",return_value=FIRST), \
             patch.object(m,"bindings"), \
             patch.object(m,"active_asset_guard"), \
             patch.object(m,"stable"), \
             patch.object(m,"upload_version",return_value=NEW), \
             patch.object(m,"_wrangler_deploy",return_value=True) as writes, \
             patch.object(m,"wait_for",return_value=SLOT_DEP), \
             patch.object(m,"verify_assets",side_effect=m.Stop("STATIC_SHA_UNVERIFIED")), \
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


if __name__=="__main__":
    unittest.main()
