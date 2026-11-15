#!/usr/bin/env python3
"""Read-only post-boot BTDigg preflight; NEVER submit a source search.

The local browser-state checker calls only authenticated /v1/browser-state.
This is an operational audit, not proof that a new PWA query succeeds.
Do not print URLs, search terms, HTML, tokens, cookies or magnet links.
"""
from __future__ import annotations

import ipaddress
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
USER_UNIT = "magnetra-btdigg-browser.service"
TAILNET = ipaddress.ip_network(((100 << 24) | (64 << 16), 10))


def command(argv, timeout=8):
    try:
        return subprocess.run(
            argv, check=False, text=True, capture_output=True, timeout=timeout
        )
    except (OSError, subprocess.TimeoutExpired):
        return None


def listener_flags(output):
    flags = {
        "gateway_8796_loopback": False,
        "browser_18896_loopback": False,
        "novnc_6088_tailnet": False,
        "no_unexpected_private_bind": output is not None,
    }
    if output is None:
        return flags
    for line in output.splitlines():
        fields = line.split()
        if len(fields) < 4:
            continue
        local = fields[3]
        host, separator, port = local.rpartition(":")
        if not separator or port not in ("8796", "18896", "6088"):
            continue
        host = host.strip("[]")
        if port in ("8796", "18896"):
            correct = host == "127.0.0.1"
            flags["gateway_8796_loopback" if port == "8796" else
                  "browser_18896_loopback"] |= correct
        else:
            try:
                correct = ipaddress.ip_address(host) in TAILNET
            except ValueError:
                correct = False
            flags["novnc_6088_tailnet"] |= correct
        if not correct:
            flags["no_unexpected_private_bind"] = False
    return flags


def evaluate(*, enabled, linger, unit_active, tmux_state, ss_output, browser):
    ports = listener_flags(ss_output)
    state = browser.get("browser_state") if isinstance(browser, dict) else None
    state = state if isinstance(state, dict) else {}
    diagnostics = state.get("tab_diagnostics")
    index = state.get("selected_tab_index")
    canonical = (isinstance(diagnostics, list)
                 and type(index) is int and 0 <= index < len(diagnostics)
                 and isinstance(diagnostics[index], dict)
                 and diagnostics[index].get("page_kind") == "canonical_search"
                 and diagnostics[index].get("validation") == "valid"
                 and type(diagnostics[index].get("paired_rows")) is int
                 and diagnostics[index]["paired_rows"] >= 1)
    browser_ok = (
        isinstance(browser, dict)
        and browser.get("local_gateway_status") == 200
        and browser.get("search_performed") is False
        and state.get("browser_connected") is True
        and state.get("selected_tab_verified") is True
        and type(state.get("verified_tabs")) is int
        and state["verified_tabs"] >= 1
        and state.get("new_searches_paused") is False
        and canonical
    )
    checks = {
        "user_unit_enabled": enabled is True,
        "linger_enabled": linger is True,
        "user_unit_active": unit_active is True,
        "legacy_tmux_absent": tmux_state == "absent",
        **ports,
        "authenticated_browser_state_valid": browser_ok,
    }
    failed = sorted(key for key, value in checks.items() if not value)
    return {
        "status": ("LOCAL_READONLY_PASS_REQUIRES_NEW_PWA_SEARCH"
                   if not failed else "NOT_VERIFIED"),
        "checks": checks,
        "failed_checks": failed,
        "source_search_performed": False,
        "new_pwa_search_verified": False,
    }


def run():
    unit_enabled = command(["systemctl", "--user", "is-enabled", USER_UNIT])
    linger = command(["loginctl", "show-user", str(__import__("os").getuid()),
                      "-p", "Linger", "--value"])
    unit_active = command(["systemctl", "--user", "is-active", USER_UNIT])
    tmux = command(["tmux", "has-session", "-t", "magnetra-browser"])
    tmux_state = ("active" if tmux and tmux.returncode == 0 else
                  "absent" if tmux and tmux.returncode == 1 else "unknown")
    sockets = command(["ss", "-H", "-ltn"])
    backend = command(
        [sys.executable, "-B", str(HERE / "check-btdigg-browser-backend.py"),
         "--browser-status"], timeout=20
    )
    try:
        browser = json.loads(backend.stdout) if (
            backend and backend.returncode == 0) else {}
    except ValueError:
        browser = {}
    result = evaluate(
        enabled=bool(unit_enabled and unit_enabled.returncode == 0
                     and unit_enabled.stdout.strip() == "enabled"),
        linger=bool(linger and linger.returncode == 0
                    and linger.stdout.strip() == "yes"),
        unit_active=bool(unit_active and unit_active.returncode == 0
                         and unit_active.stdout.strip() == "active"),
        tmux_state=tmux_state,
        ss_output=sockets.stdout if sockets and sockets.returncode == 0 else None,
        browser=browser,
    )
    print(json.dumps(result, sort_keys=True))
    return 0 if not result["failed_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(run())
