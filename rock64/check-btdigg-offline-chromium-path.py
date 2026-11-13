#!/usr/bin/env python3
"""Opt-in offline Chromium -> private HTTP gateway integration contract.

Uses a fresh temporary Chromium profile and Playwright route fulfillment. The
BTDigg-shaped pages here are synthetic TEST FIXTURES, never genuine search
evidence. Every page request is fulfilled/aborted locally: no BTDigg request,
CAPTCHA bypass, real magnet use, production tunnel, or existing GUI mutation.
This script starts a separate headless browser ONLY when explicitly invoked.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from http.client import HTTPConnection
from http.server import HTTPServer
import json
import os
from pathlib import Path
import tempfile
from urllib.parse import quote

from rock64.btdigg_browser_backend import (
    VisibleBrowserFetcher, browser_handler_class, query_url,
    validated_result_html,
)
from rock64.btdigg_gateway import (
    MIN_SEARCH_INTERVAL, SOURCE_REFUSAL_COOLDOWN_SECONDS, SearchProvider,
)

CHROMIUM = Path("/usr/bin/chromium")
EXACT = "The.Dog.Stars.2026.1080p.10bit.WEBRip.6CH.x265.HEVC-PSA"
DENIED = "The Dog Stars 2026 720p"
UNSEEN = "Different release 2026"
# Fake hashes are intentionally fixed, structurally valid placeholders, never
# taken from a live torrent, screenshot, user search, or other provider.
FAKE_HASH = "a" * 40
TEST_TOKEN = "t" * 64

# Minimal HTML with real production CSS shape, but explicitly synthetic data.
FIXTURE_HTML = (
    '<!doctype html><html><head><title>BTDigg local offline fixture</title>'
    '</head><body><div class="one_result"><div class="result">'
    '<div class="torrent_name"><a href="/torrent/local-fixture">'
    + EXACT +
    '</a></div><div class="torrent_magnet"><div class="fa-magnet">'
    '<a href="magnet:?xt=urn:btih:' + FAKE_HASH +
    '">Fixture Magnet</a></div></div>'
    '<span class="torrent_size">1.4 GB</span>'
    '</div></div></body></html>'
)


def one_local_http_request(server, path, bearer=TEST_TOKEN):
    """Run HTTPServer on Playwright's owning thread, never in a worker thread.

    A single background HTTP client supplies the connection. The server
    handler, including synchronous Playwright access, remains on the thread
    that created the Chromium context.
    """
    def client():
        conn = HTTPConnection("127.0.0.1", server.server_port, timeout=8)
        try:
            conn.request("GET", path,
                         headers={"Authorization": "Bearer " + bearer})
            response = conn.getresponse()
            return (response.status, response.read(3_000_001),
                    response.getheader("retry-after"),
                    response.getheader("x-magnetra-btdigg-429-scope"))
        finally:
            conn.close()

    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(client)
        server.handle_request()
        return future.result(timeout=10)


def verify():
    if os.geteuid() == 0:
        raise RuntimeError("Refuse root: launch as the unprivileged Rock64 runner")
    if not CHROMIUM.is_file():
        raise RuntimeError("Debian /usr/bin/chromium is missing")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as error:
        raise RuntimeError("Use the isolated magnetra-browser Playwright venv") from error

    fulfilled = []
    blocked = [0]
    now = [100.0]
    exact_url = query_url(EXACT)
    denied_url = query_url(DENIED)

    def fulfill_fixture(route):
        url = route.request.url
        if url == exact_url:
            fulfilled.append("fixture-200")
            route.fulfill(status=200, body=FIXTURE_HTML,
                          content_type="text/html; charset=utf-8")
        elif url == denied_url:
            fulfilled.append("fixture-429")
            route.fulfill(status=429, body="Too Many Requests",
                          content_type="text/plain")
        else:
            blocked[0] += 1
            route.abort("blockedbyclient")

    with tempfile.TemporaryDirectory(prefix="magnetra-btdigg-offline-") as profile:
        with sync_playwright() as playwright:
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=profile, executable_path=str(CHROMIUM),
                headless=True, chromium_sandbox=True,
                accept_downloads=False, service_workers="block",
                args=["--no-first-run", "--no-default-browser-check",
                      "--disable-background-networking",
                      "--disable-extensions"],
                timeout=15000,
            )
            try:
                # Route ALL page requests. Only the two synthetic fixture
                # responses are fulfilled; everything else is aborted.
                context.route("**/*", fulfill_fixture)
                page = context.pages[0] if context.pages else context.new_page()
                response = page.goto(exact_url, wait_until="domcontentloaded",
                                     timeout=8000)
                assert response is not None and response.status == 200
                assert len(fulfilled) == 1
                assert page.locator("div.one_result > div").count() == 1
                assert page.locator("div.one_result > div div.torrent_name > a").inner_text() == EXACT
                assert page.locator(
                    'div.one_result > div div.torrent_magnet > div.fa-magnet > a'
                ).get_attribute("href") == "magnet:?xt=urn:btih:" + FAKE_HASH
                assert validated_result_html(page) == FIXTURE_HTML.encode()

                browser = VisibleBrowserFetcher(page)
                provider = SearchProvider(fetcher=browser.fetch,
                                          clock=lambda: now[0])
                server = HTTPServer(
                    ("127.0.0.1", 0),
                    browser_handler_class(TEST_TOKEN, provider, browser),
                )
                server.timeout = 6
                try:
                    # Authentication: no source access or test HTML without a
                    # bearer token, even on a private loopback test port.
                    denied_auth = one_local_http_request(
                        server, "/v1/search?q=" + quote(EXACT), "wrong")
                    assert denied_auth[0] == 401
                    status = one_local_http_request(server, "/v1/browser-state")
                    assert status[0] == 200
                    state = json.loads(status[1])
                    assert state["verified_tabs"] == 1
                    assert state["selected_tab_verified"] is True
                    assert status[2] is None
                    assert "magnet:" not in status[1].decode()

                    # Reuse owner-verified DOM, not another source navigation.
                    exact_path = "/v1/search?q=" + quote(EXACT, safe="")
                    success = one_local_http_request(server, exact_path)
                    assert success[0] == 200
                    assert success[1] == FIXTURE_HTML.encode()
                    assert len(fulfilled) == 1
                    cached = one_local_http_request(server, exact_path)
                    assert cached[0] == 200 and cached[1] == success[1]
                    assert len(fulfilled) == 1

                    # A different explicit request is routed to a synthetic
                    # refusal. Its browser tab closes; old results survive.
                    now[0] += MIN_SEARCH_INTERVAL + 1
                    denied_path = "/v1/search?q=" + quote(DENIED, safe="")
                    refusal = one_local_http_request(server, denied_path)
                    assert refusal[0] == 429
                    assert refusal[2] == str(SOURCE_REFUSAL_COOLDOWN_SECONDS)
                    assert refusal[3] == "source"
                    assert fulfilled == ["fixture-200", "fixture-429"]

                    # No third page navigation during the actual source latch.
                    now[0] += MIN_SEARCH_INTERVAL + 1
                    third = one_local_http_request(
                        server, "/v1/search?q=" + quote(UNSEEN, safe=""))
                    assert third[0] == 429
                    assert fulfilled == ["fixture-200", "fixture-429"]
                    still = one_local_http_request(server, exact_path)
                    assert still[0] == 200 and still[1] == success[1]
                    after = one_local_http_request(server, "/v1/browser-state")
                    assert after[0] == 200
                    end_state = json.loads(after[1])
                    assert end_state["last_navigation_status"] == 429
                    assert end_state["new_searches_paused"] is True
                    assert end_state["verified_tabs"] == 1
                finally:
                    server.server_close()
            finally:
                context.close()

    return {
        "result": "PASS",
        "proof": "synthetic_fixture_not_source_availability",
        "chromium": "isolated_temporary_headless_profile",
        "requests_to_btdigg_origin": 0,
        "fixture_responses": len(fulfilled),
        "blocked_nonfixture_page_requests": blocked[0],
        "auth_required": True,
        "exact_release_reused_without_navigation": True,
        "source_429_blocks_new_queries": True,
        "original_positive_cache_survives": True,
        "tmux_session_touched": False,
    }


def main():
    try:
        summary = verify()
    except Exception as error:
        # Deliberately do not print raw URL, HTML, token, user profile paths,
        # Playwright exception text, search terms or magnet values.
        print(json.dumps({"result": "FAIL",
                          "category": type(error).__name__,
                          "requests_to_btdigg_origin": 0}, sort_keys=True))
        raise SystemExit(1) from None
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
