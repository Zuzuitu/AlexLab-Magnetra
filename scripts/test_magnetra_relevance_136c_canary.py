#!/usr/bin/env python3
"""Offline negative-path checks for bounded 136c 5% canary and restore."""
import os, sys, unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import deploy_magnetra_relevance_136c_canary as m

SLOT=({"id":"slot"},m.SLOT)
FIVE=({"id":"five"},m.FIVE)
OTHER="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"

class Canary(unittest.TestCase):
 def test_cancel_has_zero_network_or_mutation(self):
  with patch.dict(os.environ,{"MAGNETRA_RELEVANCE_CANARY_ACTION":"CANCEL"}),patch.object(m,"snapshot") as s,patch.object(m,"verify_version") as v,patch.object(m,"_wrangler_deploy") as w:
   self.assertEqual(m.execute(),2);s.assert_not_called();v.assert_not_called();w.assert_not_called()
 def test_good_canary_one_5_percent_write(self):
  with patch.dict(os.environ,{"MAGNETRA_RELEVANCE_CANARY_ACTION":m.PROMOTE}),patch.object(m,"verify_version") as v,patch.object(m,"verify_source_asset") as asset,patch.object(m,"snapshot",side_effect=[SLOT,SLOT,FIVE]),patch.object(m,"_wrangler_deploy",return_value=True) as w:
   self.assertEqual(m.execute(),0)
   self.assertEqual(w.call_args.args[0],[m.CURRENT+"@95%",m.NEW+"@5%"])
   w.assert_called_once();asset.assert_called_once();self.assertEqual(v.call_count,2)
 def test_missing_slot_or_wrong_old_does_not_write(self):
  for wrong in ({m.CURRENT:100},{m.CURRENT:99,m.NEW:1},{OTHER:100},{m.CURRENT:100,OTHER:0}):
   with self.subTest(wrong=wrong),patch.object(m,"verify_version"),patch.object(m,"snapshot",return_value=({"id":"wrong"},wrong)),patch.object(m,"_wrangler_deploy") as w:
    with self.assertRaisesRegex(m.Stop,"EXPECTED_540B100"):m.canary()
    w.assert_not_called()
 def test_unreviewed_asset_refuses_write(self):
  with patch.object(m,"verify_version"),patch.object(m,"snapshot",return_value=SLOT),patch.object(m,"request",return_value=b"wrong"),patch.object(m,"_wrangler_deploy") as w:
   with self.assertRaisesRegex(m.Stop,"ASSET_SHA_MISMATCH"):m.canary()
   w.assert_not_called()
 def test_missing_staged_asset_fails_closed_with_no_write(self):
  with patch.dict(os.environ,{"MAGNETRA_RELEVANCE_CANARY_ACTION":m.PROMOTE}),patch.object(m,"verify_version"),patch.object(m,"snapshot",return_value=SLOT),patch.object(m,"request",side_effect=m.StagedStop("OVERRIDE_TRANSPORT_UNVERIFIED")),patch.object(m,"_wrangler_deploy") as w:
   self.assertEqual(m.execute(),1)
   w.assert_not_called()
 def test_verified_asset_safely_matches_reviewed_source(self):
  blob=(Path(__file__).resolve().parent.parent/"web"/"app.js").read_bytes()
  with patch.object(m,"request",return_value=blob) as req:
   m.verify_source_asset();req.assert_called_once_with("/app.js",as_json=False)
 def test_race_before_write(self):
  with patch.object(m,"verify_version"),patch.object(m,"verify_source_asset"),patch.object(m,"snapshot",side_effect=[SLOT,({"id":"changed"},m.SLOT)]),patch.object(m,"_wrangler_deploy") as w:
   with self.assertRaisesRegex(m.Stop,"CONCURRENT"):m.canary()
   w.assert_not_called()
 def test_failed_cli_even_if_target_visible_not_verifiable(self):
  with patch.object(m,"verify_version"),patch.object(m,"verify_source_asset"),patch.object(m,"snapshot",side_effect=[SLOT,SLOT,FIVE]),patch.object(m,"_wrangler_deploy",return_value=False) as w:
   with self.assertRaisesRegex(m.Stop,"WRITE_UNVERIFIED"):m.canary()
   w.assert_called_once()
 def test_postflight_eventual_metadata_consistency_without_second_write(self):
  with patch.object(m,"verify_version"),patch.object(m,"verify_source_asset"),patch.object(m,"snapshot",side_effect=[SLOT,SLOT,SLOT,FIVE]),patch.object(m,"_wrangler_deploy",return_value=True) as w,patch.object(m.time,"sleep") as sleep:
   self.assertEqual(m.canary(),0)
   w.assert_called_once();sleep.assert_called_once_with(2)
 def test_unknown_after_write_never_redeploys_or_autorestores(self):
  with patch.object(m,"verify_version"),patch.object(m,"verify_source_asset"),patch.object(m,"snapshot",side_effect=[SLOT,SLOT,({"id":"bad"},{OTHER:100})]),patch.object(m,"_wrangler_deploy",return_value=True) as w:
   with self.assertRaisesRegex(m.Stop,"UNKNOWN_SPLIT"):m.canary()
   w.assert_called_once()
 def test_known_canary_restore_once_with_safe_target(self):
  with patch.dict(os.environ,{"MAGNETRA_RELEVANCE_CANARY_ACTION":m.RESTORE}),patch.object(m,"verify_version"),patch.object(m,"snapshot",side_effect=[FIVE,FIVE,SLOT]),patch.object(m,"_wrangler_deploy",return_value=True) as w:
   self.assertEqual(m.execute(),0)
   self.assertEqual(w.call_args.args[0],[m.CURRENT+"@100%",m.NEW+"@0%"])
   w.assert_called_once()
 def test_restore_already_safe_is_read_only(self):
  with patch.dict(os.environ,{"MAGNETRA_RELEVANCE_CANARY_ACTION":m.RESTORE}),patch.object(m,"verify_version"),patch.object(m,"snapshot",return_value=SLOT),patch.object(m,"_wrangler_deploy") as w:
   self.assertEqual(m.execute(),0);w.assert_not_called()
 def test_restore_refuses_unrecognized_or_unbounded_splits(self):
  for shares in ({OTHER:100},{m.CURRENT:94,m.NEW:6},{m.CURRENT:100}):
   with self.subTest(shares=shares),patch.object(m,"verify_version"),patch.object(m,"snapshot",return_value=({"id":"wrong"},shares)),patch.object(m,"_wrangler_deploy") as w:
    with self.assertRaisesRegex(m.Stop,"RESTORE_REQUIRES_EXACT"):m.restore()
    w.assert_not_called()

if __name__=="__main__":unittest.main()
