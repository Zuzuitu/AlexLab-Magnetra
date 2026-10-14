#!/usr/bin/env python3
"""Offline safety and classification tests for bounded multi-provider probes."""
import importlib.util
import pathlib
import sys
import unittest
from unittest.mock import patch

DIR = pathlib.Path(__file__).parent


def load(file, name):
    spec = importlib.util.spec_from_file_location(name, DIR / file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


indexers = load("probe-more-indexers.py", "magnetra_multi_indexer_probe")
eztv = load("diagnose-eztv-filter.py", "magnetra_eztv_filter_compare")
MAGNET = "magnet:?xt=urn:btih:" + "a" * 40


class SourceProbeTests(unittest.TestCase):
    def test_fixed_original_hosts_and_one_query_per_source(self):
        paths = {
            "torrentz": "https://torrentz2.nz/search?q=ubuntu",
            "uindex": "https://uindex.org/search.php?search=ubuntu&c=0",
            "1337x": "https://1337x.to/search/ubuntu/1/",
            "bt4g": "https://bt4gprx.com/search?q=ubuntu&category=all&orderby=seeders&p=1",
            "extdotto": "https://ext.to/browse/?q=ubuntu",
        }
        self.assertEqual(
            {source.provider: source.url for source in indexers.PRIORITY}, paths)
        self.assertEqual(len(indexers.EXTENDED), 6)
        all_sources = indexers.PRIORITY + indexers.EXTENDED
        self.assertEqual(len({s.provider for s in all_sources}), len(all_sources))
        for source in all_sources:
            self.assertTrue(source.url.startswith("https://"))
            self.assertTrue(source.signature)

    def test_classify_is_evidence_not_false_success(self):
        class Header(dict):
            pass
        head = Header({"content-type": "text/html"})
        source = indexers.PRIORITY[1]
        self.assertEqual(indexers.classify(403, head, b"", source.signature),
                         "ACCESS_DENIED")
        self.assertEqual(indexers.classify(429, head, b"", source.signature),
                         "RATE_LIMIT")
        self.assertEqual(indexers.classify(302, head, b"", source.signature),
                         "REDIRECT_NOT_FOLLOWED")
        self.assertEqual(indexers.classify(200, head, b"Just a moment", source.signature),
                         "CHALLENGE")
        self.assertEqual(indexers.classify(200, head, b"not a torrent listing", source.signature),
                         "HTTP_200_LAYOUT_UNVERIFIED")
        self.assertEqual(indexers.classify(200, head, b"<table class='sr-table'>", source.signature),
                         "HTML_SIGNATURE_FOUND_NOT_YET_PARSED")

    def test_run_uses_only_fixed_target(self):
        class Response:
            status = 403
            headers = {"content-type": "text/html"}
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self, n):
                self_read_size[0] = n
                return b""
        self_read_size = [None]
        seen = []
        class Opener:
            def open(self, req, timeout):
                seen.append((req.full_url, req.get_method(), timeout))
                return Response()
        source = indexers.PRIORITY[0]
        output = indexers.check(source, opener=Opener(), clock=lambda: 1.0)
        self.assertEqual(output["provider"], "torrentz")
        self.assertEqual(output["http"], 403)
        self.assertEqual(seen, [(source.url, "GET", 8)])
        self.assertEqual(self_read_size[0], indexers.MAX_PREVIEW + 1)
        with self.assertRaises(AssertionError):
            indexers.check(indexers.Source("evil", "https://invalid.example", b"x"),
                           opener=Opener())


class EZTVCompareTests(unittest.TestCase):
    def test_selects_only_genuine_magnet_with_imdb(self):
        candidate = {"imdb_id": "460681", "magnet_url": MAGNET}
        self.assertEqual(eztv.choose_recent({"torrents": [candidate]}), "460681")
        self.assertIsNone(eztv.choose_recent({"torrents_count": 123}))
        self.assertIsNone(eztv.choose_recent({"torrents": [
            {"imdb_id": "460681", "magnet_url": "bad"}
        ]}))
        self.assertIsNone(eztv.choose_recent({"torrents": None}))

    def test_compares_independent_match_count_and_total(self):
        summary = eztv.summarize({
            "imdb_id": "460681", "torrents_count": 15, "torrents": [
                {"imdb_id": "460681", "magnet_url": MAGNET},
                {"imdb_id": "460682", "magnet_url": MAGNET},
            ]}, "460681")
        self.assertTrue(summary["echo_ok"])
        self.assertEqual(summary["declared_count"], 15)
        self.assertEqual(summary["page_rows"], 2)
        self.assertEqual(summary["valid_matched_magnets"], 1)
        self.assertEqual(eztv.summarize({"imdb_id": "460681",
                                          "torrents_count": 0}, "460681")["page_rows"], None)
        self.assertFalse(eztv.summarize({"imdb_id": "460682"}, "460681")["echo_ok"])

    def test_probe_not_exposing_ids_tokens_or_magnets(self):
        fake_recent = {"torrents": [{"imdb_id": "460681", "magnet_url": MAGNET}]}
        fake_filtered = {"imdb_id": "460681", "torrents_count": 1,
                         "torrents": fake_recent["torrents"]}
        calls = []
        def fake_get(url, token=None, opener=None):
            calls.append((url, token))
            return {"http": 200}, fake_recent if "limit=2&page=1" in url and "imdb_id" not in url else fake_filtered
        import io
        from contextlib import redirect_stdout
        output = io.StringIO()
        with patch.object(eztv, "read_token", return_value="S" * 64):
            with patch.object(eztv, "request_json", side_effect=fake_get):
                with redirect_stdout(output):
                    self.assertEqual(eztv.main(), 0)
        view = output.getvalue()
        self.assertNotIn("460681", view)
        self.assertNotIn(MAGNET, view)
        self.assertNotIn("S" * 64, view)
        self.assertEqual(len(calls), 4)
        self.assertIn("limit=100", calls[2][0])
        self.assertTrue(calls[3][0].startswith("http://127.0.0.1:8797/v1/torrents"))
        self.assertEqual(calls[3][1], "S" * 64)


if __name__ == "__main__":
    unittest.main()
