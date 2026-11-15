#!/usr/bin/env python3
"""Offline contract: 8796-only CAPTCHA signal update never restarts Chromium."""
import subprocess
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parent

class ActivationContracts(unittest.TestCase):
    def test_shell_scripts_parse_offline_and_require_owner_approval(self):
        names=("activate-btdigg-captcha-gateway.sh",
               "install-btdigg-private-novnc-https.sh")
        for name in names:
            script=ROOT/name
            subprocess.run(["bash","-n",str(script)],check=True)
            proc=subprocess.run(["bash",str(script),"--apply"],
                                capture_output=True,text=True)
            self.assertEqual(proc.returncode,2,name)
            self.assertIn("Usage:",proc.stderr,name)

    def test_gateway_update_targets_exact_revisions_and_keeps_browser_up(self):
        code=(ROOT/"activate-btdigg-captcha-gateway.sh").read_text()
        self.assertIn("OLD_BLOB=ce372bdf73b895e5105e83a77bad47229d070c02",code)
        self.assertIn("NEW_BLOB=c1c0aa40554a96948921210ad6f4f0c1e8af31bf",code)
        self.assertIn("CHROMIUM_18896=UNCHANGED",code)
        self.assertIn("ROLLBACK_GATEWAY_HEALTH=",code)
        self.assertIn('sudo systemctl restart "$SERVICE"',code)
        self.assertNotIn('systemctl --user restart magnetra-btdigg-browser',code)
        self.assertNotIn('tailscale serve reset',code)
        self.assertNotIn("tailscale funnel",code)

if __name__=="__main__":
    unittest.main()
