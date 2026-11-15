#!/usr/bin/env python3
"""Offline contract for BTDigg private CAPTCHA PWA asset smoke."""
import importlib.util
import unittest
from pathlib import Path

PATH=Path(__file__).with_name("check-btdigg-private-verification-live.py")
ROOT=PATH.parent.parent
spec=importlib.util.spec_from_file_location("btdigg_private_viewer_smoke",PATH)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class PrivateViewerSmokeContracts(unittest.TestCase):
    def test_reviewed_app_and_html_contain_expected_feature_and_csp(self):
        app=(ROOT/"web/app.js").read_text(encoding="utf8")
        html=(ROOT/"web/index.html").read_text(encoding="utf8")
        csp=(ROOT/"web/_headers").read_text(encoding="utf8")
        self.assertIn("NO_SOURCE_SEARCH",module.verify(app,html,csp))

    def test_old_or_untrusted_assets_fail_closed(self):
        app=(ROOT/"web/app.js").read_text(encoding="utf8")
        html=(ROOT/"web/index.html").read_text(encoding="utf8")
        csp=(ROOT/"web/_headers").read_text(encoding="utf8")
        for change in ((app.replace("validatedBTDiggViewerOrigin","legacy"),html,csp),
                       (app,html.replace('id="btdiggViewerFrame"','id="old"'),csp),
                       (app,html,csp.replace(module.FRAME_DIRECTIVE,""))):
            with self.assertRaises(AssertionError):
                module.verify(*change)

    def test_no_provider_or_private_site_traffic_in_smoke(self):
        src=PATH.read_text(encoding="utf8")
        self.assertIn('get("/app.js")',src)
        self.assertIn('get("/")',src)
        self.assertNotIn('get("/api/search',src)
        self.assertNotIn("btdig.com",src)
        self.assertNotIn("tailscale ip",src)
        self.assertNotIn("/vnc.html",src)

if __name__=="__main__":
    unittest.main()
