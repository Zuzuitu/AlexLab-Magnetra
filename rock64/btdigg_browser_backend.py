#!/usr/bin/env python3
"""Opt-in, loopback-only BTDigg gateway backed by a human-verified GUI browser.

A visible Chromium is controlled via Playwright's local private pipe. The owner
must verify any CAPTCHA manually through the separate Tailscale-only noVNC
session. Never solve a CAPTCHA, change browser identity, replay imported cookies,
retry upstream challenges or publish a debugging port.

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
    """

    def __init__(self, page, bootstrap_state=None):
        self._bootstrap_state = bootstrap_state
        self.page = page
        self.reference_page = page
        self._source_stopped = None
        self._last_failure_reason = None
        self._last_upstream_http_status = None

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
                "new_searches_paused": (
                    self._source_stopped is not None or visible_denial
                    or len(pages) > len(checked_pages)
                ),
                # A visible 429 body is not proof of the network HTTP status.
                "last_navigation_status": self._source_stopped,
                "last_failure_reason": self._last_failure_reason,
                "last_upstream_http_status": self._last_upstream_http_status,
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
                "new_searches_paused": True,
                "last_navigation_status": None,
                "last_failure_reason": None,
                "last_upstream_http_status": None,
                "selected_tab_index": -1,
                "tab_diagnostics": [],
            }

    def fetch(self, query):
        try:
            query_url(query)  # Validate without initiating any source request.
            existing_page, existing_html = self._verified_existing_query(query)
            if existing_html is not None:
                # A manual search in another already-open tab is safe to read;
                # it must not create another network request.
                self.page = existing_page
                return 200, existing_html

            if self._source_stopped is not None:
                # A failed query cannot trigger another upstream request.
                return self._source_stopped, b""

            # A restored browser can display BTDigg's explicit refusal even
            # when no navigation occurred in this Playwright process. Do not
            # treat a fresh local latch as permission to hit the source again.
            if any(source_rate_limit_visible(p) for p in self.page.context.pages
                   if not p.is_closed()):
                return 429, b""

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
            # Never visit BTDigg merely because Chromium started.
            # A persistent profile can restore old tabs, possibly triggering
            # browser-owned reloads that Playwright cannot guarantee to prevent.
            # Do not ADD a second, explicit startup request on top of those.
            # A brand-new profile opens a blank tab until the owner chooses
            # a source page manually in noVNC.
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
            server = HTTPServer(
                (BIND, port),
                browser_handler_class(token, provider, browser_fetcher),
            )
            print("BTDigg verified-browser gateway: loopback only; "
                  "waiting for optional manual verification", flush=True)
            try:
                server.serve_forever(poll_interval=0.3)
            except KeyboardInterrupt:
                pass
            finally:
                server.server_close()
        finally:
            context.close()


if __name__ == "__main__":
    main()
