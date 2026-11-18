#!/usr/bin/env python3
"""Source-only release contract for reviewed PR307 Rock64 activation."""
from pathlib import Path
from subprocess import run
from unittest import TestCase, main

SCRIPT = Path(__file__).with_name("activate-btdigg-pr307-20261118.sh")


class Pr307ActivationTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.body = SCRIPT.read_text(encoding="utf-8")

    def test_bash_parse_only(self):
        result = run(["bash", "-n", str(SCRIPT)], capture_output=True,
                     text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_reviewed_exact_version_and_owner_optin(self):
        s = self.body
        self.assertIn("8b9b634691226cb3f87967297c4ac56e905ae1b3", s)
        self.assertIn("dee9113bcc1591c7dc535ecf72021ed38d04a3ed", s)
        self.assertIn("cd9fa5ae77388b6f4d639f6e6ef83a05266b8e37", s)
        self.assertIn("fdb7346fa60d09f6ff163d6f8e6c23873253af37", s)
        self.assertIn("--accept-session-reset", s)
        self.assertIn("READONLY_CHECK=PASS", s)
        self.assertIn("GATEWAY_8796=UPDATED_HEALTHY", s)
        self.assertIn("CHROMIUM_18896=NEW_CODE_READY", s)

    def test_private_gateway_rollback_and_browser_single_restart(self):
        s = self.body
        self.assertIn("sudo install -m 0600", s)
        self.assertIn('sudo install -m 0644 "$backup" "$dest"', s)
        self.assertIn('sudo systemctl restart "$gw"', s)
        self.assertIn('systemctl --user restart "$bu"', s)
        self.assertEqual(s.count('systemctl --user restart "$bu"'), 1)
        self.assertIn("checkbox_last_outcome", s)
        self.assertIn("checkbox_click_count", s)
        self.assertIn("search_performed", s)
        self.assertNotIn("rm -rf", s)
        self.assertNotIn("/v1/search?q=", s)
        self.assertNotIn("curl https://btdig.com", s)
        self.assertNotIn("systemctl reboot", s)
        self.assertNotIn("restart plex", s.lower())
        self.assertNotIn("restart nexacore", s.lower())


if __name__ == "__main__":
    main()
