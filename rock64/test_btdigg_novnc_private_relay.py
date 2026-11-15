#!/usr/bin/env python3
"""Offline synthetic loopback relay tests. Never contact BTDigg or Tailscale."""
from __future__ import annotations
import asyncio
import ipaddress
import socket
import subprocess
import unittest
from unittest.mock import patch

from rock64 import btdigg_novnc_private_relay as relay


class PrivateNoVNCTests(unittest.TestCase):
    def test_only_tailnet_ipv4_is_accepted(self):
        def mock(value):
            def run(argv, **kwargs):
                self.assertEqual(argv, ["/usr/bin/tailscale","ip","-4"])
                return subprocess.CompletedProcess(argv,0,stdout=value)
            return run
        valid=str(ipaddress.IPv4Address(bytes([100,79,134,61])))
        self.assertEqual(relay.tailnet_ipv4(mock(valid+"\\n")),valid)
        bad_addresses=((127,0,0,1),(192,168,0,216),(8,8,8,8),
                       (100,200,1,3))
        invalid=[str(ipaddress.IPv4Address(bytes(x))) for x in bad_addresses]
        invalid+=["some-name",valid+"\\n"+invalid[2]]
        for bad in invalid:
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                relay.tailnet_ipv4(mock(bad))
        self.assertEqual(relay.BIND,"127.0.0.1")
        self.assertEqual(relay.LISTEN,6089)
        self.assertEqual(relay.UPSTREAM_PORT,6088)
        self.assertLessEqual(relay.MAX_CLIENTS,32)

    def test_install_script_does_not_restart_existing_browser(self):
        from pathlib import Path
        code=(Path(__file__).with_name(
            "install-btdigg-private-novnc-https.sh"
        )).read_text(encoding="utf8")
        self.assertIn("tailscale serve --bg --https=8444",code)
        self.assertIn("http://127.0.0.1:6089",code)
        self.assertIn("CHROMIUM_18896=UNCHANGED",code)
        self.assertIn("Tailscale port 8444 already configured",code)
        self.assertNotIn("tailscale funnel --",code)
        self.assertNotIn("tailscale serve reset",code)
        self.assertNotIn("systemctl --user restart magnetra-btdigg-browser",code)
        self.assertNotIn("systemctl restart magnetra-btdigg",code)


class PrivateNoVNCStreamingTests(unittest.IsolatedAsyncioTestCase):
    async def test_transparent_bidirectional_tcp_through_loopback_only(self):
        # The fixture substitutes a local echo service for websockify.
        async def echo(reader,writer):
            try:
                while data:=await reader.read(65536):
                    writer.write(data)
                    await writer.drain()
            finally:
                writer.close()
                await writer.wait_closed()
        server=await asyncio.start_server(echo,"127.0.0.1",0)
        dest=server.sockets[0].getsockname()[1]
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1",0))
            listen=sock.getsockname()[1]
        with patch.object(relay,"LISTEN",listen),patch.object(
                relay,"UPSTREAM_PORT",dest):
            task=asyncio.create_task(relay.serve_private_relay("127.0.0.1"))
            try:
                reader=writer=None
                for _ in range(25):
                    try:
                        reader,writer=await asyncio.open_connection(
                            "127.0.0.1",listen)
                        break
                    except ConnectionRefusedError:
                        await asyncio.sleep(0.01)
                self.assertIsNotNone(reader)
                msg=b"GET /vnc.html HTTP/1.1\r\nHost: fixture\r\n\r\n"
                writer.write(msg)
                await writer.drain()
                self.assertEqual(await asyncio.wait_for(reader.readexactly(
                    len(msg)),timeout=2),msg)
                writer.close()
                await writer.wait_closed()
            finally:
                task.cancel()
                with self.assertRaises(asyncio.CancelledError):
                    await task
                server.close()
                await server.wait_closed()

if __name__=="__main__":
    unittest.main()
