"""Pure offline privacy-safe URL shape diagnostic tests, no network."""
import unittest
from unittest.mock import patch

import diagnose_therarbag_iphone_linkshape_20261024 as d


class AuditTests(unittest.TestCase):
    def test_only_exact_normalized_url_shape_accepts_json(self):
        base = "https://therarbg.com/post-detail/95bf8b/source-owned/"
        self.assertEqual(d.source_shape(base), "JSON_URL_ACCEPTABLE")
        self.assertEqual(d.source_shape(base + "?source=listing"), "QUERY_PRESENT")
        self.assertEqual(d.source_shape(base.replace("95bf8b", "xx yy")), "ID_PATTERN_REJECTED")
        self.assertEqual(d.source_shape(base.replace("therarbg.com", "evil.invalid")), "INVALID_HTTPS_HOST")
        self.assertEqual(d.source_shape(base + "x" * 500), "SLUG_TOO_LONG")
        self.assertEqual(d.source_shape("https://therarbg.com/post-detail/one"), "PATH_SEGMENTS_DIFFER")

    def test_user_fingerprint_match_and_sanitized_summary(self):
        url = "https://therarbg.com/post-detail/95bf8b/source-owned/?source=listing"
        with patch.object(d, "FINGERPRINT", d.fingerprint(url)), \
             patch("builtins.print") as printed:
            found = d.inspect({"results": [{
                "provider": "therarbag", "details": url,
                "name": "private title", "magnet": None,
                "info_hash": "f"*40}], "errors": []}, 1)
        self.assertTrue(found)
        content = " ".join(" ".join(str(x) for x in call.args)
                           for call in printed.call_args_list)
        self.assertIn("QUERY_PRESENT", content)
        self.assertIn("IPHONE_FINGERPRINT_MATCH: YES", content)
        self.assertNotIn("private title", content)
        self.assertNotIn(url, content)
        self.assertNotIn("f"*40, content)

    def test_non_matching_cards_do_not_log_source_data(self):
        bad = "https://therarbg.com/post-detail/abc/private-title/?secret=foo"
        with patch.object(d, "FINGERPRINT", "000000000000"), \
             patch("builtins.print") as printed:
            found = d.inspect({"results": [{"provider": "therarbag",
                                           "details": bad, "name": "PRIVATE_TITLE"}],
                               "errors": []}, 1)
        self.assertFalse(found)
        content = " ".join(" ".join(str(x) for x in call.args)
                           for call in printed.call_args_list)
        self.assertIn("FIRST_CARD_SHAPE: QUERY_PRESENT", content)
        self.assertNotIn(bad, content)
        self.assertNotIn("PRIVATE_TITLE", content)

    def test_main_refuses_without_explicit_readonly(self):
        with patch.object(d, "api_search") as requester, \
             patch.object(d.sys, "argv", ["script"]):
            self.assertEqual(d.main(), 2)
            requester.assert_not_called()


if __name__ == "__main__":
    unittest.main()
