#!/usr/bin/env python3
"""Local-only TCP relay: HTTPS Tailscale Serve -> existing tailnet-only noVNC.

The already-running BTDigg GUI binds websockify to the local machine's
Tailscale IPv4:6088 and cannot be restarted without risking a solved CAPTCHA.
Tailscale Serve proxies only local loopback backends, so a small transparent
TCP relay on 127.0.0.1:6089 is necessary to preserve that GUI. The relay
does not inspect, store, log, interpret, or modify VNC, HTTP, or WebSocket
data. It has no Internet egress and is never exposed outside loopback.

This is NOT a CAPTCHA solver or a browser automation service.
"""
from __future__ import annotations
import asyncio
import ipaddress
import subprocess
import sys

BIND = "127.0.0.1"
LISTEN = 6089
UPSTREAM_PORT = 6088
MAX_CLIENTS = 24
BUFFER_SIZE = 64 * 1024


def tailnet_ipv4(run=subprocess.run):
    completed = run(
        ["/usr/bin/tailscale", "ip", "-4"],
        capture_output=True, text=True, timeout=5, check=True
    )
    value = completed.stdout.strip()
    address = ipaddress.IPv4Address(value)
    if address not in ipaddress.IPv4Network("100.64.0.0/10"):
        raise ValueError("not a private tailnet IPv4")
    return str(address)


async def copy_stream(reader, writer):
    try:
        while True:
            data = await reader.read(BUFFER_SIZE)
            if not data:
                break
            writer.write(data)
            await writer.drain()
    except (ConnectionError, OSError):
        pass
    finally:
        if writer.can_write_eof():
            try:
                writer.write_eof()
            except (ConnectionError, OSError):
                pass


async def serve_private_relay(host):
    quota = asyncio.Semaphore(MAX_CLIENTS)

    async def handle(reader, client):
        async with quota:
            upstream = None
            try:
                upstream_reader, upstream = await asyncio.wait_for(
                    asyncio.open_connection(host, UPSTREAM_PORT),
                    timeout=5
                )
                await asyncio.gather(
                    copy_stream(reader, upstream),
                    copy_stream(upstream_reader, client)
                )
            except (ConnectionError, OSError, asyncio.TimeoutError):
                pass
            finally:
                if upstream:
                    upstream.close()
                    try:
                        await upstream.wait_closed()
                    except (ConnectionError, OSError):
                        pass
                client.close()
                try:
                    await client.wait_closed()
                except (ConnectionError, OSError):
                    pass

    server = await asyncio.start_server(handle, BIND, LISTEN, backlog=32)
    async with server:
        await server.serve_forever()


def main():
    try:
        host = tailnet_ipv4()
    except (OSError, ValueError, subprocess.CalledProcessError,
            subprocess.TimeoutExpired):
        print("STOP: no valid local Tailscale address; relay not started.",
              file=sys.stderr)
        return 1
    try:
        asyncio.run(serve_private_relay(host))
    except (OSError, KeyboardInterrupt):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
