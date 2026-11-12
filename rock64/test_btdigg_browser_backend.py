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


class FakeContext:
    def __init__(self, owner):
        self.owner = owner
        self.opened = []

    @property
    def pages(self):
        return [self.owner, *self.opened]

    def new_page(self):
        page = FakePage(url="about:blank", valid=False)
        page.context = self
        page.next_status = self.owner.next_status
        page.after_navigation_valid = self.owner.after_navigation_valid
        page.redirect_to = self.owner.redirect_to
        self.opened.append(page)
        return page


class FakePage:
    def __init__(self, url=None, valid=True):
        self.url = url or backend.query_url("The Dog Stars 2026")
        self.valid = valid
        self.next_status = 200
        self.after_navigation_valid = True
        self.goto_calls = []
        self.waits = []
        self.redirect_to = None
        self.closed = False
        self.rate_limited = False
        self.body_text = ""
        self.context = FakeContext(self)

    def locator(self, selector):
        assert selector in (backend.RESULT_PAIR_SELECTOR, "body")
        class Locator:
            def __init__(self, value, text):
                self.value = value
                self.text = text
            def count(self):
                return self.value
            def inner_text(self, **kwargs):
                return self.text
        if selector == "body":
            return Locator(1, self.body_text or (
                "Too Many Requests" if self.rate_limited else
                "Owner source release Magnet"))
        return Locator(1 if self.valid else 0, "")

    def content(self):
        return HTML if self.valid else '<html>One more step reCAPTCHA</html>'

    def goto(self, url, **kwargs):
        self.goto_calls.append((url, kwargs))
        self.url = self.redirect_to or url
        self.valid = self.after_navigation_valid
        return type("Response", (), {"status": self.next_status})()

    def wait_for_timeout(self, millis):
        self.waits.append(millis)

    def close(self):
        self.closed = True

    def is_closed(self):
        return self.closed


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
                    "https://btdig.com/search?q=foo",
                    "https://btdig.com/search?order=1&q=foo",
                    "https://btdig.com/search?order=0&q=foo&q=bar",
                    "https://btdig.com/search?order=0&q=foo&redirect=1",
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

    def test_browser_equivalent_plus_query_does_not_navigate(self):
        page = FakePage(
            url="https://btdig.com/search?order=0&q=The+Dog+Stars+2026")
        status, html = backend.VisibleBrowserFetcher(page).fetch(
            "The Dog Stars 2026")
        self.assertEqual(status, 200)
        self.assertEqual(html, HTML.encode())
        self.assertEqual(page.goto_calls, [])

    def test_manually_typed_lowercase_search_reuses_current_page(self):
        page = FakePage(url=backend.query_url("the dog stars 2026"))
        status, html = backend.VisibleBrowserFetcher(page).fetch(
            "The Dog Stars 2026")
        self.assertEqual((status, html), (200, HTML.encode("utf-8")))
        self.assertEqual(page.goto_calls, [],
                         "case-only differences must not create a source request")
        self.assertEqual(page.waits, [])

    def test_casefold_does_not_accept_unrelated_query(self):
        self.assertTrue(backend.same_search_query(
            "the dog stars 2026", "The Dog Stars 2026"))
        self.assertFalse(backend.same_search_query(
            "the dog stars 2025", "The Dog Stars 2026"))
        self.assertFalse(backend.same_search_query(
            None, "The Dog Stars 2026"))
        self.assertFalse(backend.same_search_query(
            "the dog stars 2026 720p", "The Dog Stars 2026"))

    def test_redirect_to_wrong_query_refuses_html_even_if_rows_visible(self):
        page = FakePage()
        page.redirect_to = backend.query_url("Unrelated title")
        gateway = backend.VisibleBrowserFetcher(page)
        self.assertEqual(gateway.fetch("Different title"), (503, b""))
        self.assertEqual(len(page.context.opened), 1)
        self.assertTrue(page.context.opened[0].closed)
        self.assertFalse(page.closed)
        self.assertIs(gateway.page, page)

    def test_existing_owner_verified_query_does_not_navigate_or_retry(self):
        page = FakePage(url=backend.query_url("The Dog Stars 2026"))
        status, html = backend.VisibleBrowserFetcher(page).fetch("The Dog Stars 2026")
        self.assertEqual(status, 200)
        self.assertEqual(html, HTML.encode())
        self.assertEqual(page.context.opened, [])
        self.assertEqual(page.waits, [])

    def test_manual_verification_required_does_not_navigate(self):
        page = FakePage(valid=False)
        status, body = backend.VisibleBrowserFetcher(page).fetch("another test")
        self.assertEqual((status, body), (503, b""))
        self.assertEqual(page.context.opened, [],
                         "never navigate while a challenge is displayed")

    def test_owner_verified_context_allows_one_subsequent_browser_search(self):
        page = FakePage(valid=True)
        gateway = backend.VisibleBrowserFetcher(page)
        status, html = gateway.fetch("Another 2026")
        self.assertEqual((status, html), (200, HTML.encode()))
        self.assertEqual(len(page.context.opened), 1)
        second = page.context.opened[0]
        self.assertEqual(len(second.goto_calls), 1)
        self.assertEqual(second.goto_calls[0][0], backend.query_url("Another 2026"))
        self.assertEqual(second.goto_calls[0][1]["wait_until"], "domcontentloaded")
        self.assertEqual(second.waits, [900])
        self.assertIs(gateway.page, second)
        self.assertFalse(page.closed, "initial verified tab is preserved")

    def test_challenge_reappearing_after_one_navigation_fails_closed(self):
        page = FakePage(valid=True)
        page.after_navigation_valid = False
        gateway = backend.VisibleBrowserFetcher(page)
        self.assertEqual(gateway.fetch("Another 2026"), (503, b""))
        self.assertEqual(gateway.fetch("Another 2026"), (503, b""))
        self.assertEqual(len(page.context.opened), 1,
                         "no repeat source request following a challenge")
        failed = page.context.opened[0]
        self.assertTrue(failed.closed)
        self.assertEqual(failed.waits, [900])
        self.assertFalse(page.closed)
        self.assertIs(gateway.page, page)

    def test_actual_429_or_non_200_preserved_without_fake_results(self):
        for upstream, expected in ((429, 429), (403, 503), (500, 503)):
            with self.subTest(upstream=upstream):
                original = FakePage()
                original.next_status = upstream
                gateway = backend.VisibleBrowserFetcher(original)
                self.assertEqual(gateway.fetch("New query"), (expected, b""))
                self.assertEqual(len(original.context.opened), 1)
                failed = original.context.opened[0]
                self.assertTrue(failed.closed)
                self.assertFalse(original.closed)
                self.assertEqual(gateway.fetch("New query"), (expected, b""))
                self.assertEqual(len(original.context.opened), 1)
                self.assertEqual(gateway.fetch("The Dog Stars 2026"),
                                 (200, HTML.encode()),
                                 "previously verified source results remain readable")

    def test_second_success_replaces_previous_secondary_tab_not_original(self):
        original = FakePage()
        gateway = backend.VisibleBrowserFetcher(original)
        self.assertEqual(gateway.fetch("Second query")[0], 200)
        second = gateway.page
        self.assertFalse(second.closed)
        self.assertEqual(gateway.fetch("Third query")[0], 200)
        self.assertTrue(second.closed)
        self.assertFalse(original.closed)
        self.assertFalse(gateway.page.closed)
        self.assertEqual(len(original.context.opened), 2)

    def test_new_tab_exception_is_bounded_and_never_retried(self):
        original = FakePage()
        class BrokenContext:
            def __init__(self):
                self.calls = 0
            @property
            def pages(self):
                # Real Playwright contexts always expose their open tabs.
                # The simulated failure must occur at new_page(), not before.
                return [original]
            def new_page(self):
                self.calls += 1
                raise RuntimeError("simulated local Playwright error")
        broken = BrokenContext()
        original.context = broken
        gateway = backend.VisibleBrowserFetcher(original)
        self.assertEqual(gateway.fetch("New query"), (504, b""))
        self.assertEqual(gateway.fetch("New query"), (504, b""))
        self.assertEqual(broken.calls, 1)
        self.assertFalse(original.closed)
        self.assertEqual(gateway.fetch("The Dog Stars 2026")[0], 200)

    def test_error_then_reused_original_tab_does_not_generate_request(self):
        original = FakePage()
        original.next_status = 429
        gateway = backend.VisibleBrowserFetcher(original)
        self.assertEqual(gateway.fetch("Other title"), (429, b""))
        self.assertEqual(gateway.fetch("THE DOG STARS 2026")[0], 200)
        self.assertEqual(len(original.context.opened), 1)

    def test_readonly_browser_state_inspects_tabs_without_navigation(self):
        first = FakePage()
        gateway = backend.VisibleBrowserFetcher(first)
        state = gateway.browser_state()
        self.assertEqual(state, {
            "browser_connected": True,
            "open_tabs": 1,
            "verified_tabs": 1,
            "selected_tab_verified": True,
            "new_searches_paused": False,
            "visible_source_rate_limited": False,
            "last_navigation_status": None,
        })
        extra = first.context.new_page()
        self.assertFalse(extra.valid)
        state = gateway.browser_state()
        self.assertEqual((state["open_tabs"], state["verified_tabs"]), (2, 1))
        self.assertEqual(first.goto_calls, [])
        self.assertEqual(extra.goto_calls, [])

    def test_manual_verified_tab_reused_after_denial_without_new_search(self):
        first = FakePage()
        first.next_status = 429
        gateway = backend.VisibleBrowserFetcher(first)
        self.assertEqual(gateway.fetch("Different title"), (429, b""))
        self.assertEqual(len(first.context.opened), 1)
        manually_opened = first.context.new_page()
        manually_opened.url = backend.query_url("Manual 2026")
        manually_opened.valid = True
        status, html = gateway.fetch("MANUAL 2026")
        self.assertEqual((status, html), (200, HTML.encode()))
        self.assertEqual(manually_opened.goto_calls, [])
        self.assertEqual(len(first.context.opened), 2)
        self.assertIs(gateway.page, manually_opened)
        state = gateway.browser_state()
        self.assertTrue(state["new_searches_paused"])
        self.assertEqual(state["last_navigation_status"], 429)
        self.assertEqual(state["verified_tabs"], 2)
        self.assertEqual(gateway.fetch("Other new query"), (429, b""))
        self.assertEqual(len(first.context.opened), 2)

    def test_manual_verified_tab_detected_if_initial_tab_closed(self):
        first = FakePage(valid=False)
        manually_opened = first.context.new_page()
        manually_opened.url = backend.query_url("Manual 2026")
        manually_opened.valid = True
        first.close()
        gateway = backend.VisibleBrowserFetcher(first)
        self.assertEqual(gateway.fetch("Manual 2026"), (200, HTML.encode()))
        self.assertIs(gateway.page, manually_opened)
        self.assertEqual(gateway.browser_state()["open_tabs"], 1)
        self.assertEqual(manually_opened.goto_calls, [])

    def test_authenticated_readonly_browser_route_and_rejects_querystring(self):
        first = FakePage()
        gateway = backend.VisibleBrowserFetcher(first)
        token = "a" * 64
        handler_type = backend.browser_handler_class(
            token, backend.SearchProvider(), gateway)
        handler = object.__new__(handler_type)
        captured = []
        handler.reply = lambda code, body=b"", mime="application/json": (
            captured.append((code, body, mime)))
        handler.path = "/v1/browser-state"
        handler.headers = {"authorization": "Bearer wrong"}
        handler.do_GET()
        self.assertEqual(captured[-1][0], 401)
        handler.headers = {"authorization": "Bearer " + token}
        handler.do_GET()
        self.assertEqual(captured[-1][0], 200)
        data = backend.json.loads(captured[-1][1])
        self.assertTrue(data["selected_tab_verified"])
        self.assertEqual(data["open_tabs"], 1)
        self.assertNotIn("The Dog Stars", str(data))
        self.assertNotIn("magnet:", str(data))
        self.assertEqual(first.goto_calls, [])
        handler.path = "/v1/browser-state?q=private"
        handler.do_GET()
        self.assertEqual(captured[-1][0], 404)
        handler.path = "/healthz"
        handler.do_GET()
        self.assertEqual(captured[-1][0], 200)

    def test_visible_too_many_requests_is_readonly_and_pauses_new_navigations(self):
        first = FakePage(valid=False)
        first.rate_limited = True
        gateway = backend.VisibleBrowserFetcher(first)
        status = gateway.browser_state()
        self.assertTrue(status["browser_connected"])
        self.assertEqual(status["verified_tabs"], 0)
        self.assertTrue(status["visible_source_rate_limited"])
        self.assertTrue(status["new_searches_paused"])
        self.assertIsNone(status["last_navigation_status"])
        self.assertEqual(first.goto_calls, [])
        self.assertEqual(gateway.fetch("Another query"), (429, b""))
        self.assertEqual(first.context.opened, [],
                         "observing a 429 body never opens a new tab")

    def test_source_denial_detected_on_nonselected_tab(self):
        first = FakePage()
        second = first.context.new_page()
        second.url = backend.query_url("Other source query")
        second.rate_limited = True
        second.valid = False
        gateway = backend.VisibleBrowserFetcher(first)
        status = gateway.browser_state()
        self.assertEqual(status["verified_tabs"], 1)
        self.assertTrue(status["visible_source_rate_limited"])
        self.assertEqual(gateway.fetch("Unseen query"), (429, b""))
        self.assertEqual(len(first.context.opened), 1)
        self.assertEqual(gateway.fetch("The Dog Stars 2026")[0], 200,
                         "already verified result may still be reused")

    def test_deny_marker_requires_exact_body_and_canonical_origin(self):
        page = FakePage(valid=False)
        page.body_text = "This release mentions Too Many Requests in title"
        self.assertFalse(backend.source_rate_limit_visible(page))
        page.body_text = "  TOO MANY   REQUESTS  "
        self.assertTrue(backend.source_rate_limit_visible(page))
        page.url = "https://example.com/search?order=0&q=Example"
        self.assertFalse(backend.source_rate_limit_visible(page))
        page.url = backend.query_url("Another source")
        page.close()
        self.assertFalse(backend.source_rate_limit_visible(page))
        page.closed = False
        page.body_text = "A" * 200
        self.assertFalse(backend.source_rate_limit_visible(page))

    def test_persistent_chromium_does_not_auto_visit_on_startup(self):
        source = Path(backend.__file__).read_text()
        startup = source.split("def main():", 1)[1]
        self.assertIn("launch_persistent_context(", startup)
        self.assertIn("context.pages[0] if context.pages else context.new_page()", startup)
        self.assertNotIn(".goto(", startup,
                         "cold start must never issue an explicit source request")
        self.assertNotIn("page.reload(", startup)
        self.assertIn("browser_fetcher = VisibleBrowserFetcher(page)", startup)

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
        self.assertIn("browser_handler_class(token, provider, browser_fetcher)", source)
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
