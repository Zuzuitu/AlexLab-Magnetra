#!/usr/bin/env python3
"""Offline contracts for CFFI -> Chromium systemd switch and safe rollback."""
from pathlib import Path
import subprocess
import unittest

ROOT=Path(__file__).resolve().parent
MIGRATE=ROOT/"migrate-btdigg-cffi-to-chromium.sh"
ROLLBACK=ROOT/"rollback-btdigg-cffi-to-chromium.sh"


class CffiChromiumMigrationTests(unittest.TestCase):
    def test_bash_syntax_valid_for_both_owner_scripts(self):
        for path in (MIGRATE,ROLLBACK):
            with self.subTest(path=path.name):
                p=subprocess.run(["bash","-n",str(path)],capture_output=True,text=True)
                self.assertEqual(p.returncode,0,p.stderr)

    def test_check_and_owner_approval_are_explicit(self):
        code=MIGRATE.read_text()
        self.assertIn('"$1" == "--check"',code)
        self.assertIn('"$1" == "--activate"',code)
        self.assertIn('"$2" == "--owner-approved"',code)
        self.assertIn('if [[ "$MODE" == check ]]; then',code)
        self.assertIn("CFFI_TO_CHROMIUM_PREFLIGHT=READY",code)
        self.assertLess(code.index("BROWSER_READINESS=VERIFIED_LOCAL_TAB"),
                        code.index('STAGED_BASE="$(mktemp'))
        self.assertLess(code.index("EXISTING_CFFI_HEALTH_PASS"),
                        code.index('STAGED_BASE="$(mktemp'))

    def test_current_zero_result_or_visible_refusal_blocks_writes(self):
        code=MIGRATE.read_text()
        for required in (
            '"/v1/browser-state"', 'state["verified_tabs"]>=1',
            'state.get("selected_tab_verified") is True',
            'state.get("visible_source_rate_limited") is False',
            'state.get("new_searches_paused") is False',
            'state.get("last_navigation_status") is None',
            'state["open_tabs"]==1',
            'BROWSER_READINESS=NOT_READY',
            'CFFI remains active and unchanged',
        ):
            self.assertIn(required,code)
        self.assertNotIn("/v1/search?q=",code)
        self.assertNotIn("http://btdig.com",code)
        self.assertNotIn("https://btdig.com",code)
        self.assertNotIn("systemctl restart magnetra-browser",code)

    def test_known_cffi_only_and_live_exec_are_required(self):
        code=MIGRATE.read_text()
        self.assertIn('[[ "$DROPS" == "$CFFI_DROP" ]]',code)
        self.assertIn('grep -qxF "ExecStart=$CFFI_PY -I $CFFI_EXEC"',code)
        self.assertIn('[[ "$EXEC" == *"$CFFI_EXEC"*',code)
        self.assertIn('[[ ! -e "$file" && ! -L "$file" ]]',code)
        self.assertIn("CFFI_TO_CHROMIUM_PREFLIGHT=READY",code)

    def test_higher_priority_override_is_explicit_not_ambiguous(self):
        code=MIGRATE.read_text()
        self.assertIn("60-magnetra-chromium.conf",code)
        self.assertIn("50-magnetra-cffi.conf",code)
        self.assertIn("ExecStart=\nExecStart=/usr/bin/python3 -I /opt/magnetra-btdigg/btdigg_gateway.py",code)
        self.assertIn("Environment=MAGNETRA_BTDIGG_CHROMIUM_BRIDGE=1",code)
        self.assertIn("LoadCredential=browser_token:/etc/magnetra-btdigg/browser-token",code)
        self.assertIn("systemctl daemon-reload",code)
        self.assertIn('NEW_EXEC="$(systemctl show "$SERVICE" -p ExecStart --value)"',code)
        self.assertIn('[[ "$NEW_DROPS" == *"$CFFI_DROP"*',code)
        self.assertIn("CHROMIUM_GATEWAY_AUTHENTICATED_HEALTH_PASS",code)

    def test_bounded_rollback_preserves_chromium_session_and_cffi_override(self):
        mig=MIGRATE.read_text()
        roll=ROLLBACK.read_text()
        for snippet in (
            "BACKUP=/opt/magnetra-btdigg/.btdigg-base-before-chromium.py",
            "ROLLBACK_ATTEMPT: restore CFFI without touching browser",
            'rm -f -- "$CHROME_DROP" "$NEW_TOKEN"',
            'systemctl restart "$SERVICE"',
        ):
            self.assertIn(snippet,mig)
        for snippet in (
            '[[ "$DROPS" == *"$OLD"*',
            '[[ "$(wc -w <<< "$DROPS")" -eq 2 ]]',
            'grep -qxF',
            'rm -f -- "$CHROME"',
            '[[ "$NEW_EXEC" == *"$CFFI_EXEC"* ]]',
            'RESTORED_CFFI_AUTH_HEALTH_PASS',
            'rm -f -- "$CREDENTIAL" "$BACKUP"',
        ):
            self.assertIn(snippet,roll)
        self.assertNotIn("vnc.html",mig+roll)
        self.assertNotIn("pkill",mig+roll)
        self.assertNotIn("cloudflared",mig+roll)
        self.assertNotIn("/v1/search",mig+roll)

if __name__=="__main__":
    unittest.main()
