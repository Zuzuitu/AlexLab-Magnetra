"""Offline regression tests: read-only postrelease check, no network/writes."""
import json
import unittest
from unittest.mock import patch
import audit_pwa_45_50_live_readonly_20261025 as a

LIVE="11111111-1111-4111-8111-111111111111"
OLD="76a15eae-5c8c-41a2-bace-adb9b2460933"
class Checks(unittest.TestCase):
 def test_pin_and_source_features_from_reviewed_code(self):
  a.source_guard()
 def test_exact_public_hashes_and_original_46_registry(self):
  ids=["subsplease","0magnet","therarbag"]+[str(i) for i in range(43)]
  def fixture(path,mime):
   if path=="/api/health":
    return json.dumps({"ok":True,"total":46,"ported":46}).encode()
   if path=="/api/providers":
    return json.dumps({"providers":[{"id":id} for id in ids]}).encode()
   item=next((p for p in a.ASSETS if p[0]==path),None)
   assert item is not None
   return (a.ROOT/item[1]).read_bytes()
  with patch.object(a,"read_public",side_effect=fixture):
   a.verify_assets()
  def corrupted(path,mime):
   data=fixture(path,mime)
   return data+b"changed" if path=="/app.js" else data
  with patch.object(a,"read_public",side_effect=corrupted):
   with self.assertRaises(a.Stop):a.verify_assets()
 def test_reads_limited_to_known_public_paths(self):
  with self.assertRaises(a.Stop):a.read_public("/api/companion/magnet","application/json")
  with self.assertRaises(a.Stop):a.read_public("https://attacker.example","application/json")
 def test_account_binding_and_exact_100_percent_split(self):
  old={LIVE:100,OLD:0}
  with patch.object(a,"account_list",return_value={}),       patch.object(a,"verify_account_scripts"),       patch.object(a,"snapshot",return_value=({"id":"DEP1"},old)),       patch.object(a,"_get_api",return_value={}),       patch.object(a,"verify_binding_payload") as verify:
   active,split=a.verify_deployment()
   self.assertEqual(active,LIVE)
   self.assertEqual(split,old)
   self.assertEqual(verify.call_count,2)
 def test_fail_closed_for_unverified_traffic_split(self):
  for bad in [{LIVE:50,OLD:50},{LIVE:100,OLD:20},{LIVE:0,OLD:0}]:
   with patch.object(a,"account_list",return_value={}),        patch.object(a,"verify_account_scripts"),        patch.object(a,"snapshot",return_value=({"id":"DEP1"},bad)),        patch.object(a,"_get_api") as api:
    with self.assertRaises(a.Stop):a.verify_deployment()
    api.assert_not_called()
 def test_read_only_main_never_triggers_deployment(self):
  with patch.object(a,"source_guard"),patch.object(a,"verify_assets") as assets,       patch.object(a,"verify_deployment",return_value=(LIVE,{LIVE:100})):
   self.assertEqual(a.main(),0)
   self.assertEqual(assets.call_count,2)
if __name__=="__main__":
 unittest.main()
