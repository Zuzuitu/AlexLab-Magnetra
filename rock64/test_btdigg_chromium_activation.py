#!/usr/bin/env python3
"""Offline sanity of explicitly owner-controlled Chromium bridge activation."""
from pathlib import Path
import ast
import unittest

ROOT=Path(__file__).resolve().parent.parent
class ActivationContracts(unittest.TestCase):
    def test_readonly_gate_is_before_mutating_service(self):
        text=(ROOT/"rock64/activate-btdigg-chromium-bridge.sh").read_text()
        self.assertIn('"--enable"',text)
        self.assertIn("CHROMIUM_READY:",text)
        self.assertIn('state.get("visible_source_rate_limited") is not False',text)
        self.assertIn('state.get("selected_tab_verified") is not True',text)
        self.assertIn('LoadCredential=browser_token:',text)
        self.assertLess(text.index("CHROMIUM_READY:"),text.index("ROLLBACK_NEEDED=1"))
        self.assertIn('rm -f -- "$DROP" "$CREDENTIAL"',text)
        self.assertNotIn("/v1/search?q=",text)
        self.assertNotIn("cloudflared",text)
    def test_python_gateway_still_defaults_to_original_source(self):
        src=(ROOT/"rock64/btdigg_gateway.py").read_text()
        ast.parse(src)
        self.assertIn('if mode in ("", "0"):',src)
        self.assertIn('BROWSER_PRIVATE_PORT = 18896',src)
        self.assertIn('http.client.HTTPConnection("127.0.0.1", BROWSER_PRIVATE_PORT',src)
        self.assertIn('provider = SearchProvider(fetcher=browser_bridge.fetch) if browser_bridge else SearchProvider()',src)
if __name__=="__main__":
    unittest.main()
