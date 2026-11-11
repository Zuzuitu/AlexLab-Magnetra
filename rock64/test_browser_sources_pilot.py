#!/usr/bin/env python3
"""100% offline test suite for the two-source Chromium browser pilot."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

PATH = Path(__file__).with_name("browser_sources_pilot.py")
SPEC = importlib.util.spec_from_file_location("magnetra_browser_pilot", PATH)
pilot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pilot)


class BrowserSourcePilotTests(unittest.TestCase):
    def test_only_two_owner_selected_providers(self):
        self.assertEqual(set(pilot.SOURCE_ORIGINS), {"btdigg", "thepiratebay"})
        self.assertEqual(set(pilot.ALLOWED_SUBRESOURCE_ORIGINS),
                         {"btdigg", "thepiratebay"})
        for name in ["knaben", "oxtorrent", "torrent9", "torrentscsv",
                     "eztvx", "internetarchive", "subsplease", "all"]:
            with self.subTest(name=name):
                with self.assertRaisesRegex(pilot.PilotStop, "unsupported_provider"):
                    pilot.search_target(name, "ubuntu")

    def test_known_canonical_pages_and_query_encoding(self):
        from urllib.parse import parse_qs, urlsplit
        for provider, path in [("btdigg", "/search"),
                               ("thepiratebay", "/search.php")]:
            with self.subTest(provider=provider):
                result = pilot.search_target(provider, " PSA 1080p x265 10bit ", "movies")
                u = urlsplit(result)
                self.assertEqual(u.path, path)
                self.assertEqual(parse_qs(u.query)["q"], ["PSA 1080p x265 10bit"])
                self.assertEqual(u.scheme, "https")
                self.assertTrue(pilot.approved_landing(provider, result))
        self.assertEqual(parse_qs(urlsplit(
            pilot.search_target("thepiratebay", "ubuntu", "movies")
        ).query)["cat"], ["200"])

    def test_input_validation_never_expands_source_scope(self):
        for text in ["", "X", "\r\n", "example\nsecret", "A"*181,
                     "a\x00b", "a\x7fb"]:
            with self.subTest(input_length=len(text)):
                with self.assertRaisesRegex(pilot.PilotStop, "invalid_query"):
                    pilot.search_target("btdigg", text)
        with self.assertRaisesRegex(pilot.PilotStop, "invalid_category"):
            pilot.search_target("thepiratebay", "ubuntu", "wrong")

    def test_same_origin_and_https_no_other_ports_or_hostnames(self):
        good = {
            "btdigg": ("https://btdig.com/search?q=ubuntu",),
            "thepiratebay": ("https://thepiratebay.org/search.php?q=ubuntu",
                             "https://apibay.org/q.php?q=ubuntu")
        }
        for provider, paths in good.items():
            for url in paths:
                self.assertTrue(pilot.allowed_resource(provider, url))
        bad = [
            "http://btdig.com/search?q=ubuntu",
            "https://btdig.com:8443/search?q=ubuntu",
            "https://btdig.com.attacker.example/search?q=ubuntu",
            "https://btdig.com@attacker.example/search?q=ubuntu",
            "https://attacker@btdig.com/search?q=ubuntu",
            "https://example.com",
            "file:///etc/passwd",
            "data:text/html,x",
            "https://thepiratebay.org.example/search.php",
            "https://thepiratebay.org:8796/search.php",
        ]
        for url in bad:
            with self.subTest(url=url):
                self.assertFalse(pilot.allowed_resource("btdigg", url))
                self.assertFalse(pilot.allowed_resource("thepiratebay", url))
        self.assertFalse(pilot.allowed_resource("btdigg", "https://apibay.org/q.php?q=ubuntu"))
        self.assertFalse(pilot.approved_landing(
            "thepiratebay", "https://apibay.org/q.php?q=ubuntu"))
        self.assertFalse(pilot.approved_landing(
            "btdigg", "https://btdig.com/other?q=ubuntu"))
        self.assertFalse(pilot.approved_landing(
            "thepiratebay", "https://thepiratebay.org/index.html"))

    def test_real_429_and_challenge_never_report_search_success(self):
        target = pilot.search_target("btdigg", "ubuntu")
        common = {"landing": target, "title": "Results", "rows": 5, "magnets": 5}
        self.assertEqual(pilot.classify_page("btdigg", status=429, **common),
                         "source_http_429")
        self.assertEqual(pilot.classify_page("btdigg", status=403, **common),
                         "source_access_denied")
        self.assertEqual(pilot.classify_page(
            "btdigg", status=200, landing=target,
            title="Just a moment...", rows=5, magnets=5),
            "challenge_not_solved")
        self.assertEqual(pilot.classify_page("btdigg", status=200, **{
            **common, "rows": 0, "magnets": 0
        }), "no_rows_unverified")
        self.assertEqual(pilot.classify_page("btdigg", status=200, **common),
                         "rendered_rows")
        self.assertEqual(pilot.classify_page(
            "btdigg", status=200, verified_rows=0, **common),
            "no_rows_unverified",
            "unpaired name/magnet elements must not certify result records")
        self.assertEqual(pilot.classify_page(
            "btdigg", status=200, verified_rows=3, **common),
            "rendered_rows")

    def test_tpb_nested_api_429_visible_even_if_html_navigation_is_200(self):
        site = pilot.search_target("thepiratebay", "ubuntu")
        self.assertEqual(pilot.classify_page(
            "thepiratebay", status=200, landing=site,
            title="The Pirate Bay", rows=10, magnets=10, tpb_api_status=429),
            "source_http_429")
        self.assertEqual(pilot.classify_page(
            "thepiratebay", status=200, landing=site,
            title="The Pirate Bay", rows=0, magnets=1, tpb_api_status=None),
            "rendered_rows")
        self.assertEqual(pilot.classify_page(
            "thepiratebay", status=200, landing=site,
            title="The Pirate Bay", rows=0, magnets=0, tpb_api_status=None),
            "no_rows_unverified")

    def test_unavailable_prerequisites_fail_without_navigating(self):
        with patch.object(pilot.os, "geteuid", return_value=1000), \
             patch.object(pilot, "_no_proxy_environment", return_value=True), \
             patch.object(pilot.shutil, "which", return_value=None):
            with self.assertRaisesRegex(pilot.PilotStop, "chromium_not_installed"):
                pilot.owner_probe("btdigg", "ubuntu")
        with patch.object(pilot.os, "geteuid", return_value=0):
            with self.assertRaisesRegex(pilot.PilotStop, "must_run_unprivileged"):
                pilot.owner_probe("thepiratebay", "ubuntu")
        with patch.object(pilot.os, "geteuid", return_value=1000), \
             patch.object(pilot, "_no_proxy_environment", return_value=False):
            with self.assertRaisesRegex(pilot.PilotStop, "environment_proxy_refused"):
                pilot.owner_probe("btdigg", "ubuntu")

    def test_one_owner_navigation_no_proxy_no_retry_and_no_live_side_effects(self):
        calls = []
        target = pilot.search_target("btdigg", "ubuntu")
        class FakeRoute:
            def __init__(self, url): self.request = SimpleNamespace(url=url)
            def continue_(self): calls.append("allowed")
            def abort(self): calls.append("blocked")
        class FakePage:
            url = target
            def route(self, pattern, handler):
                calls.append(("route", pattern))
                handler(FakeRoute(target))
                handler(FakeRoute("https://tracker.example/collect"))
            def on(self, event, callback): calls.append(("on", event))
            def goto(self, url, **kwargs):
                calls.append(("goto", url))
                self.url = url
                return SimpleNamespace(status=200)
            def wait_for_timeout(self, millis): calls.append(("settle", millis))
            def locator(self, selector):
                if ".one_result" == selector: return SimpleNamespace(count=lambda: 2)
                return SimpleNamespace(count=lambda: 2)
            def title(self): return "BTDigg results"
        class FakeContext:
            def new_page(self): return FakePage()
            def close(self): calls.append("context.close")
        class FakeBrowser:
            def new_context(self, **kwargs):
                calls.append(("context", kwargs))
                return FakeContext()
            def close(self): calls.append("browser.close")
        class FakeManager:
            def __enter__(self):
                class FakeChromium:
                    @staticmethod
                    def launch(**kwargs):
                        calls.append(("launch", kwargs))
                        return FakeBrowser()
                return SimpleNamespace(chromium=FakeChromium())
            def __exit__(self, *args): pass
        with patch.object(pilot.os, "geteuid", return_value=1000), \
             patch.object(pilot, "_no_proxy_environment", return_value=True), \
             patch.object(pilot.os.path, "isfile", return_value=True), \
             patch.object(pilot.os, "access", return_value=True):
            output = pilot.owner_probe(
                "btdigg", "ubuntu", chromium_path="/usr/bin/chromium",
                playwright_manager=FakeManager,
            )
        self.assertEqual(output["state"], "rendered_rows")
        self.assertFalse(output["search_results_extracted"])
        self.assertFalse(output["production_changed"])
        self.assertEqual(output["rendered_rows"], 2)
        self.assertEqual(output["raw_dom_result_blocks"], 2)
        self.assertEqual(output["raw_dom_name_links"], 2)
        self.assertEqual(output["raw_dom_magnet_candidates"], 2)
        self.assertEqual(output["magnet_links"], 2)
        self.assertEqual(output["verified_dom_result_pairs"], 2)
        self.assertEqual(output["result_structure"], "paired_result_rows")
        self.assertEqual(output["blocked_external_resources"], 1)
        self.assertEqual(output["blocked_external_scripts"], 0)
        self.assertNotIn("ubuntu",str(output),
            "only numeric DOM diagnostics and fixed labels, no queries in stdout")
        self.assertEqual(len([x for x in calls if isinstance(x, tuple) and x[0]=="goto"]), 1)
        self.assertEqual(calls.count("allowed"), 1)
        self.assertEqual(calls.count("blocked"), 1)
        launches = [x[1] for x in calls if isinstance(x, tuple) and x[0]=="launch"]
        self.assertTrue(launches[0]["chromium_sandbox"])
        self.assertFalse(any("--no-sandbox" in x for x in launches[0]["args"]))
        self.assertEqual(calls[-2:], ["context.close", "browser.close"])


if __name__ == "__main__":
    unittest.main()
