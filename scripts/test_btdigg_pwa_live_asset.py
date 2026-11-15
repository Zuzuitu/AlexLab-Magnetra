#!/usr/bin/env python3
"""Offline contracts for GET-only BTDigg activation smoke."""
import importlib.util
from pathlib import Path
import unittest

SOURCE=Path(__file__).with_name("check-btdigg-pwa-live-asset.py")
spec=importlib.util.spec_from_file_location("btdigg_pwa_live_smoke",SOURCE)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class BTDiggPWAAssetSmokeTests(unittest.TestCase):
    def test_reviewed_pwa_content_passes_without_network(self):
        source=(SOURCE.parent.parent/"web/app.js").read_bytes()
        self.assertEqual(module.verify(lambda url:source),
                         "PASS: deployed BTDigg PWA JS; NO_SOURCE_SEARCH")
    def test_old_assets_fail_closed(self):
        old=(SOURCE.parent.parent/"web/app.js").read_bytes().replace(
            b"const BTDIGG_MIN_GAP_MS=30_000;",
            b"const BTDIGG_MIN_GAP_MS=5500;")
        with self.assertRaisesRegex(AssertionError,"not the reviewed"):
            module.verify(lambda url:old)
    def test_static_validator_cannot_reach_source_search(self):
        text=SOURCE.read_text(encoding="utf-8")
        self.assertNotIn('urlopen(ORIGIN+"/api/search"',text)
        self.assertNotIn("btdig.com",text)
        self.assertIn('ORIGIN+"/app.js"',text)

if __name__=="__main__":
    unittest.main()
