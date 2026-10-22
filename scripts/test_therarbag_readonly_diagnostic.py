"""Offline regression tests for the owner-approved TheRarBg diagnostic."""
import contextlib
import io
import unittest

import diagnose_therarbag_iphone_resolve as d


def response(status, *, payload=None, content_type="application/json", mitigated="", ray=""):
    return d.ApiResponse(status, content_type, mitigated, ray, payload or {})


DETAIL = "https://therarbg.com/post-detail/abc123/safe-title/"
ROW = {"provider": "therarbag", "details": DETAIL, "name": "DO_NOT_PRINT_TITLE",
       "torrentFile": "https://therarbg.com/download/private-file", "magnet": None}


class DiagnosticTests(unittest.TestCase):
    def capture(self, fetch):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = d.run_diagnostic(fetch=fetch)
        return result, out.getvalue()

    def test_search_403_html_never_resolves_or_succeeds(self):
        calls = []
        def fetch(path, body=None):
            calls.append(path)
            if path == "/api/health":
                return response(200, payload={"ok": True}, ray="beef1234567890ab-LHR")
            return response(403, content_type="text/html; charset=UTF-8",
                            mitigated="challenge", ray="c0ffee1234567890-LHR")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            with self.assertRaisesRegex(d.DiagnosticStop, "SEARCH_BLOCKED_BEFORE_RESOLVE"):
                d.run_diagnostic(fetch=fetch)
        self.assertEqual(calls, ["/api/search?q=2026&category=all&providers=therarbag",
                                 "/api/health"])
        self.assertIn("HTTP_403_NON_JSON_EDGE_OR_CHALLENGE", out.getvalue())
        self.assertIn("HEALTH_COMPARISON_HTTP_STATUS: 200", out.getvalue())
        self.assertNotIn("RESOLVE_CLASS:", out.getvalue())
        self.assertNotIn("DO_NOT_PRINT_TITLE", out.getvalue())

    def test_search_403_json_remains_unattributed_without_source(self):
        calls = []
        def fetch(path, body=None):
            calls.append(path)
            if path == "/api/health":
                return response(403, payload={}, content_type="text/html")
            return response(403, payload={"error": "Forbidden"})
        with self.assertRaisesRegex(d.DiagnosticStop, "SEARCH_BLOCKED_BEFORE_RESOLVE"):
            self.capture(fetch)
        self.assertEqual(len(calls), 2)

    def test_provider_search_error_does_not_fake_resolver_diagnosis(self):
        calls = []
        def fetch(path, body=None):
            calls.append(path)
            return response(200, payload={"results": [], "errors": [
                {"provider": "therarbag", "error": "provider HTTP 403"}]})
        with self.assertRaisesRegex(d.DiagnosticStop, "NO_ELIGIBLE_UNRESOLVED_SOURCE_CARD"):
            self.capture(fetch)
        self.assertEqual(len(calls), 1)

    def test_complete_resolver_failure_is_classified_without_disclosing_data(self):
        calls = []
        def fetch(path, body=None):
            calls.append((path, body))
            if path.startswith("/api/search"):
                return response(200, payload={"results": [ROW], "errors": []})
            self.assertEqual(path, "/api/resolve")
            self.assertIn(b"therarbag", body)
            return response(502, payload={"error": "Provider could not resolve magnet: provider HTTP 502"})
        result, output = self.capture(fetch)
        self.assertEqual(result, "RESOLVE_FAILURE_CLASSIFIED_UPSTREAM_HTTP_502")
        self.assertIn("RESOLVE_CLASS: UPSTREAM_HTTP_502", output)
        self.assertNotIn(DETAIL, output)
        self.assertNotIn("DO_NOT_PRINT_TITLE", output)
        self.assertNotIn("private-file", output)
        self.assertEqual(len(calls), 2)

    def test_resolver_valid_bithash_is_success_without_printing_hash(self):
        hash_value = "a" * 40
        def fetch(path, body=None):
            if path.startswith("/api/search"):
                return response(200, payload={"results": [ROW], "errors": []})
            return response(200, payload={"magnet": "magnet:?xt=urn:btih:" + hash_value})
        result, output = self.capture(fetch)
        self.assertEqual(result, "RESOLVER_E2E_PASS")
        self.assertIn("RESOLVE_CLASS: RESOLVED_MAGNET", output)
        self.assertNotIn(hash_value, output)

    def test_source_allowlist_refuses_query_redirect_other_origin(self):
        self.assertTrue(d.valid_detail(DETAIL))
        self.assertFalse(d.valid_detail("https://therarbg.com.evil.example/post-detail/x"))
        self.assertFalse(d.valid_detail("https://therarbg.com/post-detail/x?a=1"))
        self.assertFalse(d.valid_detail("https://therarbg.com/post-detail/x#frag"))
        self.assertFalse(d.valid_detail("https://therarbg.com:443/post-detail/x"))
        self.assertFalse(d.valid_detail("http://therarbg.com/post-detail/x"))

    def test_unclassified_resolve_returns_diagnostic_failure(self):
        def fetch(path, body=None):
            if path.startswith("/api/search"):
                return response(200, payload={"results": [ROW], "errors": []})
            return response(502, payload={"error": "unexpected private detail"})
        with self.assertRaisesRegex(d.DiagnosticStop, "RESOLVE_FAILURE_UNCLASSIFIED"):
            self.capture(fetch)

    def test_no_redirect_is_permitted(self):
        handler = d.NoRedirect()
        self.assertIsNone(handler.redirect_request(None, None, 302, "", {}, "https://example.com"))

if __name__ == "__main__":
    unittest.main()
