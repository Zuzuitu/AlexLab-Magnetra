#!/usr/bin/env python3
"""Offline contracts: human-verified persistent BTDigg browser HTML gateway."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

from rock64 import btdigg_browser_backend as backend


HTML = (
    '<html><body><div class="one_result"><div>'
    '<div class="torrent_name"><a href="/search?q=test">Owner source release</a></div>'
    '<div class="torrent_magnet"><div class="fa-magnet">'
    '<a href="magnet:?xt=urn:btih:' + "a" * 40 + '">Magnet</a></div></div>'
    '</div></div></body></html>'
)


class FakePage:
    def __init__(self, url=None, valid=True):
        self.url = url or backend.query_url("The Dog Stars 2026")
        self.valid = valid
        self.next_status = 200
        self.after_navigation_valid = True
        self.goto_calls = []
        self.waits = []

    def locator(self, selector):
        assert selector == backend.RESULT_PAIR_SELECTOR
        class Locator:
            def __init__(self, value):
                self.value = value
            def count(self):
                return self.value
        return Locator(1 if self.valid else 0)

    def content(self):
        return HTML if self.valid else '<html>One more step reCAPTCHA</html>'

    def goto(self, url, **kwargs):
        self.goto_calls.append((url, kwargs))
        self.url = url
        self.valid = self.after_navigation_valid
        return type("Response", (), {"status": self.next_status})()

    def wait_for_timeout(self, millis):
        self.waits.append(millis)


class BrowserBackendTests(TestCase):
    def test_search_is_fixed_origin_and_correctly_encoded(self):
        url = backend.query_url("  The Dog Stars 2026 ")
        self.assertEqual(urlsplit(url).scheme, "https")
        self.assertEqual(urlsplit(url).hostname, "btdig.com")
        self.assertEqual(urlsplit(url).path, "/search")
        self.assertEqual(unquote(urlsplit(url).query),
                         "order=0&q=The Dog Stars 2026")
        self.assertTrue(backend.source_landing(url))
        for bad in ("", "a", "u" * 181, "aaa\nanything"):
            with self.subTest(bad=bad[:30]):
                with self.assertRaises(ValueError):
                    backend.query_url(bad)
        for bad in ("http://btdig.com/search?q=foo",
                    "https://evil.example/search?q=foo",
                    "https://btdig.com.evil.example/search?q=foo",
                    "https://btdig.com/search?order=0",
                    "https://btdig.com/other?q=foo",
                    "https://user@btdig.com/search?q=foo"):
            with self.subTest(url=bad):
                self.assertFalse(backend.source_landing(bad))

    def test_verified_same_row_magnet_required_for_html(self):
        verified = FakePage()
        data = backend.validated_result_html(verified)
        self.assertEqual(data, HTML.encode("utf-8"))
        verified.valid = False
        self.assertIsNone(backend.validated_result_html(verified))
        verified.valid = True
        verified.url = "https://elsewhere.example/search?q=foo"
        self.assertIsNone(backend.validated_result_html(verified))

    def test_existing_owner_verified_query_does_not_navigate_or_retry(self):
        page = FakePage(url=backend.query_url("The Dog Stars 2026"))
        status, html = backend.VisibleBrowserFetcher(page).fetch("The Dog Stars 2026")
        self.assertEqual(status, 200)
        self.assertEqual(html, HTML.encode())
        self.assertEqual(page.goto_calls, [])
        self.assertEqual(page.waits, [])

    def test_manual_verification_required_does_not_navigate(self):
        page = FakePage(valid=False)
        status, body = backend.VisibleBrowserFetcher(page).fetch("another test")
        self.assertEqual((status, body), (503, b""))
        self.assertEqual(page.goto_calls, [],
                         "never keep navigating while verification is required")

    def test_owner_verified_context_allows_one_subsequent_browser_search(self):
        page = FakePage(valid=True)
        status, html = backend.VisibleBrowserFetcher(page).fetch("Another 2026")
        self.assertEqual(status, 200)
        self.assertEqual(html, HTML.encode())
        self.assertEqual(len(page.goto_calls), 1)
        self.assertEqual(page.goto_calls[0][0], backend.query_url("Another 2026"))
        self.assertEqual(page.goto_calls[0][1]["wait_until"], "domcontentloaded")
        self.assertEqual(page.waits, [900])

    def test_challenge_reappearing_after_one_navigation_fails_closed(self):
        page = FakePage(valid=True)
        page.after_navigation_valid = False
        bridge = backend.VisibleBrowserFetcher(page)
        self.assertEqual(bridge.fetch("Another 2026"), (503, b""))
        self.assertEqual(bridge.fetch("Another 2026"), (503, b""))
        self.assertEqual(len(page.goto_calls), 1,
                         "must not automatically retry a CAPTCHA response")
        self.assertEqual(page.waits, [900])

    def test_actual_429_or_non_200_preserved_without_fake_results(self):
        for source_status, expected in ((429, 429), (403, 503), (500, 503)):
            with self.subTest(source_status=source_status):
                page = FakePage()
                page.next_status = source_status
                self.assertEqual(
                    backend.VisibleBrowserFetcher(page).fetch("New query"),
                    (expected, b""))
                self.assertEqual(len(page.goto_calls), 1)

    def test_auth_and_private_persistent_profile_are_explicit_opt_in(self):
        with TemporaryDirectory() as root:
            p = Path(root) / "profile"
            p.mkdir(mode=0o700)
            env = {
                "DISPLAY": ":99",
                "MAGNETRA_BTDIGG_BROWSER_OPT_IN": "1",
                "MAGNETRA_BTDIGG_TOKEN": "x" * 64,
                "MAGNETRA_BROWSER_PROFILE": str(p),
                "MAGNETRA_BTDIGG_BROWSER_PORT": "18896",
            }
            with patch.dict(backend.os.environ, env, clear=True), \
                 patch.object(backend.os, "geteuid", return_value=1000):
                token, folder, port = backend.validate_configuration()
                self.assertEqual((token, folder, port), ("x" * 64, p, 18896))
                backend.os.environ["MAGNETRA_BTDIGG_BROWSER_PORT"] = "8796"
                with self.assertRaisesRegex(SystemExit, "explicit authorization"):
                    backend.validate_configuration()
                backend.os.environ["MAGNETRA_BTDIGG_SOURCE_PERMISSION_CONFIRMED"] = "1"
                backend.os.environ["MAGNETRA_BTDIGG_PRODUCTION_OPT_IN"] = "1"
                self.assertEqual(backend.validate_configuration()[-1], 8796)
                p.chmod(0o755)
                with self.assertRaisesRegex(SystemExit, "mode 0700"):
                    backend.validate_configuration()
                p.chmod(0o700)
                backend.os.environ["MAGNETRA_BTDIGG_BROWSER_PORT"] = "9000"
                with self.assertRaisesRegex(SystemExit, "unsupported"):
                    backend.validate_configuration()
                backend.os.environ.pop("MAGNETRA_BTDIGG_BROWSER_OPT_IN")
                with self.assertRaisesRegex(SystemExit, "disabled"):
                    backend.validate_configuration()

    def test_safety_regression_source_only(self):
        source = Path(backend.__file__).read_text()
        self.assertIn("HTTPServer((BIND, port)", source)
        self.assertNotIn("ThreadingHTTPServer((BIND", source)
        self.assertIn("launch_persistent_context", source)
        self.assertIn("chromium_sandbox=True", source)
        self.assertIn('headless=False', source)
        self.assertNotIn("--no-sandbox", source)
        self.assertNotIn("--remote-debugging-port", source)
        self.assertNotIn("captcha.solve", source.lower())
        self.assertNotIn("playwright-stealth", source)
        self.assertNotIn("proxy=", source)


if __name__ == "__main__":
    main()
