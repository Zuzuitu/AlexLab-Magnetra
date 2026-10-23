"""No-network regression guards for owner-gated immutable Companion release."""
from __future__ import annotations

import io
import json
import os
import sys
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import release_magnetra_companion_binding_20261023 as release


class FakeHttpError(urllib.error.HTTPError):
    def __init__(self, status, data):
        super().__init__(release.ORIGIN + "/api/companion/status", status,
                         "synthetic test", None, io.BytesIO(data))


class FakeOpener:
    def __init__(self, status, message):
        self.status = status
        self.message = message

    def open(self, request, timeout):
        assert request.get_method() == "POST"
        assert request.full_url == release.ORIGIN + "/api/companion/status"
        assert request.get_header("Origin") == release.ORIGIN
        assert b"TEST_TOKEN_NOT_REAL" in request.data
        raise FakeHttpError(self.status, json.dumps({"error": self.message}).encode())


class ReleaseGuardTests(unittest.TestCase):
    def test_no_approval_means_no_api_calls_or_write(self):
        with patch.dict(os.environ, {"MAGNETRA_COMPANION_RELEASE_ACTION": ""}):
            with patch.object(release, "run", side_effect=AssertionError("forbidden")):
                self.assertEqual(release.main(), 2)

    def test_staged_401_success_uses_fake_device_and_no_real_token(self):
        with patch.object(release.urllib.request, "build_opener", return_value=FakeOpener(401, "Unauthorized")):
            release.fake_status_probe(release.ACTIVE)

    def test_502_fails_before_canary(self):
        with patch.object(release.urllib.request, "build_opener",
                          return_value=FakeOpener(502, "Companion remote relay is unavailable.")):
            with self.assertRaises(release.Stop):
                release.fake_status_probe(release.ACTIVE)

    def test_403_fails_closed(self):
        with patch.object(release.urllib.request, "build_opener", return_value=FakeOpener(403, "Forbidden")):
            with self.assertRaises(release.Stop):
                release.fake_status_probe(release.ACTIVE)

    def test_source_binding_target_is_exactly_existing_relay(self):
        config = release.reviewed_config()
        self.assertEqual(config["services"], [{"binding": "FLUD_RELAY", "service": "flud-remote-relay"}])
        self.assertEqual(config["routes"], [{"pattern": "index.alexlab.media", "custom_domain": True}])

    def test_staging_target_is_zero_and_baseline_is_immutable(self):
        self.assertEqual(release.INITIAL, {
            "a088fa41-233d-48d3-bd4c-52be6194fda8": 100,
            "056d8394-79b0-459a-b93e-b5f5a8a7295d": 0,
        })
        self.assertNotEqual(release.ACTIVE, release.ROLLBACK)
        self.assertEqual(release.TEST_DEVICE, "MAGNETRA_DIAG_NOTREAL_1234")
        self.assertNotIn("Bearer", release.TEST_TOKEN)


if __name__ == "__main__":
    unittest.main()
