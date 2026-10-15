#!/usr/bin/env python3
"""Offline fixed-origin canonical redirect candidate layout diagnostic tests."""
import importlib.util
import pathlib
import sys
import unittest
from email.message import Message
from urllib.error import HTTPError
P = pathlib.Path(__file__).with_name("probe-redirect-candidates.py")
spec = importlib.util.spec_from_file_location("magnetra_redirect_candidates", P)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


class CandidateTests(unittest.TestCase):
    def test_exact_host_allowlist_and_bounded_gets(self):
        self.assertEqual([x.url for x in mod.CANDIDATES], [
            "https://www.oxtorrent.co/recherche/ubuntu",
            "https://www7.torrent9.to/search_torrent/ubuntu.html",
            "https://bitsearch.eu/search?q=ubuntu&page=1&sortBy=seeders",
        ])
        self.assertEqual(len(mod.CANDIDATES), 3)
        self.assertLessEqual(mod.MAX_BYTES, 256_000)
        self.assertLessEqual(mod.TIMEOUT, 8)

    def test_redirect_safely_classified_never_followed(self):
        calls = []
        class Opener:
            def open(self, req, timeout):
                calls.append((req.full_url, req.get_method(), timeout))
                headers = Message()
                headers["Location"] = "https://different.example/sensitive/path?key=PRIVATE"
                raise HTTPError(req.full_url, 301, "moved", headers, None)
        candidate = mod.CANDIDATES[0]
        result = mod.check(candidate, opener=Opener())
        self.assertEqual(result["http"], 301)
        self.assertEqual(result["redirect"], "OFF_ORIGIN")
        self.assertEqual(result["redirect_host"], "different.example")
        self.assertNotIn("PRIVATE", str(result))
        self.assertEqual(calls, [(candidate.url, "GET", 8)])
        with self.assertRaises(ValueError):
            mod.check(mod.Candidate("evil", "https://evil.invalid", "table"), opener=Opener())

    def test_realistic_html_only_proves_layout_not_magnet(self):
        fake = b"<html><body><table><tbody><tr><td><a href='/example'>ubuntu</a></td></tr></tbody></table></body></html>"
        desc = mod.describe_body(mod.CANDIDATES[0], {"content-type": "text/html; charset=utf-8"}, fake)
        self.assertEqual(desc["classification"], "LAYOUT_HINT_ONLY")
        self.assertEqual(desc["magnet_anchors_seen"], 0)
        self.assertEqual(desc["table_rows_seen"], 1)
        self.assertIn("warning", desc)
        challenge = mod.describe_body(mod.CANDIDATES[0], {"content-type": "text/html"}, b"Just a moment CAPTCHA")
        self.assertEqual(challenge["classification"], "CHALLENGE")
        self.assertEqual(mod.describe_body(mod.CANDIDATES[0], {"content-type": "application/json"}, b"{}")["classification"], "NON_HTML")
        self.assertEqual(mod.describe_body(mod.CANDIDATES[0], {"content-type": "text/html"}, fake, True)["classification"], "HTML_TOO_LARGE_TO_VERIFY")

    def test_bitsearch_marker_not_equivalent_to_valid_release(self):
        body = b"<div class='space-y-4'><a href='/search'>Search</a></div>"
        desc = mod.describe_body(mod.CANDIDATES[2], {"content-type": "text/html"}, body)
        self.assertEqual(desc["classification"], "LAYOUT_HINT_ONLY")
        self.assertEqual(desc["magnet_anchors_seen"], 0)
        self.assertEqual(desc["wrapper_elements_seen"], 1)

    def test_invalid_redirect_is_not_approved(self):
        origin=mod.CANDIDATES[2].url
        self.assertEqual(mod.categorize_redirect(origin, "http://evil.invalid/"), {"redirect": "UNSAFE"})
        self.assertEqual(mod.categorize_redirect(origin, "https://bad:pwd@evil.invalid/"), {"redirect": "UNSAFE"})
        self.assertEqual(mod.categorize_redirect(origin, None), {"redirect": "MISSING_LOCATION"})
        self.assertEqual(mod.categorize_redirect(origin, "/search"), {"redirect": "SAME_ORIGIN", "redirect_host": "bitsearch.eu"})


if __name__ == "__main__":
    unittest.main()
