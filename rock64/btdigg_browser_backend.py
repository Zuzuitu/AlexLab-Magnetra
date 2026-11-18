#!/usr/bin/env python3
"""Opt-in, loopback-only BTDigg gateway backed by a human-verified GUI browser.

A visible Chromium is controlled via Playwright's local private pipe. An
authenticated owner-initiated BTDigg search may attempt one visible Google
reCAPTCHA checkbox click in the existing tab. Image puzzles and unresolved
challenges still require the Tailscale-only noVNC viewer. Never forge CAPTCHA
tokens, change browser identity, replay imported cookies, or publish CDP.

Uses the EXISTING BTDigg authenticated gateway response contract and positive
cache; no changes to the Worker, search ranking, or other source adapters.
This backend is intentionally local-only by default and NOT auto-activated.
"""
from __future__ import annotations

from http.server import HTTPServer
import hmac
import json
import os
from pathlib import Path
import re
import signal
import time
import math
import sys
from urllib.parse import quote, parse_qs, urlsplit

if __package__:
    from .btdigg_gateway import BIND, PORT, SIZE_LIMIT, SearchProvider, handler_class
    from .btdigg_bootstrap_state import BootstrapState
else:
    from btdigg_gateway import BIND, PORT, SIZE_LIMIT, SearchProvider, handler_class
    from btdigg_bootstrap_state import BootstrapState

TEST_PORT = 18896
QUERY_LIMIT = 180
SOURCE = "https://btdig.com"
RESULT_PAIR_SELECTOR = (
    'div.one_result:has(div.torrent_name a):has('
    'a[href^="magnet:?xt=urn:btih:"])'
)
QUERY_RE = re.compile(r"[\x00-\x1f\x7f]")
# A user-triggered PWA request may open one new tab only after a source
# refusal has been observed for 30 seconds. No timer sends source requests.
# An owner-initiated search alone may attempt one simple CAPTCHA checkbox
# click per current document; never solve image challenges or loop retries.
PWA_TAB_RECOVERY_DELAYS = (30, 30, 30, 30)
PAGE_AGE_SCRIPT = "() => performance.now()"
CHALLENGE_HINTS = (
    "one more step", "verify you are human", "just a moment",
    "checking your browser", "i'm not a robot", "g-recaptcha",
)


def query_url(query):
    if not isinstance(query, str) or not 2 <= len(query.strip()) <= QUERY_LIMIT:
        raise ValueError("invalid query")
    query = query.strip()
    if QUERY_RE.search(query):
        raise ValueError("invalid query")
    return SOURCE + "/search?order=0&q=" + quote(query, safe="")


def source_query(url):
    """Only canonical BTDigg search pages; never trust a redirect's query."""
    try:
        u = urlsplit(url)
        params = parse_qs(u.query, keep_blank_values=True)
        if not (u.scheme == "https" and u.hostname == "btdig.com"
                and u.username is None and u.password is None
                and u.port in (None, 443) and u.path == "/search"
                and not u.fragment and set(params) == {"order", "q"}
                and params["order"] == ["0"]
                and len(params["q"]) == 1
                and 2 <= len(params["q"][0]) <= QUERY_LIMIT):
            return None
        return params["q"][0]
    except (ValueError, TypeError, KeyError):
        return None


def source_landing(url):
    return source_query(url) is not None


def same_search_query(source_value, requested_value):
    """Source search query matching ignores letter case, not query contents.

    A manual lowercase search must not trigger another source request when a
    later owner-invoked gateway probe uses title case. Never match missing or
    unrelated queries and still require authentic source HTML and magnet rows.
    """
    return (
        isinstance(source_value, str)
        and isinstance(requested_value, str)
        and source_value.casefold() == requested_value.strip().casefold()
    )


def live_document_url(page):
    """One read-only Playwright round trip to the current document.

    The HTTPServer normally blocks the sync Playwright dispatcher while the
    owner navigates manually in Chromium. page.url and context.pages can then
    refer to old event-backed state. JS execution pumps the dispatcher AND
    returns the real document location without any source navigation.
    """
    try:
        url = page.evaluate("() => window.location.href")
        if isinstance(url, str) and len(url) <= 2600:
            return url
    except Exception:
        pass
    return None


def validated_result_html(page, live_url=None):
    """Return only genuine source-owned result HTML; otherwise no bytes.

    No cookies, challenge tokens, JS globals, or scraped results are logged.
    A missing row is NOT a confirmed zero-match search.
    """
    if live_url is None:
        live_url = live_document_url(page)
    if not source_landing(live_url):
        return None
    pairs = page.locator(RESULT_PAIR_SELECTOR).count()
    if pairs < 1:
        return None
    markup = page.content()
    if not isinstance(markup, str):
        return None
    body = markup.encode("utf-8")
    if len(body) > SIZE_LIMIT or b"one_result" not in body.lower():
        return None
    # The Worker revalidates all row titles/magnets with its original parser.
    return body


def source_rate_limit_visible(page, live_url=None):
    """Observe an explicit BTDigg denial in an ALREADY loaded page only.

    A body containing exactly the short source refusal is rate limited.
    A release title containing these words is NOT a refusal. No navigation,
    network requests, cookies or page text are logged or returned.
    """
    try:
        if page.is_closed():
            return False
        if live_url is None:
            live_url = live_document_url(page)
        if not source_landing(live_url):
            return False
        text = page.locator("body").inner_text(timeout=1500)
        if not isinstance(text, str) or len(text) > 160:
            return False
        compact = " ".join(text.casefold().split())
        return compact in ("too many requests", "429 too many requests")
    except Exception:
        return False


