#!/usr/bin/env python3
"""Offline negative-path tests: exact existing zero-share resume, no upload."""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
import cloudflare_html_asset_guard as h
import resume_magnetra_auto_pause_c86c as m

R0={"id":"old-deployment"}
R1={"id":"new-deployment"}
RAW=b"<html><body><div>reviewed html</div>\n</body>\n</html>"
CF=(b'<script src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon="/cdn-cgi/rum">' +
    b'a'*210+b'</script>')
class ResumeTests(unittest.TestCase):
 def test_known_cf_edge_insertion_accepted_but_exact_source_preserved(self):
  self.assertEqual(h.verify_reviewed_html(RAW,RAW),"EXACT")
  self.assertEqual(h.verify_reviewed_html(RAW,RAW.replace(b"</body>",CF+b"</body>")),
                   "EXACT_PLUS_CLOUDFLARE_BEACON")
 def test_unknown_or_nontrailing_html_insertions_fail(self):
  cases=(
   RAW.replace(b"reviewed",b"tampered"),
   RAW.replace(b"</body>",b"<script>alert(1)</script></body>"),
   RAW.replace(b"</body>",CF+b"<iframe></iframe></body>"),
   RAW.replace(b"</body>",CF+b"X"*2600+b"</body>"),
   RAW.replace(b"</html>",CF+b"</html>"),
   RAW.replace(b"</body>",CF+b"</body>").replace(b"reviewed",b"altered")
  )
  for item in cases:
   with self.subTest(item=item[:30]),self.assertRaises(h.HTMLAssetMismatch):
    h.verify_reviewed_html(RAW,item)
 def test_default_cancel_no_network_no_write(self):
  with patch.dict(os.environ,{"MAGNETRA_AUTO_PAUSE_RESUME_ACTION":"CANCEL"}),patch.object(m,"current") as current,patch.object(m,"_wrangler_deploy") as deploy:
   self.assertEqual(m.execute(),2)
   current.assert_not_called();deploy.assert_not_called()
 def test_wrong_live_split_aborts_before_write(self):
  with patch.object(m,"current",side_effect=m.Stop("UNEXPECTED_LIVE_DEPLOYMENT_SPLIT")),patch.object(m,"_wrangler_deploy") as deploy:
   with self.assertRaisesRegex(m.Stop,"UNEXPECTED"):m.promote()
   deploy.assert_not_called()
 def test_verified_slot_promotes_once_without_upload(self):
  with patch.object(m,"current",return_value=R0) as current,patch.object(m,"bindings") as bindings,patch.object(m,"stable") as stable,patch.object(m,"verify_assets") as assets,patch.object(m,"_wrangler_deploy",return_value=True) as deploy,patch.object(m,"wait_for",return_value=R1) as wait:
   self.assertEqual(m.promote(),0)
   current.assert_called_once_with(m.SLOT)
   self.assertEqual(deploy.call_count,1)
   self.assertEqual(deploy.call_args.args[0],[m.OLD+"@0%",m.NEW+"@100%"])
   wait.assert_called_once_with(R0,m.SLOT,m.FULL,True)
   self.assertEqual(bindings.call_count,4)
   assets.assert_any_call(m.NEW,R0,m.SLOT)
   assets.assert_any_call(None,R1,m.FULL)
 def test_staged_asset_mismatch_aborts_prewrite(self):
  with patch.object(m,"current",return_value=R0),patch.object(m,"bindings"),patch.object(m,"stable"),patch.object(m,"verify_assets",side_effect=m.Stop("HTML_NOT_REVIEWED_SOURCE")) as assets,patch.object(m,"_wrangler_deploy") as deploy:
   with self.assertRaisesRegex(m.Stop,"HTML_NOT_REVIEWED"):m.promote()
   assets.assert_called_once_with(m.NEW,R0,m.SLOT)
   deploy.assert_not_called()
 def test_wrong_html_mime_and_transport_no_retry(self):
  with patch.object(m.urllib.request,"build_opener",side_effect=m.urllib.error.URLError("transport blocked")) as opener:
   with self.assertRaisesRegex(m.Stop,"HTML_ROOT_TRANSPORT_NO_RETRY"):m.html_root(m.NEW)
   opener.assert_called_once()
 def test_static_http_429_has_no_retry_or_write(self):
  with patch.object(m,"static_get",side_effect=m.Stop("STATIC_TRANSPORT_OR_HTTP_UNVERIFIED")) as get,patch.object(m.time,"sleep") as sleep,patch.object(m,"_wrangler_deploy") as deploy:
   with self.assertRaisesRegex(m.Stop,"STATIC_TRANSPORT"):m.verify_assets(m.NEW,R0,m.SLOT)
   get.assert_called_once();sleep.assert_not_called();deploy.assert_not_called()
 def test_restore_only_exact_new_full_and_single_write(self):
  with patch.object(m,"current",return_value=R1) as current,patch.object(m,"bindings") as bindings,patch.object(m,"stable"),patch.object(m,"_wrangler_deploy",return_value=True) as deploy,patch.object(m,"wait_for",return_value=R0) as wait:
   self.assertEqual(m.restore(),0)
   current.assert_called_once_with(m.FULL)
   self.assertEqual(deploy.call_args.args[0],[m.OLD+"@100%",m.NEW+"@0%"])
   deploy.assert_called_once()
   wait.assert_called_once_with(R1,m.FULL,m.SLOT,True)
   self.assertEqual(bindings.call_count,2)
 def test_no_unnecessary_new_upload_source_probe_or_flud_code(self):
  src=Path(m.__file__).read_text(encoding="utf8")
  wf=(m.ROOT/".github/workflows/magnetra-auto-pause-resume-c86c.yml").read_text()
  for forbidden in ("upload_version(", "/api/search", "/api/resolve", "companion/magnet", "wrangler versions upload"):
   self.assertNotIn(forbidden,src)
  self.assertIn("workflow_dispatch:",wf)
  self.assertNotIn("push:",wf)
  self.assertIn("default: CANCEL",wf)
if __name__=="__main__":unittest.main()
