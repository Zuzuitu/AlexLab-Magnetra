#!/usr/bin/env python3
"""Offline guardrails for explicit isolated EZTV tunnel install. No shell executed."""
import pathlib
import subprocess
import unittest

ROOT = pathlib.Path(__file__).parent
SH = ROOT / "install-eztv-tunnel.sh"
UNIT = ROOT / "magnetra-eztv-tunnel.service"


class TunnelInstallTests(unittest.TestCase):
    def test_bash_syntax_without_execution(self):
        subprocess.run(["bash", "-n", str(SH)], check=True, capture_output=True)

    def test_installer_does_not_touch_unrelated_tunnels_or_network(self):
        content = SH.read_text(encoding="utf-8")
        for forbidden in (
            "cloudflared service install",
            "systemctl restart magnetra-btdigg",
            "systemctl restart cloudflared",
            "systemctl restart magnetra-eztv",
            "tailscale up", "iptables ", "nft ",
            "wrangler secret", "wrangler deploy",
            "curl -X POST", "curl --request POST",
        ):
            self.assertNotIn(forbidden, content)
        self.assertIn("systemctl enable --now magnetra-eztv-tunnel.service", content)
        self.assertIn("curl --noproxy '*'", content)
        self.assertIn('[[ ! -e "$unit_path" && ! -L "$unit_path" ]]', content)
        self.assertIn('[[ ! -e "$token_path" && ! -L "$token_path" ]]', content)
        self.assertIn("getpass.getpass(", content)
        self.assertIn("os.O_EXCL", content)
        self.assertIn("os.O_NOFOLLOW", content)
        self.assertIn("os.fchmod(fd, 0o600)", content)
        self.assertIn("systemctl is-active --quiet magnetra-btdigg.service", content)

    def test_unit_loads_only_separate_root_only_token_file(self):
        content = UNIT.read_text(encoding="utf-8")
        self.assertIn("LoadCredential=tunnel-token:/etc/magnetra-eztv/tunnel-token", content)
        self.assertIn("Environment=TUNNEL_TOKEN_FILE=%d/tunnel-token", content)
        self.assertIn("ExecStart=/usr/local/bin/cloudflared tunnel --no-autoupdate run", content)
        self.assertIn("DynamicUser=yes", content)
        self.assertIn("NoNewPrivileges=yes", content)
        self.assertIn("ProtectSystem=strict", content)
        self.assertNotIn("cloudflared service install", content)
        self.assertNotIn("btdigg", content.lower())


if __name__ == "__main__":
    unittest.main()
