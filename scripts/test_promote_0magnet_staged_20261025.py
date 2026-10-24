import os
import unittest
from unittest.mock import patch,call
import promote_0magnet_staged_20261025 as p

class PromotionSafetyTests(unittest.TestCase):
 def test_exact_existing_two_version_slot_no_upload(self):
  self.assertEqual(p.BASELINE,{p.g.ACTIVE:100,p.CANDIDATE:0})
  self.assertEqual(p.CANARY,{p.g.ACTIVE:95,p.CANDIDATE:5})
  self.assertEqual(p.FULL,{p.g.ACTIVE:0,p.CANDIDATE:100})
  self.assertEqual(p.CANDIDATE,"763defbe-38aa-4299-acf1-1639a59e7be6")

 def test_missing_approval_no_reads_or_writes(self):
  with patch.dict(os.environ,{"MAGNETRA_0MAGNET_PROMOTION_ACTION":""}),patch.object(p,"promote") as promote,patch.object(p.g,"rollback_if_safe") as rollback:
   self.assertEqual(p.main(),2)
   promote.assert_not_called()
   rollback.assert_not_called()

 def test_preflight_rechecks_exact_split_immutable_bindings_and_owner_source(self):
  before={"id":"original-deployment"}
  with patch.object(p.g,"source_guard"),patch.object(p.g,"verify_account_scripts"),patch.object(p.g,"account_list",return_value={}),patch.object(p.g,"current",return_value=before) as current,patch.object(p.g,"_get_api",return_value={}) as api,patch.object(p.g,"verify_binding_payload") as check,patch.object(p.g,"stable") as stable,patch.object(p.g,"verify_candidate") as candidate,patch.object(p.g,"prove_real_owner_magnet") as magnet:
   self.assertEqual(p.preflight(),before)
   current.assert_called_once_with(p.BASELINE)
   self.assertEqual([c.args[0] for c in check.call_args_list],[p.g.ACTIVE,p.CANDIDATE])
   self.assertEqual([c.args[0] for c in api.call_args_list],["/versions/"+p.g.ACTIVE,"/versions/"+p.CANDIDATE])
   candidate.assert_called_once_with(p.CANDIDATE)
   magnet.assert_called_once_with(p.CANDIDATE)
   self.assertEqual(stable.call_count,3)

 def test_exact_5_to_100_and_postflight_checks(self):
  before,at5,full=({"id":"original"},{"id":"at5"},{"id":"full"})
  with patch.object(p,"preflight",return_value=before),patch.object(p.g,"transition",side_effect=[at5,full]) as transition,patch.object(p.g,"verify_candidate") as candidate,patch.object(p.g,"stable") as stable,patch.object(p.g,"public_postflight") as public:
   self.assertEqual(p.promote(),0)
   self.assertEqual([c.args for c in transition.call_args_list],[
     (before,p.BASELINE,p.CANARY,"OWNER_CANARY_5",p.CANDIDATE),
     (at5,p.CANARY,p.FULL,"OWNER_FULL_100",p.CANDIDATE)])
   candidate.assert_called_once_with(p.CANDIDATE)
   public.assert_called_once_with(p.CANDIDATE)
   self.assertEqual(stable.call_count,2)

 def test_fail_closed_rollback_only_through_guarded_existing_implementation(self):
  with patch.dict(os.environ,{"MAGNETRA_0MAGNET_PROMOTION_ACTION":p.ACTION}),patch.object(p,"promote",side_effect=p.g.Stop("failed")),patch.object(p.g,"rollback_if_safe") as rollback:
   self.assertEqual(p.main(),1)
   rollback.assert_called_once_with(p.CANDIDATE)

 def test_source_code_forbids_upload_and_torrent_flud_mutation(self):
  from pathlib import Path
  code=Path(p.__file__).read_text(encoding="utf8")
  for prohibited in ("g.upload(","versions upload","/api/companion","/api/flud","/torrent/download","versions deploy"):
   self.assertNotIn(prohibited,code)

if __name__=="__main__":unittest.main()
