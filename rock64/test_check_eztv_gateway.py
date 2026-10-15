#!/usr/bin/env python3
"""Only local fixtures. Never makes source or gateway network requests."""
import importlib.util
import pathlib
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch
from urllib.error import URLError, HTTPError

P = pathlib.Path(__file__).with_name("check-eztv-gateway.py")
spec = importlib.util.spec_from_file_location("eztv_local_check", P)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
MAGNET = "magnet:?xt=urn:btih:" + "a" * 40
GOOD_ROW = {"imdb_id": "460681", "magnet_url": MAGNET, "title": "fixture"}


class LocalCheckTests(unittest.TestCase):
    def test_recent_requires_genuine_row(self):
        self.assertEqual(mod.choose_known_positive({"torrents": [GOOD_ROW]}), "460681")
        self.assertIsNone(mod.choose_known_positive({"torrents_count": 123}))
        self.assertIsNone(mod.choose_known_positive({"torrents": [
            {"imdb_id": "460681", "magnet_url": "https://bad.invalid/file"},
        ]}))
        self.assertIsNone(mod.choose_known_positive({"torrents": [
            {"imdb_id": None, "magnet_url": MAGNET},
        ]}))

    def test_filtered_does_not_count_wrong_imdb(self):
        data = {"imdb_id": "460681", "torrents": [
            GOOD_ROW, {"imdb_id": "460682", "magnet_url": MAGNET},
            {"imdb_id": "460681", "magnet_url": "not-magnet"},
        ]}
        self.assertEqual(mod.inspect_filtered(data, "460681"), (3, 1))
        self.assertEqual(mod.inspect_filtered(data, "460682"), (0, 0))

    def test_unsupported_payload_is_empty_not_fabricated(self):
        self.assertEqual(mod.inspect_filtered({"imdb_id": "460681",
                                             "torrents_count": 15}, "460681"), (0, 0))
        self.assertEqual(mod.inspect_filtered({"imdb_id": "460681",
                                             "torrents": []}, "460681"), (0, 0))

    def test_real_token_file_shape_reads_with_trailing_newline(self):
        with tempfile.TemporaryDirectory() as folder:
            path = pathlib.Path(folder) / "gateway.env"
            value = "T" * 64
            path.write_text("MAGNETRA_EZTV_TOKEN=" + value + "\n", encoding="ascii")
            with patch.object(mod, "CONFIG", path):
                self.assertEqual(mod.read_token(), value)

    def test_local_listener_startup_wait_is_bounded(self):
        retry = URLError(ConnectionRefusedError(111, "Connection refused"))
        with patch.object(mod, "get_json", side_effect=[retry, retry, {"ok": True}]) as run:
            with patch.object(mod.time, "sleep") as sleep:
                self.assertEqual(mod.health_when_ready({}, attempts=3, delay=0.1), {"ok": True})
                self.assertEqual(run.call_count, 3)
                self.assertEqual(sleep.call_count, 2)

    def test_auth_failure_does_not_retry_or_reveal_credentials(self):
        unauthorized = HTTPError("http://127.0.0.1:8797/healthz", 401, "unauthorized", {}, None)
        with patch.object(mod, "read_token", return_value="T" * 64):
            with patch.object(mod, "get_json", side_effect=unauthorized) as run:
                with redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(mod.main(), 1)
        self.assertEqual(run.call_count, 1)
        self.assertIn("FAIL stage=local-health HTTP=401", output.getvalue())
        self.assertNotIn("T" * 64, output.getvalue())

    def test_credentials_failure_reports_stage_not_content(self):
        with patch.object(mod, "read_token", side_effect=ValueError("SECRET PRIVATE")):
            with redirect_stdout(io.StringIO()) as output:
                self.assertEqual(mod.main(), 1)
        self.assertIn("FAIL stage=credentials cause=local-data-or-response", output.getvalue())
        self.assertNotIn("SECRET PRIVATE", output.getvalue())

    def test_source_candidates_are_genuine_and_deduplicated(self):
        good = {"imdb_id": "460681", "magnet_url": MAGNET}
        recent = {"torrents": [good, good,
                  {"imdb_id": "tt0903747", "magnet_url": MAGNET},
                  {"imdb_id": "460682", "magnet_url": "https://unsafe.invalid"},
                  {"imdb_id": "tt0396375", "magnet_url": MAGNET}]}
        self.assertEqual(mod.source_candidates(recent), ["460681", "903747", "396375"])
        self.assertEqual(mod.source_candidates({"torrents_count": 20}), [])

    def test_find_source_positive_skips_zero_and_does_not_exceed_four(self):
        calls = []
        def fake_get(url, headers):
            calls.append(url)
            target = url.split("imdb_id=", 1)[1].split("&", 1)[0]
            if target == "460682":
                return {"imdb_id": target, "torrents_count": 1,
                        "torrents": [{"imdb_id": target, "magnet_url": MAGNET}]}
            return {"imdb_id": target, "torrents_count": 0}
        answer = mod.find_source_positive(["460681", "460682", "460683"], get=fake_get)
        self.assertEqual(answer, ("460682", 2, 1, 1))
        self.assertEqual(len(calls), 2)
        calls.clear()
        self.assertIsNone(mod.find_source_positive(["460681"] * 10, get=fake_get))
        self.assertEqual(len(calls), 4)
        self.assertTrue(all(url.startswith(mod.SOURCE_FILTER) for url in calls))

    def test_main_proves_positive_direct_and_gateway_without_outputting_identity(self):
        calls = []
        source = {"torrents": [
            {"imdb_id": "460681", "magnet_url": MAGNET},
            {"imdb_id": "460682", "magnet_url": MAGNET}]}
        def fake_get(url, headers):
            calls.append((url, headers))
            if url == mod.RECENT:
                return source
            if url.startswith(mod.SOURCE_FILTER):
                imdb = url.split("imdb_id=", 1)[1].split("&", 1)[0]
                if imdb == "460681":
                    return {"imdb_id": imdb, "torrents_count": 0}
                return {"imdb_id": imdb, "torrents_count": 1,
                        "torrents": [{"imdb_id": imdb, "magnet_url": MAGNET}]}
            if url.startswith(mod.LOCAL_SEARCH):
                imdb = url.split("imdb_id=", 1)[1]
                return {"imdb_id": imdb, "torrents_count": 1,
                        "torrents": [{"imdb_id": imdb, "magnet_url": MAGNET}]}
            raise AssertionError("Unexpected URL")
        out = io.StringIO()
        with patch.object(mod, "read_token", return_value="T" * 64):
            with patch.object(mod, "health_when_ready", return_value={"ok": True}):
                with patch.object(mod, "get_json", side_effect=fake_get):
                    with redirect_stdout(out):
                        self.assertEqual(mod.main(), 0)
        view = out.getvalue()
        self.assertIn("EZTV direct matching magnet count: 1", view)
        self.assertIn("EZTV gateway matching magnet count: 1", view)
        self.assertIn("PASS: genuine EZTV magnet metadata reached isolated local gateway", view)
        self.assertNotIn("460682", view)
        self.assertNotIn(MAGNET, view)
        self.assertNotIn("T" * 64, view)
        self.assertEqual(len([url for url, _ in calls if url.startswith(mod.LOCAL_SEARCH)]), 1)
        self.assertEqual(len(calls), 4)

    def test_all_zero_source_does_not_call_gateway_or_fake_success(self):
        calls = []
        def fake_get(url, headers):
            calls.append(url)
            if url == mod.RECENT:
                return {"torrents": [
                    {"imdb_id": str(500000 + i), "magnet_url": MAGNET} for i in range(5)]}
            imdb = url.split("imdb_id=", 1)[1].split("&", 1)[0]
            return {"imdb_id": imdb, "torrents_count": 0}
        out = io.StringIO()
        with patch.object(mod, "read_token", return_value="T" * 64):
            with patch.object(mod, "health_when_ready", return_value={"ok": True}):
                with patch.object(mod, "get_json", side_effect=fake_get):
                    with redirect_stdout(out):
                        self.assertEqual(mod.main(), 2)
        self.assertEqual(len(calls), 5)
        self.assertTrue(all(not x.startswith(mod.LOCAL_SEARCH) for x in calls))
        self.assertIn("UNVERIFIED: source returned no positive filtered candidates", out.getvalue())

    def test_no_source_data_in_output_contract(self):
        # The script deliberately emits only fixed labels and numeric counts.
        source = P.read_text(encoding="utf8")
        self.assertNotIn('print(token)', source)
        self.assertNotIn('print(magnet)', source)
        self.assertIn('print("EZTV gateway matching magnet count:", valid)', source)


if __name__ == "__main__":
    unittest.main()
