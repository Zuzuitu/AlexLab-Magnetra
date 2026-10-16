#!/usr/bin/env python3
"""Offline contract tests for strictly allowlisted OxTorrent/Torrent9 egress."""
import importlib.util
import pathlib
import sys
import unittest
from email.message import Message
from urllib.error import HTTPError, URLError

PATH=pathlib.Path(__file__).with_name("magnetra_html_egress.py")
spec=importlib.util.spec_from_file_location("magnetra_html_egress_test",PATH)
mod=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=mod
spec.loader.exec_module(mod)


class Response:
    status=200
    def __init__(self,body=b"<html><tbody>test</tbody></html>",content_type="text/html",extra=None):
        self.data=body
        self.headers=Message()
        self.headers["content-type"]=content_type
        self.headers["content-length"]=str(len(body))
        for key,value in (extra or {}).items():
            self.headers[key]=value
    def __enter__(self):return self
    def __exit__(self,*_):pass
    def read(self,n):return self.data[:n]


class HTMLGatewayTests(unittest.TestCase):
    def test_two_verified_hosts_only_and_no_arbitrary_proxy(self):
        self.assertEqual(set(mod.SOURCES),{"oxtorrent","torrent9"})
        self.assertEqual(mod.fixed_source_url("oxtorrent","search","ubuntu"),
                         "https://www.oxtorrent.co/recherche/ubuntu")
        self.assertEqual(mod.fixed_source_url("torrent9","search","ubuntu"),
                         "https://www7.torrent9.to/search_torrent/ubuntu.html")
        self.assertEqual(mod.fixed_source_url("oxtorrent","detail","/torrent/123/ubuntu"),
                         "https://www.oxtorrent.co/torrent/123/ubuntu")
        self.assertEqual(mod.fixed_source_url("torrent9","detail","/torrent/123/ubuntu"),
                         "https://www7.torrent9.to/torrent/123/ubuntu")
        self.assertEqual(mod.TIMEOUT,8)
        self.assertLessEqual(mod.MAX_BYTES,256_000)
        for value in ("", "a", "ubuntu/other", "ubuntu?x=1", "ubuntu#fragment",
                      "a"*200, " ubuntu", "ubuntu ", "ubuntu\nother"):
            self.assertIsNone(mod.fixed_source_url("oxtorrent","search",value))
        for path in ("//evil.invalid", "https://evil.invalid/torrent/1/x",
                     "/admin/", "/recherche/ubuntu", "/torrent/abc/title",
                     "/torrent/1/ubuntu?key=secret", "/torrent/1/ubuntu#fragment",
                     "/torrent/1/../private", "/torrent/1/", "/torrent/1/x/two"):
            self.assertIsNone(mod.fixed_source_url("torrent9","detail",path))
        self.assertIsNone(mod.fixed_source_url("other","search","ubuntu"))
        self.assertIsNone(mod.fixed_source_url("oxtorrent","proxy","ubuntu"))

    def test_single_fixed_get_preserves_real_html_no_magnet_fabrication(self):
        calls=[]
        class Opener:
            def open(self,req,timeout):
                calls.append((req.full_url,req.get_method(),timeout,req.get_header("Accept")))
                return Response()
        gateway=mod.HtmlEgress(opener=Opener())
        self.assertEqual(gateway.fetch("oxtorrent","search","ubuntu"),(200,b"<html><tbody>test</tbody></html>"))
        self.assertEqual(calls,[("https://www.oxtorrent.co/recherche/ubuntu","GET",8,
                                 "text/html,application/xhtml+xml")])
        self.assertEqual(gateway.fetch("oxtorrent","detail","/torrent/1/ubuntu")[0],200)
        self.assertEqual(len(calls),2)
        self.assertEqual(gateway.fetch("oxtorrent","detail","/admin"),(400,b""))
        self.assertEqual(len(calls),2)

    def test_rate_limit_challenge_redirect_and_failure_never_retry(self):
        cases=[("429",429),("403",403),("520",502),("301",502)]
        for label,expected in cases:
            calls=[]
            class Denied:
                def open(self,req,timeout):
                    calls.append(1)
                    raise HTTPError(req.full_url,int(label),"blocked",{},None)
            self.assertEqual(mod.HtmlEgress(opener=Denied()).fetch("torrent9","search","ubuntu"),
                             (expected,b""))
            self.assertEqual(len(calls),1)
        class Challenge:
            def open(self,req,timeout):
                return Response(b"<title>Just a moment</title>")
        self.assertEqual(mod.HtmlEgress(opener=Challenge()).fetch("oxtorrent","search","ubuntu"),
                         (403,b""))
        class WrongType:
            def open(self,req,timeout):
                return Response(b'{"ok":true}',"application/json")
        self.assertEqual(mod.HtmlEgress(opener=WrongType()).fetch("oxtorrent","search","ubuntu"),
                         (502,b""))
        class TooLarge:
            def open(self,req,timeout):
                return Response(b"x"*(mod.MAX_BYTES+1))
        self.assertEqual(mod.HtmlEgress(opener=TooLarge()).fetch("oxtorrent","search","ubuntu"),
                         (502,b""))
        class Down:
            def open(self,req,timeout):
                raise URLError("do not display user URL")
        self.assertEqual(mod.HtmlEgress(opener=Down()).fetch("oxtorrent","search","ubuntu"),
                         (504,b""))


if __name__=="__main__":
    unittest.main()
