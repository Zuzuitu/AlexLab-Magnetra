#!/usr/bin/env python3
"""Offline fixture audit for BTDigg one-shot PWA static release."""
import importlib.util
import unittest
from pathlib import Path

FILE=Path(__file__).with_name("check-btdigg-one-shot-retry-live.py")
ROOT=FILE.parent.parent
spec=importlib.util.spec_from_file_location("one_shot_btdigg_assets",FILE)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class OneShotPWAAssetSmoke(unittest.TestCase):
    def fixtures(self):
        return (
            (ROOT/"web/app.js").read_text(encoding="utf8"),
            (ROOT/"web/index.html").read_text(encoding="utf8"),
            (ROOT/"web/i18n.js").read_text(encoding="utf8"),
            (ROOT/"web/styles.css").read_text(encoding="utf8"),
            (ROOT/"web/_headers").read_text(encoding="utf8"),
        )

    def test_reviewed_release_assets(self):
        self.assertIn("NO_PROVIDER_SEARCH",module.verify(*self.fixtures()))

    def test_no_one_shot_or_private_viewer_fails_closed(self):
        app,html,i18n,css,headers=self.fixtures()
        cases=(
            (app.replace("fetchBTDiggWithOneGuardedNewTab","old"),html,i18n,css,headers),
            (app,html.replace('id="btdiggViewerFrame"','id="old"'),i18n,css,headers),
            (app,html,i18n.replace('"Inspect BTDigg refusal in Magnetra"','"old"'),css,headers),
            (app,html,i18n,css.replace("#btdiggVerificationRetry[hidden]","#legacy"),headers),
            (app,html,i18n,css,headers.replace("frame-src https://*.ts.net:8444","")),
        )
        for args in cases:
            with self.assertRaises(AssertionError):
                module.verify(*args)

    def test_no_search_or_private_link_calls_in_prod_smoke(self):
        source=FILE.read_text(encoding="utf8")
        for static in ('get_static("/")','get_static("/app.js")',
                       'get_static("/i18n.js")','get_static("/styles.css")'):
            self.assertIn(static,source)
        self.assertNotIn('get_static("/api/search',source)
        self.assertNotIn('get_static("/vnc.html',source)
        self.assertNotIn("btdig.com",source)
        self.assertNotIn("tailscale serve",source)


if __name__=="__main__":
    unittest.main()
