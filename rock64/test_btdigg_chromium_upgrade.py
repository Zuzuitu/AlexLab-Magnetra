#!/usr/bin/env python3
"""Offline upgrade-script guard tests; never executes any service actions."""
from pathlib import Path
import subprocess
import unittest

SCRIPT=Path(__file__).with_name("update-btdigg-chromium-bridge.sh")


class ChromiumBridgeUpgradeContract(unittest.TestCase):
    def test_shell_parses_and_has_exact_version_pins(self):
        subprocess.run(["bash","-n",str(SCRIPT)],check=True)
        text=SCRIPT.read_text(encoding="utf8")
        self.assertIn("OLD_BLOB=f188d69f6b9fa40c7a81f498b5bb2ae0c4b9f0e5",text)
        self.assertIn("NEW_BLOB=3553454a227614d5d108aa548a074a4536eb74e1",text)
        self.assertIn('[[ "$OLD_INSTALLED" == "$OLD_BLOB" ]]',text)
        self.assertIn("local_health || fail",text)
        self.assertIn('if [[ "$MODE" == check ]]; then',text)
        self.assertIn("ROLLBACK=1",text)
        self.assertIn("ROLLBACK=0",text)

    def test_explicit_approval_and_service_isolation(self):
        text=SCRIPT.read_text(encoding="utf8")
        self.assertIn("--apply && \"$2\" == --owner-approved",text)
        self.assertIn('SERVICE=magnetra-btdigg.service',text)
        self.assertIn('CHROMIUM_DROP=/etc/systemd/system/magnetra-btdigg.service.d/60-magnetra-chromium.conf',text)
        self.assertIn('CFFI_DROP=/etc/systemd/system/magnetra-btdigg.service.d/50-magnetra-cffi.conf',text)
        self.assertIn('[[ "$EFFECTIVE_EXEC" == *"/usr/bin/python3"*',text)
        self.assertNotIn("curl ",text)
        self.assertNotIn("btdig.com/search",text)
        self.assertNotIn("cloudflared tunnel",text)
        self.assertNotIn("systemctl restart magnetra-btdigg-browser",text)

    def test_unapproved_invocation_fails_before_any_preflight(self):
        result=subprocess.run(["bash",str(SCRIPT),"--apply"],capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertIn("Usage:",result.stderr)


if __name__=="__main__":
    unittest.main()