def _recaptcha_frame_kind(url):
    """Allowlist Google-hosted reCAPTCHA v2 frames, not arbitrary iframes."""
    try:
        value = urlsplit(url)
        if (value.scheme != "https"
                or value.hostname not in ("www.google.com", "www.recaptcha.net")
                or value.username is not None or value.password is not None
                or value.port not in (None, 443)):
            return None
        if value.path in ("/recaptcha/api2/anchor", "/recaptcha/enterprise/anchor"):
            return "anchor"
        if value.path in ("/recaptcha/api2/bframe", "/recaptcha/enterprise/bframe"):
            return "image_challenge"
    except (ValueError, TypeError):
        pass
    return None


def simple_recaptcha_checkbox(page):
    """Locate one visible unchecked checkbox; never solve image tiles.

    No clicking or browser mutation occurs in this read-only helper.
    """
    try:
        if page.is_closed() or not source_landing(live_document_url(page)):
            return None
        frames = page.frames
        # Google can pre-create a hidden image-challenge iframe before the
        # owner sees a puzzle. A hidden bframe is NOT a visible puzzle; refusing
        # the checkbox merely because it exists makes simple verification fail.
        # Never interact when the actual image challenge is visible.
        if any(_recaptcha_frame_kind(frame.url) == "image_challenge"
               and frame.frame_element().is_visible() for frame in frames):
            return None
        candidates = []
        for frame in frames:
            if _recaptcha_frame_kind(frame.url) != "anchor":
                continue
            if not frame.frame_element().is_visible():
                continue
            checkbox = frame.locator("#recaptcha-anchor")
            if (checkbox.count() == 1 and checkbox.is_visible()
                    and checkbox.get_attribute("aria-checked") == "false"):
                candidates.append(checkbox)
        return candidates[0] if len(candidates) == 1 else None
    except Exception:
        return None


def source_challenge_visible(page, live_url=None):
    """Read-only detection of recognizable human-verification UI.

    Never treat hidden reCAPTCHA assets or strings in genuine result rows as a
    challenge. Only visible short body text on an unverified source-owned tab
    can report a human gate. No page HTML/text leaves this browser.
    """
    try:
        if page.is_closed():
            return False
        if live_url is None:
            live_url = live_document_url(page)
        if not source_landing(live_url):
            return False
        if validated_result_html(page, live_url) is not None:
            return False
        # Captcha checkbox text can live only in its Google cross-origin iframe.
        if simple_recaptcha_checkbox(page) is not None:
            return True
        body = page.locator("body").inner_text(timeout=1500)
        if not isinstance(body, str):
            return False
        # Only inspect a bounded prefix. A source verification page can
        # include long explanatory/footer text while the "One more step"
        # heading and checkbox are at the top of the visible document.
        # Verified result rows were ruled out above.
        visible = " ".join(body[:1800].casefold().split())
        if visible in ("too many requests", "429 too many requests"):
            return False
        return any(hint in visible for hint in (
            "i'm not a robot", "i am not a robot", "verify you are human",
            "please verify you are human", "one more step",
            "checking your browser", "verify that you are human",
            "captcha verification",
        ))
    except Exception:
        return False


def sanitized_tab_diagnostic(page, live_url=None):
    """Read DOM from one Playwright-owned tab; return counts, never content/URLs.

    The GUI noVNC may show a tab different from the page attached to the
    browser gateway. This snapshot distinguishes a wrong tab from a selector,
    HTML size, or marker failure without generating source/network requests.
    """
    out = {
        "page_kind": "other",
        "paired_rows": 0,
        "title_rows": 0,
        "magnet_rows": 0,
        "html_bytes": None,
        "validation": "not_source",
    }
    try:
        if page.is_closed():
            out["page_kind"] = "closed"
            out["validation"] = "closed"
            return out
        url = live_url if live_url is not None else live_document_url(page)
        if not source_landing(url):
            if url == "about:blank":
                out["page_kind"] = "blank"
            elif isinstance(url, str) and urlsplit(url).hostname == "btdig.com":
                out["page_kind"] = "btdigg_noncanonical"
            return out
        out["page_kind"] = "canonical_search"
        # Numbers describe DOM structure only, not any release or magnet.
        out["paired_rows"] = min(page.locator(RESULT_PAIR_SELECTOR).count(), 100000)
        out["title_rows"] = min(
            page.locator("div.one_result div.torrent_name a").count(), 100000)
        out["magnet_rows"] = min(
            page.locator('div.one_result a[href^="magnet:"]').count(), 100000)
        if out["paired_rows"] == 0:
            out["validation"] = "no_paired_rows"
            return out
        markup = page.content()
        if not isinstance(markup, str):
            out["validation"] = "nontext_html"
            return out
        body = markup.encode("utf-8")
        out["html_bytes"] = len(body)
        if len(body) > SIZE_LIMIT:
            out["validation"] = "oversize_html"
        elif b"one_result" not in body.lower():
            out["validation"] = "missing_marker"
        else:
            out["validation"] = "valid"
        return out
    except Exception:
        # Never expose browser exception, page URL or private DOM.
        out["validation"] = "inspection_error"
        return out


