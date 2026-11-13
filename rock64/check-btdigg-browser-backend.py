#!/usr/bin/env python3
"""Owner-triggered local-only probe of the persistent BTDigg browser gateway.

Does not log source HTML, query strings, magnet links, tokens or cookies.
Nothing is sent to Cloudflare or exposed by the host.
"""
import argparse
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request

LOCAL = "http://127.0.0.1:18896"
STATE = Path.home() / ".local" / "state" / "magnetra-btdigg-browser"
TOKEN_FILE = STATE / "gateway.token"
PREFERENCES_FILE = STATE / "profile" / "Default" / "Preferences"


def local_profile_exit_state(path=None):
    """Read only two nonsecret Chromium profile markers. No browser requests.

    Chromium can mark a profile unclean WHILE it is running, so this is not
    a verdict on whether a previous Ctrl+C was graceful. Compare only after
    an intentional clean shutdown, never write or repair Preferences here.
    """
    if path is None:
        path = PREFERENCES_FILE
    try:
        if (path.is_symlink() or path.parent.is_symlink()
                or path.parent.parent.is_symlink()
                or not path.is_file() or path.stat().st_size > 8_000_000):
            return {"profile_marker_available": False}
        data = json.loads(path.read_text(encoding="utf-8"))
        profile = data.get("profile", {})
        if not isinstance(profile, dict):
            profile = {}
        marker = profile.get("exit_type")
        if marker not in ("Normal", "Crashed", "SessionEnded"):
            marker = "unknown"
        clean = profile.get("exited_cleanly")
        if type(clean) is not bool:
            clean = None
        return {
            "profile_marker_available": True,
            "exit_type": marker,
            "exited_cleanly": clean,
            "runtime_caveat": "markers_may_indicate_current_running_browser",
        }
    except (OSError, ValueError, TypeError, UnicodeError):
        return {"profile_marker_available": False}


def main():
    parser = argparse.ArgumentParser()
    tests = parser.add_mutually_exclusive_group()
    tests.add_argument("--profile-exit-state", action="store_true",
                       help="Read Chromium exit markers locally, never contact gateway")
    tests.add_argument("--browser-status", action="store_true",
                       help="Inspect existing Chromium tabs without source requests")
    tests.add_argument("--test-search", action="store_true",
                       help="Fetch original owner-verified search once")
    tests.add_argument("--test-next-search", action="store_true",
                       help="Perform one distinct follow-up query in the same browser")
    args = parser.parse_args()
    if args.profile_exit_state:
        print(json.dumps({"local_profile": local_profile_exit_state()},
                         sort_keys=True))
        return
    search_performed = args.test_search or args.test_next_search
    try:
        if TOKEN_FILE.is_symlink() or not TOKEN_FILE.is_file():
            raise ValueError("missing private token")
        if TOKEN_FILE.stat().st_mode & 0o077:
            raise ValueError("insecure private token permissions")
        token = TOKEN_FILE.read_text().strip()
        if not re.fullmatch(r"[A-Za-z0-9_-]{48,256}", token):
            raise ValueError("invalid token")
        path = "/v1/browser-state" if args.browser_status else "/healthz"
        if search_performed:
            # Real source screenshot confirms 720p rows for this title/year.
            # This is different from Chromium's boot query and proves that
            # the browser can navigate for one user-invoked search.
            query = ("The Dog Stars 2026 720p"
                     if args.test_next_search else "The Dog Stars 2026")
            path = "/v1/search?q=" + urllib.parse.quote(query, safe="")
        req = urllib.request.Request(
            LOCAL + path,
            headers={"authorization": "Bearer " + token,
                     "accept": "text/html" if args.test_search else "application/json"},
        )
        with urllib.request.urlopen(req, timeout=14) as r:
            body = r.read(3_000_001)
            status = r.status
        result = {"local_gateway_status": status, "search_performed": search_performed}
        if args.browser_status:
            state = json.loads(body)
            required = {
                "browser_connected": bool,
                "open_tabs": int,
                "verified_tabs": int,
                "selected_tab_verified": bool,
                "new_searches_paused": bool,
            }
            if not isinstance(state, dict) or any(
                type(state.get(name)) is not kind for name, kind in required.items()
            ):
                raise ValueError("unexpected browser-state response")
            stop = state.get("last_navigation_status")
            if stop is not None and stop not in (429, 503, 504):
                raise ValueError("unexpected browser-state status")
            # A live GUI started before the visible-429 correction does not
            # hot-reload with git pull. Its /v1/browser-state response lacks
            # this field: *unknown* is not the same as source available.
            legacy = "visible_source_rate_limited" not in state
            if not legacy and type(state["visible_source_rate_limited"]) is not bool:
                raise ValueError("unexpected browser-state source flag")
            result["browser_state"] = {
                **{name: state[name] for name in required
                   if name != "new_searches_paused"},
                "visible_source_rate_limited": (
                    None if legacy else state["visible_source_rate_limited"]
                ),
                "new_searches_paused": (
                    None if legacy else state["new_searches_paused"]
                ),
                "last_navigation_status": stop,
                "diagnostic_capability": (
                    "legacy_navigation_latch_only" if legacy
                    else "visible_source_rate_limit_detection"
                ),
            }
            if legacy:
                result["browser_state"]["in_process_navigation_latch"] = (
                    state["new_searches_paused"]
                )
            # New browser versions disclose only fixed, secret-free reason codes.
            reasons = {
                "no_navigation_response", "upstream_http_429",
                "upstream_http_non200", "unexpected_final_query",
                "unverified_result_html", "browser_navigation_exception",
            }
            if "last_failure_reason" in state:
                reason = state["last_failure_reason"]
                if reason is not None and reason not in reasons:
                    raise ValueError("unexpected failure reason")
                http_status = state.get("last_upstream_http_status")
                if http_status is not None and (
                    type(http_status) is not int
                    or not 100 <= http_status <= 599
                ):
                    raise ValueError("unexpected HTTP status")
                result["browser_state"]["last_failure_reason"] = reason
                result["browser_state"]["last_upstream_http_status"] = http_status
        if search_performed:
            result.update({
                "source_html_bounded": 0 < len(body) <= 3_000_000,
                "source_result_marker": b"one_result" in body.lower(),
                "source_magnet_marker": b"magnet:?xt=urn:btih:" in body.lower(),
            })
        print(json.dumps(result, sort_keys=True))
    except urllib.error.HTTPError as e:
        print(json.dumps({
            "local_gateway_status": e.code,
            "search_performed": search_performed,
            "verified_results": False,
        }, sort_keys=True))
    except (OSError, ValueError, urllib.error.URLError):
        print(json.dumps({"local_gateway_status": "unavailable",
                          "search_performed": False}, sort_keys=True))


if __name__ == "__main__":
    main()
