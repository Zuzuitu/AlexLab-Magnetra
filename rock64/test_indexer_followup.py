#!/usr/bin/env python3
"""Offline invariants for fixed-source Rock64 redirect/Torrentz/EZTV diagnostic."""
import errno
import importlib.util
import io
import pathlib
import socket
import sys
import unittest
from contextlib import redirect_stdout
from email.message import Message
from unittest.mock import patch
from urllib.error import HTTPError, URLError

P = pathlib.Path(__file__).with_name("probe-indexer-followup.py")
spec = importlib.util.spec_from_file_location("magnetra_indexer_followup", P)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
HASH = "a" * 40
GOOD = "magnet:?xt=urn:btih:" + HASH


class FollowupTests(unittest.TestCase):
    def test_only_exact_four_provider_sources(self):
        self.assertEqual([x.name for x in module.TARGETS],
                         ["torrentz", "oxtorrent", "torrent9", "bitsearch"])
        for source in module.TARGETS:
            self.assertTrue(source.url.startswith("https://"))
        self.assertEqual(module.MAX_CANDIDATES, 4)
        self.assertLessEqual(module.TIMEOUT, 8)
        self.assertLessEqual(module.MAX_BYTES, 350_000)

    def test_torrentz_transport_reason_safely_categorized(self):
        self.assertEqual(module.categorize_error(URLError(
            socket.gaierror(-3, "DNS server URL private"))), "DNS_RESOLUTION_FAILURE")
        self.assertEqual(module.categorize_error(ConnectionRefusedError(
            errno.ECONNREFUSED, "private host")), "CONNECTION_REFUSED")
        self.assertEqual(module.categorize_error(
            OSError(errno.ENETUNREACH, "host address")), "NETWORK_UNREACHABLE")
        self.assertEqual(module.categorize_error(URLError("private DNS info")),
                         "TRANSPORT_FAILURE")

    def test_redirect_keeps_exact_source_origin_without_fetch(self):
        original = module.TARGETS[2].url
        self.assertEqual(module.redirect_target(original, "/search/?q=ubuntu"),
                         {"redirect_class": "SAME_ORIGIN", "destination_host": "www6.torrent9.to"})
        self.assertEqual(module.redirect_target(original, "https://example.invalid/"),
                         {"redirect_class": "OFF_ORIGIN", "destination_host": "example.invalid"})
        self.assertEqual(module.redirect_target(original, "javascript:alert(1)"),
                         {"redirect_class": "UNSAFE_OR_UNSUPPORTED"})
        self.assertEqual(module.redirect_target(original, "http://www6.torrent9.to/"),
                         {"redirect_class": "UNSAFE_OR_UNSUPPORTED"})
        self.assertEqual(module.redirect_target(original, "https://u:p@example.invalid/"),
                         {"redirect_class": "UNSAFE_OR_UNSUPPORTED"})
        self.assertEqual(module.redirect_target(original, None),
                         {"redirect_class": "MISSING_LOCATION"})

    def test_no_redirect_get_and_safe_host_only_reported(self):
        actual_calls = []
        class Stub:
            def open(self, request, timeout):
                actual_calls.append((request.full_url, timeout))
                headers = Message()
                headers["Location"] = "https://different.example/search?token=SECRET_QUERY"
                raise HTTPError(request.full_url, 301, "moved", headers, None)
        data = module.inspect_html(module.TARGETS[1], Stub())
        self.assertEqual(data["source"], "oxtorrent")
        self.assertEqual(data["http"], 301)
        self.assertEqual(data["redirect_class"], "OFF_ORIGIN")
        self.assertEqual(data["destination_host"], "different.example")
        self.assertNotIn("SECRET_QUERY", str(data))
        self.assertEqual(actual_calls, [(module.TARGETS[1].url, 8)])
        with self.assertRaises(ValueError):
            module.inspect_html(module.SourceProbe("evil", "https://evil.invalid"))

    def test_eztv_recent_ids_are_unique_and_genuine_only(self):
        rows = [{"imdb_id": "tt0460681", "magnet_url": GOOD},
                {"imdb_id": "460681", "magnet_url": GOOD},
                {"imdb_id": "tt0903747", "magnet_url": "https://bad.example"},
                {"imdb_id": "tt0903747", "magnet_url": GOOD},
                {"imdb_id": "tt0396375", "magnet_url": GOOD}]
        self.assertEqual(module.candidate_ids({"torrents": rows}), ["460681", "903747", "396375"])
        self.assertEqual(module.candidate_ids({"torrents_count": 10}), [])
        self.assertEqual(module.candidate_ids({"torrents": None}), [])

    def test_eztv_filtered_count_and_missing_array(self):
        rows = [
            {"imdb_id": "460681", "magnet_url": GOOD},
            {"imdb_id": "460682", "magnet_url": GOOD},
            {"imdb_id": "460681", "magnet_url": "not a magnet"}]
        valid = module.result_counts(
            {"imdb_id": "460681", "torrents_count": 15, "torrents": rows}, "460681")
        self.assertEqual(valid, {"valid_echo": True, "declared_count": 15,
                                  "page_rows": 3, "matching_magnets": 1})
        absent = module.result_counts({"imdb_id": "460681", "torrents_count": 0}, "460681")
        self.assertEqual(absent["page_rows"], None)
        self.assertEqual(absent["matching_magnets"], 0)

    def test_no_sensitive_output_and_upper_bound(self):
        sample = [
            {"imdb_id": str(100001 + i), "magnet_url": GOOD}
            for i in range(5)
        ]
        visits = []
        def fake_api(url, opener=None):
            visits.append(url)
            if "?limit=5" in url:
                return {"http": 200}, {"torrents": sample}
            imdb = url.split("imdb_id=", 1)[1].split("&", 1)[0]
            return {"http": 200}, {"imdb_id": imdb, "torrents_count": 1,
                                  "torrents": [{"imdb_id": imdb, "magnet_url": GOOD}]}
        out = io.StringIO()
        with patch.object(module, "inspect_html", side_effect=lambda x,y: {"source":x.name, "http":301,
                     "redirect_class":"SAME_ORIGIN"}), patch.object(module, "get_api", side_effect=fake_api):
            with redirect_stdout(out):
                module.run(opener=object())
        self.assertEqual(len(visits), 5)
        self.assertEqual(sum("imdb_id=" in x for x in visits), 4)
        self.assertNotIn("100001", out.getvalue())
        self.assertNotIn(GOOD, out.getvalue())
        self.assertNotIn("magnet:?", out.getvalue())
        self.assertIn('"matching_magnets": 1', out.getvalue())


if __name__ == "__main__":
    unittest.main()
