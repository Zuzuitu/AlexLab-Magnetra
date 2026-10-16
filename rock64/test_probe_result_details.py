#!/usr/bin/env python3
"""Offline no-network contracts for two-source search->details proof."""
import importlib.util
import pathlib
import sys
import unittest
from email.message import Message
from urllib.error import HTTPError

FILE = pathlib.Path(__file__).with_name("probe-result-details.py")
spec = importlib.util.spec_from_file_location("magnetra_source_detail_probe", FILE)
probe = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = probe
spec.loader.exec_module(probe)

MAGNET = "magnet:?xt=urn:btih:" + "a" * 40
FAKE = (
    "<table><tbody><tr>"
    "<td><a href='/torrent/ubuntu-release'>Ubuntu release</a></td>"
    "<td>1 GB</td><td>42</td><td>11</td><td>yes</td>"
    "</tr><tr><td><a href='https://untrusted.invalid/t/ubuntu'>Ubuntu bad</a></td>"
    "<td>1 GB</td><td>42</td><td>11</td><td>yes</td></tr></tbody></table>"
).encode()


class FakeResponse:
    status = 200

    def __init__(self, body, status=200, headers=None):
        self.body = body
        self.status = status
        self.headers = Message()
        self.headers["content-type"] = "text/html; charset=utf-8"
        for key, value in (headers or {}).items():
            self.headers[key] = value

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def read(self, amount):
        assert amount == probe.MAX_BYTES + 1
        return self.body[:amount]


class FakeOpener:
    def __init__(self, search, details):
        self.search = search
        self.details = details
        self.calls = []

    def open(self, req, timeout):
        self.calls.append((req.full_url, req.get_method(), timeout))
        return self.search if len(self.calls) == 1 else self.details


class SearchDetailProofTests(unittest.TestCase):
    def test_exact_approved_fixed_hosts_and_limits(self):
        self.assertEqual([(s.provider, s.url) for s in probe.SOURCES], [
            ("oxtorrent", "https://www.oxtorrent.co/recherche/ubuntu"),
            ("torrent9", "https://www7.torrent9.to/search_torrent/ubuntu.html")
        ])
        self.assertEqual(probe.TIMEOUT, 8)
        self.assertLessEqual(probe.MAX_BYTES, 256_000)
        for s in probe.SOURCES:
            for raw in ("https://evil.invalid/x", "//evil.invalid/x",
                        "https://user:pass@evil.invalid/x", "magnet:?xt=urn:btih:a",
                        "/recherche/ubuntu", "/search_torrent/ubuntu.html",
                        "/torrent/ubuntu?q=secret", "/torrent/ubuntu#section"):
                self.assertIsNone(probe.safe_detail(s, raw))
            self.assertEqual(probe.safe_detail(s, "/torrent/ubuntu"),
                             s.url.split("/")[0] + "//" +
                             s.url.split("/")[2] + "/torrent/ubuntu")

    def test_only_genuine_looking_original_first_column_link_gets_one_detail(self):
        for s in probe.SOURCES:
            page = FakeResponse(FAKE)
            detail_html = (
                "<html><div class='btn-magnet'><a href='" + MAGNET +
                "'>Get magnet</a></div></html>"
            ) if s.provider == "oxtorrent" else (
                "<a href='" + MAGNET + "'>Magnet</a>"
            )
            f = FakeOpener(page, FakeResponse(detail_html.encode()))
            result = probe.inspect(s, opener=f)
            self.assertEqual(result["search"]["http"], 200)
            self.assertEqual(result["rows"], 2)
            self.assertEqual(result["query_matched_rows"], 2)
            self.assertEqual(result["safe_details_candidates"], 1)
            self.assertTrue(result["details_fetched"])
            self.assertTrue(result["well_formed_magnet_in_details"])
            self.assertEqual(result["details"]["state"], "MAGNET_ANCHOR_FORMAT_FOUND")
            self.assertEqual(f.calls, [
                (s.url, "GET", 8),
                (probe.safe_detail(s, "/torrent/ubuntu-release"), "GET", 8),
            ])
            self.assertNotIn(MAGNET, str(result))
            self.assertNotIn("Ubuntu release", str(result))
            self.assertNotIn("/torrent/ubuntu-release", str(result))

    def test_table_hint_and_search_header_cannot_impersonate_release(self):
        s = probe.SOURCES[0]
        cases = (
            b"<html><table><tbody><tr><td>Page 1</td></tr></tbody></table></html>",
            b"<table><tbody><tr><td><a href='/torrent/x'>Other</a></td>"
            b"<td>X</td><td>X</td><td>X</td></tr></tbody></table>",
        )
        for body in cases:
            f = FakeOpener(FakeResponse(body), None)
            result = probe.inspect(s, opener=f)
            self.assertEqual(result["safe_details_candidates"], 0)
            self.assertFalse(result["details_fetched"])
            self.assertEqual(len(f.calls), 1)
            self.assertEqual(result["search"]["state"], "NO_VERIFIED_DETAIL_CANDIDATE")

    def test_not_allow_fabricated_success_on_challenge_or_520(self):
        s = probe.SOURCES[1]
        f = FakeOpener(FakeResponse(b"Just a moment, CAPTCHA"), None)
        result = probe.inspect(s, opener=f)
        self.assertEqual(result["search"]["state"], "CHALLENGE")
        self.assertFalse(result["details_fetched"])
        class Fail:
            def open(self, req, timeout):
                raise HTTPError(req.full_url, 520, "blocked", {}, None)
        failure = probe.inspect(s, opener=Fail())
        self.assertEqual(failure["search"]["http"], 520)
        self.assertFalse(failure["well_formed_magnet_in_details"])

    def test_magnet_must_be_anchor_not_plain_html_and_correct_selector(self):
        for s in probe.SOURCES:
            p = probe.MagnetAnchors(s.magnet_parent)
            p.feed("<p>" + MAGNET + "</p>")
            self.assertEqual(p.count, 0)
        ox = probe.MagnetAnchors("btn-magnet")
        ox.feed("<a href='" + MAGNET + "'>Fake outside</a>")
        self.assertEqual(ox.count, 0)
        ox.feed("<div class='btn-magnet'><a href='magnet:?xt=urn:btih:bad'>Wrong hash</a></div>")
        self.assertEqual(ox.count, 0)

    def test_no_valid_magnet_format_proof_not_claimed(self):
        s = probe.SOURCES[0]
        f = FakeOpener(FakeResponse(FAKE), FakeResponse(b"<div class='btn-magnet'><a href='/download.torrent'>Download</a></div>"))
        out = probe.inspect(s, opener=f)
        self.assertTrue(out["details_fetched"])
        self.assertFalse(out["well_formed_magnet_in_details"])
        self.assertEqual(out["details"]["state"], "MAGNET_ANCHOR_NOT_FOUND")

    def test_arbitrary_targets_refused(self):
        with self.assertRaises(ValueError):
            probe.inspect(probe.Source("evil", "https://evil.invalid/", 4, ""), opener=FakeOpener(None, None))


if __name__ == "__main__":
    unittest.main()
