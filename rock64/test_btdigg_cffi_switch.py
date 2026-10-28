#!/usr/bin/env python3
"""Static/offline checks for owner-operated Rock64 BTDigg cffi switch."""
from pathlib import Path
import subprocess
import unittest

HERE=Path(__file__).resolve().parent
class SwitchSafetyTest(unittest.TestCase):
    def test_bash_syntax_and_rollback(self):
        for script in ("activate-btdigg-cffi.sh","rollback-btdigg-cffi.sh"):
            p=HERE/script
            subprocess.run(["bash","-n",str(p)],check=True,
                           capture_output=True,text=True)
        a=(HERE/"activate-btdigg-cffi.sh").read_text()
        b=(HERE/"rollback-btdigg-cffi.sh").read_text()
        for s in ("--activate", "--permission-confirmed",
                  "curl_cffi==0.17.0", "--only-binary=:all:",
                  "MAGNETRA_BTDIGG_CFFI_OPT_IN=1",
                  "MAGNETRA_BTDIGG_SOURCE_PERMISSION_CONFIRMED=1",
                  "rollback_needed=1", "CFFI_AUTHENTICATED_LOCAL_HEALTH_PASS",
                  "127.0.0.1:8796/healthz"):
            self.assertIn(s,a)
        self.assertNotIn("run-btdigg-cffi-one-shot",a)
        self.assertIn("BTDIGG_ORIGINAL_GATEWAY_RESTORED",b)
        self.assertNotIn("curl_cffi==",b)
    def test_old_unit_kept_and_auth_protected(self):
        old=(HERE/"magnetra-btdigg.service").read_text()
        self.assertIn("DynamicUser=yes",old)
        self.assertIn("ProtectSystem=strict",old)
        self.assertIn("ExecStart=/usr/bin/python3 -I /opt/magnetra-btdigg/btdigg_gateway.py",old)
        script=(HERE/"activate-btdigg-cffi.sh").read_text()
        self.assertNotIn("curl -k",script)
        self.assertNotIn("BTDIGG_GATEWAY_TOKEN=",script)
        self.assertNotIn("echo $MAGNETRA_BTDIGG_TOKEN",script)

if __name__=="__main__": unittest.main()
