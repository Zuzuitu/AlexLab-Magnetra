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


class VisibleBrowserFetcher:
    """Runs exclusively on the HTTP server's one main Playwright thread."""

    def __init__(self, page):
        self.page = page

    def fetch(self, query):
        try:
            target = query_url(query)
            # With a fresh profile the owner has to complete verification.
            # Never navigate again automatically when a CAPTCHA is currently
            # displayed: one source challenge must not trigger a retry loop.
            current = self.page.url
            if not validated_result_html(self.page):
                return 503, b""
            # + vs %20 are equivalent URL encodings for the SAME query;
            # do not trigger an unnecessary second browser navigation.
            if source_query(current) != query.strip():
                result = self.page.goto(
                    target, wait_until="domcontentloaded", timeout=10000)
                if result is None:
                    return 503, b""
                if result.status == 429:
                    return 429, b""
                if result.status != 200:
                    return 503, b""
                self.page.wait_for_timeout(900)
            html = validated_result_html(self.page)
            if source_query(self.page.url) != query.strip() or html is None:
                return 503, b""
            return 200, html
        except (ValueError, TypeError):
            return 400, b""
        except Exception:
            # No raw Playwright exceptions: they may contain query/URL/site data.
            return 504, b""


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
            page = context.pages[0] if context.pages else context.new_page()
            # Single bootstrap navigation to show any CAPTCHA visually.
            # No automatic verification, polling, or retry loops.
            if not source_landing(page.url):
                try:
                    page.goto(query_url("The Dog Stars 2026"),
                              wait_until="domcontentloaded", timeout=10000)
                except Exception:
                    pass
            provider = SearchProvider(fetcher=VisibleBrowserFetcher(page).fetch)
            # HTTPServer (NOT ThreadingHTTPServer): Playwright sync page remains
            # owned by the same thread for every subsequent search.
            server = HTTPServer((BIND, port), handler_class(token, provider))
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
