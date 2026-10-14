#!/usr/bin/env python3
"""Only local fixtures. Never makes source or gateway network requests."""
import importlib.util
import pathlib
import unittest

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

    def test_no_source_data_in_output_contract(self):
        # The script deliberately emits only fixed labels and numeric counts.
        source = P.read_text(encoding="utf8")
        self.assertNotIn('print(token)', source)
        self.assertNotIn('print(magnet)', source)
        self.assertIn('print("EZTV rows with matching IMDb and valid magnet:", valid)', source)


if __name__ == "__main__":
    unittest.main()
