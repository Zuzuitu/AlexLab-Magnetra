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
        self.owner=owner
        self.opened=[]
    @property
    def pages(self):
        return [self.owner,*self.opened]
    def new_page(self):
        # Only used to model HUMAN-opened tabs; the backend must never call.
        page=FakePage(url="about:blank",valid=False)
        page.context=self
        self.opened.append(page)
        return page


class FakePage:
    def __init__(self, url=None, valid=True):
        self.url=url or backend.query_url("The Dog Stars 2026")
        self.valid=valid
        self.next_status=200
        self.after_navigation_valid=True
        self.goto_calls=[]
        self.waits=[]
        self.redirect_to=None
        self.closed=False
        self.rate_limited=False
        self.body_text=""
        self.context=FakeContext(self)
        self.submit_calls=0
        self.search_fills=[]
        self.pending_query=None
        self.has_search_input=True
        self.raise_on_press=False
        self.no_navigation_response=False
        self.navigation_options=[]
        self._response=None
        self.live_url_override=None
        self.evaluate_count=0
        self.navigation_age_ms=0.0
        self.document_time_ms=1700000000000.0
        self.frames=[]

    def evaluate(self, script):
        self.evaluate_count += 1
        if script == backend.PAGE_AGE_SCRIPT:
            return self.navigation_age_ms
        if script == "() => performance.timeOrigin":
            return self.document_time_ms
        assert script == "() => window.location.href"
        return self.live_url_override if self.live_url_override is not None else self.url

    def locator(self, selector):
        assert selector in (
            backend.RESULT_PAIR_SELECTOR, "body", 'input[name="q"]',
            "div.one_result div.torrent_name a",
            'div.one_result a[href^="magnet:"]',
        )
        page=self
        class Locator:
            def count(self):
                if selector=='input[name="q"]':
                    return 1 if page.has_search_input else 0
                if selector=="body": return 1
                return 1 if page.valid else 0
            def inner_text(self, **kwargs):
                return page.body_text or (
                    "Too Many Requests" if page.rate_limited else
                    "Owner source release Magnet")
            def fill(self, value, **kwargs):
                assert selector=='input[name="q"]'
                assert page.has_search_input
                page.pending_query=value
                page.search_fills.append(value)
            def press(self, key, **kwargs):
                assert selector=='input[name="q"]' and key=="Enter"
                page.submit_calls+=1
                if page.raise_on_press:
                    raise RuntimeError("simulated Playwright form error")
                page.url=page.redirect_to or backend.query_url(page.pending_query)
                page.valid=page.after_navigation_valid and page.next_status==200
                page._response=(None if page.no_navigation_response else
                                type("Response",(),{"status":page.next_status})())
        return Locator()

    def content(self):
        return HTML if self.valid else '<html>One more step reCAPTCHA</html>'

    def expect_navigation(self, **kwargs):
        self.navigation_options.append(kwargs)
        page=self
        class Navigation:
            def __enter__(self): return self
            def __exit__(self,*_args): return False
            @property
            def value(self): return page._response
        return Navigation()

    def goto(self, url, **kwargs):
        self.goto_calls.append(url)
        self.url=url
        self.valid=self.after_navigation_valid and self.next_status==200
        return type("Response",(),{"status":self.next_status})()

    def wait_for_timeout(self, millis):
        self.waits.append(millis)

    def close(self):
        self.closed=True

    def is_closed(self):
        return self.closed


