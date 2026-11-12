#!/usr/bin/env python3
"""Offline-by-default browser capability pilot for ONLY BTDigg and ThePirateBay.

This is NOT a gateway, a scraper, or a production search backend. One explicit
owner invocation navigates one approved search page in an isolated Chromium
context and reports only bounded status/DOM counts. No background scheduling,
login/session import, challenge solving, stealth, retries, proxy or IP rotation.

Rock64 prerequisites (not installed by this script): Debian's Chromium ARM64
and Python Playwright. Never run as root. Does not affect existing services.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from urllib.parse import urlencode, urlsplit

SOURCE_ORIGINS = {
    "btdigg": "https://btdig.com",
    "thepiratebay": "https://thepiratebay.org",
}
ALLOWED_SUBRESOURCE_ORIGINS = {
    "btdigg": frozenset({"https://btdig.com"}),
    "thepiratebay": frozenset({"https://thepiratebay.org", "https://apibay.org"}),
}
TPB_CATEGORIES = {
    "all": 0, "apps": 300, "books": 601, "games": 400, "movies": 200,
    "series": 200, "music": 101, "porn": 500, "other": 600,
}
MAX_QUERY_CHARS = 180
PAGE_TIMEOUT_MS = 15000
SETTLE_MS = 1500
VERIFICATION_SETTLE_MS = 5000
MAX_DOM_ROWS = 100
CHALLENGE_TITLES = ("just a moment", "checking your browser", "attention required")


class PilotStop(Exception):
    """A safe, fixed reason; never include URLs, queries or exception text."""


def validate_query(value):
    if not isinstance(value, str):
        raise PilotStop("invalid_query")
    trimmed = value.strip()
    if not 2 <= len(trimmed) <= MAX_QUERY_CHARS:
        raise PilotStop("invalid_query")
    if re.search(r"[\x00-\x1f\x7f]", trimmed):
        raise PilotStop("invalid_query")
    return trimmed


def search_target(provider, query, category="all"):
    query = validate_query(query)
    if provider not in SOURCE_ORIGINS:
        raise PilotStop("unsupported_provider")
    if provider == "btdigg":
        if category not in TPB_CATEGORIES:
            raise PilotStop("invalid_category")
        return "https://btdig.com/search?" + urlencode({"order": 0, "q": query})
    if category not in TPB_CATEGORIES:
        raise PilotStop("invalid_category")
    return "https://thepiratebay.org/search.php?" + urlencode({
        "q": query, "cat": TPB_CATEGORIES[category],
    })


def allowed_resource(provider, url):
    if provider not in ALLOWED_SUBRESOURCE_ORIGINS:
        return False
    try:
        parsed = urlsplit(url)
        return (parsed.scheme == "https" and not parsed.username
                and not parsed.password and parsed.port in (None, 443)
                and f"{parsed.scheme}://{parsed.hostname}"
                    in ALLOWED_SUBRESOURCE_ORIGINS[provider])
    except (TypeError, ValueError):
        return False


def approved_google_recaptcha_resource(provider, url):
    """ONLY standard Google reCAPTCHA assets; not a proxy or challenge bypass.

    Never add arbitrary third-party origins. No redirects, challenge solving,
    cookies, sitekey or target URL exposure to any Magnetra endpoint.
    """
    if provider != "btdigg":
        return False
    try:
        parsed = urlsplit(url)
        if (parsed.scheme != "https" or parsed.username or parsed.password
                or parsed.port not in (None, 443)):
            return False
        return (parsed.hostname in {
            "www.google.com", "www.gstatic.com", "recaptcha.google.com"
        } and parsed.path.startswith("/recaptcha/"))
    except (TypeError, ValueError):
        return False


def approved_landing(provider, current_url):
    if not allowed_resource(provider, current_url):
        return False
    url = urlsplit(current_url)
    return (url.scheme + "://" + url.hostname == SOURCE_ORIGINS[provider]
            and url.path == ("/search" if provider == "btdigg" else "/search.php"))


def classify_page(provider, *, status, landing, title, rows, magnets,
                  tpb_api_status=None, verified_rows=None):
    """Pure, fixture-testable categorization; never treats absence as proof of no matches."""
    if not approved_landing(provider, landing):
        return "redirect_or_origin_refused"
    if status == 429 or tpb_api_status == 429:
        return "source_http_429"
    if status in (401, 403) or tpb_api_status in (401, 403):
        return "source_access_denied"
    if status != 200:
        return "source_non_200"
    if any(s in str(title).lower() for s in CHALLENGE_TITLES):
        return "challenge_not_solved"
    if provider == "btdigg" and (
        verified_rows > 0 if verified_rows is not None else rows > 0 and magnets > 0
    ):
        return "rendered_rows"
    if magnets > 0 and provider == "thepiratebay":
        return "rendered_rows"
    # A 200 homepage/script shell can lack results even when the API was blocked
    # or when JS changed; never report this as a genuine empty search.
    return "no_rows_unverified"


def classify_blocked_script(url):
    """Coarse categories only, never emit an external path, host or URL."""
    try:
        parsed = urlsplit(url)
        host = (parsed.hostname or "").lower()
        path = parsed.path.lower()
        if (host in {"www.google.com", "www.gstatic.com",
                     "recaptcha.google.com"}
                and ("recaptcha" in path or host == "recaptcha.google.com")):
            return "verification"
        if host in {"cdnjs.cloudflare.com", "cdn.jsdelivr.net",
                    "unpkg.com", "code.jquery.com"}:
            return "static_cdn"
    except (TypeError, ValueError):
        pass
    return "other"


def classify_document_markup(markup, content_type=None):
    """Read-only metadata from response body; never persist or output markup."""
    if not isinstance(markup, str):
        return {
            "response_html_chars": None,
            "response_markup_result_marker": None,
            "response_search_form_marker": None,
            "response_verification_marker": None,
            "response_is_html": None,
            "response_recaptcha_script_marker": None,
            "response_recaptcha_widget_marker": None,
            "response_recaptcha_invisible_marker": None,
        }
    lower = markup[:3_000_000].lower()
    return {
        "response_html_chars": min(len(markup), 3_000_000),
        "response_markup_result_marker": bool(re.search(
            r"""\bclass\s*=\s*['"][^'"]*\bone_result\b""", lower)),
        "response_search_form_marker": (
            'name="q"' in lower or "name='q'" in lower
        ),
        # Hints only, not proof of reCAPTCHA version or solved challenge.
        "response_recaptcha_script_marker": (
            "/recaptcha/" in lower
        ),
        "response_recaptcha_widget_marker": (
            "g-recaptcha" in lower or "data-sitekey" in lower
        ),
        "response_recaptcha_invisible_marker": (
            "grecaptcha.execute" in lower or
            "api.js?render=" in lower
        ),
        "response_verification_marker": any(x in lower for x in (
            "cf-mitigated", "just a moment", "checking your browser",
            "verify you are human", "recaptcha", "captcha"
        )),
        "response_is_html": ("text/html" in str(content_type).lower())
            if content_type is not None else None,
    }