class VisibleBrowserFetcher:
    """One-thread Playwright gateway; preserve verified tabs on source refusal.

    A different query enters text in the BTDigg search form of the currently
    verified tab and presses Enter, like the owner. No new tab or direct goto.
    Any source denial or unexpected response pauses further submissions.
    An opt-in boot-restored blank tab or visible refusal may be recovered by
    ONE explicit PWA query. A page already older than the 30-second
    interval needs no extra wait; new refusals still pace further attempts.
    """

    def __init__(self, page, bootstrap_state=None, clock=None):
        self._bootstrap_state = bootstrap_state
        self.page = page
        self.reference_page = page
        self._source_stopped = None
        self._last_failure_reason = None
        self._last_upstream_http_status = None
        self._clock = clock if clock is not None else time.monotonic
        self._recovery_next_at = None
        self._recovery_failures = 0
        self._recovery_locked = False
        # Bounded, private diagnostics: no search terms, URLs, HTML, tokens,
        # cookies, magnet names or browser identity are retained or returned.
        self._recovery_attempts = 0
        self._recovery_last_outcome = None
        self._recovery_last_http_status = None
        # One click per top-level document, maximum 128 different documents.
        self._simple_checkbox_attempts = set()
        # Private, fixed-category diagnostics; no URLs, sitekeys or tokens.
        self._checkbox_last_outcome = "not_attempted"
        self._checkbox_click_count = 0

    def _record_recovery(self, outcome, http_status=None):
        self._recovery_last_outcome = outcome
        self._recovery_last_http_status = (
            http_status if type(http_status) is int
            and 100 <= http_status <= 599 else None
        )

    def _adopt_recovery_tab(self, original, fresh, *,
                            preserve_dual_refusal=False):
        """Adopt a verified source-owned tab; optionally retain two refusals.

        With exactly two source-owned, visibly refused documents, retain BOTH
        for the owner's comparison. Neither tab is verified; the recovery is
        terminal and cannot automatically create a third tab. A prior blank
        tab is always closed, and successful results still replace old tabs.
        Return True only when the two refusal tabs were safely retained.
        """
        keep_both = False
        if preserve_dual_refusal:
            try:
                pages = [p for p in original.context.pages if not p.is_closed()]
                keep_both = (
                    len(pages) == 2 and original in pages and fresh in pages
                    and source_rate_limit_visible(original)
                    and source_rate_limit_visible(fresh)
                    and validated_result_html(original) is None
                    and validated_result_html(fresh) is None
                )
            except Exception:
                keep_both = False
        self.page = fresh
        self.reference_page = fresh
        if keep_both:
            return True
        try:
            original.close()
        except Exception:
            pass
        return False

    def _adopt_owner_verified_tab(self, requested_query=None):
        """Adopt exactly one owner-verified tab without external navigation.

        Supports either a refused/verified pair or the owner's real recovery
        case: two visibly refused BTDigg tabs plus a third, manually verified
        tab containing actual title/magnet rows. An authenticated PWA search
        is required; read-only status never closes tabs. For the three-tab
        case, require the request to match the *already verified* document
        so adoption cannot implicitly submit another source query.
        """
        try:
            if (self._source_stopped is not None
                    or self._last_upstream_http_status == 429):
                return False
            pages = [p for p in self.page.context.pages if not p.is_closed()]
            if len(pages) not in (2, 3) or self.page not in pages:
                return False
            # The currently controlled tab must be one visibly refused source
            # page. No arbitrary, CAPTCHA, valid or blank page can be adopted
            # from, even when another tab happens to contain results.
            selected_url = live_document_url(self.page)
            if (not source_rate_limit_visible(self.page, selected_url)
                    or validated_result_html(self.page, selected_url) is not None
                    or source_challenge_visible(self.page, selected_url)):
                return False
            refused = [self.page]
            verified = []
            for p in pages:
                if p is self.page:
                    continue
                url = live_document_url(p)
                html = validated_result_html(p, url)
                if html is not None:
                    if (source_rate_limit_visible(p, url)
                            or source_challenge_visible(p, url)):
                        return False
                    verified.append((p, url, html))
                elif (source_rate_limit_visible(p, url)
                        and not source_challenge_visible(p, url)):
                    refused.append(p)
                else:
                    # Unknown pages, additional challenges and incomplete
                    # DOMs make the entire adoption ambiguous.
                    return False
            if len(verified) != 1 or len(refused) != len(pages) - 1:
                return False
            candidate, url, html = verified[0]
            if len(pages) == 3 and (
                requested_query is None
                or not same_search_query(source_query(url), requested_query)
            ):
                return False
            # All DOM checks are complete before the first mutation. The new
            # tab becomes authoritative, then each stale refusal is closed.
            self._remember_verified(url, html)
            self.page = candidate
            self.reference_page = candidate
            for stale in refused:
                try:
                    stale.close()
                except Exception:
                    # No new navigation. An unclosed refusal stays visible
                    # and prevents future searches through the 8796 preflight.
                    pass
            self._record_recovery("manual_verified_tab_adopted")
            self._recovery_next_at = None
            self._recovery_failures = 0
            self._recovery_locked = False
            return True
        except Exception:
            # Do not leak URLs, titles, HTML or Playwright exception details.
            return False

    def _refusal_page_age_seconds(self):
        """Read navigation age from the open tab, no network activity.

        A persisted refusal may be hours old. It is not a new HTTP 429 just
        because the user first observes it now. If age cannot be read, use
        the full 30-second local guard instead of assuming the page is old.
        """
        try:
            elapsed_ms = self.page.evaluate(PAGE_AGE_SCRIPT)
            if (type(elapsed_ms) not in (float, int)
                    or not math.isfinite(elapsed_ms)
                    or elapsed_ms < 0):
                return 0.0
            return min(elapsed_ms / 1000, PWA_TAB_RECOVERY_DELAYS[0])
        except Exception:
            return 0.0

    def _recovery_reason(self, pages, urls, visible_denial, visible_challenge):
        """Only a single controlled, unverified tab may trigger recovery.

        Never auto-open a new tab for a CAPTCHA, an arbitrary site, or an
        ambiguous multi-tab context. The OS-boot marker prevents confusing a
        genuinely fresh blank profile with an already attempted restoration.
        """
        if (self._recovery_locked or visible_challenge or len(pages) != 1
                or pages[0] is not self.page or self.page.is_closed()):
            return None
        # A genuine transport HTTP 429 is authoritative even if Chromium
        # happens to render its text on a canonical search page. Never
        # treat that as a stale HTTP-200 tab that can be replaced.
        if self._source_stopped == 429 or self._last_upstream_http_status == 429:
            return None
        if visible_denial:
            return "visible_refusal"
        if (self._source_stopped is None
                and urls.get(self.page) == "about:blank"
                and self._bootstrap_state is not None
                and self._bootstrap_state.boot_attempted_this_boot()):
            return "blank_after_boot"
        return None

    def _recovery_status(self, pages, urls, visible_denial, visible_challenge):
        reason = self._recovery_reason(
            pages, urls, visible_denial, visible_challenge
        )
        if reason is None:
            return False, None, None
        now = self._clock()
        if self._recovery_next_at is None:
            elapsed = (self._refusal_page_age_seconds()
                       if reason == "visible_refusal" else 0.0)
            self._recovery_next_at = now + max(
                0.0, PWA_TAB_RECOVERY_DELAYS[0] - elapsed
            )
        wait = max(0, math.ceil(self._recovery_next_at - now))
        return wait == 0, reason, wait

    def _recovery_failed(self, terminal=False):
        """No network activity: protect subsequent explicit PWA requests."""
        self._recovery_failures = min(
            self._recovery_failures + 1, len(PWA_TAB_RECOVERY_DELAYS) - 1
        )
        self._recovery_next_at = self._clock() + (
            PWA_TAB_RECOVERY_DELAYS[self._recovery_failures]
        )
        if terminal:
            self._recovery_locked = True

    def _recover_in_one_new_tab(self, query):
        """One owner-requested navigation; no loop or source-rate-limit bypass.

        Keep both canonical refused tabs as evidence when both show the same
        visible source denial. Otherwise replace the stale/blank tab with the
        new source-owned tab. An untrusted new tab is always discarded.
        """
        original = self.page
        fresh = None
        self._recovery_attempts = min(self._recovery_attempts + 1, 1_000_000)
        self._record_recovery("started")
        try:
            fresh = original.context.new_page()
            response = fresh.goto(
                query_url(query), wait_until="domcontentloaded", timeout=8000
            )
            if response is None:
                self._record_recovery("no_navigation_response")
                self._recovery_failed(terminal=True)
                return 503, b""

            http_status = response.status
            if http_status == 200:
                fresh.wait_for_timeout(500)
            current_url = live_document_url(fresh)
            if not same_search_query(source_query(current_url), query):
                self._record_recovery("untrusted_navigation", http_status)
                self._recovery_failed(terminal=True)
                return 503, b""

            # The fresh tab is a real source-owned document. Keep it visible
            # for a future human challenge and close the old blank/refusal.
            if http_status == 429:
                self._record_recovery("source_http_429", 429)
                self._stop_navigation(429, "upstream_http_429", 429)
                self._recovery_failed(terminal=True)
                self._adopt_recovery_tab(
                    original, fresh, preserve_dual_refusal=True
                )
                fresh = None
                return 429, b""
            if http_status != 200:
                self._record_recovery("source_http_non200", http_status)
                self._stop_navigation(
                    503, "upstream_http_non200", http_status
                )
                self._recovery_failed(terminal=True)
                self._adopt_recovery_tab(original, fresh)
                fresh = None
                return 503, b""

            html = validated_result_html(fresh, current_url)
            if html is None:
                denied = source_rate_limit_visible(fresh, current_url)
                challenge = source_challenge_visible(fresh, current_url)
                self._record_recovery(
                    "visible_refusal" if denied else
                    "captcha_required" if challenge else
                    "unverified_result_html",
                    200,
                )
                # Preserve both tabs only when BOTH show source refusals;
                # otherwise replace the old blank/refusal as before. On a
                # CAPTCHA, attempt only the eligible checkbox in the new tab.
                # A retained pair is terminal; never auto-create a third tab.
                kept_two_refusals = self._adopt_recovery_tab(
                    original, fresh, preserve_dual_refusal=denied
                )
                fresh = None
                if challenge:
                    result = self._attempt_simple_recaptcha_checkbox(query)
                    if result[0] == 200:
                        self._record_recovery("verified_after_checkbox", 200)
                        self._source_stopped = None
                        self._recovery_locked = False
                        self._recovery_failures = 0
                        self._recovery_next_at = None
                        return result
                    self._recovery_failed(terminal=True)
                    return 428, b""
                self._recovery_failed(
                    terminal=not denied or kept_two_refusals
                )
                return (425 if denied else 503), b""

            self._remember_verified(current_url, html)
            self._record_recovery("verified_results", 200)
            self._adopt_recovery_tab(original, fresh)
            fresh = None
            self._source_stopped = None
            self._last_failure_reason = None
            self._last_upstream_http_status = None
            self._recovery_failures = 0
            self._recovery_next_at = None
            self._recovery_locked = False
            return 200, html
        except Exception:
            self._record_recovery("navigation_exception")
            self._recovery_failed(terminal=True)
            return 504, b""
        finally:
            # Do not leave an untrusted or blank temporary tab attached.
            # A trusted new BTDigg tab has already transferred ownership and
            # set 'fresh = None', so it is NEVER closed here.
            if fresh is not None:
                try:
                    fresh.close()
                except Exception:
                    pass

    def _stop_navigation(self, code, reason, http_status=None):
        """Sanitized, fixed-category reason. Never retain source HTML or URL."""
        self._source_stopped = code
        self._last_failure_reason = reason
        self._last_upstream_http_status = (
            http_status if type(http_status) is int
            and 100 <= http_status <= 599 else None
        )
        return code, b""

    def _remember_verified(self, url, markup):
        if self._bootstrap_state is None or markup is None:
            return
        query = source_query(url)
        if query is None:
            return
        try:
            self._bootstrap_state.remember_verified(query)
        except (OSError, ValueError):
            # Readiness must not depend on optional on-disk resume state.
            pass

    def _verified_existing_query(self, query):
        """Reuse owner-opened verified tabs without network navigation.

        Never trust a tab solely because its URL contains the query: the
        source-owned canonical URL and paired result/magnet HTML are required.
        """
        # A read-only browser call pumps queued GUI navigation/tab events.
        first_url = live_document_url(self.page)
        pages = [self.page]
        pages.extend(p for p in self.page.context.pages if p is not self.page)
        for page in pages:
            url = first_url if page is self.page else live_document_url(page)
            if (not page.is_closed()
                    and same_search_query(source_query(url), query)):
                html = validated_result_html(page, url)
                if html is not None:
                    self._remember_verified(url, html)
                    return page, html
        return None, None

    def browser_state(self):
        """Authenticated, read-only state of existing DOM; no source requests."""
        try:
            # Pump pending Playwright events from owner GUI navigation first;
            # context.pages and page.url may otherwise be stale.
            first_url = live_document_url(self.page)
            pages = [p for p in self.page.context.pages if not p.is_closed()]
            # Bound inspection to eight pages, with fail-closed overflow.
            checked_pages = pages[:8]
            urls = {
                p: (first_url if p is self.page else live_document_url(p))
                for p in checked_pages
            }
            verified_by_page = {
                p: validated_result_html(p, urls[p]) for p in checked_pages
            }
            verified = sum(v is not None for v in verified_by_page.values())
            if self.page in verified_by_page:
                self._remember_verified(urls[self.page],
                                        verified_by_page[self.page])
            visible_denial = any(
                source_rate_limit_visible(p, urls[p]) for p in checked_pages
            )
            visible_challenge = any(
                verified_by_page[p] is None and source_challenge_visible(
                    p, urls[p]
                ) for p in checked_pages
            )
            recovery_ready, recovery_reason, recovery_wait = (
                self._recovery_status(
                    pages, urls, visible_denial, visible_challenge
                )
            )
            tab_diagnostics = [
                sanitized_tab_diagnostic(p, urls[p]) for p in checked_pages
            ]
            selected_index = next(
                (i for i, p in enumerate(checked_pages) if p is self.page), -1
            )
            return {
                "browser_connected": bool(pages),
                "open_tabs": len(pages),
                "verified_tabs": verified,
                "selected_tab_verified": (
                    not self.page.is_closed()
                    and self.page in urls
                    and verified_by_page[self.page] is not None
                ),
                "visible_source_rate_limited": visible_denial,
                "visible_captcha_required": visible_challenge,
                "new_searches_paused": (
                    self._source_stopped is not None or visible_denial
                    or visible_challenge
                    or len(pages) > len(checked_pages)
                ),
                # A visible 429 body is not proof of the network HTTP status.
                "last_navigation_status": self._source_stopped,
                "last_failure_reason": self._last_failure_reason,
                "last_upstream_http_status": self._last_upstream_http_status,
                "pwa_tab_recovery_ready": recovery_ready,
                "pwa_tab_recovery_reason": recovery_reason,
                "pwa_tab_recovery_wait_seconds": recovery_wait,
                "pwa_tab_recovery_attempts": self._recovery_attempts,
                "pwa_tab_recovery_last_outcome": self._recovery_last_outcome,
                "pwa_tab_recovery_last_http_status": (
                    self._recovery_last_http_status
                ),
                "checkbox_last_outcome": self._checkbox_last_outcome,
                "checkbox_click_count": self._checkbox_click_count,
                "selected_tab_index": selected_index,
                "tab_diagnostics": tab_diagnostics,
            }
        except Exception:
            return {
                "browser_connected": False,
                "open_tabs": 0,
                "verified_tabs": 0,
                "selected_tab_verified": False,
                "visible_source_rate_limited": False,
                "visible_captcha_required": False,
                "new_searches_paused": True,
                "last_navigation_status": None,
                "last_failure_reason": None,
                "last_upstream_http_status": None,
                "pwa_tab_recovery_ready": False,
                "pwa_tab_recovery_reason": None,
                "pwa_tab_recovery_wait_seconds": None,
                "pwa_tab_recovery_attempts": self._recovery_attempts,
                "pwa_tab_recovery_last_outcome": self._recovery_last_outcome,
                "pwa_tab_recovery_last_http_status": (
                    self._recovery_last_http_status
                ),
                "checkbox_last_outcome": self._checkbox_last_outcome,
                "checkbox_click_count": self._checkbox_click_count,
                "selected_tab_index": -1,
                "tab_diagnostics": [],
            }

    def _attempt_simple_recaptcha_checkbox(self, query):
        """One guarded Google checkbox click in the owner's ongoing search.

        Wait briefly for an asynchronously mounted checkbox, because the
        challenge heading can render before Google's anchor iframe. Hidden
        image-challenge iframes are ignored, but a visible puzzle is never
        clicked or solved. No refresh, new tab, offsite request or loop retry.
        """
        try:
            state = self.browser_state()
            if (state["open_tabs"] != 1 or state["verified_tabs"] != 0
                    or state["visible_captcha_required"] is not True
                    or state["visible_source_rate_limited"] is not False
                    or state["selected_tab_index"] != 0
                    or self._source_stopped is not None
                    or self._last_upstream_http_status == 429):
                self._checkbox_last_outcome = "unsafe_context"
                return 428, b""
            checkbox = None
            # Allow up to 1.2 seconds for Google's asynchronous iframe mount.
            # This is an observation of the current source-owned document;
            # it never navigates or sends another BTDigg request.
            for attempt in range(7):
                if any(
                    _recaptcha_frame_kind(frame.url) == "image_challenge"
                    and frame.frame_element().is_visible()
                    for frame in self.page.frames
                ):
                    self._checkbox_last_outcome = "image_challenge"
                    return 428, b""
                checkbox = simple_recaptcha_checkbox(self.page)
                if checkbox is not None:
                    break
                if attempt < 6:
                    self.page.wait_for_timeout(200)
            if checkbox is None:
                self._checkbox_last_outcome = "checkbox_not_visible"
                return 428, b""
            navigation_time = self.page.evaluate("() => performance.timeOrigin")
            if (type(navigation_time) not in (int, float)
                    or not math.isfinite(navigation_time)
                    or navigation_time <= 0):
                self._checkbox_last_outcome = "invalid_document"
                return 428, b""
            marker = (id(self.page), int(navigation_time))
            if (marker in self._simple_checkbox_attempts
                    or len(self._simple_checkbox_attempts) >= 128):
                self._checkbox_last_outcome = "already_attempted"
                return 428, b""
            # Record BEFORE interaction; exceptions cannot rearm the click.
            self._simple_checkbox_attempts.add(marker)
            self._checkbox_last_outcome = "click_started"
            self._checkbox_click_count += 1
            checkbox.click(timeout=1200)
            for _ in range(6):
                current_url = live_document_url(self.page)
                if (source_landing(current_url)
                        and not source_rate_limit_visible(self.page, current_url)
                        and validated_result_html(self.page, current_url) is not None):
                    # Return ONLY the original requested query's verified HTML,
                    # or perform its already authorized same-tab form submit.
                    result = self.fetch(query)
                    if result[0] == 200:
                        self._checkbox_last_outcome = "verified_after_click"
                    else:
                        self._checkbox_last_outcome = "verified_other_query"
                    return result
                if any(
                    _recaptcha_frame_kind(frame.url) == "image_challenge"
                    and frame.frame_element().is_visible()
                    for frame in self.page.frames
                ):
                    self._checkbox_last_outcome = "image_challenge"
                    return 428, b""
                self.page.wait_for_timeout(300)
            self._checkbox_last_outcome = "clicked_not_verified"
            return 428, b""
        except Exception:
            if self._checkbox_last_outcome == "click_started":
                self._checkbox_last_outcome = "click_failed"
            else:
                self._checkbox_last_outcome = "inspection_failed"
            return 428, b""

    def fetch(self, query):
        try:
            query_url(query)  # Validate without initiating any source request.
            # This runs ONLY for an authenticated owner PWA /v1/search call;
            # browser-state/healthz remain strictly read-only.
            # Attempt the single visible checkbox only on an authenticated,
            # owner-initiated search, never from health/status or idle tasks.
            if (self._source_stopped is None
                    and source_challenge_visible(self.page)):
                return self._attempt_simple_recaptcha_checkbox(query)
            adopted = self._adopt_owner_verified_tab(query)
            if not adopted:
                # A 3+-tab context must never bypass failed adoption by
                # scanning and returning a matching but ambiguous document.
                # In particular, no new source request may be submitted.
                open_pages = [
                    p for p in self.page.context.pages if not p.is_closed()
                ]
                if len(open_pages) >= 3:
                    refused = any(
                        source_rate_limit_visible(p) for p in open_pages
                    )
                    return (425 if refused else 503), b""
            existing_page, existing_html = self._verified_existing_query(query)
            if existing_html is not None:
                # A manual search in another already-open tab is safe to read;
                # it must not create another network request.
                self.page = existing_page
                return 200, existing_html

            # Recovery only on one explicit PWA search. A pre-existing old
            # refusal may already satisfy the local 30-second interval.
            # The preceding authenticated browser-state preflight
            # is repeated here; it does not navigate to any source.
            recovery = self.browser_state()
            if recovery["pwa_tab_recovery_ready"] is True:
                return self._recover_in_one_new_tab(query)

            if self._source_stopped is not None:
                # An explicit prior navigation failure cannot be retried
                # until a guarded recovery is eligible (or human verifies).
                return self._source_stopped, b""

            # A restored browser can display BTDigg's explicit refusal even
            # when no navigation occurred in this Playwright process. Do not
            # treat a fresh local latch as permission to hit the source again.
            if any(source_rate_limit_visible(p) for p in self.page.context.pages
                   if not p.is_closed()):
                return 425, b""

            # No automated navigation while the currently controlled tab is
            # unverified. Owner can first verify an existing tab manually.
            if validated_result_html(self.page) is None:
                return 503, b""

            try:
                # Interact with the ALREADY VERIFIED source tab, not an empty
                # programmatically opened tab. Exactly one form submission.
                box = self.page.locator('input[name="q"]')
                if box.count() != 1:
                    return self._stop_navigation(503, "search_input_missing")
                box.fill(query, timeout=2000)
                with self.page.expect_navigation(
                    wait_until="domcontentloaded", timeout=8000
                ) as navigation:
                    box.press("Enter", timeout=1500)
                response = navigation.value
                if response is None:
                    return self._stop_navigation(503, "no_navigation_response")
                if response.status == 429:
                    return self._stop_navigation(
                        429, "upstream_http_429", response.status)
                if response.status != 200:
                    return self._stop_navigation(
                        503, "upstream_http_non200", response.status)
                self.page.wait_for_timeout(500)
                if not same_search_query(
                    source_query(live_document_url(self.page)), query
                ):
                    return self._stop_navigation(503, "unexpected_final_query", 200)
                html = validated_result_html(self.page)
                if html is None:
                    if source_challenge_visible(self.page):
                        return self._attempt_simple_recaptcha_checkbox(query)
                    return self._stop_navigation(503, "unverified_result_html", 200)
                self._remember_verified(live_document_url(self.page), html)
                return 200, html
            except Exception:
                # No query, URL, HTML, browser cookies or exception details.
                return self._stop_navigation(504, "browser_navigation_exception")
        except (ValueError, TypeError):
            return 400, b""
        except Exception:
            return 504, b""


