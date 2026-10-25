"""Fail-closed offline regressions for reviewed 11-source release."""
import hashlib
import os
import unittest
from unittest.mock import patch
import release_curated_11_indexers_50_20261025 as r

NEW="11111111-1111-4111-8111-111111111111"
MAGNET="magnet:?xt=urn:btih:"+"a"*40

class Tests(unittest.TestCase):
 def test_exact_baseline_and_owner_gate(self):
  self.assertEqual(r.BASELINE,{r.ACTIVE:100})
  self.assertEqual(r.ACTIVE,"8d9c19f4-ca38-428b-888e-757ef578c829")
  self.assertEqual(r.OLD_PUBLIC_SHA_PREFIX,"1160fa81597ce6ca")
  with patch.dict(os.environ,{"MAGNETRA_CURATED_11_RELEASE_ACTION":""}),patch.object(r,"release") as run:
   self.assertEqual(r.main(),2)
   run.assert_not_called()
 def test_pinned_source_has_11_selectable_and_50_pages(self):
  with patch.object(r,"validate_source",return_value={"name":"alexlab-magnetra"}):
   self.assertEqual(r.source_guard()["name"],"alexlab-magnetra")
 def test_no_flud_or_unlisted_routes_in_immutable_reads(self):
  for url in ["/api/companion/magnet","/api/search","//invalid","https://evil.example"]:
   with self.assertRaises(r.Stop):r.candidate_http(url,NEW)
  with self.assertRaises(r.Stop):r.candidate_http("/api/resolve",NEW,body={"provider":"nonameclub"})
 def test_five_asset_validation_and_original_46_catalog(self):
  app=(r.ROOT/"web/app.js").read_bytes()
  ids=[{"id":"subsplease"}]+[{"id":"source"+str(n)} for n in range(45)]
  def request(path,version):
   assert version==NEW
   if path=="/api/health":return (200,{"ok":True,"total":46,"ported":46})
   if path=="/api/providers":return (200,{"providers":ids})
   path_to_file={"/app.js":"web/app.js","/styles.css":"web/styles.css","/sw.js":"web/sw.js","/i18n.js":"web/i18n.js","/":"web/index.html"}
   return (r.ROOT/path_to_file[path]).read_bytes()
  with patch.object(r,"candidate_http",side_effect=request):r.verify_candidate(NEW)
  with patch.object(r,"candidate_http",side_effect=lambda path,version:b"tampered" if path=="/app.js" else request(path,version)):
   with self.assertRaises(r.Stop):r.verify_candidate(NEW)
 def test_version_only_canary_stages_ordered(self):
  with patch.object(r,"source_guard",return_value={}),patch.object(r,"split_guard",return_value={"id":"initial"}),patch.object(r,"live_http",return_value=b"old"),patch.object(r,"OLD_PUBLIC_SHA_PREFIX",hashlib.sha256(b"old").hexdigest()[:16]),patch.object(r,"stable"),patch.object(r,"upload",return_value=NEW),patch.object(r,"_get_api",return_value={}),patch.object(r,"verify_binding_payload"),patch.object(r,"transition",side_effect=[{"id":"zero"},{"id":"five"},{"id":"full"}]) as transition,patch.object(r,"verify_candidate") as candidate,patch.object(r,"prove_real_owner_magnet") as magnet,patch.object(r,"prove_owner_search_card") as card,patch.object(r,"public_postflight") as final:
   self.assertEqual(r.release(),0)
   self.assertEqual([x.args[1:3] for x in transition.call_args_list],[
    (r.BASELINE,{r.ACTIVE:100,NEW:0}),
    ({r.ACTIVE:100,NEW:0},{r.ACTIVE:95,NEW:5}),
    ({r.ACTIVE:95,NEW:5},{r.ACTIVE:0,NEW:100})])
   self.assertEqual(candidate.call_count,2)
   magnet.assert_called_once_with(NEW)
   final.assert_called_once_with(NEW)
 def test_unexpected_split_never_rolls_back_blindly(self):
  with patch.object(r,"snapshot",return_value=({"id":"unknown"},{"different":100})),patch.object(r,"_wrangler_deploy") as deploy:
   r.rollback_if_safe(NEW)
   deploy.assert_not_called()

if __name__=="__main__":unittest.main()
