"""Offline version-only recovery guards after completed 0% staging."""
import hashlib
import os
import unittest
from unittest.mock import patch
import resume_curated_11_immutable_20261025 as s

class Resume(unittest.TestCase):
 def test_fixed_slot_and_no_upload_in_release_script(self):
  self.assertEqual(s.SLOT,{s.r.ACTIVE:100,s.NEW:0})
  self.assertEqual(s.CANARY,{s.r.ACTIVE:95,s.NEW:5})
  self.assertEqual(s.FULL,{s.r.ACTIVE:0,s.NEW:100})
  source=open(s.__file__,encoding="utf8").read()
  self.assertNotIn("r.upload(",source)
  self.assertNotIn("versions upload",source)
 def test_owner_approval_denies_all_writes(self):
  with patch.dict(os.environ,{"MAGNETRA_CURATED_11_RESUME_ACTION":""}),patch.object(s,"run") as go:
   self.assertEqual(s.main(),2)
   go.assert_not_called()
 def test_version_only_5_then_100_and_owner_magnet_proof(self):
  with patch.object(s.r,"source_guard"),patch.object(s.r,"account_list",return_value={}),patch.object(s.r,"verify_account_scripts"),patch.object(s.r,"current",return_value={"id":"zero"}),patch.object(s.r,"_get_api",return_value={}),patch.object(s.r,"verify_binding_payload") as binds,patch.object(s.r,"stable"),patch.object(s.r,"live_http",return_value=b"old"),patch.object(s.r,"OLD_PUBLIC_SHA_PREFIX",hashlib.sha256(b"old").hexdigest()[:16]),patch.object(s.r,"verify_candidate") as verified,patch.object(s.r,"prove_real_owner_magnet") as magnet,patch.object(s.r,"prove_owner_search_card") as card,patch.object(s.r,"transition",side_effect=[{"id":"canary"},{"id":"full"}]) as flow,patch.object(s.r,"public_postflight") as post,patch.object(s.r,"upload") as upload:
   self.assertEqual(s.run(),0)
   self.assertEqual([x.args[1:3] for x in flow.call_args_list],[(s.SLOT,s.CANARY),(s.CANARY,s.FULL)])
   self.assertEqual(verified.call_count,2)
   self.assertEqual(binds.call_count,2)
   magnet.assert_called_once_with(s.NEW)
   post.assert_called_once_with(s.NEW)
   upload.assert_not_called()
 def test_unknown_failure_attempts_only_existing_bounded_rollback(self):
  with patch.dict(os.environ,{"MAGNETRA_CURATED_11_RESUME_ACTION":s.ACTION}),patch.object(s,"run",side_effect=s.r.Stop("finite")),patch.object(s.r,"rollback_if_safe") as roll:
   self.assertEqual(s.main(),1)
   roll.assert_called_once_with(s.NEW)
if __name__=="__main__":unittest.main()
