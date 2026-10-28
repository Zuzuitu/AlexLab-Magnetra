#!/usr/bin/env python3
"""Offline safety and original-gateway parity tests; no source/network traffic."""
import importlib.util
import os
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

PATH=Path(__file__).with_name("btdigg_cffi_gateway.py")
SPEC=importlib.util.spec_from_file_location("bt_cffi_entry",PATH)
ENTRY=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ENTRY)
TOKEN="t"*64


class Response:
    status_code=200
    headers={"content-type":"text/html; charset=utf-8"}
    def __init__(self):
        self.closed=False
    def iter_content(self,chunk_size=65536):
        yield b"<html><div class='one_result'>valid source row</div></html>"
    def close(self):
        self.closed=True


class MockTransport:
    def __init__(self):
        self.calls=0
    def get(self,url,**options):
        self.calls+=1
        if url!="https://btdig.com/search" or options["allow_redirects"]:
            raise AssertionError("unexpected source")
        return Response()


class AlternateGatewayTests(unittest.TestCase):
    def test_default_disabled_even_with_secret(self):
        with patch.dict(os.environ,{"MAGNETRA_BTDIGG_TOKEN":TOKEN,
             "MAGNETRA_BTDIGG_CFFI_OPT_IN":"0",
             "MAGNETRA_BTDIGG_SOURCE_PERMISSION_CONFIRMED":"0"}):
            with self.assertRaisesRegex(SystemExit,"opt-in not approved"):
                ENTRY.main()

    def test_no_source_authorization_refuses_before_import(self):
        with patch.dict(os.environ,{"MAGNETRA_BTDIGG_TOKEN":TOKEN,
             "MAGNETRA_BTDIGG_CFFI_OPT_IN":"1",
             "MAGNETRA_BTDIGG_SOURCE_PERMISSION_CONFIRMED":"0"}):
            with self.assertRaisesRegex(SystemExit,"source authorization not confirmed"):
                ENTRY.main()

    def test_authorized_mode_still_requires_existing_strong_secret(self):
        with patch.dict(os.environ,{"MAGNETRA_BTDIGG_TOKEN":"x",
             "MAGNETRA_BTDIGG_CFFI_OPT_IN":"1",
             "MAGNETRA_BTDIGG_SOURCE_PERMISSION_CONFIRMED":"1"}):
            with self.assertRaisesRegex(SystemExit,"invalid original BTDigg gateway credential"):
                ENTRY.main()

    def test_bounded_original_cache_singleflight_semantics_still_apply(self):
        now=[100.0]
        transport=MockTransport()
        provider=ENTRY.create_provider(transport=transport,clock=lambda:now[0])
        code,html=provider.search("The Dog Stars 2026")
        self.assertEqual(code,200)
        self.assertIn(b"one_result",html)
        self.assertEqual(provider.search("The Dog Stars 2026"),(200,html))
        self.assertEqual(transport.calls,1,"same positive query must reuse cache")
        self.assertEqual(provider.search("other query"),(429,b""),
            "new query must honor original five-second source interval")
        self.assertEqual(transport.calls,1)
        now[0]+=6
        self.assertEqual(provider.search("other query")[0],200)
        self.assertEqual(transport.calls,2)

    def test_opted_in_service_reuses_original_loopback_handler_without_printing_secret(self):
        fakecffi=types.ModuleType("curl_cffi")
        fakecffi.requests=object()
        events=[]
        class Server:
            def __init__(self,addr,handler):
                events.append(("bind",addr,handler.__name__))
            def serve_forever(self,poll_interval=0.5):
                events.append(("serve",poll_interval))
            def server_close(self):
                events.append(("close",))
        original=ENTRY._load("btdigg_gateway")
        original.LimitedHTTPServer=Server
        old_load=ENTRY._load
        with (patch.dict(os.environ,{"MAGNETRA_BTDIGG_TOKEN":TOKEN,
                "MAGNETRA_BTDIGG_CFFI_OPT_IN":"1",
                "MAGNETRA_BTDIGG_SOURCE_PERMISSION_CONFIRMED":"1"}),
              patch.dict(sys.modules,{"curl_cffi":fakecffi}),
              patch.object(ENTRY,"_load",side_effect=lambda name:original if name=="btdigg_gateway" else old_load(name)),
              patch("builtins.print")):
            ENTRY.main()
        self.assertEqual(events[0][:2],("bind",("127.0.0.1",8796)))
        self.assertEqual(events[1:], [("serve",0.5),("close",)])

if __name__=="__main__":
    unittest.main()
