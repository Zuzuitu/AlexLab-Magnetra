#!/usr/bin/env python3
"""Offline: sanitized BTDigg private Chromium diagnostic outcome contracts."""
from pathlib import Path
import runpy
import unittest

CHECKER = Path(__file__).with_name("check-btdigg-browser-backend.py")


class BrowserStatusOutcomeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.check = runpy.run_path(str(CHECKER))["valid_recovery_outcome"]

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
