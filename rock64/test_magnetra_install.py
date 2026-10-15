#!/usr/bin/env python3
"""Offline regression tests. Never touch physical services, source APIs or config."""
import contextlib
import importlib.util
import io
import json
import pathlib
import subprocess
import sys
import unittest
from urllib.error import HTTPError, URLError
from collections import Counter
from unittest.mock import patch

ROOT = pathlib.Path(__file__).parent
FILE = ROOT / "check-magnetra-gateway.py"
spec = importlib.util.spec_from_file_location("magnetra_acceptance", FILE)
accept = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = accept
spec.loader.exec_module(accept)

IMDB = "460681"
MAGNET1 = "magnet:?xt=urn:btih:" + "a" * 40
MAGNET2 = "magnet:?xt=urn:btih:" + "b" * 40
PRIVATE = "VerySensitivePrivateTitle-DoNotPrint"
SOURCE = {"imdb_id": IMDB, "torrents_count": 2, "torrents": [
    {"imdb_id": IMDB, "magnet_url": MAGNET1, "title": PRIVATE},
    {"imdb_id": IMDB, "magnet_url": MAGNET2, "title": PRIVATE},
]}
RECENT = {"torrents": [SOURCE["torrents"][0]]}


class AcceptanceTests(unittest.TestCase):
    def test_no_secrets_or_live_network_in_static_contract(self):
        installer = (ROOT / "install-magnetra-gateway.sh").read_text(encoding="utf8")
        unit = (ROOT / "magnetra-gateway.service").read_text(encoding="utf8")
        self.assertEqual(subprocess.run(
            ["bash", "-n", str(ROOT / "install-magnetra-gateway.sh")],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            check=False).returncode, 0)
        for required in (
            "EUID", "systemctl is-active --quiet",
            "systemctl show -p LoadState", "ss -H -ltn",
            'python3 -B -m unittest discover',
            "os.O_EXCL", "os.O_NOFOLLOW", "secrets.token_urlsafe",
            "trap rollback EXIT", "systemctl daemon-reload",
            "MAGNETRA_GATEWAY_TOKEN", "MAGNETRA_EZTV_TOKEN",
            "check-magnetra-gateway.py", "--smoke",
        ):
            self.assertIn(required, installer)
        for forbidden in ("Rotate token", "global_fetch_strictly_public",
                          "wrangler deploy", "cloudflared tunnel create",
                          "systemctl restart magnetra-btdigg",
                          "systemctl restart magnetra-eztv",
                          "systemctl stop magnetra-btdigg"):
            self.assertNotIn(forbidden, installer.lower())
        self.assertIn("DynamicUser=yes", unit)
        self.assertIn("MemoryMax=128M", unit)
        self.assertIn("CPUQuota=20%", unit)

    def test_positive_source_detection_never_makes_up_imdb(self):
        self.assertEqual(accept.source_candidates(RECENT), [IMDB])
        self.assertEqual(accept.source_candidates({"torrents": [
            {"imdb_id": IMDB, "magnet_url": "notmagnet"},
            {"imdb_id": "", "magnet_url": MAGNET1},
        ]}), [])
        self.assertEqual(accept.source_candidates({}), [])
        self.assertEqual(accept.source_candidates({"torrents": [
            {"imdb_id": IMDB, "magnet_url": MAGNET1}] * 6}), [IMDB])

    def test_exact_original_magnet_multiset_and_echo(self):
        self.assertEqual(accept.matching_magnets(SOURCE, IMDB),
                         Counter({MAGNET1: 1, MAGNET2: 1}))
        for invalid in [
            {"imdb_id": IMDB, "torrents_count": 1,
             "torrents": [SOURCE["torrents"][0], SOURCE["torrents"][1]]},
            {"imdb_id": "999999", "torrents_count": 2,
             "torrents": SOURCE["torrents"]},
            {"imdb_id": IMDB, "torrents_count": 2,
             "torrents": [{"imdb_id": IMDB, "magnet_url": "https://invalid.test"},
                          SOURCE["torrents"][1]]},
            {"imdb_id": IMDB, "torrents_count": 2,
             "torrents": [{"magnet_url": MAGNET1}, SOURCE["torrents"][1]]},
            {"imdb_id": IMDB, "torrents_count": 2,
             "torrents": SOURCE["torrents"], "error": "blocked"},
        ]:
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    accept.matching_magnets(invalid, IMDB)

    def test_true_empty_not_claimed_as_positive(self):
        self.assertEqual(accept.matching_magnets(
            {"imdb_id": IMDB, "torrents_count": 0}, IMDB), Counter())

    def run_accept(self, hub_rows=SOURCE, local_rows=SOURCE):
        calls = []
        def fake_json(url, token=None):
            calls.append(url)
            if "limit=5" in url:
                return RECENT
            if "limit=100" in url:
                return SOURCE
            if "127.0.0.1:8797" in url:
                return local_rows
            if "127.0.0.1:8798" in url:
                return hub_rows
            raise AssertionError("off-allowlist URL requested")
        output = io.StringIO()
        with patch.object(accept, "get_json", side_effect=fake_json), \
             contextlib.redirect_stdout(output):
            result = accept.acceptance("H" * 64, "E" * 64)
        return result, calls, output.getvalue()

    def test_real_source_chain_contract_with_mocked_same_identity(self):
        status, urls, output = self.run_accept()
        self.assertEqual(status, 0)
        self.assertEqual(len(urls), 4)
        self.assertTrue(urls[0].startswith("https://eztvx.to/api/"))
        self.assertIn("127.0.0.1:8797", urls[2])
        self.assertIn("127.0.0.1:8798", urls[3])
        self.assertIn("PASS: exact genuine magnet multiset", output)
        for value in (IMDB, MAGNET1, MAGNET2, PRIVATE):
            self.assertNotIn(value, output)

    def test_different_magnets_equal_counts_must_fail(self):
        other = json.loads(json.dumps(SOURCE))
        other["torrents"][0]["magnet_url"] = "magnet:?xt=urn:btih:" + "c" * 40
        status, _, output = self.run_accept(hub_rows=other)
        self.assertEqual(status, 1)
        self.assertIn("identities or counts differ", output)
        self.assertNotIn(PRIVATE, output)

    def test_different_8797_magnets_must_fail(self):
        other = json.loads(json.dumps(SOURCE))
        other["torrents"] = [other["torrents"][0]]
        status, _, output = self.run_accept(local_rows=other)
        self.assertEqual(status, 1)

    def test_no_candidates_never_calls_local_gateways(self):
        calls = []
        def fake_json(url, token=None):
            calls.append(url)
            return {"torrents": []}
        with patch.object(accept, "get_json", side_effect=fake_json), \
             contextlib.redirect_stdout(io.StringIO()):
            status = accept.acceptance("H" * 64, "E" * 64)
        self.assertEqual(status, 2)
        self.assertEqual(len(calls), 1)

    def test_smoke_checks_exact_existing_services_and_unauth(self):
        output = io.StringIO()
        with patch.object(accept, "units_healthy", return_value=True), \
             patch.object(accept, "get_status", return_value=401) as probe, \
             patch.object(accept, "get_json", return_value={"ok": True}), \
             contextlib.redirect_stdout(output):
            accept.check_smoke("H" * 64, "E" * 64)
        self.assertEqual(probe.call_count, 3)
        self.assertIn("8798 auth=200", output.getvalue())
        with patch.object(accept, "units_healthy", return_value=True), \
             patch.object(accept, "get_status", return_value=200), \
             self.assertRaises(ValueError):
            accept.check_smoke("H" * 64, "E" * 64)

    def test_credentials_distinct_and_private_parser_strict(self):
        with self.assertRaises(ValueError):
            accept.check_smoke("H" * 64, "H" * 64)
        self.assertTrue(accept.TOKEN.fullmatch("H" * 64))
        self.assertFalse(accept.TOKEN.fullmatch("weak"))
        self.assertIsNone(accept.normalized_imdb("bad"))


    def test_8798_readiness_waits_only_for_connection_refused(self):
        refused = URLError(ConnectionRefusedError(111, "Connection refused"))
        with patch.object(accept, "get_status", side_effect=[refused, 401]) as probe, \
             patch.object(accept.time, "sleep") as sleeping:
            accept.wait_for_central_ready(attempts=2, pause=0.01)
        self.assertEqual(probe.call_count, 2)
        sleeping.assert_called_once_with(0.01)

    def test_8798_readiness_timeout_is_bounded_and_safe(self):
        refused = URLError(ConnectionRefusedError(111, "Connection refused"))
        with patch.object(accept, "get_status", side_effect=[refused, refused]) as probe, \
             patch.object(accept.time, "sleep") as sleeping, \
             self.assertRaisesRegex(accept.SmokeFailure, "central-listener-timeout"):
            accept.wait_for_central_ready(attempts=2, pause=0.01)
        self.assertEqual(probe.call_count, 2)
        sleeping.assert_called_once()

    def test_8798_readiness_never_retries_wrong_http_or_other_network(self):
        for status in (200, 403, 404, 502):
            with self.subTest(status=status), \
                 patch.object(accept, "get_status", return_value=status) as probe, \
                 patch.object(accept.time, "sleep") as sleeping, \
                 self.assertRaisesRegex(accept.SmokeFailure, "unauth-8798-status"):
                accept.wait_for_central_ready(attempts=25)
            self.assertEqual(probe.call_count, 1)
            sleeping.assert_not_called()
        with patch.object(accept, "get_status", side_effect=URLError("unrelated")), \
             patch.object(accept.time, "sleep") as sleeping, \
             self.assertRaisesRegex(accept.SmokeFailure, "central-listener-transport"):
            accept.wait_for_central_ready(attempts=25)
        sleeping.assert_not_called()

    def test_smoke_diagnostic_identifies_auth_only_without_secrets(self):
        with patch.object(accept, "units_healthy", return_value=True), \
             patch.object(accept, "get_status", return_value=401), \
             patch.object(accept, "get_json", side_effect=HTTPError(
                 accept.CENTRAL + "/healthz", 401, "denied", {}, None
             )), \
             self.assertRaisesRegex(accept.SmokeFailure, "^auth-8798-failed$"):
            accept.check_smoke("H" * 64, "E" * 64)

    def test_smoke_diagnostic_safely_distinguishes_old_port_status(self):
        with patch.object(accept, "units_healthy", return_value=True), \
             patch.object(accept, "get_status", side_effect=[401, 404]), \
             self.assertRaisesRegex(accept.SmokeFailure, "^unauth-8797-status$"):
            accept.check_smoke("H" * 64, "E" * 64)


if __name__ == "__main__":
    unittest.main()