def _no_proxy_environment():
    return not any(value for name, value in os.environ.items()
                   if name.upper() in {"HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"})


def owner_probe(provider, query, category="all", *, chromium_path=None,
                playwright_manager=None, allow_recaptcha_assets=False):
    """At most one top-level navigation; subresources restricted to fixed origins."""
    target = search_target(provider, query, category)
    if allow_recaptcha_assets and provider != "btdigg":
        raise PilotStop("verification_assets_only_for_btdigg")
    if os.geteuid() == 0:
        raise PilotStop("must_run_unprivileged")
    if not _no_proxy_environment():
        raise PilotStop("environment_proxy_refused")
    executable = chromium_path or shutil.which("chromium")
    if not executable or not os.path.isabs(executable):
        raise PilotStop("chromium_not_installed")
    if not os.path.isfile(executable) or not os.access(executable, os.X_OK):
        raise PilotStop("chromium_not_executable")
    if playwright_manager is None:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise PilotStop("playwright_not_installed") from exc
        playwright_manager = sync_playwright

    try:
        with playwright_manager() as p:
            # Chromium sandbox stays enabled; fail closed instead of asking
            # for --no-sandbox, imported sessions, stealth or fingerprint hacks.
            browser = p.chromium.launch(
                executable_path=executable, headless=True,
                chromium_sandbox=True,
                args=["--disable-background-networking", "--disable-extensions"],
                timeout=10000,
            )
            try:
                context = browser.new_context(
                    accept_downloads=False, service_workers="block",
                    java_script_enabled=True,
                )
                try:
                    page = context.new_page()
                    blocked_resources = {"total": 0, "scripts": 0}
                    allowed_verification = {"requests": 0, "ok": 0,
                                            "blocked": 0}
                    script_categories = {"verification": 0,
                                         "static_cdn": 0, "other": 0}
                    def route_handler(route):
                        if allowed_resource(provider, route.request.url):
                            route.continue_()
                        elif (allow_recaptcha_assets
                              and approved_google_recaptcha_resource(
                                  provider, route.request.url)):
                            allowed_verification["requests"] = min(
                                100, allowed_verification["requests"] + 1
                            )
                            route.continue_()
                        else:
                            blocked_resources["total"] = min(
                                100, blocked_resources["total"] + 1
                            )
                            if getattr(route.request, "resource_type", None) == "script":
                                blocked_resources["scripts"] = min(
                                    100, blocked_resources["scripts"] + 1
                                )
                                category = classify_blocked_script(
                                    route.request.url
                                )
                                script_categories[category] = min(
                                    100, script_categories[category] + 1
                                )
                            route.abort()
                    page.route("**/*", route_handler)
                    api_statuses = []
                    def record_response(response):
                        if (allow_recaptcha_assets
                            and approved_google_recaptcha_resource(
                                provider, response.url)):
                            status = response.status
                            if 200 <= status <= 299:
                                allowed_verification["ok"] = min(
                                    100, allowed_verification["ok"] + 1
                                )
                            elif status in (401, 403, 429):
                                allowed_verification["blocked"] = min(
                                    100, allowed_verification["blocked"] + 1
                                )
                        if (provider == "thepiratebay"
                            and allowed_resource("thepiratebay", response.url)
                            and urlsplit(response.url).hostname == "apibay.org"):
                            api_statuses.append(response.status)
                    page.on("response", record_response)
                    result = page.goto(
                        target, wait_until="domcontentloaded",
                        timeout=PAGE_TIMEOUT_MS,
                    )
                    if result is None:
                        raise PilotStop("navigation_no_response")
                    # Short bounded visual settle, NOT a request retry/poll loop.
                    page.wait_for_timeout(
                        VERIFICATION_SETTLE_MS if allow_recaptcha_assets
                        else SETTLE_MS
                    )
                    status = result.status
                    # The original navigation response body is ALREADY loaded.
                    # Read it locally without any additional BTDigg request.
                    # Never print source HTML, query, cookie, magnets or URLs.
                    markup = None
                    try:
                        read_text = getattr(result, "text", None)
                        if callable(read_text):
                            markup = read_text()
                    except Exception:
                        pass
                    content_type = None
                    try:
                        content_type = getattr(result, "headers", {}).get(
                            "content-type"
                        )
                    except Exception:
                        pass
                    response_features = classify_document_markup(
                        markup, content_type
                    )
                    # These are independent RAW DOM counts, not inferred matches.
                    # Never mask them to zero merely because strict validation fails.
                    rows = min(MAX_DOM_ROWS, page.locator(".one_result").count())
                    name_links = min(MAX_DOM_ROWS, page.locator(
                        "div.one_result div.torrent_name a").count())
                    magnet_candidates = min(MAX_DOM_ROWS, page.locator(
                        'a[href^="magnet:?"]').count())
                    magnets = min(MAX_DOM_ROWS, page.locator(
                        'a[href^="magnet:?xt=urn:btih:"]').count())
                    verified_rows = min(MAX_DOM_ROWS, page.locator(
                        'div.one_result:has(div.torrent_name a):has(a[href^="magnet:?xt=urn:btih:"])'
                    ).count()) if provider == "btdigg" else 0
                    final_url = page.url
                    classification = classify_page(
                        provider, status=status, landing=final_url,
                        title=page.title(), rows=rows, magnets=magnets,
                        tpb_api_status=429 if 429 in api_statuses
                          else (403 if 403 in api_statuses else None),
                        verified_rows=verified_rows if provider == "btdigg" else None,
                    )
                    structure = (
                        "paired_result_rows" if verified_rows else
                        "rows_without_btih_magnets" if rows and not magnets else
                        "unpaired_result_elements" if rows and magnets else
                        "magnet_without_result_rows" if magnets else
                        "no_result_selectors"
                    )
                    return {
                        "provider": provider,
                        "mode": "isolated_chromium",
                        "state": classification,
                        "navigation_status": status,
                        "tpb_api_status": 429 if 429 in api_statuses
                          else (403 if 403 in api_statuses else None),
                        "rendered_rows": verified_rows if provider == "btdigg"
                            else rows,
                        "magnet_links": magnets,
                        "raw_dom_result_blocks": rows,
                        "raw_dom_name_links": name_links,
                        "raw_dom_magnet_candidates": magnet_candidates,
                        "verified_dom_result_pairs": verified_rows,
                        "result_structure": structure,
                        "blocked_external_resources": blocked_resources["total"],
                        "blocked_external_scripts": blocked_resources["scripts"],
                        "blocked_script_categories": script_categories,
                        "recaptcha_assets_mode": ("official_google_only"
                            if allow_recaptcha_assets else "blocked"),
                        "recaptcha_subresources": allowed_verification,
                        **response_features,
                        "search_results_extracted": False,
                        "production_changed": False,
                    }
                finally:
                    context.close()
            finally:
                browser.close()
    except PilotStop:
        raise
    except Exception as exc:
        # Never print Playwright errors: they may contain URL/query, cookies or IP.
        raise PilotStop("browser_navigation_failed") from exc


def main(argv=None):
    parser = argparse.ArgumentParser(description=
        "Read-only, one-request Chromium browser capability pilot for BTDigg or TPB")
    parser.add_argument("--provider", choices=tuple(SOURCE_ORIGINS), required=True)
    parser.add_argument("--category", choices=tuple(TPB_CATEGORIES), default="all")
    parser.add_argument("--allow-recaptcha-assets", action="store_true",
        help="Opt in to loading ONLY Google's standard reCAPTCHA resources on BTDigg; no challenge solving")
    args = parser.parse_args(argv)
    try:
        if sys.stdin.isatty():
            print("Introduce o cautare de test (nu este afisata in jurnal):", file=sys.stderr)
        query = sys.stdin.readline(MAX_QUERY_CHARS + 2).rstrip("\r\n")
        report = owner_probe(args.provider, query, args.category,
                             allow_recaptcha_assets=args.allow_recaptcha_assets)
    except PilotStop as exc:
        print(json.dumps({"provider": args.provider, "mode": "isolated_chromium",
                          "state": str(exc), "production_changed": False}))
        return 1
    print(json.dumps(report,sort_keys=True))
    return 0 if report["state"] == "rendered_rows" else 2


if __name__ == "__main__":
    raise SystemExit(main())
