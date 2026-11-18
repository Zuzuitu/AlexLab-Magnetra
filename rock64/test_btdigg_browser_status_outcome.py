#!/usr/bin/env python3
"""Offline: sanitized BTDigg private Chromium diagnostic outcome contracts."""
from pathlib import Path
import runpy
import unittest

CHECKER = Path(__file__).with_name("check-btdigg-browser-backend.py")


class BrowserStatusOutcomeTests(unittest.TestCase):
    def setUp(self):
        # Store as an instance attribute so Python does not bind self.
        helpers = runpy.run_path(str(CHECKER))
        self.check = helpers["valid_recovery_outcome"]
        self.checkbox = helpers["valid_checkbox_outcome"]

    def test_only_fixed_checkbox_diagnostic_codes_are_exposed(self):
        for value in ("not_attempted", "unsafe_context", "image_challenge",
                      "checkbox_not_visible", "invalid_document",
                      "already_attempted", "click_started",
                      "verified_after_click", "verified_other_query",
                      "clicked_not_verified", "click_failed",
                      "inspection_failed"):
            self.assertTrue(self.checkbox(value))
        for value in (None, 0, 428, False, [], {}, "",
                      "https://www.google.com/recaptcha/api2/anchor?k=secret",
                      "magnet:?xt=urn:btih:" + "a" * 40):
            self.assertFalse(self.checkbox(value))

    def test_checkbox_success_is_safe_diagnostic(self):
        self.assertTrue(self.check("verified_after_checkbox"))
        self.assertTrue(self.check("verified_results"))
        self.assertTrue(self.check("captcha_required"))
        self.assertTrue(self.check(None))

    def test_arbitrary_or_sensitive_values_never_escape(self):
        for value in ("unexpected-success", "magnet:?xt=urn:btih:" + "a" * 40,
                      "https://other.example/search?q=secret", "", 428,
                      {}, [], False):
            with self.subTest(value_type=type(value).__name__):
                self.assertFalse(self.check(value))


if __name__ == "__main__":
    unittest.main()
