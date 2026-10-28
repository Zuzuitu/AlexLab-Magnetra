#!/usr/bin/env python3
"""Offline static safety review for optional BTDigg one-shot diagnostic."""
import pathlib
import re
import subprocess
import unittest

PATH=pathlib.Path(__file__).with_name("run-btdigg-cffi-one-shot.sh")


class OneShotScriptTests(unittest.TestCase):
    def test_shell_syntax_and_safety_boundary(self):
        script=PATH.read_text(encoding="utf-8")
        subprocess.run(["bash","-n",str(PATH)],check=True,capture_output=True,text=True)
        for required in [
          "if (( EUID == 0 ))", "mktemp -d", "trap cleanup EXIT",
          "python3 -m venv", "curl_cffi==0.17.0",
          "--only-binary=:all:", "timeout 25",
          "diagnose_btdigg_cffi_exact.py",
        ]:
            self.assertIn(required,script)
        for forbidden in [
          r"systemctl\s+(?:restart|stop|start|reload|enable|disable)",
          r"\b(?:sudo|ssh|scp)\s",
          r"\bwrangler\b",
          r"gateway\.env",r"BTDIGG_GATEWAY_TOKEN",
          r"MAGNETRA_BTDIGG_TOKEN",
          r"\/opt\/magnetra-btdigg",
          r"\/etc\/magnetra-btdigg",
          r"--upgrade\s+pip",
          r"\bpip\s+install\s+(?!.*only-binary)",
        ]:
            self.assertIsNone(re.search(forbidden,script),forbidden)

if __name__=="__main__":
    unittest.main()