def restore_boot_page_once(context, page, state):
    """Opt-in cold-boot restore: at most ONE source navigation per OS boot.

    No action for a still-visible tab, absent saved query, failed state guard
    or different Chromium context. A 429/challenge is never retried.
    """
    try:
        if state is None or len(context.pages) != 1 or context.pages[0] is not page:
            return "skipped"
        if live_document_url(page) != "about:blank":
            return "existing_tab"
        query = state.last_query()
        if query is None:
            return "no_saved_query"
        url = query_url(query)  # Fixed HTTPS origin and canonical search path.
        if not state.claim_boot_attempt():
            return "already_attempted_this_boot"
        try:
            response = page.goto(
                url, wait_until="domcontentloaded", timeout=8000
            )
            if response is None or response.status != 200:
                return "upstream_non200"
            html = validated_result_html(page)
            if html is None:
                return "unverified_source"
            return "verified"
        except Exception:
            return "navigation_exception"
    except (OSError, UnicodeError, ValueError):
        return "state_unavailable"


class BrowserProcessUnavailable(RuntimeError):
    """Fatal local Chromium loss; let the existing user systemd unit restart."""


class BrowserLivenessSupervisor:
    """Bounded read-only GUI liveness checks while HTTPServer is idle.

    This makes a dead Chromium process visible to the existing
    Restart=on-failure user unit instead of leaving a healthy-looking HTTP
    listener on 18896 forever. Each probe reads ONLY existing page/DOM state,
    never navigates BTDigg or retries a CAPTCHA. Three consecutive failures
    are needed so transient Playwright event delays do not drop a good session.
    """

    INTERVAL_SECONDS = 10
    CONSECUTIVE_FAILURES = 3

    def __init__(self, reader, clock=time.monotonic):
        self._reader = reader
        self._clock = clock
        self._next_at = clock() + self.INTERVAL_SECONDS
        self._failures = 0

    def check(self):
        now = self._clock()
        if now < self._next_at:
            return
        self._next_at = now + self.INTERVAL_SECONDS
        try:
            snapshot = self._reader()
            connected = (isinstance(snapshot, dict)
                         and snapshot.get("browser_connected") is True)
        except Exception:
            # A dead Playwright connection may raise instead of reporting
            # a disconnected browser; do not expose exception details.
            connected = False
        if connected:
            self._failures = 0
            return
        self._failures += 1
        if self._failures >= self.CONSECUTIVE_FAILURES:
            raise BrowserProcessUnavailable("local Chromium is disconnected")


