import io,os,json,unittest
from unittest.mock import patch
from contextlib import redirect_stdout
import diagnose_nonameclub_card_exact_20261025 as d

HASH="123456789abcdef0123456789abcdef012345678"
MAGNET="magnet:?xt=urn:btih:"+HASH
class TestSearchCard(unittest.TestCase):
 def test_bounded_same_card(self):
  rows=[{"provider":"nonameclub","details":"https://nnmclub.to/forum/viewtopic.php?t=1"},
        {"provider":"nonameclub","details":d.EXACT,"magnetSource":None}]
  body=json.dumps({"results":rows}).encode()
  n,r,total=d.extract(200,"application/json",body)
  self.assertEqual((n,total),(1,2))
  self.assertEqual(d.row_stage(r),"CANONICAL_DETAILS_ONLY")
 def test_wrong_card_no_guess(self):
  body=json.dumps({"results":[{"provider":"nonameclub","details":"https://nnmclub.to/forum/viewtopic.php?t=1896365"}]}).encode()
  n,r,total=d.extract(200,"application/json",body)
  self.assertEqual((n,r,total),(0,None,1))
 def test_same_card_with_auxiliary_or_inline_magnet(self):
  self.assertEqual(d.row_stage({"details":d.EXACT,"magnetSource":"https://nnmclub.to/elsewhere"}),"AUXILIARY_MAGNET_SOURCE_PRESENT")
  self.assertEqual(d.row_stage({"details":d.EXACT,"magnet":MAGNET}),"PRE_RESOLVED_MAGNET")
 def test_strict_url_method_guards(self):
  with self.assertRaises(d.Stop):d.request("https://nnmclub.to/forum/viewtopic.php?t=1896364")
  with self.assertRaises(d.Stop):d.request(d.PROD+"/api/resolve")
  with self.assertRaises(d.Stop):d.request(d.PROD+"/api/resolve",{"provider":"nonameclub","details":"https://nnmclub.to/forum/viewtopic.php?t=9999"})
 def test_no_approval_no_calls(self):
  with patch.object(d.sys,"argv",["test"]),patch.object(d,"request") as req,redirect_stdout(io.StringIO()):
   self.assertEqual(d.main(),2);req.assert_not_called()
 def test_real_order_and_secret_redaction(self):
  outputs=io.StringIO();calls=[]
  def mocked(url,payload=None):
   calls.append((url,payload))
   if "/api/search?" in url:
    return (200,"application/json",json.dumps({"results":[{"provider":"nonameclub","details":d.EXACT,"magnet":None,"name":"PRIVATE_TITLE"}]}).encode())
   return (200,"application/json",json.dumps({"magnet":MAGNET}).encode())
  with patch.dict(os.environ,{"MAGNETRA_NONAMECLUB_CARD_READONLY":d.ACTION}),patch.object(d,"request",side_effect=mocked),redirect_stdout(outputs):
   self.assertEqual(d.run(),0)
  self.assertEqual(len(calls),2)
  self.assertEqual(calls[-1][1],{"provider":d.P,"details":d.EXACT})
  for secret in (MAGNET,HASH,d.EXACT,"PRIVATE_TITLE"):
   self.assertNotIn(secret,outputs.getvalue())
  self.assertIn("OWNER_CARD_EXACT_RESOLVE_CLASS: VALID_BTIH",outputs.getvalue())
if __name__=="__main__":unittest.main()
