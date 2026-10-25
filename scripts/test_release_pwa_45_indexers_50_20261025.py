"""Offline fail-closed regression tests for immutable 45-indexer PWA release."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import release_pwa_45_indexers_50_20261025 as r

CANDIDATE="11111111-1111-4111-8111-111111111111"
DEP0={"id":"stable"}
DEP1={"id":"zero"}
DEP5={"id":"canary"}
DEP100={"id":"full"}
MAGNET="magnet:?xt=urn:btih:"+"a"*40

class SafeReleaseTests(unittest.TestCase):
 def test_new_owner_authorization_and_last_proven_production_baseline(self):
  self.assertEqual(r.BASELINE,{r.ACTIVE:100,r.ROLLBACK:0})
  self.assertEqual(r.ACTIVE,"76a15eae-5c8c-41a2-bace-adb9b2460933")
  self.assertEqual(r.ROLLBACK,"24642346-9db0-4cea-a56e-12e30f35569f")
  self.assertEqual(r.ACTION,"CONFIRM_MAGNETRA_45_SOURCES_50_RESULTS_RELEASE_20261025")
  self.assertEqual(r.ORIGINAL,"https://nnmclub.to/forum/viewtopic.php?t=1896364")
 def test_missing_approval_never_writes(self):
  with patch.dict(os.environ,{"MAGNETRA_INDEXERS_45_PAGING_50_RELEASE_ACTION":""}),\
       patch.object(r,"release") as run,patch.object(r,"rollback_if_safe") as rollback:
   self.assertEqual(r.main(),2)
   run.assert_not_called()
   rollback.assert_not_called()
 def test_production_source_guards_require_real_owner_fix(self):
  with patch.object(r,"validate_source",return_value={"name":"alexlab-magnetra"}) as v:
   self.assertEqual(r.source_guard(),{"name":"alexlab-magnetra"})
   v.assert_called_once()
 def test_account_and_4_bindings_guard_stable_twice(self):
  with patch.object(r,"account_list",return_value={}),patch.object(r,"verify_account_scripts"),\
       patch.object(r,"current",return_value=DEP0) as current,\
       patch.object(r,"_get_api",return_value={}),patch.object(r,"verify_binding_payload") as vb,\
       patch.object(r,"stable") as stable:
   self.assertEqual(r.split_guard(),DEP0)
   current.assert_called_once_with(r.BASELINE)
   self.assertEqual([x.args[0] for x in vb.call_args_list],[r.ACTIVE,r.ROLLBACK])
   stable.assert_called_once_with(DEP0,r.BASELINE)
 def test_candidate_exact_search_card_without_false_auxiliary(self):
  row={"provider":"nonameclub","details":r.ORIGINAL,"magnetSource":None}
  with patch.object(r,"candidate_http",return_value=(200,{"results":[row]})) as get:
   r.prove_owner_search_card(CANDIDATE)
   get.assert_called_once_with(r.SEARCH_PATH,CANDIDATE)
  for rows in [
    [{"provider":"nonameclub","details":r.ORIGINAL,"magnetSource":"https://nnmclub.to/undefined"}],
    [{"provider":"nonameclub","details":r.ORIGINAL,"magnetSource":"https://nnmclub.to/undefined"},
     {"provider":"nonameclub","details":r.ORIGINAL,"magnetSource":None}],
    [{"provider":"nonameclub","details":"https://nnmclub.to/forum/viewtopic.php?t=999"}]
  ]:
   with patch.object(r,"candidate_http",return_value=(200,{"results":rows})):
    with self.assertRaises(r.Stop):r.prove_owner_search_card(CANDIDATE)
 def test_owner_same_source_metadata_only_magnet(self):
  with patch.object(r,"candidate_http",return_value=(200,{"magnet":MAGNET})) as request:
   r.prove_real_owner_magnet(CANDIDATE)
   request.assert_called_once_with("/api/resolve",CANDIDATE,body={"provider":"nonameclub","details":r.ORIGINAL})
  for status,body in [(502,{"error":"source"}),(200,{"magnet":"bad"}),(200,{"magnet":"magnet:?xt=urn:btih:wrong"})]:
   with patch.object(r,"candidate_http",return_value=(status,body)):
    with self.assertRaises(r.Stop):r.prove_real_owner_magnet(CANDIDATE)
 def test_five_immutable_assets_and_backend_catalog(self):
  files={"/app.js":"web/app.js","/styles.css":"web/styles.css","/sw.js":"web/sw.js",
         "/i18n.js":"web/i18n.js","/index.html":"web/index.html"}
  ids=["subsplease","0magnet","therarbag"]+[f"provider-{i}" for i in range(43)]
  def response(path,version):
   self.assertEqual(version,CANDIDATE)
   if path in files:return (r.ROOT/files[path]).read_bytes()
   if path=="/api/health":return 200,{"ok":True,"total":46,"ported":46}
   if path=="/api/providers":return 200,{"providers":[{"id":id} for id in ids]}
   raise AssertionError("Unexpected external probe")
  with patch.object(r,"candidate_http",side_effect=response):
   r.verify_candidate(CANDIDATE)
  for corrupt in files:
   def wrong(path,version):
    return response(path,version)+b" changed" if path==corrupt else response(path,version)
   with patch.object(r,"candidate_http",side_effect=wrong):
    with self.assertRaises(r.Stop):r.verify_candidate(CANDIDATE)
  def missing_subsplease(path,version):
   if path=="/api/providers":
    return 200,{"providers":[{"id":"x"+str(i)} for i in range(46)]}
   return response(path,version)
  with patch.object(r,"candidate_http",side_effect=missing_subsplease):
   with self.assertRaises(r.Stop):r.verify_candidate(CANDIDATE)
 def test_reviewed_source_has_one_bulk_selector_and_50_pagination(self):
  app=(r.ROOT/"web/app.js").read_text(encoding="utf8")
  html=(r.ROOT/"web/index.html").read_text(encoding="utf8")
  assert 'const hiddenIndexerIds=new Set(["subsplease"]);' in app
  assert 'const RESULTS_PER_PAGE=50;' in app
  assert 'id="resultsPagination"' in html
  assert 'id="selectWorking"' not in html
  assert 'id="selectAllProviders">Selectează toate' in html

 def test_no_unrelated_candidate_fetch_or_unapproved_post(self):
  with self.assertRaises(r.Stop):r.candidate_http("/api/companion/magnet",CANDIDATE)
  with self.assertRaises(r.Stop):r.candidate_http("/api/resolve","not-uuid")
  with self.assertRaises(r.Stop):r.candidate_http(r.SEARCH_PATH,CANDIDATE,body={"provider":"nonameclub"})
 def test_upload_does_not_promote_or_print_secrets(self):
  with tempfile.TemporaryDirectory() as folder:
   tmp=Path(folder)/"test-config.jsonc"
   proc=SimpleNamespace(returncode=0,stdout="Worker Version ID: "+CANDIDATE,stderr="")
   with patch.object(r,"TEMP_CONFIG",tmp),patch.object(r.subprocess,"run",return_value=proc) as sp:
    self.assertEqual(r.upload({"name":"alexlab-magnetra","services":[{"binding":"FLUD_RELAY","service":"flud-remote-relay"}]}),CANDIDATE)
    self.assertFalse(tmp.exists())
    argv=sp.call_args.args[0]
    self.assertEqual(argv[0:3],["npx","--yes","wrangler@4.102.0"])
    self.assertEqual(argv[3:5],["versions","upload"])
    self.assertIn("--keep-vars",argv)
    self.assertNotIn("deploy",argv)
 def test_zero_five_full_version_only_with_prior_rollback(self):
  with patch.object(r,"source_guard",return_value={}),\
       patch.object(r,"split_guard",return_value=DEP0),\
       patch.object(r,"live_http",return_value=b"old-pwa"),\
       patch.object(r,"stable"),\
       patch.object(r,"upload",return_value=CANDIDATE),\
       patch.object(r,"_get_api",return_value={}),\
       patch.object(r,"verify_binding_payload"),\
       patch.object(r,"transition",side_effect=[DEP1,DEP5,DEP100]) as move,\
       patch.object(r,"verify_candidate") as candidate,\
       patch.object(r,"prove_real_owner_magnet") as magnet,\
       patch.object(r,"prove_owner_search_card") as card,\
       patch.object(r,"public_postflight") as public:
   self.assertEqual(r.release(),0)
   self.assertEqual([x.args[1:3] for x in move.call_args_list],[
    (r.BASELINE,{r.ACTIVE:100,CANDIDATE:0}),
    ({r.ACTIVE:100,CANDIDATE:0},{r.ACTIVE:95,CANDIDATE:5}),
    ({r.ACTIVE:95,CANDIDATE:5},{r.ACTIVE:0,CANDIDATE:100})])
   self.assertEqual(candidate.call_count,2)
   self.assertEqual(card.call_count,2)
   magnet.assert_called_once_with(CANDIDATE)
   public.assert_called_once_with(CANDIDATE)
 def test_known_failed_canary_restores_previous_0magnet(self):
  for current in [{r.ACTIVE:95,CANDIDATE:5},{r.ACTIVE:0,CANDIDATE:100}]:
   with patch.object(r,"snapshot",return_value=(DEP5,current)),\
        patch.object(r,"_get_api",return_value={}),\
        patch.object(r,"verify_binding_payload"),\
        patch.object(r,"stable"),\
        patch.object(r,"_wrangler_deploy",return_value=True) as deploy,\
        patch.object(r,"wait_for",return_value=DEP100):
    r.rollback_if_safe(CANDIDATE)
    self.assertEqual(deploy.call_args.args[0],[r.ACTIVE+"@100%",CANDIDATE+"@0%"])
  for unknown in [{r.ACTIVE:70,CANDIDATE:30},{r.ACTIVE:100,r.ROLLBACK:0}]:
   with patch.object(r,"snapshot",return_value=(DEP0,unknown)),patch.object(r,"_wrangler_deploy") as deploy:
    r.rollback_if_safe(CANDIDATE)
    deploy.assert_not_called()
 def test_failure_stops_then_calls_checked_rollback(self):
  with patch.dict(os.environ,{"MAGNETRA_INDEXERS_45_PAGING_50_RELEASE_ACTION":r.ACTION}),patch.object(r,"release",side_effect=r.Stop("safe")),patch.object(r,"rollback_if_safe") as rollback:
   self.assertEqual(r.main(),1)
   rollback.assert_called_once()
if __name__=="__main__":unittest.main()