class BrowserSupervisedHTTPServer(HTTPServer):
    """Plain single-threaded private HTTPServer with idle Playwright checks.

    socketserver.BaseServer.serve_forever() calls service_actions() on every
    polling iteration. Playwright sync operations therefore remain in the
    SAME thread that owns the browser; there is no watchdog thread.
    """

    def __init__(self, address, handler, browser_state_reader,
                 clock=time.monotonic):
        self._browser_supervisor = BrowserLivenessSupervisor(
            browser_state_reader, clock=clock
        )
        super().__init__(address, handler)

    def service_actions(self):
        super().service_actions()
        self._browser_supervisor.check()


def browser_handler_class(token, provider, fetcher):
    """Extra authenticated read-only route, experimental loopback only.

    The production BTDigg handler and its /healthz and /v1/search semantics
    remain unchanged. No query, URL, cookie, magnet or token is returned.
    """
    parent = handler_class(token, provider)

    class BrowserHandler(parent):
        def do_GET(self):
            if self.path != "/v1/browser-state":
                return super().do_GET()
            provided = self.headers.get("authorization", "")
            if not hmac.compare_digest(provided, "Bearer " + token):
                self.reply(401, b'{"error":"unauthorized"}')
                return
            data = json.dumps(
                fetcher.browser_state(), separators=(",", ":"), sort_keys=True
            ).encode("utf-8")
            self.reply(200, data)

    return BrowserHandler


