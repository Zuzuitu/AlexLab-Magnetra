#!/usr/bin/env python3
"""Offline regression gates for immutable 6dad resume after safe rollback."""
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import resume_magnetra_hide_anime_mikan as m

FIRST={"id":"previous_slot"}
CANARY_REC={"id":"canary"}
FULL_REC={"id":"full"}


class ResumeSafety(unittest.TestCase):
    def approved(self):
        with patch.dict(os.environ,{"MAGNETRA_ANIME_MIKAN_RESUME_ACTION":m.ACTION}):
            return m.main()

    def test_missing_owner_marker_must_make_zero_cloudflare_calls(self):
        with patch.dict(os.environ,{"MAGNETRA_ANIME_MIKAN_RESUME_ACTION":"CANCEL"}), \
             patch.object(m,"current") as read, \
             patch.object(m,"_wrangler_deploy") as write:
            self.assertEqual(m.main(),2)
            read.assert_not_called()
            write.assert_not_called()

    def test_only_exact_9bbb100_6dad0_allows_resume(self):
        with patch.object(m,"identity_guard"), \
             patch.object(m,"current",side_effect=m.Stop("UNEXPECTED_LIVE_DEPLOYMENT_SPLIT")) as check, \
             patch.object(m,"_wrangler_deploy") as write:
            self.assertEqual(self.approved(),1)
            check.assert_called_once_with(m.SLOT)
            write.assert_not_called()

    def test_full_sequence_from_existing_zero_slot_without_upload(self):
        with patch.object(m,"identity_guard") as guard, \
             patch.object(m,"current",return_value=FIRST) as read, \
             patch.object(m,"bindings") as bind, \
             patch.object(m,"stable"), \
             patch.object(m,"catalog_guard") as catalog, \
             patch.object(m,"verify_assets") as assets, \
             patch.object(m,"_wrangler_deploy",side_effect=[True,True]) as writes, \
             patch.object(m,"wait_for",side_effect=[CANARY_REC,FULL_REC]) as waits, \
             patch.object(m,"verify_public_with_html_settle") as settled, \
             patch.object(m,"rollback_if_safe") as rollback:
            self.assertEqual(self.approved(),0)
            guard.assert_called_once()
            read.assert_called_once_with(m.SLOT)
            self.assertEqual(writes.call_count,2)
            self.assertEqual([x.args[0] for x in writes.call_args_list],[
                [m.ACTIVE+"@95%",m.NEW+"@5%"],
                [m.ACTIVE+"@0%",m.NEW+"@100%"]
            ])
            waits.assert_any_call(FIRST,m.SLOT,m.CANARY,True)
            waits.assert_any_call(CANARY_REC,m.CANARY,m.FULL,True)
            assets.assert_any_call(m.NEW,FIRST,m.SLOT)
            assets.assert_any_call(m.NEW,CANARY_REC,m.CANARY)
            settled.assert_called_once_with(FULL_REC)
            self.assertEqual([x.args[0] for x in catalog.call_args_list],[m.NEW,None])
            self.assertEqual(bind.call_count,4)
            rollback.assert_not_called()

    def test_only_http200_html_mismatch_may_wait_once(self):
        with patch.object(m,"verify_assets",side_effect=[m.Stop(m.HTML_200_MISMATCH),None]) as assets, \
             patch.object(m,"stable") as stable, \
             patch.object(m.time,"sleep") as sleep:
            m.verify_public_with_html_settle(FULL_REC)
            self.assertEqual(assets.call_count,2)
            stable.assert_called_once_with(FULL_REC,m.FULL)
            sleep.assert_called_once_with(8)

    def test_http_transport_429_504_never_retries(self):
        for reason in ("HTML_ROOT_TRANSPORT_NO_RETRY","STATIC_TRANSPORT_OR_HTTP_UNVERIFIED","ASSET_SHA_MISMATCH_/app.js"):
            with self.subTest(reason=reason), \
                 patch.object(m,"verify_assets",side_effect=m.Stop(reason)) as assets, \
                 patch.object(m.time,"sleep") as sleep, \
                 patch.object(m,"stable") as stable:
                with self.assertRaisesRegex(m.Stop,reason.split("_")[0]):
                    m.verify_public_with_html_settle(FULL_REC)
                assets.assert_called_once()
                sleep.assert_not_called()
                stable.assert_not_called()

    def test_bounded_html_wait_exhaustion_then_fail_closed(self):
        with patch.object(m,"verify_assets",side_effect=m.Stop(m.HTML_200_MISMATCH)) as assets, \
             patch.object(m,"stable") as stable, \
             patch.object(m.time,"sleep") as sleep:
            with self.assertRaisesRegex(m.Stop,m.HTML_200_MISMATCH):
                m.verify_public_with_html_settle(FULL_REC)
            self.assertEqual(assets.call_count,6)
            self.assertEqual(stable.call_count,5)
            self.assertEqual(sleep.call_count,5)

    def test_canary_verification_failure_requests_one_safe_rollback(self):
        with patch.object(m,"identity_guard"),patch.object(m,"current",return_value=FIRST), \
             patch.object(m,"bindings"),patch.object(m,"stable"), \
             patch.object(m,"catalog_guard"), \
             patch.object(m,"verify_assets",side_effect=[None,m.Stop("CANARY_SHA_UNVERIFIED")]), \
             patch.object(m,"_wrangler_deploy",return_value=True) as writes, \
             patch.object(m,"wait_for",return_value=CANARY_REC), \
             patch.object(m,"rollback_if_safe") as rollback:
            self.assertEqual(self.approved(),1)
            writes.assert_called_once()
            rollback.assert_called_once_with(m.NEW)

    def test_full_html_fail_requests_one_guarded_rollback(self):
        with patch.object(m,"identity_guard"),patch.object(m,"current",return_value=FIRST), \
             patch.object(m,"bindings"),patch.object(m,"stable"), \
             patch.object(m,"catalog_guard"),patch.object(m,"verify_assets"), \
             patch.object(m,"_wrangler_deploy",side_effect=[True,True]) as writes, \
             patch.object(m,"wait_for",side_effect=[CANARY_REC,FULL_REC]), \
             patch.object(m,"verify_public_with_html_settle",side_effect=m.Stop(m.HTML_200_MISMATCH)), \
             patch.object(m,"rollback_if_safe") as rollback:
            self.assertEqual(self.approved(),1)
            self.assertEqual(writes.call_count,2)
            rollback.assert_called_once_with(m.NEW)


if __name__=="__main__":
    unittest.main()
