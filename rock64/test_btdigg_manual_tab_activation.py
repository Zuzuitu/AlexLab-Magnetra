#!/usr/bin/env python3
"""Offline, no-privilege contract for BTDigg verified-manual-tab activation."""
import subprocess
import unittest
from pathlib import Path

SCRIPT=Path(__file__).with_name("activate-btdigg-manual-tab-gateway.sh")

class ManualTabActivationContract(unittest.TestCase):
    def test_script_parses_and_pins_old_and_new_gateway_exactly(self):
        subprocess.run(["bash","-n",str(SCRIPT)],check=True)
        code=SCRIPT.read_text(encoding="utf-8")
        self.assertIn("OLD_BLOB=d2af8118c95eeb6a5f3ecb848471263442ff440d",code)
        self.assertIn("NEW_BLOB=ce372bdf73b895e5105e83a77bad47229d070c02",code)
        self.assertIn("NO_BTDIGG_SEARCH; NO_CLOUDFLARE_DEPLOY",code)
        self.assertIn("ROLLBACK_GATEWAY_HEALTH=",code)
        self.assertIn("CHROMIUM_18896=UNCHANGED",code)
        self.assertIn('[[ "$MODE" == check ]]',code)
    def test_explicit_owner_approval_and_only_gateway_restart(self):
        code=SCRIPT.read_text(encoding="utf-8")
        self.assertIn('"$2" == --owner-approved',code)
        self.assertIn('sudo systemctl restart "$SERVICE"',code)
        self.assertIn('SERVICE=magnetra-btdigg.service',code)
        self.assertNotIn('systemctl --user restart',code)
        self.assertNotIn('systemctl restart "$USER_SERVICE"',code)
        for denied in ('/v1/search?', 'btdig.com/search',
                       'systemctl reboot', 'docker restart',
                       'systemctl restart plex',
                       'systemctl restart nexacore', 'cloudflared tunnel'):
            self.assertNotIn(denied,code)
    def test_unapproved_apply_stops_before_mutation(self):
        proc=subprocess.run(["bash",str(SCRIPT),"--apply"],
                            capture_output=True,text=True)
        self.assertEqual(proc.returncode,2)
        self.assertIn("Usage:",proc.stderr)

if __name__=="__main__":
    unittest.main()
