#!/usr/bin/env python3
"""Offline guardrails for optional BTDigg user-systemd boot setup."""
import pathlib
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
SCRIPT = ROOT / "install-btdigg-browser-autostart.sh"


class BrowserAutostartTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SCRIPT.read_text()

    def test_shell_syntax(self):
        result = subprocess.run(["bash", "-n", str(SCRIPT)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_no_unapproved_live_impact(self):
        s = self.source
        for term in [
            "--check", "--install", "--seed-query",
            "MAGNETRA_BTDIGG_RESTORE_ON_BOOT=1",
            "systemctl --user enable",
            "systemctl --user daemon-reload",
            "loginctl show-user",
            "enable-linger",
            "Restart=on-failure",
            "--persistent-backend",
            "magnetra-cffi-live-20261028",
            "UMask=0077",
        ]:
            self.assertIn(term, s)
        for forbidden in [
            "systemctl --user start ",
            "systemctl --user restart ",
            "tmux send-keys",
            "tmux kill-session",
            "killall", "pkill ", "curl ", "wget ",
            "--remote-debugging-port", "--no-sandbox",
            "sudo systemctl", "rm -rf ",
        ]:
            self.assertNotIn(forbidden, s)
        self.assertIn("UNIT=ABSENT", s)
        self.assertIn("RUNNING_BROWSER=UNCHANGED", s)


if __name__ == "__main__":
    unittest.main()
