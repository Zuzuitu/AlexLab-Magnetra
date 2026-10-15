#!/usr/bin/env python3
"""Offline safety guard for read-only shared-tunnel probe."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).parent
SH = ROOT / "check-shared-tunnel.sh"


class SharedTunnelPreflightTests(unittest.TestCase):
    def test_bash_syntax_only(self):
        subprocess.run(["bash", "-n", str(SH)], check=True, capture_output=True)

    def test_only_known_services_loopback_no_tokens(self):
        source = SH.read_text(encoding="utf8")
        self.assertIn("magnetra-btdigg-tunnel.service", source)
        self.assertIn("magnetra-eztv.service", source)
        self.assertIn("port_%s_listener_count", source)
        self.assertIn("port_%s_health_http", source)
        self.assertIn("8796 8797 8798", source)
        self.assertIn("--noproxy '*'", source)
        forbidden = ("systemctl restart ", "systemctl stop ", "systemctl enable ",
                     "cloudflared service install", "journalctl ", "cat /etc/",
                     "systemctl cat ", "systemctl show -p ExecStart",
                     "tunnel-token", "MAGNETRA_BTDIGG_TOKEN",
                     "MAGNETRA_EZTV_TOKEN", "iptables ", "nft ",
                     "tailscale up", "wg-quick")
        for x in forbidden:
            self.assertNotIn(x, source, msg=x)


if __name__ == "__main__":
    unittest.main()
