#!/usr/bin/env python3
"""Offline contract for the exact-version BTDigg 8796-only release command."""
from pathlib import Path
import subprocess
import unittest

SCRIPT = Path(__file__).with_name("rollout-btdigg-checkbox-8796-20261116.sh")

class CheckboxGatewayRolloutTests(unittest.TestCase):
    def test_shell_is_parseable_without_running_it(self):
        self.assertEqual(
            subprocess.run(["bash", "-n", str(SCRIPT)], capture_output=True,
                           check=False).returncode,
            0)

    def test_exact_reviewed_gateway_and_browser_source_blobs(self):
        s = SCRIPT.read_text(encoding="utf8")
        self.assertIn("OLD=c1c0aa40554a96948921210ad6f4f0c1e8af31bf", s)
        self.assertIn("NEW=dee9113bcc1591c7dc535ecf72021ed38d04a3ed", s)
        self.assertIn("BROWSER_NEW=4290f440e73fff409b9f86fa4e0324f9775b5794", s)
        self.assertIn("git merge-base --is-ancestor b7425d590156ebf361c1381aad41c27ff11ccd58 HEAD", s)

    def test_gateway_only_mutation_and_private_health_rollback(self):
        s = SCRIPT.read_text(encoding="utf8")
        self.assertIn("--apply --owner-approved", s)
        self.assertIn("BACKUP=/opt/magnetra-btdigg/.gateway-before-checkbox-20261116.py", s)
        self.assertIn('sudo install -m 0600 "$DEST" "$BACKUP"', s)
        self.assertIn('sudo install -m 0644 "$BACKUP" "$DEST"', s)
        self.assertIn('sudo systemctl restart "$SERVICE"', s)
        self.assertIn('BROWSER_18896=UNTOUCHED', s)
        self.assertIn("rock64/check-btdigg-browser-backend.py --browser-status", s)
        self.assertNotIn('systemctl --user restart "$USER_SERVICE"', s)
        self.assertNotIn('systemctl restart plex', s.lower())
        self.assertNotIn('systemctl restart nexacore', s.lower())
        self.assertNotIn("api/search", s)
        self.assertNotIn(' --test-search', s)
        self.assertNotIn(' --test-next-search', s)

if __name__ == "__main__":
    unittest.main()
