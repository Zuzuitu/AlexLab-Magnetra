#!/usr/bin/env python3
"""Offline contract tests: manual guarded PWA-only release, no source retries."""
import os
import sys
from pathlib import Path
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import deploy_magnetra_auto_pause_once as m

CANDIDATE="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
OLD={m.OLD:100,m.OLD_ROLLBACK:0}
SLOT={m.OLD:100,CANDIDATE:0}
FULL={m.OLD:0,CANDIDATE:100}
R0={"id":"r0"}
R1={"id":"r1"}
R2={"id":"r2"}

class SafeRelease(unittest.TestCase):
 def test_cancel_does_not_contact_cloudflare(self):
  with patch.dict(os.environ,{"MAGNETRA_AUTO_PAUSE_ACTION":"CANCEL"}),patch.object(m,"current") as check,patch.object(m,"_wrangler_deploy") as write,patch.object(m,"upload_version") as upload:
   self.assertEqual(m.main(),2)
   check.assert_not_called();write.assert_not_called();upload.assert_not_called()
 def test_uploaded_uuid_is_extracted_from_real_wranger_format_only(self):
  self.assertEqual(m.uploaded_version_id("Uploaded alexlab-magnetra\nWorker Version ID: "+CANDIDATE),CANDIDATE)
  for text in ("Worker Version ID: invalid","no id","Worker Version ID: "+CANDIDATE+"\nWorker Version ID: "+CANDIDATE):
   with self.subTest(text=text),self.assertRaises(m.Stop):m.uploaded_version_id(text)
 def test_exact_known_old_distribution_required_pre_mutation(self):
  with patch.object(m,"current",side_effect=m.Stop("UNEXPECTED_LIVE_DEPLOYMENT_SPLIT")),patch.object(m,"upload_version") as upload,patch.object(m,"_wrangler_deploy") as write:
   with self.assertRaisesRegex(m.Stop,"UNEXPECTED_LIVE"):m.release()
   upload.assert_not_called();write.assert_not_called()
 def test_owner_release_stages_verified_zero_slot_then_100_preserving_136c(self):
  with patch.object(m,"current",return_value=R0) as current,patch.object(m,"bindings") as binds,patch.object(m,"stable") as stable,patch.object(m,"upload_version",return_value=CANDIDATE) as upload,patch.object(m,"_wrangler_deploy",side_effect=[True,True]) as writes,patch.object(m,"wait_for",side_effect=[R1,R2]) as wait,patch.object(m,"verify_assets") as assets:
   self.assertEqual(m.release(),0)
   current.assert_called_once_with(OLD)
   self.assertEqual(binds.call_count,3)
   self.assertEqual(upload.call_count,1)
   self.assertEqual(writes.call_count,2)
   self.assertEqual(writes.call_args_list[0].args[0],[m.OLD+"@100%",CANDIDATE+"@0%"])
   self.assertEqual(writes.call_args_list[1].args[0],[m.OLD+"@0%",CANDIDATE+"@100%"])
   self.assertEqual(assets.call_count,2)
   assets.assert_any_call(CANDIDATE,R1,SLOT)
   assets.assert_any_call(None,R2,FULL)
 def test_first_asset_mismatch_prevents_full_promotion(self):
  with patch.object(m,"current",return_value=R0),patch.object(m,"bindings"),patch.object(m,"stable"),patch.object(m,"upload_version",return_value=CANDIDATE),patch.object(m,"_wrangler_deploy",return_value=True) as writes,patch.object(m,"wait_for",return_value=R1),patch.object(m,"verify_assets",side_effect=m.Stop("STATIC_SHA_UNVERIFIED")):
   with self.assertRaisesRegex(m.Stop,"STATIC_SHA"):m.release()
   writes.assert_called_once()
 def test_after_unknown_cloudflare_state_no_extra_deploy_or_auto_restore(self):
  with patch.object(m,"snapshot",return_value=({"id":"rogue"},{m.OLD:99,CANDIDATE:1})),patch.object(m,"_wrangler_deploy") as w:
   with self.assertRaisesRegex(m.Stop,"UNKNOWN_POSTWRITE"):
    m.wait_for(R0,OLD,SLOT,True)
   w.assert_not_called()
 def test_target_visible_but_wranger_failed_is_not_success(self):
  with patch.object(m,"snapshot",return_value=(R1,SLOT)):
   with self.assertRaisesRegex(m.Stop,"WRITE_UNVERIFIED"):m.wait_for(R0,OLD,SLOT,False)
 def test_only_http_200_static_mismatch_waits_bounded_no_source_requests(self):
  content=(m.ROOT/"web/app.js").read_bytes()
  other=[(m.ROOT/f).read_bytes() for _,f,_ in m.ASSETS]
  side=[b"old",other[0],other[1],other[2]]
  with patch.object(m,"static_get",side_effect=side) as get,patch.object(m,"stable") as stable,patch.object(m.time,"sleep") as sleep:
   m.verify_assets(CANDIDATE,R1,SLOT)
   self.assertEqual(get.call_count,4)
   sleep.assert_called_once_with(8)
 def test_static_transport_429_does_not_retry(self):
  with patch.object(m,"static_get",side_effect=m.Stop("STATIC_TRANSPORT_OR_HTTP_UNVERIFIED")) as get,patch.object(m.time,"sleep") as sleep:
   with self.assertRaisesRegex(m.Stop,"STATIC_TRANSPORT"):m.verify_assets(CANDIDATE,R1,SLOT)
   get.assert_called_once();sleep.assert_not_called()
 def test_static_get_denies_any_indexer_or_external_path_before_request(self):
  with patch.object(m.urllib.request,"build_opener") as opener:
   for path in ("/api/search?q=test","/api/resolve","//evil.invalid/app.js","/private"):
    with self.subTest(path=path),self.assertRaisesRegex(m.Stop,"UNAPPROVED_STATIC"):
     m.static_get(path)
   opener.assert_not_called()
 def test_restoration_requires_exact_supplied_new_version_and_full_state(self):
  with patch.dict(os.environ,{"MAGNETRA_AUTO_PAUSE_RESTORE_ID":""}),patch.object(m,"current") as check,patch.object(m,"_wrangler_deploy") as writes:
   with self.assertRaisesRegex(m.Stop,"RESTORE_REQUIRES_EXACT"):m.restore()
   check.assert_not_called();writes.assert_not_called()
  with patch.dict(os.environ,{"MAGNETRA_AUTO_PAUSE_RESTORE_ID":CANDIDATE}),patch.object(m,"current",side_effect=m.Stop("UNEXPECTED_LIVE_DEPLOYMENT_SPLIT")),patch.object(m,"_wrangler_deploy") as writes:
   with self.assertRaisesRegex(m.Stop,"UNEXPECTED_LIVE"):m.restore()
   writes.assert_not_called()
 def test_restore_only_from_exact_candidate_100_keeps_original_version(self):
  with patch.dict(os.environ,{"MAGNETRA_AUTO_PAUSE_RESTORE_ID":CANDIDATE}),patch.object(m,"current",return_value=R2) as current,patch.object(m,"bindings") as bindings,patch.object(m,"stable"),patch.object(m,"_wrangler_deploy",return_value=True) as write,patch.object(m,"wait_for",return_value=R1) as wait:
   self.assertEqual(m.restore(),0)
   current.assert_called_once_with(FULL)
   self.assertEqual(write.call_args.args[0],[m.OLD+"@100%",CANDIDATE+"@0%"])
   write.assert_called_once()
   wait.assert_called_once_with(R2,FULL,SLOT,True)

if __name__=="__main__":unittest.main()
