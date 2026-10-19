#!/usr/bin/env python3
"""Offline regression for production static PWA/checkout parity observation."""
import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

script = Path(__file__).with_name("check-production-smoke.py")
spec = importlib.util.spec_from_file_location("magnetra_prod_smoke_parity", script)
smoke = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = smoke
spec.loader.exec_module(smoke)


class ProductionAssetParityTests(unittest.TestCase):
    def test_matching_bytes_are_confirmed_without_provider_queries(self):
        reviewed = (smoke.ROOT / "web" / "app.js").read_text("utf-8")
        with patch.object(smoke, "fetch", return_value=reviewed) as get:
            self.assertEqual(smoke.app_asset_parity(), "LIVE_APP_JS_PARITY=PASS")
            get.assert_called_once_with("/app.js", response_json=False)

    def test_stale_or_altered_live_asset_is_reported_not_deployed(self):
        with patch.object(smoke, "fetch", return_value="old iPhone app bundle") as get:
            self.assertEqual(smoke.app_asset_parity(), "LIVE_APP_JS_PARITY=DRIFT")
            get.assert_called_once_with("/app.js", response_json=False)


if __name__ == "__main__":
    unittest.main()
