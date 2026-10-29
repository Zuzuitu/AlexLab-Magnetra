#!/usr/bin/env python3
"""Offline validation of diagnostic-only in-place upgrade safety."""
import pathlib, subprocess, unittest
HERE=pathlib.Path(__file__).resolve().parent
class DiagnosticsRolloutTest(unittest.TestCase):
    def test_updater_is_valid_and_fails_closed(self):
        path=HERE/"apply-btdigg-cffi-diagnostics.sh"
        subprocess.run(["bash","-n",str(path)],capture_output=True,text=True,check=True)
        content=path.read_text()
        for item in ("git hash-object", "8f70fefa6a06159626afc6c9ad7eb3c6b530d8d0",
                     "systemctl is-active", "CFFI_DIAGNOSTIC_LOCAL_HEALTH_PASS",
                     "NO_UPSTREAM_SEARCH_WAS_SENT_BY_INSTALLER", "restore_temp",
                     "test_btdigg_cffi_*.py", "127.0.0.1:8796/healthz"):
            self.assertIn(item,content)
        for denied in ("curl -k", "wrangler deploy", "systemctl disable",
                       "MAGNETRA_BTDIGG_TOKEN=$", "curl_cffi==0.18"):
            self.assertNotIn(denied,content)
    def test_unchanged_cffi_gateway_and_base_service(self):
        text=(HERE/"magnetra-btdigg.service").read_text()
        self.assertIn("ExecStart=/usr/bin/python3 -I /opt/magnetra-btdigg/btdigg_gateway.py",text)
        self.assertIn("DynamicUser=yes",text)
