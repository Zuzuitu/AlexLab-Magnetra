#!/usr/bin/env python3
"""Offline safeguards for the BTDigg local visual-process inventory."""
import importlib.util
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import subprocess
from unittest import TestCase, main
from unittest.mock import patch

MODULE_PATH = Path(__file__).with_name("check-btdigg-visual-processes.py")
SPEC = importlib.util.spec_from_file_location("btdigg_visual_process_audit", MODULE_PATH)
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)

FAKE_PS = """8503 1 Xvfb Xvfb :99 -screen 0 1280x800x24 -auth /tmp/old/private
9235 1 Xvfb Xvfb :100 -screen 0 1280x800x24
11554 1 Xvfb Xvfb :101 -screen 0 1280x800x24
15086 14700 sh /bin/sh /usr/bin/xvfb-run -a -s -screen 0 1280x800
15096 15086 Xvfb Xvfb :102 -screen 0 1280x800x24
15099 15086 bash bash -c 'secret bearer password btdig.com'
15100 15099 x11vnc x11vnc -norc -display :102 -localhost -rfbauth /private/password
15101 15099 python3 /usr/bin/python3 /usr/bin/websockify --web=/usr/share/novnc TAILSCALE_IP_REDACTED:6088 127.0.0.1:5993
15103 15099 python /home/runner/.venvs/magnetra-browser/bin/python /home/runner/magnetra-cffi-live-20261028/rock64/btdigg_browser_backend.py
"""


class VisualProcessAuditTests(TestCase):
    def test_classifies_known_owner_snapshot_without_orphan_claims(self):
        result = AUDIT.inspect_processes(FAKE_PS, "magnetra-browser\n")
        self.assertTrue(result["tmux_session_present"])
        self.assertEqual(result["browser_backend_pids"], [15103])
        self.assertEqual(result["x11vnc_pids"], [15100])
        self.assertEqual(result["websockify_pids"], [15101])
        self.assertEqual([x["display"] for x in result["xvfb_displays"]],
                         [":99", ":100", ":101", ":102"])
        self.assertFalse(result["xvfb_displays"][0]["vnc_observed"])
        self.assertTrue(result["xvfb_displays"][-1]["vnc_observed"])
        self.assertEqual(result["displays_without_observed_vnc"],
                         [":99", ":100", ":101"])
        self.assertEqual(result["source_requests"], 0)
        text = json.dumps(result)
        for forbidden in ("secret", "btdig.com", "TAILSCALE_IP_REDACTED",
                          "password", "magnet:?xt"):
            self.assertNotIn(forbidden, text)

    def test_other_sessions_and_malformed_ps_cannot_be_declared_safe_to_kill(self):
        snapshot = """abc 1 Xvfb Xvfb :12
999 1 Xvfb Xvfb :13
123 1 Xvfb Xvfb :8
124 1 x11vnc x11vnc -display :8 -localhost
125 1 python python /tmp/other-script.py
"""
        state = AUDIT.inspect_processes(snapshot, "unrelated-session\n")
        self.assertFalse(state["tmux_session_present"])
        self.assertEqual(state["xvfb_displays"], [
            {"display": ":8", "pid": 123, "vnc_observed": True},
            {"display": ":13", "pid": 999, "vnc_observed": False},
        ])
        self.assertEqual(state["browser_backend_pids"], [])
        self.assertIn("does_not_prove_orphan", state["warning"])
        self.assertNotIn("kill", json.dumps(state).lower())

    def test_invokes_ps_and_tmux_readonly_once_and_sanitizes_output(self):
        responses = [
            subprocess.CompletedProcess([], 0, FAKE_PS, ""),
            subprocess.CompletedProcess([], 0, "magnetra-browser\n", ""),
        ]
        out = StringIO()
        with patch.object(AUDIT.subprocess, "run", side_effect=responses) as run, \
             redirect_stdout(out):
            AUDIT.main()
        self.assertEqual(run.call_count, 2)
        self.assertEqual(run.call_args_list[0].args[0],
                         ["ps", "-eo", "pid=,ppid=,comm=,args="])
        self.assertEqual(run.call_args_list[1].args[0],
                         ["tmux", "list-sessions", "-F", "#S"])
        self.assertFalse(run.call_args_list[0].kwargs.get("shell", False))
        text = out.getvalue()
        self.assertEqual(json.loads(text)["browser_backend_pids"], [15103])
        self.assertNotIn("secret", text)
        self.assertNotIn("btdig.com", text)
        self.assertNotIn("TAILSCALE_IP_REDACTED", text)

    def test_fail_closed_if_ps_unavailable_and_tmux_missing(self):
        out = StringIO()
        with patch.object(AUDIT.subprocess, "run",
                          side_effect=OSError("test error")), redirect_stdout(out):
            AUDIT.main()
        self.assertEqual(json.loads(out.getvalue()), {
            "diagnostic": "local_process_snapshot",
            "status": "unavailable",
            "source_requests": 0,
        })
        out = StringIO()
        with patch.object(AUDIT.subprocess, "run", side_effect=[
            subprocess.CompletedProcess([], 0, FAKE_PS, ""),
            subprocess.CalledProcessError(1, ["tmux"]),
        ]), redirect_stdout(out):
            AUDIT.main()
        self.assertFalse(json.loads(out.getvalue())["tmux_session_present"])


if __name__ == "__main__":
    main()
