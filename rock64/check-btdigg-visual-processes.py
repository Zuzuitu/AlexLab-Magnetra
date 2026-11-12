#!/usr/bin/env python3
"""Read-only local Xvfb/noVNC process audit for the owner-controlled BTDigg GUI.

No BTDigg HTTP calls, no process changes, no profile reads, and no raw
command lines, URL strings, VNC auth paths or environment values printed.
An Xvfb without observed x11vnc is NOT necessarily orphaned.
"""
from __future__ import annotations

import json
import re
import subprocess


XVFB_DISPLAY = re.compile(r"(?:^|[ /])Xvfb\s+(:[0-9]+)(?:\s|$)")
VNC_DISPLAY = re.compile(r"(?:^|\s)-display\s+(:[0-9]+)(?:\s|$)")
BACKEND_COMMAND = re.compile(r"(?:^|\s)(?:/\S*/)?btdigg_browser_backend\.py(?:\s|$)")
WEBSOCKIFY_COMMAND = re.compile(r"(?:^|\s)(?:/\S*/)?websockify(?:\s|$)")


def inspect_processes(snapshot: str, tmux_sessions: str = "") -> dict:
    """Parse a bounded ps snapshot. Never return original argv or secrets."""
    displays: dict[str, int] = {}
    vnc_displays: set[str] = set()
    vnc_pids: list[int] = []
    backend_pids: list[int] = []
    websocket_pids: list[int] = []
    for line in snapshot.splitlines()[:4096]:
        fields = line.strip().split(None, 3)
        if len(fields) != 4:
            continue
        pid_text, ppid_text, comm, args = fields
        if (not pid_text.isdecimal() or not ppid_text.isdecimal()
                or len(args) > 6000):
            continue
        pid = int(pid_text)
        if pid <= 0:
            continue
        if comm == "Xvfb":
            found = XVFB_DISPLAY.search(args)
            if found:
                displays[found.group(1)] = pid
        elif comm == "x11vnc":
            found = VNC_DISPLAY.search(args)
            if found:
                vnc_displays.add(found.group(1))
                vnc_pids.append(pid)
        elif comm in ("python", "python3", "python3.11", "python3.13", "websockify"):
            if WEBSOCKIFY_COMMAND.search(args):
                websocket_pids.append(pid)
            if BACKEND_COMMAND.search(args):
                backend_pids.append(pid)

    return {
        "diagnostic": "local_process_snapshot",
        "source_requests": 0,
        "tmux_session_present": "magnetra-browser" in tmux_sessions.splitlines(),
        "browser_backend_pids": sorted(set(backend_pids)),
        "x11vnc_pids": sorted(set(vnc_pids)),
        "websockify_pids": sorted(set(websocket_pids)),
        "xvfb_displays": [
            {"display": display, "pid": pid,
             "vnc_observed": display in vnc_displays}
            for display, pid in sorted(displays.items(), key=lambda pair: int(pair[0][1:]))
        ],
        "displays_without_observed_vnc": sorted(
            (display for display in displays if display not in vnc_displays),
            key=lambda item: int(item[1:]),
        ),
        "warning": "no_vnc_observed_does_not_prove_orphan_or_safe_to_stop",
    }


def main() -> None:
    try:
        processes = subprocess.run(
            ["ps", "-eo", "pid=,ppid=,comm=,args="],
            capture_output=True, text=True, check=True, timeout=5,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        print(json.dumps({
            "diagnostic": "local_process_snapshot",
            "status": "unavailable",
            "source_requests": 0,
        }, sort_keys=True))
        return

    try:
        sessions = subprocess.run(
            ["tmux", "list-sessions", "-F", "#S"],
            capture_output=True, text=True, check=True, timeout=3,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        sessions = ""

    print(json.dumps(inspect_processes(processes, sessions), sort_keys=True))


if __name__ == "__main__":
    main()
