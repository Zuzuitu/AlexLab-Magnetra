import io,os,unittest
from contextlib import redirect_stdout
from unittest.mock import patch
import diagnose_nonameclub_owner_exact_20261025 as d

BTIH="0123456789abcdef0123456789abcdef01234567"
MAGNET="magnet:?xt=urn:btih:"+BTIH

class TestExactOwner(unittest.TestCase):
 def test_exact_url_and_no_calls_without_owner_mode(self):
  self.assertEqual(d.ORIGINAL,"https://nnmclub.to/forum/viewtopic.php?t=1896364")
  with patch.object(d.sys,"argv",["script"]),patch.object(d,"request_exact") as call,redirect_stdout(io.StringIO()):
   self.assertEqual(d.main(),2);call.assert_not_called()
 def test_block_unapproved_urls_and_body(self):
  with self.assertRaises(d.Stop):d.request_exact("https://external.example/")
  with self.assertRaises(d.Stop):d.request_exact(d.PRODUCTION,{"provider":"anything","details":d.ORIGINAL})
 def test_real_worker_selector_parity_and_icon_distinctions(self):
  body=('<html><a href="'+MAGNET+'&amp;dn=x"><img alt="Примагнититься"></a></html>').encode()
  self.assertEqual(d.source_summary(200,"text/html",body),("HTML_MAGNET_ANCHOR_VALID",BTIH))
  x=b'<html><a href="/forum/magnet-link"><img alt="Magnet"></a></html>'
  self.assertEqual(d.source_summary(200,"text/html",x)[0],"MAGNET_ICON_ANCHOR_WITHOUT_MAGNET_HREF")
  x=b'<html><a onclick="location.href=&#39;magnet:?xt=urn:btih:dummy&#39;"><img alt="Magnet"></a></html>'
  self.assertEqual(d.source_summary(200,"text/html",x)[0],"JS_ONCLICK_MAGNET_ONLY")
  self.assertEqual(d.source_summary(403,"text/html",b"")[0],"HTTP_403")
 def test_response_class(self):
  import json
  val=json.dumps({"magnet":MAGNET}).encode()
  self.assertEqual(d.worker_summary(200,"application/json",val),("RESOLVED_VALID_BTIH",BTIH))
  msg=json.dumps({"error":"provider details page contains no supported magnet link"}).encode()
  self.assertEqual(d.worker_summary(502,"application/json",msg)[0],"NO_SUPPORTED_MAGNET_IN_HTML")
 def test_no_sensitive_values_logged_or_devices_contacted(self):
  requests=[]
  def fake(url,payload=None):
   requests.append((url,payload))
   if url==d.ORIGINAL:return (200,"text/html",('<a href="'+MAGNET+'"><img alt="Magnet"></a>').encode())
   if url==d.PRODUCTION:return (200,"application/json",__import__('json').dumps({"magnet":MAGNET}).encode())
   self.fail("Extra request")
  output=io.StringIO()
  with patch.dict(os.environ,{"MAGNETRA_NONAMECLUB_OWNER_READONLY":d.ACTION}),patch.object(d,"request_exact",fake),redirect_stdout(output):
   self.assertEqual(d.run(),0)
  self.assertEqual(requests,[(d.ORIGINAL,None),(d.PRODUCTION,{"provider":"nonameclub","details":d.ORIGINAL})])
  for secret in (MAGNET,BTIH,d.ORIGINAL):
   self.assertNotIn(secret,output.getvalue())
  self.assertIn("SOURCE_AND_WORKER_BTIH_EQUAL: YES",output.getvalue())
if __name__=="__main__":unittest.main()
