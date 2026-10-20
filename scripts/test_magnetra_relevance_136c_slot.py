#!/usr/bin/env python3
"""Offline tests for exact immutable 136c zero-slot safety; never contact internet."""
import os
import sys
from pathlib import Path
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import deploy_magnetra_relevance_136c_slot as m

OTHER="aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
FIRST=({"id":"first"},m.BEFORE)
SECOND=({"id":"second"},m.SLOT)
GOOD={"success":True,"result":{"id":m.NEW,"resources":{"bindings":[
 {"name":"BTDIGG_GATEWAY_TOKEN","type":"secret_text"},
 {"name":"MAGNETRA_GATEWAY_TOKEN","type":"secret_key"},
 {"name":"ASSETS","type":"assets"},
]}}}

class ProtectedStage(unittest.TestCase):
 def test_cancel_before_network_or_write(self):
  with patch.dict(os.environ,{"MAGNETRA_RELEVANCE_ZERO_ACTION":"CANCEL"}),patch.object(m,"verify_version") as v,patch.object(m,"snapshot") as s,patch.object(m,"_wrangler_deploy") as w:
   self.assertEqual(m.execute(),2);v.assert_not_called();s.assert_not_called();w.assert_not_called()

 def test_three_required_binding_names_mandatory(self):
  for missing in ("BTDIGG_GATEWAY_TOKEN","MAGNETRA_GATEWAY_TOKEN","ASSETS"):
   payload={"success":True,"result":{"id":m.NEW,"resources":{"bindings":[x for x in GOOD["result"]["resources"]["bindings"] if x["name"]!=missing]}}}
   with self.subTest(missing=missing),patch.object(m,"_get_api",return_value=payload):
    with self.assertRaisesRegex(m.Stop,"BINDING_UNVERIFIED"):m.verify_version(m.NEW)
 def test_unknown_version_refused_before_cloudflare(self):
  with patch.object(m,"_get_api") as api:
   with self.assertRaisesRegex(m.Stop,"UNRECOGNIZED"):m.verify_version(OTHER)
   api.assert_not_called()

 def test_exact_zero_slot_only_one_write_and_stage_e2e(self):
  with patch.dict(os.environ,{"MAGNETRA_RELEVANCE_ZERO_ACTION":m.ACTION}),patch.object(m,"verify_version") as v,patch.object(m,"snapshot",side_effect=[FIRST,FIRST,SECOND,SECOND]),patch.object(m,"_wrangler_deploy",return_value=True) as write,patch.object(m,"stage_e2e",return_value=True) as e2e:
   self.assertEqual(m.execute(),0)
   self.assertEqual(write.call_args.args[0],[m.CURRENT+"@100%",m.NEW+"@0%"])
   write.assert_called_once();self.assertEqual(v.call_count,3);e2e.assert_called_once()
 def test_writes_once_if_provider_e2e_ends_inconclusive(self):
  with patch.dict(os.environ,{"MAGNETRA_RELEVANCE_ZERO_ACTION":m.ACTION}),patch.object(m,"verify_version"),patch.object(m,"snapshot",side_effect=[FIRST,FIRST,SECOND,SECOND]),patch.object(m,"_wrangler_deploy",return_value=True) as w,patch.object(m,"stage_e2e",return_value=False):
   self.assertEqual(m.execute(),1);w.assert_called_once()
 def test_wrong_traffic_or_third_version_denies_mutation(self):
  for wrong in ({m.CURRENT:99,m.PREVIOUS:1},{OTHER:100},{m.CURRENT:100,m.NEW:0}):
   with self.subTest(wrong=wrong),patch.dict(os.environ,{"MAGNETRA_RELEVANCE_ZERO_ACTION":m.ACTION}),patch.object(m,"verify_version"),patch.object(m,"snapshot",return_value=({"id":"before"},wrong)),patch.object(m,"_wrangler_deploy") as w:
    with self.assertRaisesRegex(m.Stop,"EXPECTED_540B100_249D0"):m.execute()
    w.assert_not_called()
 def test_concurrent_deployment_refuses_write(self):
  with patch.dict(os.environ,{"MAGNETRA_RELEVANCE_ZERO_ACTION":m.ACTION}),patch.object(m,"verify_version"),patch.object(m,"snapshot",side_effect=[FIRST,({"id":"race"},m.BEFORE)]),patch.object(m,"_wrangler_deploy") as w:
   with self.assertRaisesRegex(m.Stop,"CONCURRENT"):m.execute()
   w.assert_not_called()
 def test_unconfirmed_cli_cannot_claim_success(self):
  with patch.dict(os.environ,{"MAGNETRA_RELEVANCE_ZERO_ACTION":m.ACTION}),patch.object(m,"verify_version"),patch.object(m,"snapshot",side_effect=[FIRST,FIRST,SECOND]),patch.object(m,"_wrangler_deploy",return_value=False) as w,patch.object(m,"stage_e2e") as e:
   with self.assertRaisesRegex(m.Stop,"WRITE_UNVERIFIED"):m.execute()
   w.assert_called_once();e.assert_not_called()
 def test_unknown_state_after_single_write_never_rolls_back(self):
  with patch.dict(os.environ,{"MAGNETRA_RELEVANCE_ZERO_ACTION":m.ACTION}),patch.object(m,"verify_version"),patch.object(m,"snapshot",side_effect=[FIRST,FIRST,({"id":"other"},{OTHER:100})]),patch.object(m,"_wrangler_deploy",return_value=True) as w,patch.object(m,"stage_e2e") as e:
   with self.assertRaisesRegex(m.Stop,"UNEXPECTED_STATE"):m.execute()
   w.assert_called_once();e.assert_not_called()
 def test_bounded_postflight_reads_no_second_deploy(self):
  with patch.dict(os.environ,{"MAGNETRA_RELEVANCE_ZERO_ACTION":m.ACTION}),patch.object(m,"verify_version"),patch.object(m,"snapshot",side_effect=[FIRST,FIRST,FIRST,SECOND,SECOND]),patch.object(m,"_wrangler_deploy",return_value=True) as w,patch.object(m,"stage_e2e",return_value=True),patch.object(m.time,"sleep") as sleep:
   self.assertEqual(m.execute(),0)
   sleep.assert_called_once_with(2);w.assert_called_once()
 def test_reviewed_js_and_original_title_api_schema(self):
  reviewed=(Path(__file__).resolve().parent.parent/"web"/"app.js").read_bytes()
  catalog={"providers":[{"id":"id"+str(i)} for i in range(46)]}
  rows=[{"provider":"knaben","name":"The Good Dinosaur (2015) 1080p HEVC"}]
  api={"results":rows,"stats":[
   {"provider":"knaben","count":1,"rawCount":3,"excludedOffTopic":2},
   {"provider":"torrentscsv","count":0,"rawCount":1,"excludedOffTopic":1}
  ],"errors":[],"total":1,"excludedOffTopic":3}
  with patch.object(m,"request",side_effect=[reviewed,catalog,api]) as request:
   self.assertTrue(m.stage_e2e());self.assertEqual(request.call_count,3)
 def test_off_topic_api_row_in_accepted_set_fails(self):
  reviewed=(Path(__file__).resolve().parent.parent/"web"/"app.js").read_bytes()
  catalog={"providers":[{"id":"id"+str(i)} for i in range(46)]}
  api={"results":[{"provider":"knaben","name":"Knock Knock 2015"}],
   "stats":[{"provider":"knaben","count":1,"rawCount":1,"excludedOffTopic":0},
            {"provider":"torrentscsv","count":0,"rawCount":0,"excludedOffTopic":0}],
   "errors":[],"total":1,"excludedOffTopic":0}
  with patch.object(m,"request",side_effect=[reviewed,catalog,api]):
   with self.assertRaisesRegex(m.Stop,"UNRELATED_RESULT"):m.stage_e2e()

if __name__=="__main__": unittest.main()
