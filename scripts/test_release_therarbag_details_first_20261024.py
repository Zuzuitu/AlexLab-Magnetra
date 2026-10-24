"""Offline fail-closed real owner details-first release/rollback guards."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch,call,SimpleNamespace
import release_therarbag_details_first_20261024 as r

CANDIDATE="11111111-1111-4111-8111-111111111111"
OLD={"id":"old-deployment"}
ZERO={"id":"zero-deployment"}
CANARY={"id":"five-deployment"}
FULL={"id":"full-deployment"}

class ReleaseTests(unittest.TestCase):
 def test_original_active_and_exact_split(self):
  self.assertEqual(r.BASELINE,{r.ACTIVE:100,r.ROLLBACK:0})
  self.assertNotEqual(r.ACTIVE,r.ROLLBACK)
  self.assertEqual(r.ACTION,"CONFIRM_THERARBAG_DETAILS_FIRST_PRODUCTION_20261024")

 def test_requires_explicit_owner_activation_no_action_without(self):
  with patch.dict(os.environ,{"MAGNETRA_THERARBAG_DETAILS_FIRST_ACTION":""}),patch.object(r,"release") as release,patch.object(r,"rollback_if_safe") as rollback:
   self.assertEqual(r.main(),2)
   release.assert_not_called()
   rollback.assert_not_called()

 def test_source_guard_preserves_three_details_first_and_existing_others(self):
  with patch.object(r,"validate_source",return_value={"name":"alexlab-magnetra"}) as validate:
   self.assertEqual(r.source_guard(),{"name":"alexlab-magnetra"})
   validate.assert_called_once_with()

 def test_preflight_exact_owner_version_four_bindings_and_account(self):
  with patch.object(r,"account_list",return_value={}),patch.object(r,"verify_account_scripts"),patch.object(r,"current",return_value=OLD) as current,patch.object(r,"_get_api",return_value={}),patch.object(r,"verify_binding_payload") as verify,patch.object(r,"stable") as stable:
   self.assertEqual(r.split_guard(),OLD)
   current.assert_called_once_with(r.BASELINE)
   self.assertEqual([c.args[0] for c in verify.call_args_list],[r.ACTIVE,r.ROLLBACK])
   stable.assert_called_once_with(OLD,r.BASELINE)

 def test_upload_temp_config_keeps_secrets_and_returns_only_verified_uuid(self):
  with tempfile.TemporaryDirectory() as folder:
   tmp=Path(folder)/"single-use-wrangler.json"
   proc=SimpleNamespace(returncode=0,stdout="Worker Version ID: "+CANDIDATE,stderr="")
   with patch.object(r,"TEMP_CONFIG",tmp),patch.object(r.subprocess,"run",return_value=proc) as sp:
    self.assertEqual(r.upload({"name":"alexlab-magnetra","services":[{"binding":"FLUD_RELAY","service":"flud-remote-relay"}]}),CANDIDATE)
    self.assertFalse(tmp.exists())
    cmd=sp.call_args.args[0]
    self.assertIn("--keep-vars",cmd)
    self.assertIn("versions",cmd)
    self.assertIn("upload",cmd)

 def test_transition_uses_only_exact_uuid_version_percentages(self):
  source={r.ACTIVE:100,CANDIDATE:0}
  target={r.ACTIVE:95,CANDIDATE:5}
  with patch.object(r,"stable"),patch.object(r,"_wrangler_deploy",return_value=True) as deploy,patch.object(r,"wait_for",return_value=CANARY) as wait:
   self.assertEqual(r.transition(ZERO,source,target,"CANARY_5",CANDIDATE),CANARY)
   self.assertEqual(deploy.call_args.args[0],[r.ACTIVE+"@95%",CANDIDATE+"@5%"])
   wait.assert_called_once_with(ZERO,source,target,True)

 def test_fails_closed_if_cloudflare_write_rejected(self):
  with patch.object(r,"stable"),patch.object(r,"_wrangler_deploy",return_value=False),patch.object(r,"wait_for") as wait:
   with self.assertRaises(r.Stop):r.transition(OLD,r.BASELINE,{r.ACTIVE:100,CANDIDATE:0},"ZERO_SLOT",CANDIDATE)
   wait.assert_not_called()

 def test_full_release_staged_canary_100_sequence_with_no_generic_deploy(self):
  with patch.object(r,"source_guard",return_value={}),patch.object(r,"split_guard",return_value=OLD),patch.object(r,"live_http",return_value=b"old-asset"),patch.object(r,"stable"),patch.object(r,"upload",return_value=CANDIDATE),patch.object(r,"_get_api",return_value={}),patch.object(r,"verify_binding_payload"),patch.object(r,"transition",side_effect=[ZERO,CANARY,FULL]) as transitions,patch.object(r,"verify_candidate") as verify,patch.object(r,"prove_real_owner_magnet") as magnet,patch.object(r,"public_postflight") as public:
   self.assertEqual(r.release(),0)
   self.assertEqual(
    [(call.args[1],call.args[2]) for call in transitions.call_args_list],
    [(r.BASELINE,{r.ACTIVE:100,CANDIDATE:0}),
     ({r.ACTIVE:100,CANDIDATE:0},{r.ACTIVE:95,CANDIDATE:5}),
     ({r.ACTIVE:95,CANDIDATE:5},{r.ACTIVE:0,CANDIDATE:100})])
   self.assertEqual(verify.call_count,2)
   magnet.assert_called_once_with(CANDIDATE)
   public.assert_called_once_with(CANDIDATE)

 def test_direct_source_must_return_actual_valid_magnet(self):
  diag={"build":"THERARBAG_IPHONE_DIAG_V1","htmlStage":"HTML_ANCHOR_VALID"}
  with patch.object(r,"candidate_http",return_value=(200,{"diagnostic":diag,"magnet":"magnet:?xt=urn:btih:"+"a"*40})):
   r.prove_real_owner_magnet(CANDIDATE)
  with patch.object(r,"candidate_http",return_value=(502,{"diagnostic":diag,"code":"DETAIL_NO_BTIH"})):
   with self.assertRaises(r.Stop):r.prove_real_owner_magnet(CANDIDATE)

 def test_no_magnet_or_flud_http_path_and_invalid_version(self):
  with self.assertRaises(r.Stop):r.candidate_http("/api/companion/magnet",CANDIDATE)
  with self.assertRaises(r.Stop):r.candidate_http("/api/resolve","not-a-uuid")
  with self.assertRaises(r.Stop):r.candidate_http("/api/health",CANDIDATE,body={})

 def test_rollback_only_known_current_5_or_full(self):
  for shares in [{r.ACTIVE:95,CANDIDATE:5},{r.ACTIVE:0,CANDIDATE:100}]:
   with patch.object(r,"snapshot",return_value=(ZERO,shares)),patch.object(r,"_get_api",return_value={}),patch.object(r,"verify_binding_payload"),patch.object(r,"stable"),patch.object(r,"_wrangler_deploy",return_value=True) as deploy,patch.object(r,"wait_for",return_value=FULL):
    r.rollback_if_safe(CANDIDATE)
    self.assertEqual(deploy.call_args.args[0],[r.ACTIVE+"@100%",CANDIDATE+"@0%"])
  for shares in [r.BASELINE,{r.ACTIVE:100,CANDIDATE:0},{r.ACTIVE:60,CANDIDATE:40}]:
   with patch.object(r,"snapshot",return_value=(ZERO,shares)),patch.object(r,"_wrangler_deploy") as deploy:
    r.rollback_if_safe(CANDIDATE)
    deploy.assert_not_called()

 def test_main_guards_rollback_on_runtime_failure(self):
  with patch.dict(os.environ,{"MAGNETRA_THERARBAG_DETAILS_FIRST_ACTION":r.ACTION}),patch.object(r,"release",side_effect=r.Stop("safe")),patch.object(r,"rollback_if_safe") as rollback:
   self.assertEqual(r.main(),1)
   rollback.assert_called_once()

if __name__=="__main__":unittest.main()
