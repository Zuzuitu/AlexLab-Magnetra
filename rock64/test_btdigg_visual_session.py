#!/usr/bin/env python3
"""Offline guardrails for the human-controlled, Tailscale-only BTDigg GUI."""
import pathlib
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
SCRIPT = ROOT / "run-btdigg-visual-session.sh"


class VisualSessionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SCRIPT.read_text()

    def test_shell_syntax(self):
        completed = subprocess.run(["bash", "-n", str(SCRIPT)],
                                   capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_safe_listeners_and_authentication(self):
        s = self.source
        for mandatory in [
            "tailscale ip -4", "octets[0] == 100", "MAGNETRA_TS_IP",
            '"$MAGNETRA_TS_IP:6088"', "127.0.0.1:5993", "-localhost",
            "-rfbauth", "-storepasswd", "chmod 600", "xauth",
            "-nolisten tcp", "xvfb-run -a", "websockify --web=/usr/share/novnc",
            "-norc", "-noxdamage", "--user-data-dir=", "umask 077",
        ]:
            with self.subTest(mandatory=mandatory):
                self.assertIn(mandatory, s)
        for forbidden in [
            "0.0.0.0", "-nopw", "--no-sandbox", "--remote-debugging-port",
            "cloudflared", "-allow 0.0.0.0", "--disable-web-security",
            "--disable-site-isolation-trials", "-shared -nopw",
            "sudo ", "-forever -nopw", "--incognito", "-listen 0.0.0.0",
        ]:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, s)

    def test_persistent_backend_remains_optin_and_private(self):
        s = self.source
        required = [
            "--persistent-backend",
            "MAGNETRA_BTDIGG_BROWSER_OPT_IN=1",
            "MAGNETRA_BTDIGG_BROWSER_PORT=8798",
            "MAGNETRA_BROWSER_PROFILE",
            "MAGNETRA_BROWSER_PYTHON",
            "MAGNETRA_BROWSER_ENTRY",
            "chmod 700",
            "chmod 600",
            "magnetra-btdigg-browser",
            "gateway.token",
            "MAGNETRA_VNC_PASS",
            "mktemp -d",
            "trap cleanup EXIT",
        ]
        for term in required:
            with self.subTest(term=term):
                self.assertIn(term, s)
        self.assertIn('VISUAL_MODE=temporary', s)
        self.assertIn('VISUAL_MODE=persistent', s)
        self.assertIn('[[ "$MAGNETRA_VISUAL_MODE" == persistent ]]', s)
        for forbidden in [
            "MAGNETRA_BTDIGG_PRODUCTION_OPT_IN=1",
            "MAGNETRA_BTDIGG_BROWSER_PORT=8796",
            "--remote-debugging-port",
            "chmod 777",
        ]:
            self.assertNotIn(forbidden, s)

    def test_session_is_interactive_one_page_without_scraping(self):
        s = self.source
        self.assertIn("https://btdig.com/search?order=0&q=The+Dog+Stars+2026", s)
        self.assertIn('wait "$CHROME_PID"', s)
        self.assertIn("trap cleanup EXIT", s)
        self.assertIn('rm -rf -- "$SESSION_DIR"', s)
        self.assertIn("mktemp -d", s)
        self.assertNotIn("magnet:?xt=", s)
        # The default manual mode still launches normal Chromium directly.
        # The separate opt-in persistent mode intentionally uses Playwright.
        self.assertIn('  else\n    chromium --user-data-dir=', s)
        self.assertNotIn("captcha.solve", s.lower())
        self.assertNotIn("curl ", s)


if __name__ == "__main__":
    unittest.main()
