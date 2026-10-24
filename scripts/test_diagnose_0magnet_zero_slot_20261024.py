import unittest,io
from unittest.mock import patch
from contextlib import redirect_stdout
import diagnose_0magnet_zero_slot_20261024 as d

class TestReadonly(unittest.TestCase):
 def test_no_approval_no_egress(self):
  with patch.object(d.sys,"argv",["script"]),patch.object(d,"snapshot") as snapshot,patch.object(d,"fetch") as fetch,redirect_stdout(io.StringIO()):
   self.assertEqual(d.main(),2)
   snapshot.assert_not_called()
   fetch.assert_not_called()
 def test_asset_cases(self):
  self.assertEqual(d.asset_state(200,"application/javascript",b"same",b"same"),"SHA_MATCH")
  self.assertEqual(d.asset_state(200,"application/javascript",b"old",b"new"),"SHA_MISMATCH")
  self.assertEqual(d.asset_state(200,"text/html",b"same",b"same"),"MIME_MISMATCH")
  self.assertEqual(d.asset_state(403,"text/html",b"",b"same"),"HTTP_403")
 def test_fixed_routes_only(self):
  with self.assertRaises(d.Stop):d.fetch("/api/resolve",d.NEW)
  with self.assertRaises(d.Stop):d.fetch("https://example.com",None)
 def test_catalog_shape(self):
  import json
  data=json.dumps({"providers":[{"id":"0magnet"}]*46}).encode()
  self.assertEqual(d.api_state(200,"application/json",data,"/api/providers"),"CATALOG_IDENTITIES_MISMATCH")
 def test_wrong_split_no_http(self):
  with patch.dict(d.os.environ,{"MAGNETRA_0MAGNET_ZERO_READONLY":d.ACTION}),patch.object(d,"validated_source"),patch.object(d,"verify_account_scripts"),patch.object(d,"account_list",return_value={}),patch.object(d,"snapshot",return_value=({"id":"demo"},{d.ACTIVE:95,d.NEW:5})),patch.object(d,"fetch") as fetch:
   with self.assertRaises(d.Stop):d.run()
   fetch.assert_not_called()

if __name__=="__main__":unittest.main()
