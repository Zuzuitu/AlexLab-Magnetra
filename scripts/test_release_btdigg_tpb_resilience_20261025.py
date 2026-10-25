"""Fail closed checks for the BTDigg and TPB rollout."""
import os
import unittest
from unittest.mock import patch
import release_btdigg_tpb_resilience_20261025 as release

class Tests(unittest.TestCase):
    def test_explicit_activation_required(self):
        with patch.dict(os.environ, {"MAGNETRA_BTDIGG_TPB_RELEASE_ACTION": ""}):
            with patch.object(release, "release") as execute:
                self.assertEqual(release.main(), 2)
                execute.assert_not_called()

    def test_original_provider_set_and_baseline(self):
        self.assertEqual(set(release.POSITIVE_PATHS), {"btdigg", "thepiratebay"})
        self.assertEqual(release.BASELINE, {
            "74754dac-1842-47b2-8e6f-92a10731f124": 100,
            "8d9c19f4-ca38-428b-888e-757ef578c829": 0,
        })

    def test_disallowed_api_paths_fail_closed(self):
        for path in ["/api/companion/magnet", "/api/search", "//outside.example"]:
            with self.assertRaises(release.Stop):
                release.candidate_http(path, "11111111-1111-4111-8111-111111111111")

if __name__ == "__main__":
    unittest.main()
