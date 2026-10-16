#!/usr/bin/env python3
"""Offline 8798 source acceptance tests; no source HTTP, no private credentials."""
import contextlib
import importlib.util
import io
import json
import pathlib
import sys
import unittest
from unittest.mock import patch

PATH=pathlib.Path(__file__).with_name("check-magnetra-html.py")
spec=importlib.util.spec_from_file_location("magnetra_html_acceptance",PATH)
mod=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=mod
spec.loader.exec_module(mod)
MAGNET="magnet:?xt=urn:btih:"+"a"*40
SENSITIVE="ubuntu-PrivateVeryLongTitle"
SEARCH=("<html><table><tbody><tr><td><a href='/torrent/123/ubuntu-test'>"+
        SENSITIVE+"</a></td><td>3</td><td>4</td><td>5</td><td>6</td></tr>"+
        "</tbody></table></html>").encode()
DETAIL=("<html><div class='btn-magnet'><a href='"+MAGNET+"'>Download</a></div></html>").encode()


class FakeConn:
    events=[]
    def __init__(self,host,port,timeout):
        assert host=="127.0.0.1" and port==8798 and timeout==12
    def request(self,method,path,headers):
        assert method=="GET" and headers["Authorization"]=="Bearer "+"S"*64
        self.path=path
        self.events.append(path)
    def getresponse(self):
        data=DETAIL if "mode=detail" in self.path else SEARCH
        class R:
            status=200
            def getheader(self,k):return "text/html" if k=="content-type" else None
            def read(self,n):
                assert n==mod.MAX_BYTES+1
                return data
        return R()
    def close(self):pass


class AcceptanceTest(unittest.TestCase):
    def setUp(self):
        FakeConn.events=[]
    def test_both_sources_end_to_end_loopback_no_info_leak(self):
        for source in mod.probe.SOURCES:
            result=mod.check(source,"S"*64,connector=FakeConn)
            self.assertEqual(result["search"]["http"],200)
            self.assertEqual(result["query_matches"],1)
            self.assertTrue(result["details_checked"])
            self.assertTrue(result["valid_magnet_anchor"])
            self.assertNotIn(SENSITIVE,str(result))
            self.assertNotIn(MAGNET,str(result))
        self.assertEqual(len(FakeConn.events),4)
        self.assertTrue(all(s.startswith("/v1/") for s in FakeConn.events))
        self.assertTrue(all("evil.invalid" not in s for s in FakeConn.events))
    def test_unknown_provider_rejected(self):
        with self.assertRaises(ValueError):
            mod.check(mod.probe.Source("bad","https://evil.invalid",4,""),"S"*64,connector=FakeConn)
    def test_no_source_match_never_requests_details(self):
        class SearchOnly(FakeConn):
            def getresponse(self):
                class R:
                    status=200
                    def getheader(self,k):return "text/html"
                    def read(self,n):return b"<table><tbody><tr><td>Not a result</td></tr></tbody></table>"
                return R()
        x=mod.check(mod.probe.SOURCES[0],"S"*64,connector=SearchOnly)
        self.assertFalse(x["details_checked"])
        self.assertEqual(len(FakeConn.events),1)
    def test_failure_does_not_print_credential_or_source_payload(self):
        with patch.object(mod,"private_token",return_value="S"*64),\
             patch.object(mod,"check",return_value={
                 "provider":"oxtorrent","search":{"http":403},
                 "query_matches":0,"details":None,"valid_magnet_anchor":False
             }),contextlib.redirect_stdout(io.StringIO()) as capture:
            self.assertEqual(mod.main(),1)
        printed=capture.getvalue()
        self.assertNotIn("S"*64,printed)
        self.assertNotIn(MAGNET,printed)


if __name__=="__main__":
    unittest.main()
