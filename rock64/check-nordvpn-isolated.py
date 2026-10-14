#!/usr/bin/env python3
"""Non-invasive NordVPN SOCKS5 readiness check; NO network requests or VPN login.

Use on physical Rock64 before any isolated proxy trial. This intentionally does
not create an OS route, proxy process, tunnel, secret, config or systemd service.
"""
import importlib.util
import os
import shutil
import socket
import sys

def report():
    print("Magnetra · isolated NordVPN readiness (read-only)")
    print("NordVPN CLI:", "present" if shutil.which("nordvpn") else "not installed")
    print("curl:", "present" if shutil.which("curl") else "not installed")
    print("curl SOCKS5 support: check manually with 'curl -V' if needed")
    print("Python SOCKS library:", "present" if importlib.util.find_spec("socks") else "not installed")
    print("Tailscale CLI:", "present" if shutil.which("tailscale") else "not installed")
    print("Local network routes, DNS, existing services: unchanged")
    print("Credentials: not requested or read")
    print("Upstream requests: none")
    print("Next: obtain exact current NordVPN SOCKS5 hostname/port from the owner's account")
    print("and confirm provider permits these destination domains; do not guess a proxy.")
    print("Only after verification: a one-shot curl --proxy socks5h://... per")
    print("fixed origin, without modifying system-wide proxy, iptables, VPN or DNS.")
    return 0

if __name__ == "__main__":
    raise SystemExit(report())
