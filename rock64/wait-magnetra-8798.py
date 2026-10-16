#!/usr/bin/env python3
"""Bounded loopback readiness check for the existing authenticated port 8798.

systemctl restart of a Type=simple unit can return before the Python HTTP
listener is bound. Probe unauthenticated /healthz on 127.0.0.1:8798 until 401
or a strict deadline. The retry is ONLY for this local socket readiness check;
never retry upstream providers, torrent requests, credentials, or 429/403.
"""
from __future__ import annotations

import http.client
import sys
import time

HOST = "127.0.0.1"
PORT = 8798
HEALTH_PATH = "/healthz"
MAX_WAIT_SEC = 12.0
CONNECT_TIMEOUT_SEC = 1.0
SLEEP_SEC = 0.25


def wait_for_authenticated_listener(
    *,
    max_wait=MAX_WAIT_SEC,
    connection_factory=http.client.HTTPConnection,
    clock=time.monotonic,
    sleeper=time.sleep,
):
    """Return (ready, status); unexpected HTTP is immediately fatal, not retried."""
    deadline = clock() + max_wait
    while True:
        conn = None
        try:
            conn = connection_factory(HOST, PORT, timeout=CONNECT_TIMEOUT_SEC)
            conn.request("GET", HEALTH_PATH)
            response = conn.getresponse()
            status = response.status
            response.read(512)
            # Any HTTP status demonstrates a listening server; only 401 is safe.
            return (status == 401, status)
        except (OSError, TimeoutError, http.client.HTTPException):
            pass  # normal short-lived closed socket immediately after restart
        finally:
            if conn is not None:
                conn.close()
        remaining = deadline - clock()
        if remaining <= 0:
            return (False, None)
        sleeper(min(SLEEP_SEC, remaining))


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if args not in (["--post-restart"], ["--rollback"]):
        print("STOP: expected --post-restart or --rollback, read-only.", file=sys.stderr)
        return 2
    ok, code = wait_for_authenticated_listener()
    label = "POST_RESTART" if args[0] == "--post-restart" else "ROLLBACK"
    if ok:
        print(label + "_READY: loopback 8798 responded HTTP 401")
        return 0
    result = "NO_LISTENER_WITHIN_12S" if code is None else "UNEXPECTED_HTTP_" + str(code)
    print("STOP: " + label + "_NOT_READY: " + result, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
