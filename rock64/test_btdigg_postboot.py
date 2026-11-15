#!/usr/bin/env python3
"""Offline, source-free tests for the single-command post-boot readiness audit."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parent / "check-btdigg-postboot.py"
spec = importlib.util.spec_from_file_location("postboot", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

SOCKETS = (
    "LISTEN 0 128 127.0.0.1:8796 0.0.0.0:*\n"
    "LISTEN 0 128 127.0.0.1:18896 0.0.0.0:*\n"
    "LISTEN 0 128 100.79.134.61:6088 0.0.0.0:*\n"
)


def browser():
    return {
        "local_gateway_status": 200,
        "search_performed": False,
        "browser_state": {
            "browser_connected": True,
            "selected_tab_verified": True,
            "verified_tabs": 1,
            "new_searches_paused": False,
            "selected_tab_index": 0,
            "tab_diagnostics": [
                {"page_kind": "canonical_search", "validation": "valid",
                 "paired_rows": 10}
            ],
        },
    }


def good(**changes):
    kwargs = {"enabled": True, "linger": True, "unit_active": True,
              "tmux_state": "absent", "ss_output": SOCKETS,
              "browser": browser()}
    kwargs.update(changes)
    return audit.evaluate(**kwargs)


class PostbootAuditTests(unittest.TestCase):
    def test_real_success_is_only_local_readonly_not_new_pwa_query(self):
        result = good()
        self.assertEqual(result["failed_checks"], [])
        self.assertEqual(result["status"],
                         "LOCAL_READONLY_PASS_REQUIRES_NEW_PWA_SEARCH")
        self.assertFalse(result["source_search_performed"])
        self.assertFalse(result["new_pwa_search_verified"])

    def test_existing_tmux_or_disabled_unit_cannot_pass(self):
        for kwargs in ({"tmux_state": "active"},
                       {"tmux_state": "unknown"},
                       {"unit_active": False},
                       {"enabled": False},
                       {"linger": False}):
            with self.subTest(kwargs=kwargs):
                self.assertEqual(good(**kwargs)["status"], "NOT_VERIFIED")

    def test_public_private_port_or_missing_tailnet_is_failure(self):
        for changed in (
            SOCKETS + "LISTEN 0 128 0.0.0.0:18896 0.0.0.0:*\n",
            SOCKETS.replace("100.79.134.61:6088", "0.0.0.0:6088"),
            SOCKETS.replace("127.0.0.1:8796", "0.0.0.0:8796"),
            None,
        ):
            with self.subTest(sockets=changed):
                self.assertEqual(good(ss_output=changed)["status"],
                                 "NOT_VERIFIED")

    def test_health200_without_canonical_verified_html_fails(self):
        for field, value in (("selected_tab_verified", False),
                             ("new_searches_paused", True),
                             ("verified_tabs", 0),
                             ("tab_diagnostics", [])):
            broken = browser()
            broken["browser_state"][field] = value
            self.assertEqual(good(browser=broken)["status"], "NOT_VERIFIED")

    def test_browser_state_fails_when_new_search_occurred(self):
        broken = browser()
        broken["search_performed"] = True
        self.assertEqual(good(browser=broken)["status"], "NOT_VERIFIED")

    def test_untrusted_fields_never_get_reflected(self):
        b = browser()
        b["query"] = "Sensitive filename"
        b["magnet"] = "magnet:?xt=urn:btih:SHOULD_NOT_PRINT"
        report = str(good(browser=b))
        self.assertNotIn("Sensitive filename", report)
        self.assertNotIn("magnet:?", report)

    def test_missing_status_or_unparsed_browser_response_fails(self):
        for candidate in ({}, {"local_gateway_status": 200}, None):
            self.assertEqual(good(browser=candidate)["status"],
                             "NOT_VERIFIED")


if __name__ == "__main__":
    unittest.main()
