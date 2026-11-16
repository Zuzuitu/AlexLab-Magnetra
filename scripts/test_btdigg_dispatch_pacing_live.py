#!/usr/bin/env python3
"""Offline regression for the GET-only BTDigg pacing production smoke."""
import importlib.util
import unittest
from pathlib import Path

FILE=Path(__file__).with_name("check-btdigg-dispatch-pacing-live.py")
ROOT=FILE.parent.parent
spec=importlib.util.spec_from_file_location("btdigg_dispatch_pacing_smoke",FILE)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class DispatchPacingSmokeTests(unittest.TestCase):
    def assets(self):
        return ((ROOT/"web/app.js").read_text(encoding="utf8"),
                (ROOT/"web/index.html").read_text(encoding="utf8"),
                (ROOT/"web/_headers").read_text(encoding="utf8"))

    def test_current_assets_are_dispatch_anchored(self):
        self.assertIn("NO_SOURCE_SEARCH",module.verify(*self.assets()))

    def test_old_response_completion_reset_fails_closed(self):
        app,html,csp=self.assets()
        search_anchor='const observed=(data.stats||[]).find(s=>s.provider===id);'
        self.assertIn(search_anchor,app)
        old=app.replace(search_anchor,
            'btdiggPacing.nextAllowedAt=Date.now()+BTDIGG_MIN_GAP_MS;\n'+search_anchor)
        with self.assertRaisesRegex(AssertionError,"post-response timer"):
            module.verify(old,html,csp)

    def test_missing_dispatch_timestamp_fails_closed(self):
        app,html,csp=self.assets()
        no_stamp=app.replace("recordBTDiggRequestDispatch();",
                             "/* no source stamp */",1)
        with self.assertRaises(AssertionError):
            module.verify(no_stamp,html,csp)

    def test_private_viewer_restriction_remains(self):
        app,html,csp=self.assets()
        with self.assertRaisesRegex(AssertionError,"CSP"):
            module.verify(app,html,csp.replace(
                "frame-src https://*.ts.net:8444",""))

    def test_live_smoke_never_searches_or_connects_to_private_services(self):
        source=FILE.read_text(encoding="utf8")
        self.assertIn('get("/app.js")',source)
        self.assertIn('get("/")',source)
        self.assertNotIn('get("/api/search',source)
        self.assertNotIn('get("/vnc.html',source)
        self.assertNotIn('get("/api/providers',source)
        self.assertNotIn("btdig.com",source)
        self.assertNotIn("tailscale serve",source)

if __name__=="__main__":
    unittest.main()
