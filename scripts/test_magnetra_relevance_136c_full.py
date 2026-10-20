#!/usr/bin/env python3
"""Offline fail-closed tests for owner-manual full release and separate restore."""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import deploy_magnetra_relevance_136c_full as m

OLD=({"id":"old"},m.FIVE)
FULL=({"id":"full"},m.FULL)
RESTORE=({"id":"restore"},m.RESTORED)
OTHER="ffffffff-ffff-4fff-8fff-ffffffffffff"

class FullGateTests(unittest.TestCase):
 def test_cancel_never_reads_or_writes(self):
  with patch.dict(os.environ,{"MAGNETRA_RELEVANCE_FULL_ACTION":"CANCEL"}),patch.object(m,"snapshot") as s,patch.object(m,"_wrangler_deploy") as w:
   self.assertEqual(m.execute(),2);s.assert_not_called();w.assert_not_called()
 def test_source_preflight_authentic_five_providers_and_stable_id(self):
  with patch.object(m,"verify_versions") as v,patch.object(m,"snapshot",return_value=OLD),patch.object(m,"verify_source_asset") as asset,patch.object(m.source,"stage_e2e",return_value=True) as e2e,patch.object(m,"screenshot_source_gate") as extra,patch.object(m,"stable") as stable:
   self.assertEqual(m.read_only_preflight(),OLD[0])
   v.assert_called_once();asset.assert_called_once();e2e.assert_called_once();extra.assert_called_once();stable.assert_called_once()
 def test_wrong_split_and_unknown_versions_abort_before_write(self):
  for bad in ({m.CURRENT:100,m.NEW:0},{m.CURRENT:90,m.NEW:10},{m.CURRENT:95,OTHER:5},{m.NEW:100,m.CURRENT:0}):
   with self.subTest(bad=bad),patch.object(m,"verify_versions"),patch.object(m,"snapshot",return_value=({"id":"bad"},bad)),patch.object(m,"_wrangler_deploy") as w,patch.object(m,"verify_source_asset") as a:
    with self.assertRaisesRegex(m.Stop,"CANARY_MISSING"):m.read_only_preflight()
    w.assert_not_called();a.assert_not_called()
 def test_source_fail_prevents_mutation(self):
  with patch.object(m,"read_only_preflight",side_effect=m.Stop("SOURCES_UNVERIFIED")),patch.dict(os.environ,{"MAGNETRA_RELEVANCE_FULL_ACTION":m.PROMOTE}),patch.object(m,"_wrangler_deploy") as w:
   self.assertEqual(m.execute(),1);w.assert_not_called()
 def test_preflight_race_before_write_refuses_change(self):
  with patch.object(m,"read_only_preflight",return_value=OLD[0]),patch.object(m,"stable",side_effect=m.Stop("CONCURRENT")),patch.object(m,"_wrangler_deploy") as w:
   with self.assertRaisesRegex(m.Stop,"CONCURRENT"):m.promote()
   w.assert_not_called()
 def test_promote_exact_100_and_keep_540b_at_zero(self):
  with patch.object(m,"read_only_preflight",return_value=OLD[0]),patch.object(m,"stable"),patch.object(m,"_wrangler_deploy",return_value=True) as w,patch.object(m,"await_version_split",return_value=FULL[0]) as post,patch.object(m,"verify_versions") as v,patch.object(m,"verify_source_asset") as js,patch.object(m,"verify_public_assets") as pub,patch.object(m,"snapshot",return_value=FULL):
   self.assertEqual(m.promote(),0)
   self.assertEqual(w.call_args.args[0],[m.CURRENT+"@0%",m.NEW+"@100%"])
   w.assert_called_once();post.assert_called_once_with(OLD[0],m.FULL,m.FIVE,True)
   v.assert_called_once();js.assert_called_once();pub.assert_called_once()
 def test_failed_cli_never_claim_success_or_redeploy(self):
  with patch.object(m,"snapshot",return_value=FULL),patch.object(m,"_wrangler_deploy") as w:
   with self.assertRaisesRegex(m.Stop,"WRITE_UNVERIFIED"):
    m.await_version_split(OLD[0],m.FULL,m.FIVE,False)
   w.assert_not_called()
 def test_only_bounded_reads_when_old_split_propagates_slowly(self):
  with patch.object(m,"snapshot",side_effect=[OLD,FULL]),patch.object(m.time,"sleep") as sleep,patch.object(m,"_wrangler_deploy") as w:
   self.assertEqual(m.await_version_split(OLD[0],m.FULL,m.FIVE,True),FULL[0])
   sleep.assert_called_once_with(2);w.assert_not_called()
 def test_unknown_split_after_single_write_no_auto_rollback(self):
  with patch.object(m,"snapshot",return_value=({"id":"rogue"},{m.CURRENT:90,m.NEW:10})),patch.object(m,"_wrangler_deploy") as w:
   with self.assertRaisesRegex(m.Stop,"UNKNOWN_OR_CONCURRENT"):
    m.await_version_split(OLD[0],m.FULL,m.FIVE,True)
   w.assert_not_called()
 def test_public_static_hash_mismatch_converges_successful_gets_only(self):
  real=(Path(__file__).resolve().parent.parent/"web/app.js").read_bytes()
  with patch.object(m,"public_static_asset",side_effect=[b"previous",real]) as get,patch.object(m,"snapshot",return_value=FULL),patch.object(m.time,"sleep") as sleep:
   m.verify_public_assets(FULL[0]);self.assertEqual(get.call_count,2);sleep.assert_called_once_with(10)
 def test_public_static_persistent_mismatch_fails_after_twelve_gets(self):
  with patch.object(m,"public_static_asset",return_value=b"old") as get,patch.object(m,"snapshot",return_value=FULL),patch.object(m.time,"sleep") as sleep:
   with self.assertRaisesRegex(m.Stop,"SHA_UNVERIFIED"):m.verify_public_assets(FULL[0])
   self.assertEqual(get.call_count,12);self.assertEqual(sleep.call_count,11)
 def test_public_static_transport_error_not_retried(self):
  with patch.object(m,"public_static_asset",side_effect=m.Stop("TRANSPORT")) as get,patch.object(m.time,"sleep") as sleep:
   with self.assertRaisesRegex(m.Stop,"TRANSPORT"):m.verify_public_assets(FULL[0])
   get.assert_called_once();sleep.assert_not_called()
 def test_public_asset_poll_deployment_change_immediate_stop(self):
  with patch.object(m,"public_static_asset",return_value=b"old"),patch.object(m,"snapshot",return_value=({"id":"changed"},m.FULL)),patch.object(m.time,"sleep") as sleep:
   with self.assertRaisesRegex(m.Stop,"DEPLOYMENT_CHANGED"):m.verify_public_assets(FULL[0])
   sleep.assert_not_called()
 def test_restores_only_from_full_100_and_not_from_canary(self):
  with patch.object(m,"verify_versions"),patch.object(m,"snapshot",return_value=OLD),patch.object(m,"_wrangler_deploy") as w:
   with self.assertRaisesRegex(m.Stop,"RESTORE_ONLY"):m.restore()
   w.assert_not_called()
 def test_manual_restore_exact_540b_100_from_full(self):
  with patch.object(m,"verify_versions"),patch.object(m,"snapshot",return_value=FULL),patch.object(m,"stable"),patch.object(m,"_wrangler_deploy",return_value=True) as w,patch.object(m,"await_version_split",return_value=RESTORE[0]) as wait:
   self.assertEqual(m.restore(),0)
   self.assertEqual(w.call_args.args[0],[m.CURRENT+"@100%",m.NEW+"@0%"])
   w.assert_called_once();wait.assert_called_once_with(FULL[0],m.RESTORED,m.FULL,True)
 def test_no_write_if_restored_already(self):
  with patch.object(m,"verify_versions"),patch.object(m,"snapshot",return_value=RESTORE),patch.object(m,"_wrangler_deploy") as w:
   self.assertEqual(m.restore(),0);w.assert_not_called()

if __name__=="__main__":unittest.main()