def validate_configuration():
    if os.geteuid() == 0:
        raise SystemExit("STOP: run the browser as an unprivileged user")
    if os.environ.get("MAGNETRA_BTDIGG_BROWSER_OPT_IN") != "1":
        raise SystemExit("STOP: browser gateway is disabled by default")
    if not os.environ.get("DISPLAY"):
        raise SystemExit("STOP: Xvfb/graphical DISPLAY is required")
    token = os.environ.get("MAGNETRA_BTDIGG_TOKEN", "")
    if not re.fullmatch(r"[A-Za-z0-9_-]{48,256}", token):
        raise SystemExit("STOP: missing private gateway token")
    profile_dir = Path(os.environ.get("MAGNETRA_BROWSER_PROFILE", ""))
    if (not profile_dir.is_absolute() or profile_dir.is_symlink()
            or not profile_dir.is_dir()):
        raise SystemExit("STOP: a private persistent browser profile is required")
    if profile_dir.stat().st_mode & 0o077:
        raise SystemExit("STOP: persistent browser profile must be mode 0700")
    port = os.environ.get("MAGNETRA_BTDIGG_BROWSER_PORT", str(TEST_PORT))
    if port not in (str(TEST_PORT), str(PORT)):
        raise SystemExit("STOP: unsupported gateway port")
    if port == str(PORT) and (
        os.environ.get("MAGNETRA_BTDIGG_SOURCE_PERMISSION_CONFIRMED") != "1"
        or os.environ.get("MAGNETRA_BTDIGG_PRODUCTION_OPT_IN") != "1"
    ):
        raise SystemExit("STOP: production gateway requires explicit authorization")
    return token, profile_dir, int(port)


