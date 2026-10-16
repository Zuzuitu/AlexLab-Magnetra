#!/usr/bin/env python3
"""Fully offline deterministic readiness/race regression. No real socket or systemctl."""
import importlib.util
import pathlib
import sys
import unittest

FILE = pathlib.Path(__file__).with_name("wait-magnetra-8798.py")
spec = importlib.util.spec_from_file_location("magnetra_8798_readiness", FILE)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


class Clock:
    def __init__(self):
        self.time = 0
        self.delays = []
    def now(self):
        return self.time
    def sleep(self, delay):
        assert 0 < delay <= mod.SLEEP_SEC
        self.delays.append(delay)
        self.time += delay


class Response:
    def __init__(self, status):
        self.status = status
    def read(self, length):
        assert length == 512
        return b""


class FakeConnection:
    def __init__(self, status, calls):
        self.status = status
        self.calls = calls
    def request(self, method, path):
        self.calls.append((method, path))
    def getresponse(self):
        if isinstance(self.status, Exception):
            raise self.status
        return Response(self.status)
    def close(self):
        self.calls.append(("close", None))


class WaitTests(unittest.TestCase):
    def test_bounded_loopback_and_configuration(self):
        self.assertEqual((mod.HOST, mod.PORT, mod.HEALTH_PATH),
                         ("127.0.0.1", 8798, "/healthz"))
        self.assertLessEqual(mod.MAX_WAIT_SEC, 12)
        self.assertLessEqual(mod.CONNECT_TIMEOUT_SEC, 1)
        self.assertLessEqual(mod.SLEEP_SEC, 0.25)

    def test_realistic_systemd_race_refused_twice_then_401(self):
        clock = Clock()
        attempts = []
        events = []
        sequence = [ConnectionRefusedError(111, "refused"),
                    ConnectionRefusedError(111, "refused"), 401]
        def factory(host, port, timeout):
            self.assertEqual((host, port, timeout),
                             ("127.0.0.1", 8798, 1))
            attempts.append(1)
            return FakeConnection(sequence.pop(0), events)
        success, status = mod.wait_for_authenticated_listener(
            connection_factory=factory, clock=clock.now, sleeper=clock.sleep)
        self.assertEqual((success, status), (True, 401))
        self.assertEqual(len(attempts), 3)
        self.assertEqual(clock.time, 0.5)
        self.assertEqual(len(clock.delays), 2)
        self.assertEqual(events.count(("GET", "/healthz")), 3)

    def test_immediately_ready_does_not_sleep(self):
        clock = Clock()
        def factory(*args, **kwargs):
            return FakeConnection(401, [])
        self.assertEqual(mod.wait_for_authenticated_listener(
            connection_factory=factory, clock=clock.now, sleeper=clock.sleep),
            (True, 401))
        self.assertEqual(clock.delays, [])

    def test_unexpected_200_is_fatal_not_interpreted_as_ready(self):
        clock = Clock()
        attempts = []
        def factory(*args, **kwargs):
            attempts.append(1)
            return FakeConnection(200, [])
        self.assertEqual(mod.wait_for_authenticated_listener(
            connection_factory=factory, clock=clock.now, sleeper=clock.sleep),
            (False, 200))
        self.assertEqual(len(attempts), 1)
        self.assertEqual(clock.delays, [])

    def test_closed_socket_entire_window_times_out_no_infinite_retry(self):
        clock = Clock()
        attempts = []
        def factory(*args, **kwargs):
            attempts.append(1)
            return FakeConnection(ConnectionRefusedError(111, "refused"), [])
        self.assertEqual(mod.wait_for_authenticated_listener(
            max_wait=1.0, connection_factory=factory,
            clock=clock.now, sleeper=clock.sleep), (False, None))
        self.assertEqual(len(attempts), 5)
        self.assertEqual(clock.time, 1.0)

    def test_nonexistent_wrong_args_fail_closed(self):
        self.assertEqual(mod.main(["--retries-unbounded"]), 2)
        self.assertEqual(mod.main([]), 2)
        self.assertEqual(mod.main(["--rollback", "--post-restart"]), 2)


if __name__ == "__main__":
    unittest.main()
