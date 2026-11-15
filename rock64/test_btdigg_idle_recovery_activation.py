#!/usr/bin/env python3
"""No-service, no-network contract for opt-in BTDigg-only activation."""
from pathlib import Path
import subprocess
import unittest

SCRIPT=Path(__file__).with_name("activate-btdigg-idle-recovery.sh")

class BTDiggIdleRecoveryDeploymentTests(unittest.TestCase):
    def test_syntax_source_pins_and_approval(self):
        subprocess.run(["bash","-n",str(SCRIPT)],check=True)
        code=SCRIPT.read_text(encoding="utf8")
        self.assertIn("BROWSER_BLOB=aeef396fa509fd0984d909619c5d22b271d9435c",code)
        self.assertIn("GATEWAY_BLOB=d2af8118c95eeb6a5f3ecb848471263442ff440d",code)
        self.assertIn("OLD_INSTALLED_BLOB=3553454a227614d5d108aa548a074a4536eb74e1",code)
        self.assertIn("CHECKER_BLOB=8f30d449bd7ceb2ead24a191366f77bdf6500c2a",code)
        self.assertIn('"$2" == "--owner-approved"',code)
        self.assertIn('[[ "$MODE" == check ]]',code)
        self.assertIn("NO_CHANGES; NO_SOURCE_SEARCH",code)

    def test_only_btdigg_services_and_private_health(self):
        code=SCRIPT.read_text(encoding="utf8")
        self.assertIn("systemctl --user restart \"$USER_SERVICE\"",code)
        self.assertIn("sudo systemctl restart \"$GATEWAY_SERVICE\"",code)
        self.assertIn("http://127.0.0.1:18896/v1/browser-state",code)
        self.assertIn("http://127.0.0.1:8796/healthz",code)
        self.assertIn("PWA_CLOUDFLARE=NOT_YET_DEPLOYED",code)
        for forbidden in ("systemctl reboot","sudo reboot","cloudflared tunnel",
                          "curl https://btdig.com","/v1/search?q=",
                          "systemctl restart plex","systemctl restart nexacore"):
            self.assertNotIn(forbidden,code)

    def test_invalid_invocation_does_not_start_preflight(self):
        proc=subprocess.run(["bash",str(SCRIPT),"--apply"],
                            capture_output=True,text=True)
        self.assertEqual(proc.returncode,2)
        self.assertIn("Usage:",proc.stderr)

if __name__=="__main__":
    unittest.main()
