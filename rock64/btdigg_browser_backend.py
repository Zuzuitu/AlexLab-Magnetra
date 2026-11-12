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
else:
    from btdigg_gateway import BIND, PORT, SIZE_LIMIT, SearchProvider, handler_class

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


def validated_result_html(page):
    """Return only genuine source-owned result HTML; otherwise no bytes.

    No cookies, challenge tokens, JS globals, or scraped results are logged.
    A missing row is NOT a confirmed zero-match search.
    """
    if not source_landing(page.url):
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


def source_rate_limit_visible(page):
    """Observe an explicit BTDigg denial in an ALREADY loaded page only.

    A body containing exactly the short source refusal is rate limited.
    A release title containing these words is NOT a refusal. No navigation,
    network requests, cookies or page text are logged or returned.
    """
    try:
        if page.is_closed() or not source_landing(page.url):
            return False
        text = page.locator("body").inner_text(timeout=1500)
        if not isinstance(text, str) or len(text) > 160:
            return False
        compact = " ".join(text.casefold().split())
        return compact in ("too many requests", "429 too many requests")
    except Exception:
        return False


class VisibleBrowserFetcher:
    """One-thread Playwright gateway; preserve verified tabs on source refusal.

    A different query opens one tab in the SAME browser context, with the same
    network identity. This does not circumvent challenges or rate limiting.
    One source refusal stops new navigations for this foreground process.
    """

    def __init__(self, page):
        self.page = page
        self.reference_page = page
        self._source_stopped = None

    def _verified_existing_query(self, query):
        """Reuse owner-opened verified tabs without network navigation.

        Never trust a tab solely because its URL contains the query: the
        source-owned canonical URL and paired result/magnet HTML are required.
        """
        pages = [self.page]
        pages.extend(p for p in self.page.context.pages if p is not self.page)
        for page in pages:
            if (not page.is_closed()
                    and same_search_query(source_query(page.url), query)):
                html = validated_result_html(page)
                if html is not None:
                    return page, html
        return None, None

    def browser_state(self):
        """Authenticated, read-only state of existing DOM; no source requests."""
        try:
            pages = [p for p in self.page.context.pages if not p.is_closed()]
            verified = sum(validated_result_html(p) is not None for p in pages)
            visible_denial = any(source_rate_limit_visible(p) for p in pages)
            return {
                "browser_connected": bool(pages),
                "open_tabs": len(pages),
                "verified_tabs": verified,
                "selected_tab_verified": (
                    not self.page.is_closed()
                    and validated_result_html(self.page) is not None
                ),
                "visible_source_rate_limited": visible_denial,
                "new_searches_paused": (
                    self._source_stopped is not None or visible_denial
                ),
                # A visible 429 body is not proof of the network HTTP status.
                "last_navigation_status": self._source_stopped,
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
            }

    def fetch(self, query):
        try:
            target = query_url(query)
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

            candidate = None
            accepted = False
            try:
                # Exactly one owner-triggered navigation in the original context.
                candidate = self.page.context.new_page()
                response = candidate.goto(
                    target, wait_until="domcontentloaded", timeout=10000)
                if response is None:
                    self._source_stopped = 503
                    return 503, b""
                if response.status == 429:
                    self._source_stopped = 429
                    return 429, b""
                if response.status != 200:
                    self._source_stopped = 503
                    return 503, b""

                candidate.wait_for_timeout(900)
                html = validated_result_html(candidate)
                if (not same_search_query(source_query(candidate.url), query)
                        or html is None):
                    self._source_stopped = 503
                    return 503, b""

                old = self.page
                self.page = candidate
                accepted = True
                # Keep the initial owner-verified tab plus one latest success.
                if old is not self.reference_page:
                    try:
                        old.close()
                    except Exception:
                        pass
                return 200, html
            except Exception:
                # Do not emit query, URLs, source HTML or Playwright exceptions.
                self._source_stopped = 504
                return 504, b""
            finally:
                if candidate is not None and not accepted:
                    try:
                        candidate.close()
                    except Exception:
                        pass
        except (ValueError, TypeError):
            return 400, b""
        except Exception:
            return 504, b""


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
            browser_fetcher = VisibleBrowserFetcher(page)
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