class FakeRecaptchaFrame:
    """Synthetic Google checkbox; no real CAPTCHA requests or secrets."""
    def __init__(self, page, *, accepted=False, visible=True,
                 url="https://www.google.com/recaptcha/api2/anchor?k=fixture"):
        self.page=page
        self.url=url
        self.accepted=accepted
        self.visible=visible
        self.clicks=0

    def frame_element(self):
        return self

    def is_visible(self):
        return self.visible

    def locator(self, selector):
        assert selector=="#recaptcha-anchor"
        parent=self
        class Checkbox:
            def count(self): return 1
            def is_visible(self): return parent.visible
            def get_attribute(self, name):
                assert name=="aria-checked"
                return "false"
            def click(self, **kwargs):
                assert kwargs.get("timeout")==1200
                parent.clicks+=1
                if parent.accepted:
                    parent.page.valid=True
                    parent.page.body_text=""
                    parent.page.frames=[]
        return Checkbox()


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
        page=FakePage()
        page.redirect_to=backend.query_url("Unrelated title")
        gateway=backend.VisibleBrowserFetcher(page)
        self.assertEqual(gateway.fetch("Different title"),(503,b""))
        self.assertEqual(page.submit_calls,1)
        self.assertEqual(page.context.opened,[])
        self.assertEqual(gateway.browser_state()["last_failure_reason"],
                         "unexpected_final_query")

    def test_owner_optin_cold_boot_uses_saved_verified_query_once(self):
        class State:
            def __init__(self):
                self.attempts = 0
            def last_query(self):
                return "The Dog Stars 2026 720p"
            def claim_boot_attempt(self):
                self.attempts += 1
                return self.attempts == 1
            def remember_verified(self, query):
                pass
        page = FakePage(url="about:blank", valid=False)
        state = State()
        result = backend.restore_boot_page_once(page.context, page, state)
        self.assertEqual(result, "verified")
        self.assertEqual(page.goto_calls,
                         [backend.query_url("The Dog Stars 2026 720p")])
        self.assertEqual(backend.restore_boot_page_once(page.context, page, state),
                         "existing_tab")
        self.assertEqual(state.attempts, 1)
        self.assertEqual(backend.validated_result_html(page), HTML.encode())

    def test_boot_never_navigates_if_existing_source_or_missing_consent(self):
        class State:
            def last_query(self):
                return "Source query"
            def claim_boot_attempt(self):
                raise AssertionError("must not claim when page is occupied")
        page = FakePage()
        self.assertEqual(backend.restore_boot_page_once(page.context, page, None),
                         "skipped")
        self.assertEqual(backend.restore_boot_page_once(page.context, page, State()),
                         "existing_tab")
        self.assertEqual(page.goto_calls, [])
        page.context.new_page()
        self.assertEqual(backend.restore_boot_page_once(page.context, page, State()),
                         "skipped")
        self.assertEqual(page.goto_calls, [])

    def test_boot_upstream_denial_never_retries(self):
        class State:
            attempts=0
            def last_query(self):
                return "Source query"
            def claim_boot_attempt(self):
                self.attempts += 1
                return self.attempts == 1
        page = FakePage(url="about:blank",valid=False)
        page.next_status = 429
        state=State()
        self.assertEqual(backend.restore_boot_page_once(page.context,page,state),
                         "upstream_non200")
        self.assertEqual(len(page.goto_calls),1)
        self.assertEqual(backend.restore_boot_page_once(page.context,page,state),
                         "existing_tab")
        self.assertEqual(len(page.goto_calls),1)
        self.assertEqual(state.attempts,1)

    def test_verified_browser_snapshot_remembers_only_real_html(self):
        class State:
            seen=[]
            def remember_verified(self, query):
                self.seen.append(query)
        state=State()
        page=FakePage(url=backend.query_url("The Dog Stars 2026"))
        gateway=backend.VisibleBrowserFetcher(page,state)
        gateway.browser_state()
        self.assertEqual(state.seen,["The Dog Stars 2026"])
        page.valid=False
        gateway.browser_state()
        self.assertEqual(state.seen,["The Dog Stars 2026"])
        page.valid=True
        page.url="https://example.invalid/not-btdigg"
        gateway.browser_state()
        self.assertEqual(state.seen,["The Dog Stars 2026"])

    def test_manual_navigation_refreshes_stale_playwright_page_metadata(self):
        # Browser UI is already on BTDigg, but sync API cached page.url
        # remains about:blank until a browser roundtrip pumps its events.
        page = FakePage(url="about:blank", valid=True)
        page.live_url_override = backend.query_url("The Dog Stars 2026")
        gateway = backend.VisibleBrowserFetcher(page)
        state = gateway.browser_state()
        self.assertEqual(state["open_tabs"], 1)
        self.assertTrue(state["selected_tab_verified"])
        self.assertEqual(state["verified_tabs"], 1)
        self.assertEqual(state["tab_diagnostics"][0]["validation"], "valid")
        self.assertEqual(state["tab_diagnostics"][0]["page_kind"],
                         "canonical_search")
        self.assertGreater(page.evaluate_count, 0)
        before = page.evaluate_count
        status, data = gateway.fetch("The Dog Stars 2026")
        self.assertEqual((status, data), (200, HTML.encode()))
        self.assertGreater(page.evaluate_count, before)
        self.assertEqual(page.submit_calls, 0)
        self.assertEqual(page.context.opened, [])

    def test_bad_live_url_fail_closed_without_fabricated_results(self):
        page = FakePage(valid=True)
        page.live_url_override = "https://example.invalid/elsewhere"
        gateway = backend.VisibleBrowserFetcher(page)
        state = gateway.browser_state()
        self.assertEqual(state["verified_tabs"], 0)
        self.assertFalse(state["selected_tab_verified"])
        self.assertEqual(state["tab_diagnostics"][0]["validation"], "not_source")
        self.assertEqual(gateway.fetch("Unseen search"), (503, b""))
        self.assertEqual(page.submit_calls, 0)

    def test_live_location_evaluation_failure_keeps_fail_closed(self):
        page = FakePage(valid=True)
        def fail(_script):
            raise RuntimeError("private browser exception")
        page.evaluate = fail
        state = backend.VisibleBrowserFetcher(page).browser_state()
        self.assertEqual(state["verified_tabs"], 0)
        self.assertEqual(state["tab_diagnostics"][0]["validation"], "not_source")
        self.assertNotIn("private", str(state))

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

    def test_form_missing_never_navigates_and_latches(self):
        page=FakePage()
        page.has_search_input=False
        gateway=backend.VisibleBrowserFetcher(page)
        self.assertEqual(gateway.fetch("Another 2026"),(503,b""))
        self.assertEqual(page.submit_calls,0)
        self.assertEqual(page.context.opened,[])
        self.assertEqual(gateway.browser_state()["last_failure_reason"],
                         "search_input_missing")

    def test_no_navigation_response_after_form_press_latches(self):
        page=FakePage()
        page.no_navigation_response=True
        gateway=backend.VisibleBrowserFetcher(page)
        self.assertEqual(gateway.fetch("Another 2026"),(503,b""))
        self.assertEqual(page.submit_calls,1)
        self.assertEqual(gateway.browser_state()["last_failure_reason"],
                         "no_navigation_response")

    def test_owner_verified_context_allows_one_subsequent_browser_search(self):
        page=FakePage(valid=True)
        gateway=backend.VisibleBrowserFetcher(page)
        self.assertEqual(gateway.fetch("Another 2026"),(200,HTML.encode()))
        self.assertEqual(page.search_fills,["Another 2026"])
        self.assertEqual(page.submit_calls,1)
        self.assertEqual(page.context.opened,[])
        self.assertEqual(page.waits,[500])
        self.assertEqual(page.navigation_options,
                         [{"wait_until":"domcontentloaded","timeout":8000}])
        self.assertIs(gateway.page,page)
        self.assertEqual(backend.source_query(page.url),"Another 2026")

    def test_challenge_reappearing_after_one_navigation_fails_closed(self):
        page=FakePage(valid=True)
        page.after_navigation_valid=False
        gateway=backend.VisibleBrowserFetcher(page)
        self.assertEqual(gateway.fetch("Another 2026"),(503,b""))
        self.assertEqual(gateway.fetch("Another 2026"),(503,b""))
        self.assertEqual(page.submit_calls,1)
        self.assertEqual(page.context.opened,[])
        self.assertEqual(page.waits,[500])
        self.assertEqual(gateway.browser_state()["last_failure_reason"],
                         "unverified_result_html")

    def test_actual_429_or_non_200_preserved_without_fake_results(self):
        for upstream,expected in ((429,429),(403,503),(500,503)):
            page=FakePage()
            page.next_status=upstream
            gateway=backend.VisibleBrowserFetcher(page)
            self.assertEqual(gateway.fetch("New query"),(expected,b""))
            self.assertEqual(gateway.fetch("New query"),(expected,b""))
            self.assertEqual(page.submit_calls,1)
            self.assertEqual(page.context.opened,[])
            self.assertEqual(gateway.browser_state()["last_upstream_http_status"],
                             upstream)
            # Manual owner restoration, no automated bypass.
            page.url=backend.query_url("The Dog Stars 2026")
            page.valid=True
            self.assertEqual(gateway.fetch("The Dog Stars 2026")[0],200)

    def test_second_success_replaces_previous_secondary_tab_not_original(self):
        page=FakePage()
        gateway=backend.VisibleBrowserFetcher(page)
        self.assertEqual(gateway.fetch("Second query")[0],200)
        self.assertEqual(gateway.fetch("Third query")[0],200)
        self.assertEqual(page.submit_calls,2)
        self.assertEqual(page.context.opened,[])
        self.assertIs(gateway.page,page)
        self.assertFalse(page.closed)

    def test_new_tab_exception_is_bounded_and_never_retried(self):
        page=FakePage()
        page.raise_on_press=True
        gateway=backend.VisibleBrowserFetcher(page)
        self.assertEqual(gateway.fetch("New query"),(504,b""))
        self.assertEqual(gateway.fetch("New query"),(504,b""))
        self.assertEqual(page.submit_calls,1)
        self.assertFalse(page.closed)
        self.assertEqual(gateway.fetch("The Dog Stars 2026")[0],200)

    def test_error_then_reused_original_tab_does_not_generate_request(self):
        page=FakePage()
        page.next_status=429
        gateway=backend.VisibleBrowserFetcher(page)
        self.assertEqual(gateway.fetch("Other title"),(429,b""))
        page.url=backend.query_url("The Dog Stars 2026")
        page.valid=True
        self.assertEqual(gateway.fetch("THE DOG STARS 2026")[0],200)
        self.assertEqual(page.submit_calls,1)

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
            "visible_captcha_required": False,
            "last_navigation_status": None,
            "last_failure_reason": None,
            "last_upstream_http_status": None,
            "pwa_tab_recovery_ready": False,
            "pwa_tab_recovery_reason": None,
            "pwa_tab_recovery_wait_seconds": None,
            "pwa_tab_recovery_attempts": 0,
            "pwa_tab_recovery_last_outcome": None,
            "pwa_tab_recovery_last_http_status": None,
            "selected_tab_index": 0,
            "tab_diagnostics": [{
                "page_kind": "canonical_search",
                "paired_rows": 1,
                "title_rows": 1,
                "magnet_rows": 1,
                "html_bytes": len(HTML.encode("utf-8")),
                "validation": "valid",
            }],
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
        self.assertEqual(len(first.context.opened), 0)
        manually_opened = first.context.new_page()
        manually_opened.url = backend.query_url("Manual 2026")
        manually_opened.valid = True
        status, html = gateway.fetch("MANUAL 2026")
        self.assertEqual((status, html), (200, HTML.encode()))
        self.assertEqual(manually_opened.goto_calls, [])
        self.assertEqual(len(first.context.opened), 1)
        self.assertIs(gateway.page, manually_opened)
        state = gateway.browser_state()
        self.assertTrue(state["new_searches_paused"])
        self.assertEqual(state["last_navigation_status"], 429)
        self.assertEqual(state["verified_tabs"], 1,
                         "failed same-tab navigation invalidates its prior rows")
        self.assertEqual(gateway.fetch("Other new query"), (429, b""))
        self.assertEqual(len(first.context.opened), 1)

    def test_owner_verified_second_tab_adopted_without_new_source_request(self):
        old = FakePage(valid=False)
        old.rate_limited = True
        manual = old.context.new_page()
        manual.url = backend.query_url("The dog stars 720p")
        manual.valid = True
        fetcher = backend.VisibleBrowserFetcher(old)
        preflight = fetcher.browser_state()
        self.assertEqual(preflight["open_tabs"], 2)
        self.assertFalse(preflight["selected_tab_verified"])
        self.assertEqual(preflight["verified_tabs"], 1)
        self.assertTrue(preflight["visible_source_rate_limited"])
        self.assertFalse(old.closed, "read-only status never mutates tabs")
        self.assertEqual(fetcher.fetch("THE DOG STARS 720P"),(200,HTML.encode()))
        self.assertTrue(old.closed, "only verified adoption closes stale refusal")
        self.assertFalse(manual.closed)
        self.assertIs(fetcher.page, manual)
        self.assertEqual(manual.goto_calls, [])
        self.assertEqual(manual.submit_calls, 0)
        self.assertEqual(len(old.context.opened), 1)
        state = fetcher.browser_state()
        self.assertEqual((state["open_tabs"],state["verified_tabs"]), (1,1))
        self.assertTrue(state["selected_tab_verified"])
        self.assertFalse(state["visible_source_rate_limited"])
        self.assertFalse(state["new_searches_paused"])
        self.assertEqual(state["pwa_tab_recovery_last_outcome"],
                         "manual_verified_tab_adopted")

    def test_owner_adopted_tab_can_submit_one_different_user_query(self):
        old=FakePage(valid=False)
        old.rate_limited=True
        manual=old.context.new_page()
        manual.url=backend.query_url("The dog stars 720p")
        manual.valid=True
        gateway=backend.VisibleBrowserFetcher(old)
        self.assertEqual(gateway.fetch("Other movie 2026"),(200,HTML.encode()))
        self.assertTrue(old.closed)
        self.assertIs(gateway.page,manual)
        self.assertEqual(manual.submit_calls,1)
        self.assertEqual(manual.search_fills,["Other movie 2026"])
        self.assertEqual(manual.goto_calls,[])
        self.assertEqual(manual.url,backend.query_url("Other movie 2026"))

    def test_manual_adoption_refuses_invalid_challenge_or_ambiguous_tab(self):
        cases=("invalid_manual","captcha_manual","untrusted_manual",
               "three_tabs","old_not_denied","real_http_429")
        for variant in cases:
            with self.subTest(variant=variant):
                old=FakePage(valid=False)
                old.rate_limited=True
                manual=old.context.new_page()
                manual.url=backend.query_url("The dog stars 720p")
                manual.valid=True
                gateway=backend.VisibleBrowserFetcher(old)
                if variant=="invalid_manual":
                    manual.valid=False
                if variant=="captcha_manual":
                    manual.valid=False
                    manual.body_text="Please verify you are human"
                if variant=="untrusted_manual":
                    manual.url="https://example.invalid/source"
                if variant=="three_tabs":
                    old.context.new_page()
                if variant=="old_not_denied":
                    old.rate_limited=False
                if variant=="real_http_429":
                    gateway._source_stopped=429
                    gateway._last_upstream_http_status=429
                self.assertFalse(gateway._adopt_owner_verified_tab())
                self.assertFalse(old.closed)
                self.assertFalse(manual.closed)
                self.assertIs(gateway.page,old)
                self.assertEqual(manual.goto_calls,[])
                self.assertEqual(manual.submit_calls,0)

    def test_failure_reason_for_upstream_http_or_invalid_html(self):
        for status,reason in ((429,"upstream_http_429"),
                              (503,"upstream_http_non200"),
                              (403,"upstream_http_non200")):
            page=FakePage()
            page.next_status=status
            fetcher=backend.VisibleBrowserFetcher(page)
            expected=429 if status==429 else 503
            self.assertEqual(fetcher.fetch("New Title 2026"),(expected,b""))
            state=fetcher.browser_state()
            self.assertEqual(state["last_failure_reason"],reason)
            self.assertEqual(state["last_upstream_http_status"],status)
            self.assertEqual(state["last_navigation_status"],expected)
            self.assertEqual(page.submit_calls,1)
            self.assertEqual(page.context.opened,[])
            self.assertEqual(fetcher.fetch("New Title 2026"),(expected,b""))
            self.assertEqual(page.submit_calls,1)
        page=FakePage()
        page.after_navigation_valid=False
        fetcher=backend.VisibleBrowserFetcher(page)
        self.assertEqual(fetcher.fetch("New Title 2026"),(503,b""))
        self.assertEqual(fetcher.browser_state()["last_failure_reason"],
                         "unverified_result_html")
        self.assertEqual(fetcher.browser_state()["last_upstream_http_status"],200)

    def test_redirect_failure_remains_sanitized(self):
        page=FakePage()
        page.redirect_to=backend.query_url("Unrelated title")
        fetcher=backend.VisibleBrowserFetcher(page)
        self.assertEqual(fetcher.fetch("New Title 2026"),(503,b""))
        state=fetcher.browser_state()
        self.assertEqual(state["last_failure_reason"],"unexpected_final_query")
        self.assertEqual(state["last_upstream_http_status"],200)
        self.assertNotIn("Unrelated",str(state))

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

    def test_sanitized_tab_diagnostic_identifies_nonselected_visible_page(self):
        original = FakePage(url="about:blank", valid=False)
        second = original.context.new_page()
        second.url = backend.query_url("Visible title")
        second.valid = True
        gateway = backend.VisibleBrowserFetcher(original)
        state = gateway.browser_state()
        self.assertEqual(state["open_tabs"], 2)
        self.assertEqual(state["verified_tabs"], 1)
        self.assertFalse(state["selected_tab_verified"])
        self.assertEqual(state["selected_tab_index"], 0)
        tabs = state["tab_diagnostics"]
        self.assertEqual([x["page_kind"] for x in tabs],
                         ["blank", "canonical_search"])
        self.assertEqual(tabs[0]["validation"], "not_source")
        self.assertEqual(tabs[1]["validation"], "valid")
        self.assertEqual(tabs[1]["paired_rows"], 1)
        self.assertEqual(tabs[1]["magnet_rows"], 1)
        self.assertNotIn("Visible title", str(tabs))
        self.assertNotIn("magnet:?xt=", str(tabs))
        self.assertEqual(original.goto_calls, [])
        self.assertEqual(second.goto_calls, [])

    def test_diagnostic_distinguishes_invalid_dom_oversize_and_noncanonical(self):
        page = FakePage(url=backend.query_url("Source query"))
        baseline = backend.sanitized_tab_diagnostic(page)
        self.assertEqual(baseline["validation"], "valid")
        self.assertEqual(baseline["html_bytes"], len(HTML.encode("utf-8")))
        with patch.object(backend, "SIZE_LIMIT", 10):
            self.assertEqual(backend.sanitized_tab_diagnostic(page)["validation"],
                             "oversize_html")
        page.valid = False
        self.assertEqual(backend.sanitized_tab_diagnostic(page)["validation"],
                         "no_paired_rows")
        page.url = "https://btdig.com/search?q=Source+query"
        self.assertEqual(backend.sanitized_tab_diagnostic(page)["page_kind"],
                         "btdigg_noncanonical")
        page.url = "https://elsewhere.invalid/path/private?secret=1"
        entry = backend.sanitized_tab_diagnostic(page)
        self.assertEqual(entry["page_kind"], "other")
        self.assertNotIn("secret", str(entry))
        page.close()
        self.assertEqual(backend.sanitized_tab_diagnostic(page)["validation"],
                         "closed")

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
        self.assertEqual(gateway.fetch("Another query"), (425, b""))
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
        self.assertEqual(gateway.fetch("Unseen query"), (425, b""))
        self.assertEqual(len(first.context.opened), 1)
        self.assertEqual(gateway.fetch("The Dog Stars 2026")[0], 200,
                         "already verified result may still be reused")

    def test_pwa_one_new_tab_only_after_source_refusal_cooldown(self):
        now = [100.0]
        first = FakePage(valid=False)
        first.rate_limited = True
        gateway = backend.VisibleBrowserFetcher(first, clock=lambda: now[0])
        before = gateway.browser_state()
        self.assertEqual(before["pwa_tab_recovery_reason"], "visible_refusal")
        self.assertFalse(before["pwa_tab_recovery_ready"])
        self.assertEqual(before["pwa_tab_recovery_wait_seconds"], 30)
        self.assertEqual(gateway.fetch("Second query"), (425, b""))
        self.assertEqual(first.context.opened, [])
        now[0] += 30
        allowed = gateway.browser_state()
        self.assertTrue(allowed["pwa_tab_recovery_ready"])
        self.assertEqual(allowed["pwa_tab_recovery_wait_seconds"], 0)
        status, body = gateway.fetch("Second query")
        self.assertEqual((status, body), (200, HTML.encode()))
        self.assertEqual(len(first.context.opened), 1)
        new = first.context.opened[0]
        self.assertEqual(new.goto_calls, [backend.query_url("Second query")])
        self.assertIs(gateway.page, new)
        self.assertTrue(first.closed, "old refusal closed after valid magnets")
        self.assertFalse(new.closed)
        self.assertEqual(gateway.browser_state()["open_tabs"], 1)
        self.assertFalse(gateway.browser_state()["new_searches_paused"])
        self.assertEqual(gateway.fetch("Second query"), (200, HTML.encode()))
        self.assertEqual(len(new.goto_calls), 1, "cached tab never navigated again")

    def test_stale_refusal_page_allows_first_user_query_without_new_wait(self):
        now=[50.0]
        first=FakePage(valid=False)
        first.rate_limited=True
        first.navigation_age_ms=60 * 60 * 1000
        gateway=backend.VisibleBrowserFetcher(first, clock=lambda:now[0])
        before=gateway.browser_state()
        self.assertEqual(before["pwa_tab_recovery_reason"],"visible_refusal")
        self.assertTrue(before["pwa_tab_recovery_ready"])
        self.assertEqual(before["pwa_tab_recovery_wait_seconds"],0)
        status,html=gateway.fetch("The Dog Stars 2026 1080p")
        self.assertEqual((status,html),(200,HTML.encode()))
        self.assertEqual(len(first.context.opened),1)
        self.assertTrue(first.closed)
        self.assertEqual(first.context.opened[0].goto_calls,
            [backend.query_url("The Dog Stars 2026 1080p")])

    def test_recent_denial_uses_only_remaining_time_not_fresh_30s(self):
        now=[1000.0]
        first=FakePage(valid=False)
        first.rate_limited=True
        first.navigation_age_ms=25_000.0
        gateway=backend.VisibleBrowserFetcher(first,clock=lambda:now[0])
        status=gateway.browser_state()
        self.assertFalse(status["pwa_tab_recovery_ready"])
        self.assertEqual(status["pwa_tab_recovery_wait_seconds"],5)
        self.assertEqual(gateway.fetch("Requested title"),(425,b""))
        self.assertEqual(first.context.opened,[])
        now[0]+=5
        self.assertEqual(gateway.fetch("Requested title")[0],200)

    def test_explicit_network_429_never_becomes_soft_refusal_even_when_old(self):
        first=FakePage(valid=True)
        first.next_status=429
        gateway=backend.VisibleBrowserFetcher(first,clock=lambda:90000.0)
        self.assertEqual(gateway.fetch("Other title"),(429,b""))
        first.rate_limited=True
        first.navigation_age_ms=5*60*60*1000
        status=gateway.browser_state()
        self.assertTrue(status["visible_source_rate_limited"])
        self.assertFalse(status["pwa_tab_recovery_ready"])
        self.assertIsNone(status["pwa_tab_recovery_reason"])
        self.assertEqual(gateway.fetch("Another title"),(429,b""))
        self.assertEqual(first.context.opened,[])

    def test_unreadable_or_invalid_page_age_fails_closed_with_30s_wait(self):
        for age in (None,False,"old",-1,float("nan"),float("inf")):
            first=FakePage(valid=False)
            first.rate_limited=True
            first.navigation_age_ms=age
            gateway=backend.VisibleBrowserFetcher(first,clock=lambda:0.0)
            status=gateway.browser_state()
            self.assertEqual(status["pwa_tab_recovery_wait_seconds"],30)
            self.assertEqual(first.context.opened,[])

    def test_recovery_refusal_keeps_new_tab_closes_old_and_paces_30s(self):
        now = [0.0]
        first = FakePage(valid=False)
        first.rate_limited = True
        original_new = first.context.new_page
        def blocked_new_tab():
            page = original_new()
            page.rate_limited = True
            page.after_navigation_valid = False
            return page
        first.context.new_page = blocked_new_tab
        gateway = backend.VisibleBrowserFetcher(first, clock=lambda: now[0])
        gateway.browser_state()
        now[0] += 30
        self.assertEqual(gateway.fetch("One requested query"), (425, b""))
        self.assertEqual(len(first.context.opened), 1)
        new = first.context.opened[0]
        self.assertFalse(new.closed, "new BTDigg refusal must remain visible")
        self.assertTrue(first.closed, "old blank/refusal must be closed")
        self.assertIs(gateway.page, new)
        state = gateway.browser_state()
        self.assertEqual(state["open_tabs"], 1)
        self.assertEqual(state["pwa_tab_recovery_attempts"], 1)
        self.assertEqual(state["pwa_tab_recovery_last_outcome"],
                         "visible_refusal")
        self.assertEqual(state["pwa_tab_recovery_last_http_status"], 200)
        self.assertEqual(state["pwa_tab_recovery_wait_seconds"], 30)
        self.assertEqual(gateway.fetch("Other query"), (425, b""))
        self.assertEqual(len(first.context.opened), 1)
        now[0] += 30
        self.assertTrue(gateway.browser_state()["pwa_tab_recovery_ready"])
        self.assertEqual(first.goto_calls, [], "never reuses old page")

    def test_new_captcha_page_stays_visible_until_owner_verifies(self):
        class Marker:
            def boot_attempted_this_boot(self):
                return True
            def remember_verified(self, _query):
                pass
        now=[0.0]
        old=FakePage(url="about:blank", valid=False)
        original_new=old.context.new_page
        def challenge_new_tab():
            new=original_new()
            new.after_navigation_valid=False
            new.body_text="Please verify you are human. I'm not a robot"
            return new
        old.context.new_page=challenge_new_tab
        gateway=backend.VisibleBrowserFetcher(old,Marker(),clock=lambda:now[0])
        gateway.browser_state()
        now[0]+=30
        self.assertEqual(gateway.fetch("The Dog Stars 2026"),(428,b""))
        new=old.context.opened[0]
        self.assertTrue(old.closed)
        self.assertFalse(new.closed)
        self.assertIs(gateway.page,new)
        state=gateway.browser_state()
        self.assertTrue(state["visible_captcha_required"])
        self.assertFalse(state["pwa_tab_recovery_ready"])
        self.assertEqual(state["pwa_tab_recovery_last_outcome"],
                         "captcha_required")
        self.assertEqual(state["pwa_tab_recovery_attempts"],1)
        self.assertEqual(gateway.fetch("Different query"),(428,b""))
        self.assertEqual(len(old.context.opened),1,
                         "no automatic CAPTCHA bypass or tab rotation")

    def test_untrusted_navigation_discards_only_new_tab(self):
        class Marker:
            def boot_attempted_this_boot(self):
                return True
            def remember_verified(self, _query):
                pass
        old=FakePage(url="about:blank",valid=False)
        original_new=old.context.new_page
        def untrusted_new_tab():
            new=original_new()
            new.redirect_to="https://example.invalid/not-btdigg"
            new.live_url_override="https://example.invalid/not-btdigg"
            new.after_navigation_valid=False
            return new
        old.context.new_page=untrusted_new_tab
        gateway=backend.VisibleBrowserFetcher(old,Marker(),clock=lambda:0.0)
        gateway.browser_state()
        gateway._recovery_next_at=0.0
        self.assertEqual(gateway.fetch("Owner query 2026"),(503,b""))
        self.assertFalse(old.closed)
        self.assertTrue(old.context.opened[0].closed)
        self.assertIs(gateway.page,old)
        self.assertEqual(gateway.browser_state()["pwa_tab_recovery_last_outcome"],
                         "untrusted_navigation")

    def test_real_source_http_429_tab_stays_visible_but_no_auto_retry(self):
        class Marker:
            def boot_attempted_this_boot(self):
                return True
            def remember_verified(self, _query):
                pass
        old=FakePage(url="about:blank",valid=False)
        original_new=old.context.new_page
        def http429_new_tab():
            new=original_new()
            new.next_status=429
            new.after_navigation_valid=False
            new.rate_limited=True
            return new
        old.context.new_page=http429_new_tab
        gateway=backend.VisibleBrowserFetcher(old,Marker(),clock=lambda:0.0)
        gateway.browser_state()
        gateway._recovery_next_at=0.0
        self.assertEqual(gateway.fetch("Owner query 2026"),(429,b""))
        self.assertTrue(old.closed)
        self.assertFalse(old.context.opened[0].closed)
        state=gateway.browser_state()
        self.assertEqual(state["pwa_tab_recovery_last_outcome"],
                         "source_http_429")
        self.assertEqual(state["pwa_tab_recovery_last_http_status"],429)
        self.assertFalse(state["pwa_tab_recovery_ready"])
        self.assertEqual(gateway.fetch("Another query 2026"),(429,b""))
        self.assertEqual(len(old.context.opened),1)

    def test_blank_after_guarded_boot_can_recover_after_cooldown(self):
        class Marker:
            def boot_attempted_this_boot(self):
                return True
            def remember_verified(self, _query):
                pass
        now = [0]
        first = FakePage(url="about:blank",valid=False)
        gateway = backend.VisibleBrowserFetcher(first,Marker(),clock=lambda:now[0])
        state = gateway.browser_state()
        self.assertEqual(state["pwa_tab_recovery_reason"],"blank_after_boot")
        self.assertFalse(state["pwa_tab_recovery_ready"])
        self.assertEqual(gateway.fetch("The Dog Stars 2026"),(503,b""))
        now[0] += 30
        self.assertEqual(gateway.fetch("The Dog Stars 2026")[0],200)
        self.assertEqual(len(first.context.opened),1)
        self.assertTrue(first.closed)
        self.assertEqual(first.context.opened[0].goto_calls,
                         [backend.query_url("The Dog Stars 2026")])

    def test_unverified_challenge_or_multiple_tabs_never_recovers(self):
        now = [0]
        challenged = FakePage(valid=False)
        challenged.body_text = "I am not a robot"
        gateway = backend.VisibleBrowserFetcher(challenged,clock=lambda:now[0])
        now[0] += 999999
        self.assertFalse(gateway.browser_state()["pwa_tab_recovery_ready"])
        self.assertEqual(gateway.fetch("Requested 2026"),(428,b""))
        self.assertEqual(challenged.context.opened,[])
        limited = FakePage(valid=False)
        limited.rate_limited = True
        multiple = limited.context.new_page()
        gateway = backend.VisibleBrowserFetcher(limited,clock=lambda:now[0])
        now[0] += 30
        self.assertIsNone(gateway.browser_state()["pwa_tab_recovery_reason"])
        self.assertFalse(gateway.browser_state()["pwa_tab_recovery_ready"])
        self.assertEqual(gateway.fetch("Requested 2026"),(425,b""))
        self.assertEqual(len(limited.context.opened),1)
        self.assertIs(multiple,limited.context.opened[0])

    def test_visible_captcha_pauses_search_without_tab_rotation(self):
        now=[0]
        challenged=FakePage(valid=False)
        challenged.body_text="Please verify you are human. I'm not a robot"
        gateway=backend.VisibleBrowserFetcher(challenged,clock=lambda:now[0])
        state=gateway.browser_state()
        self.assertTrue(state["visible_captcha_required"])
        self.assertFalse(state["pwa_tab_recovery_ready"])
        self.assertIsNone(state["pwa_tab_recovery_reason"])
        self.assertTrue(state["new_searches_paused"])
        now[0] += 100_000
        self.assertEqual(gateway.fetch("New owner search"),(428,b""))
        self.assertEqual(challenged.context.opened,[])
        self.assertFalse(challenged.closed)

    def test_simple_checkbox_clicked_once_and_same_query_reused(self):
        page=FakePage(valid=False)
        captcha=FakeRecaptchaFrame(page,accepted=True)
        page.frames=[captcha]
        gateway=backend.VisibleBrowserFetcher(page)
        self.assertTrue(gateway.browser_state()["visible_captcha_required"])
        self.assertEqual(captcha.clicks,0,
                         "read-only status must never click CAPTCHA")
        status,body=gateway.fetch("The Dog Stars 2026")
        self.assertEqual((status,body),(200,HTML.encode()))
        self.assertEqual(captcha.clicks,1)
        self.assertEqual(page.submit_calls,0)
        self.assertEqual(page.goto_calls,[])
        self.assertFalse(gateway.browser_state()["visible_captcha_required"])

    def test_after_checkbox_acceptance_searches_original_requested_query(self):
        page=FakePage(url=backend.query_url("Deep Water 2025"),valid=False)
        captcha=FakeRecaptchaFrame(page,accepted=True)
        page.frames=[captcha]
        gateway=backend.VisibleBrowserFetcher(page)
        self.assertEqual(gateway.fetch("The Dog Stars 2026"),
                         (200,HTML.encode()))
        self.assertEqual(captcha.clicks,1)
        self.assertEqual(page.search_fills,["The Dog Stars 2026"])
        self.assertEqual(page.submit_calls,1)
        self.assertEqual(page.goto_calls,[])
        self.assertEqual(backend.source_query(page.url),"The Dog Stars 2026")

    def test_unaccepted_checkbox_is_attempted_once_per_document(self):
        page=FakePage(valid=False)
        captcha=FakeRecaptchaFrame(page,accepted=False)
        page.frames=[captcha]
        gateway=backend.VisibleBrowserFetcher(page)
        self.assertEqual(gateway.fetch("Different query"),(428,b""))
        self.assertEqual(gateway.fetch("Different query"),(428,b""))
        self.assertEqual(captcha.clicks,1,"never loop or re-click document")
        self.assertEqual(page.submit_calls,0)
        self.assertEqual(page.goto_calls,[])
        self.assertEqual(len(page.waits),6)

    def test_captcha_image_challenge_is_never_clicked_or_solved(self):
        page=FakePage(valid=False)
        page.body_text="Please verify you are human"
        anchor=FakeRecaptchaFrame(page,accepted=True)
        image=FakeRecaptchaFrame(
            page,url="https://www.google.com/recaptcha/api2/bframe?k=fixture")
        page.frames=[anchor,image]
        gateway=backend.VisibleBrowserFetcher(page)
        self.assertEqual(gateway.fetch("Different query"),(428,b""))
        self.assertEqual(anchor.clicks,0)
        self.assertEqual(image.clicks,0)
        self.assertEqual(page.submit_calls,0)

    def test_untrusted_hidden_or_ambiguous_checkbox_never_clicks(self):
        for variant in ("untrusted","hidden","duplicate","multiple_tabs"):
            with self.subTest(variant=variant):
                page=FakePage(valid=False)
                page.body_text="I'm not a robot"
                captcha=FakeRecaptchaFrame(page,accepted=True)
                if variant=="untrusted":
                    captcha.url="https://evil.example/recaptcha/api2/anchor"
                elif variant=="hidden":
                    captcha.visible=False
                elif variant=="duplicate":
                    page.frames=[FakeRecaptchaFrame(page,accepted=True)]
                elif variant=="multiple_tabs":
                    page.context.new_page()
                page.frames.append(captcha)
                gateway=backend.VisibleBrowserFetcher(page)
                self.assertEqual(gateway.fetch("Owner query"),(428,b""))
                self.assertEqual(captcha.clicks,0)
                self.assertEqual(page.submit_calls,0)

    def test_new_challenge_after_form_submit_attempts_checkbox_once(self):
        page=FakePage(valid=True)
        page.after_navigation_valid=False
        page.body_text="Please verify you are human"
        captcha=FakeRecaptchaFrame(page,accepted=True)
        page.frames=[captcha]
        gateway=backend.VisibleBrowserFetcher(page)
        self.assertEqual(gateway.fetch("New query"),(200,HTML.encode()))
        self.assertEqual(page.submit_calls,1)
        self.assertEqual(captcha.clicks,1)
        self.assertEqual(page.goto_calls,[])

    def test_captcha_hints_inside_verified_results_are_not_a_human_gate(self):
        page=FakePage(valid=True)
        page.body_text="A release called I'm not a robot"
        self.assertFalse(backend.source_challenge_visible(page))
        self.assertFalse(
            backend.VisibleBrowserFetcher(page).browser_state()[
                "visible_captcha_required"
            ]
        )

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

    def test_persistent_chromium_only_restores_on_explicit_optin(self):
        source = Path(backend.__file__).read_text()
        startup = source.split("def main():", 1)[1]
        self.assertIn("launch_persistent_context(", startup)
        self.assertIn("context.pages[0] if context.pages else context.new_page()", startup)
        self.assertNotIn(".goto(", startup,
                         "default startup must never navigate unconditionally")
        self.assertNotIn("page.reload(", startup)
        self.assertIn('if os.environ.get("MAGNETRA_BTDIGG_RESTORE_ON_BOOT") == "1":',
                      startup)
        self.assertIn("restore_boot_page_once(context, page, resume)", startup)
        self.assertIn("browser_fetcher = VisibleBrowserFetcher(page, resume)",startup)

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
