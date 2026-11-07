#!/usr/bin/env python3
"""Static offline guards for BTDigg Retry-After observation rollout.

No live source request, Cloudflare API, token use or systemd interaction.
"""
from pathlib import Path
import subprocess
import unittest

HERE = Path(__file__).resolve().parent


class RetryAfterRolloutTests(unittest.TestCase):
    def test_shell_gate_and_expected_current_diagnostic_sha(self):
        script=HERE/"apply-btdigg-cffi-retry-after-observation.sh"
        subprocess.run(["bash","-n",str(script)],check=True,capture_output=True,text=True)
        content=script.read_text()
        must_include=(
            "PREVIOUS_BLOB=efed2989adc695c7cb33fc247112243ab07a8107",
            "git hash-object",
            "systemctl is-active --quiet",
            "test_btdigg_cffi_*.py",
            "CFFI_RETRY_AFTER_LOCAL_HEALTH_PASS",
            "CFFI_RETRY_AFTER_OBSERVER_INSTALLED",
            "NO_UPSTREAM_SEARCH_WAS_SENT_BY_INSTALLER",
            "RETRY_AFTER_HEALTH_FAILED",
            '127.0.0.1:8796/healthz',
            'chmod',
        )
        for text in must_include:
            if text=="chmod":
                self.assertIn("install -m 0644",content)
            else:self.assertIn(text,content)
        for forbidden in ("wrangler deploy","curl -k","git reset --hard",
                          "systemctl disable","https://btdig.com/search",
                          "rm -rf /opt","--insecure"):
            self.assertNotIn(forbidden,content)
    def test_candidate_retains_single_fixed_origin_and_status_contract(self):
        code=(HERE/"btdigg_cffi_candidate.py").read_text()
        self.assertIn('SEARCH_URL = ORIGIN + "/search"',code)
        self.assertIn("timeout=TIMEOUT_SECONDS",code)
        self.assertIn("allow_redirects=False",code)
        self.assertIn("stream=True",code)
        self.assertIn('return 429, b""',code)
        self.assertIn("source_retry_after_kind",code)
        self.assertIn("source_retry_after_seconds",code)
        self.assertIn("MAX_RETRY_AFTER_SECONDS = 24 * 60 * 60",code)

if __name__=="__main__":unittest.main()
