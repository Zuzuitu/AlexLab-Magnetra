"""Offline regression tests: one exact source read, SSRF safety, no secret output."""
import contextlib
from email.message import Message
from io import StringIO
import unittest
from unittest.mock import patch

import diagnose_therarbag_exact_detail as d

URL = "https://therarbg.com/post-detail/abcdef/visible-legal-sample/"
HASH = "a" * 40

class FakeResponse:
    status = 200
    def __init__(self, html, *, content_type="text/html", content_length=None):
        self.body = html.encode("utf-8")
        self.headers = Message()
        self.headers["Content-Type"] = content_type
        if content_length is not None:
            self.headers["Content-Length"] = str(content_length)
    def __enter__(self): return self
    def __exit__(self, *args): return None
    def read(self, n): return self.body[:n]

class FakeOpener:
    def __init__(self, html):
        self.calls = []
        self.html = html
    def open(self, request, timeout):
        self.calls.append((request.full_url, request.get_method(), timeout))
        return FakeResponse(self.html)

class Tests(unittest.TestCase):
    def test_allowlist_fail_closed(self):
        good = [URL, "https://therarbg.com/post-detail/abcdef/Genshin%20Impact/"]
        bad = ["https://therarbg.com.evil.test/post-detail/a/b",
               "https://therarbg.com:443/post-detail/a/b",
               "https://user@therarbg.com/post-detail/a/b",
               "http://therarbg.com/post-detail/a/b",
               "https://therarbg.com/get-posts/keywords:2026",
               "https://therarbg.com/post-detail/a/b?url=evil",
               "https://therarbg.com/post-detail/a/b#f",
               "https://therarbg.com/post-detail/a/%2fsecret",
               "https://therarbg.com/post-detail/a//b",
               "https://therarbg.com/post-detail/a/../b",
               "https://therarbg.com/post-detail/a/b\n"]
        self.assertTrue(all(d.valid_detail(x) for x in good))
        self.assertTrue(all(not d.valid_detail(x) for x in bad))

    def test_only_structure_no_identifiers(self):
        html = ("<p>Info Hash:</p><input value='" + HASH + "'>"
                "<a href='https://itorrents.org/torrent/" + HASH + ".torrent'>.torrent File</a>"
                "<button data-clipboard-text='magnet:?xt=urn:btih:" + HASH + "'>Copy</button>"
                "<script>const magnet='magnet:?xt=urn:btih:" + HASH + "'</script>")
        p = d.DetailShape()
        p.feed(html)
        s = p.summary()
        self.assertEqual(s["LABELLED_VISIBLE_HEX_COUNT"], 0)
        self.assertTrue(s["VISIBLE_INFO_HASH_LABEL"])
        self.assertEqual(s["INPUT_VALUE_HEX_COUNT"], 1)
        self.assertEqual(s["STRICT_CACHE_URL_COUNT"], 1)
        self.assertEqual(s["CLIPBOARD_MAGNET_COUNT"], 1)
        self.assertEqual(s["SCRIPT_MAGNET_MARKER_COUNT"], 1)
        self.assertNotIn(HASH, str(s))
        self.assertNotIn("magnet:?", str(s))

    def test_labelled_visible_hash_without_cache(self):
        p = d.DetailShape()
        p.feed("<div>Info Hash:</div><code>" + HASH + "</code>")
        self.assertEqual(p.summary()["LABELLED_VISIBLE_HEX_COUNT"], 1)

    def test_reject_lookalike_cache(self):
        self.assertTrue(d.is_cache_link("https://itorrents.org/torrent/" + HASH + ".torrent"))
        self.assertFalse(d.is_cache_link("http://itorrents.org/torrent/" + HASH + ".torrent"))
        self.assertFalse(d.is_cache_link("https://itorrents.org.evil.test/torrent/" + HASH + ".torrent"))
        self.assertFalse(d.is_cache_link("https://itorrents.org/torrent/" + HASH + ".torrent?q=x"))

    def test_one_bounded_original_request(self):
        op = FakeOpener("<h1>Info Hash: " + HASH + "</h1>")
        with patch.object(d, "build_opener", return_value=op):
            output = d.inspect_once(URL)
        self.assertEqual(output["HTTP_STATUS"], 200)
        self.assertEqual(output["LABELLED_VISIBLE_HEX_COUNT"], 1)
        self.assertEqual(op.calls, [(URL, "GET", 11)])
        self.assertNotIn(HASH, str(output))
        self.assertNotIn(URL, str(output))

    def test_invalid_detail_makes_zero_source_calls(self):
        op = FakeOpener("unused")
        with patch.object(d, "build_opener", return_value=op):
            with self.assertRaisesRegex(d.DiagnosticStop, "DETAIL_URL_REJECTED"):
                d.inspect_once("https://attacker.invalid/post-detail/a/b")
        self.assertEqual(op.calls, [])

    def test_max_size_and_non_html(self):
        class ConfigOpener:
            def __init__(self, response): self.response = response
            def open(self, *args, **kwargs): return self.response
        with patch.object(d, "build_opener", return_value=ConfigOpener(
                FakeResponse("x", content_length=d.MAX_HTML + 1))):
            with self.assertRaisesRegex(d.DiagnosticStop, "SOURCE_PAGE_TOO_LARGE"):
                d.inspect_once(URL)
        with patch.object(d, "build_opener", return_value=ConfigOpener(
                FakeResponse("{}", content_type="application/json"))):
            with self.assertRaisesRegex(d.DiagnosticStop, "SOURCE_NOT_HTML"):
                d.inspect_once(URL)

    def test_strict_challenge(self):
        self.assertEqual(d.classify_document("<title>Just a moment...</title>"),
                         "POSSIBLE_BROWSER_CHALLENGE")

    def test_no_approval_no_network_and_no_url_printed(self):
        with patch("sys.argv", ["diagnostic", "--detail-url", URL]):
            stream = StringIO()
            with contextlib.redirect_stdout(stream):
                self.assertEqual(d.main(), 2)
            self.assertNotIn(URL, stream.getvalue())
            self.assertIn("OWNER_APPROVAL_REQUIRED", stream.getvalue())

    def test_redirects_disallowed(self):
        self.assertIsNone(d.NoRedirect().redirect_request(None, None, 302, "", {}, "https://evil.test/"))

if __name__ == "__main__":
    unittest.main()
