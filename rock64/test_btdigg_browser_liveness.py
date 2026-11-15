#!/usr/bin/env python3
"""Offline contracts: dead Chromium exits for systemd, not a stuck 18896."""
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from unittest import TestCase,main

from rock64 import btdigg_browser_backend as backend


class BrowserLivenessSupervisorTests(TestCase):
    def fake(self, initial=None):
        now=[0.0]
        rows=[] if initial is None else list(initial)
        calls=[]
        def reader():
            calls.append(now[0])
            return rows.pop(0)
        guard=backend.BrowserLivenessSupervisor(reader,clock=lambda:now[0])
        return now,rows,calls,guard

    def test_no_automatic_check_until_interval_and_no_network_requests(self):
        now,rows,calls,guard=self.fake([
            {"browser_connected":True,"selected_tab_verified":False,
             "visible_source_rate_limited":True},
        ])
        guard.check()
        now[0]=9.9
        guard.check()
        self.assertEqual(calls,[])
        now[0]=10
        guard.check()
        self.assertEqual(calls,[10])
        self.assertEqual(rows,[])
        self.assertEqual(guard._failures,0)

    def test_crashed_browser_dies_after_three_consecutive_checks(self):
        now,rows,calls,guard=self.fake(
            [{"browser_connected":False} for _ in range(3)]
        )
        for second in (10,20):
            now[0]=second
            guard.check()
        self.assertEqual(guard._failures,2)
        now[0]=30
        with self.assertRaisesRegex(
            backend.BrowserProcessUnavailable,"local Chromium is disconnected"
        ):
            guard.check()
        self.assertEqual(calls,[10,20,30])

    def test_valid_blank_or_captcha_tab_does_not_restart_browser(self):
        now,rows,calls,guard=self.fake([
            {"browser_connected":False},
            {"browser_connected":True,"open_tabs":1,
             "selected_tab_verified":False},
            {"browser_connected":False},
            {"browser_connected":True,"visible_captcha_required":True},
            {"browser_connected":True,"visible_source_rate_limited":True},
        ])
        for second in (10,20,30,40,50):
            now[0]=second
            guard.check()
        self.assertEqual(len(calls),5)
        self.assertEqual(guard._failures,0)

    def test_temporary_playwright_exception_requires_three_failures(self):
        now=[0.0]
        attempts=[]
        def reader():
            attempts.append(now[0])
            if len(attempts)==1:
                raise RuntimeError("private Playwright connection transient")
            return {"browser_connected":True}
        guard=backend.BrowserLivenessSupervisor(reader,clock=lambda:now[0])
        now[0]=10
        guard.check()
        self.assertEqual(guard._failures,1)
        now[0]=20
        guard.check()
        self.assertEqual(guard._failures,0)

    def test_single_threaded_http_server_uses_idle_service_actions(self):
        now=[0.0]
        calls=[]
        def reader():
            calls.append(now[0])
            return {"browser_connected":False}
        server=backend.BrowserSupervisedHTTPServer(
            ("127.0.0.1",0),BaseHTTPRequestHandler,
            reader,clock=lambda:now[0]
        )
        try:
            for second in (0,9,10,20):
                now[0]=second
                server.service_actions()
            self.assertEqual(calls,[10,20])
            now[0]=30
            with self.assertRaises(backend.BrowserProcessUnavailable):
                server.service_actions()
            self.assertEqual(calls,[10,20,30])
        finally:
            server.server_close()

    def test_existing_user_unit_has_failure_restart_and_no_new_service(self):
        installer=(Path(__file__).with_name(
            "install-btdigg-browser-autostart.sh"
        )).read_text()
        launcher=(Path(__file__).with_name(
            "run-btdigg-visual-session.sh"
        )).read_text()
        self.assertIn("Restart=on-failure",installer)
        self.assertIn("RestartSec=45s",installer)
        self.assertIn('wait "$CHROME_PID"',launcher)
        self.assertIn("BrowserSupervisedHTTPServer",Path(
            backend.__file__).read_text())
        self.assertEqual(backend.BrowserLivenessSupervisor.INTERVAL_SECONDS,10)
        self.assertEqual(
            backend.BrowserLivenessSupervisor.CONSECUTIVE_FAILURES,3
        )


if __name__=="__main__":
    main()
