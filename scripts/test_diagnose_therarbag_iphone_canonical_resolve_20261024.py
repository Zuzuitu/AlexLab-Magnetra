import unittest
from unittest.mock import patch
import diagnose_therarbag_iphone_canonical_resolve_20261024 as d
CARD={"provider":"therarbag","name":"Cyberpunk Edgerunners 2 Original Series Soundtrack","size":"352.7 MB","details":d.PUBLIC_URL,"magnetSource":None}
class Tests(unittest.TestCase):
 def test_exact_source_no_magnet_source(self):
  with patch("builtins.print") as printer:d.verify_source({"results":[CARD]})
  value=" ".join(" ".join(map(str,x.args)) for x in printer.call_args_list)
  self.assertIn("OWNER_SEARCH_MAGNETSOURCE: ABSENT",value)
  self.assertNotIn(d.PUBLIC_URL,value)
 def test_different_source_no_private_link_logged(self):
  with patch("builtins.print") as printer:d.verify_source({"results":[{**CARD,"magnetSource":"https://therarbg.com/secret"}]})
  value=" ".join(" ".join(map(str,x.args)) for x in printer.call_args_list)
  self.assertIn("OWNER_SEARCH_MAGNETSOURCE: DIFFERENT",value)
  self.assertNotIn("secret",value)
 def test_source_mismatch_stops(self):
  with self.assertRaises(d.Stop):d.verify_source({"results":[{**CARD,"details":d.PUBLIC_URL+"?q=wrong"}]})
 def test_direct_success_and_original_fingerprint(self):
  trace={"build":"THERARBAG_IPHONE_DIAG_V1","detailFingerprint":d.fingerprint(d.PUBLIC_URL),"htmlStage":"HTML_NO_BTIH","jsonStage":"JSON_VALID"}
  magnet="magnet:?xt=urn:btih:"+"a"*40
  with patch("builtins.print") as printer:d.verify_resolver(fn=lambda *args,**kw:(200,{"magnet":magnet,"diagnostic":trace}))
  value=" ".join(" ".join(map(str,x.args)) for x in printer.call_args_list)
  self.assertIn("DIRECT_CANONICAL_PROBE_CLASS: VALID_MAGNET",value)
  self.assertNotIn(magnet,value)
 def test_direct_error_enum(self):
  trace={"build":"THERARBAG_IPHONE_DIAG_V1","detailFingerprint":d.fingerprint(d.PUBLIC_URL),"htmlStage":"HTML_NO_BTIH","jsonStage":"JSON_HTTP_503"}
  with patch("builtins.print") as printer:d.verify_resolver(fn=lambda *args,**kw:(502,{"code":"DETAIL_NO_BTIH","diagnostic":trace}))
  value=" ".join(" ".join(map(str,x.args)) for x in printer.call_args_list)
  self.assertIn("DIRECT_CANONICAL_ERROR_CODE: DETAIL_NO_BTIH",value)
 def test_unapproved_does_not_fetch(self):
  with patch.object(d.sys,"argv",["script"]),patch.object(d,"api_search") as api:
   self.assertEqual(d.main(),2)
   api.assert_not_called()
if __name__=="__main__":unittest.main()