def main():
    token, profile, port = validate_configuration()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise SystemExit("STOP: missing Playwright in isolated browser venv") from None
    executable = "/usr/bin/chromium"
    if not Path(executable).is_file():
        raise SystemExit("STOP: Debian Chromium not available")

    def on_term(_signum, _frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, on_term)
    with sync_playwright() as p:
        # Chromium is a real, visible browser, no CDP/web debugging listener.
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile), executable_path=executable,
            headless=False, chromium_sandbox=True,
            accept_downloads=False,
            args=["--no-first-run", "--no-default-browser-check",
                  "--disable-extensions", "--disk-cache-size=16777216"],
            timeout=12000,
        )
        try:
            # Default: never visit BTDigg merely because Chromium started.
            # The explicit opt-in below can restore one previously verified
            # search only if Chromium has a blank sole tab, at most once per
            # OS boot. An existing tab will never receive an extra request.
            # A brand-new profile opens a blank tab until the owner verifies
            # a source page or saves an explicit seed.
            page = context.pages[0] if context.pages else context.new_page()
            # No startup request unless the owner explicitly enabled the boot
            # service, previously saved a verified query and opened a blank tab.
            # Mark this OS boot before the only possible source navigation.
            resume = None
            if os.environ.get("MAGNETRA_BTDIGG_RESTORE_ON_BOOT") == "1":
                resume = BootstrapState(profile.parent)
                boot_result = restore_boot_page_once(context, page, resume)
                print("BTDigg cold boot: " + boot_result, flush=True)
            browser_fetcher = VisibleBrowserFetcher(page, resume)
            provider = SearchProvider(fetcher=browser_fetcher.fetch)
            # HTTPServer (NOT ThreadingHTTPServer): Playwright sync page remains
            # owned by the same thread for every subsequent search.
            server = BrowserSupervisedHTTPServer(
                (BIND, port),
                browser_handler_class(token, provider, browser_fetcher),
                browser_fetcher.browser_state,
            )
            print("BTDigg verified-browser gateway: loopback only; "
                  "waiting for optional manual verification", flush=True)
            try:
                server.serve_forever(poll_interval=0.3)
            except KeyboardInterrupt:
                pass
            except BrowserProcessUnavailable:
                # Deliberately fail the backend, not the Rock64 host. The
                # existing user systemd Restart=on-failure can now recreate
                # ONLY this BTDigg GUI after repeated disconnection.
                print("BTDigg local Chromium process lost; exiting for "
                      "existing user service recovery", flush=True)
                raise
            finally:
                server.server_close()
        finally:
            context.close()


if __name__ == "__main__":
    main()
