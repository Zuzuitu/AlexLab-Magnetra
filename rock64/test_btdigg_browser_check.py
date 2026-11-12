#!/usr/bin/env python3
"""Offline regression: source browser-backed localhost probe mode and privacy."""
from contextlib import redirect_stdout
from io import StringIO
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "magnetra_local_browser_check",
    HERE / "check-btdigg-browser-backend.py",
)
PROBE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROBE)


class Response:
    status = 200
    def __enter__(self):
        return self
    def __exit__(self, *_):
        return False
    def read(self, _limit):
        return b'<html><div class="one_result"><a href="magnet:?xt=urn:btih:FAKE"></a></div></html>'


class BrowserLocalCheckTests(TestCase):
    def test_exactly_one_local_fetch_per_owner_mode_without_leaks(self):
        with TemporaryDirectory() as root:
            token = Path(root) / "gateway.token"
            token.write_text("x" * 64)
            token.chmod(0o600)
            for args, expected in [
                ([], "/healthz"),
                (["--test-search"], "/v1/search?q=The%20Dog%20Stars%202026"),
                (["--test-next-search"], "/v1/search?q=The%20Dog%20Stars%202026%20720p"),
            ]:
                requests = []
                def fetch(req, timeout):
                    self.assertEqual(timeout, 14)
                    requests.append(req)
                    return Response()
                out = StringIO()
                with self.subTest(args=args), \
                     patch.object(PROBE, "TOKEN_FILE", token), \
                     patch.object(PROBE.urllib.request, "urlopen", fetch), \
                     patch.object(PROBE.argparse._sys, "argv", ["local-probe", *args]), \
                     redirect_stdout(out):
                    PROBE.main()
                self.assertEqual(len(requests), 1)
                self.assertEqual(requests[0].full_url, PROBE.LOCAL + expected)
                self.assertEqual(requests[0].get_header("Authorization"), "Bearer " + "x" * 64)
                result = json.loads(out.getvalue())
                self.assertEqual(result["local_gateway_status"], 200)
                self.assertEqual(result["search_performed"], bool(args))
                self.assertNotIn("The Dog Stars", out.getvalue())
                self.assertNotIn("magnet:?xt=", out.getvalue())
                self.assertNotIn("x" * 64, out.getvalue())
                if args:
                    self.assertTrue(result["source_result_marker"])
                    self.assertTrue(result["source_magnet_marker"])
                else:
                    self.assertNotIn("source_result_marker", result)

    def test_local_probe_never_calls_source_without_private_token(self):
        with TemporaryDirectory() as root:
            token = Path(root) / "gateway.token"
            token.write_text("x" * 64)
            token.chmod(0o644)
            out = StringIO()
            with patch.object(PROBE, "TOKEN_FILE", token), \
                 patch.object(PROBE.urllib.request, "urlopen",
                              side_effect=AssertionError("MUST NOT FETCH")), \
                 patch.object(PROBE.argparse._sys, "argv",
                              ["local-probe", "--test-next-search"]), \
                 redirect_stdout(out):
                PROBE.main()
            result = json.loads(out.getvalue())
            self.assertEqual(result["local_gateway_status"], "unavailable")
            self.assertFalse(result["search_performed"])


if __name__ == "__main__":
    main()
