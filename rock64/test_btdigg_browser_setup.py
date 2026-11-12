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
            "assert version('playwright') in ('1.65.0', '1.65.1')",
            "secure_existing_venv", "INSECURE_PERMISSIONS",
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

    def test_reject_group_writable_existing_venv_without_modification(self):
        with tempfile.TemporaryDirectory() as root:
            home = Path(root) / "home"
            home.mkdir()
            venv = home / ".venvs" / "magnetra-browser"
            venv.mkdir(parents=True, mode=0o700)
            venv.chmod(0o775)
            config = venv / "pyvenv.cfg"
            config.write_text("home = /usr/bin\n")
            config.chmod(0o664)
            run = subprocess.run(["bash", str(SCRIPT), "--check"],
                                 env={**os.environ, "HOME": str(home)},
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertIn("INSECURE_PERMISSIONS", run.stderr)
            self.assertEqual(venv.stat().st_mode & 0o777, 0o775)
            self.assertEqual(config.stat().st_mode & 0o777, 0o664)

    def test_readonly_compatible_venv_without_pip_install(self):
        with tempfile.TemporaryDirectory() as root:
            home = Path(root) / "home"
            home.mkdir()
            venv = home / ".venvs" / "magnetra-browser"
            (venv / "bin").mkdir(parents=True, mode=0o700)
            venv.chmod(0o700)
            cfg = venv / "pyvenv.cfg"
            cfg.write_text("home = /usr/bin\n")
            cfg.chmod(0o600)
            fake_python = venv / "bin" / "python"
            fake_python.write_text('#!/bin/sh\ncase "$2" in *"print(version("* ) echo 1.65.0 ;; esac\nexit 0\n')
            fake_python.chmod(0o700)
            run = subprocess.run(["bash", str(SCRIPT), "--check"],
                                 env={**os.environ, "HOME": str(home)},
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn("PLAYWRIGHT_ENV=READY VERSION=1.65.0", run.stdout)


if __name__ == "__main__":
    unittest.main()
