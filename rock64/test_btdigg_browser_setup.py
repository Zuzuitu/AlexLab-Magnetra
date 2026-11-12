#!/usr/bin/env python3
"""Offline safety checks for user-controlled Rock64 Playwright venv setup."""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent
SCRIPT = ROOT / "setup-btdigg-browser-env.sh"


class BrowserSetupTests(unittest.TestCase):
    def test_syntax(self):
        result = subprocess.run(["bash", "-n", str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_readonly_default_does_not_create_venv(self):
        with tempfile.TemporaryDirectory() as root:
            home = Path(root) / "home"
            home.mkdir()
            env = {**os.environ, "HOME": str(home)}
            check = subprocess.run(["bash", str(SCRIPT)], env=env,
                                   capture_output=True, text=True)
            self.assertEqual(check.returncode, 2, check.stderr)
            self.assertIn("PLAYWRIGHT_ENV=NOT_READY", check.stdout)
            self.assertFalse((home / ".venvs").exists())

    def test_unknown_switch_does_not_create_files(self):
        with tempfile.TemporaryDirectory() as root:
            home = Path(root) / "home"
            home.mkdir()
            run = subprocess.run(["bash", str(SCRIPT), "--production"],
                                 env={**os.environ, "HOME": str(home)},
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertFalse((home / ".venvs").exists())

    def test_production_isolation_and_optin(self):
        s = SCRIPT.read_text()
        for required in (
            'MODE="${1:---check}"', "--install", "PLAYWRIGHT_VERSION=1.65.1",
            'VENV="$VENV_BASE/magnetra-browser"', "python3 -m venv",
            "pip --isolated install", "--only-binary=:all:",
            "--index-url https://pypi.org/simple", "read-only check",
            "aarch64", "$(id -u)", '[[ ! -e "$VENV" ]]',
        ):
            with self.subTest(required=required):
                self.assertIn(required, s)
        for forbidden in (
            "sudo ", "systemctl", "cloudflared", "playwright install",
            "btdig.com", "--remote-debugging-port", "magnetra-btdigg.service",
            "--no-sandbox", "curl ", "wget ", "rm -rf",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, s)


if __name__ == "__main__":
    unittest.main()
