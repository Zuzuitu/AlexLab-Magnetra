import unittest
from email.message import Message
from urllib.request import Request
import importlib.util
import pathlib

PATH = pathlib.Path(__file__).with_name("probe-blocked-indexers.py")
SPEC = importlib.util.spec_from_file_location("probe_blocked", PATH)
mod = importlib.util.module_from_spec(SPEC)
import sys
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)

class ProbeContracts(unittest.TestCase):
    def test_exact_origins_no_arbitrary_search(self):
        expected = {
            "1337x": "1337x.to",
            "BT4G": "bt4gprx.com",
            "Ext": "ext.to",
            "EZTV web": "eztvx.to",
            "EZTV API": "eztvx.to",
        }
        self.assertEqual(set(expected), {target.name for target in mod.TARGETS})
        self.assertEqual(len(mod.TARGETS), 5)
        from urllib.parse import urlsplit
        for target in mod.TARGETS:
            parsed = urlsplit(target.url)
            self.assertEqual(parsed.scheme, "https")
            self.assertEqual(parsed.hostname, expected[target.name])
            self.assertNotIn("@", target.url)
            req = mod.request_for(target)
            self.assertIsInstance(req, Request)
            self.assertEqual(req.get_method(), "GET")
            self.assertNotIn("Authorization", dict(req.header_items()))
        self.assertEqual(mod.NoRedirect().redirect_request(None,None,None,None,None,None),None)

    def test_classification_no_unauthorized_content_leaks(self):
        h = Message()
        fixtures = (
            (200, b'<table class="table-list"></table>', b'table-list', "HTTP_OK + expected page/API marker"),
            (200, b'<html>data unavailable</html>', b'table-list', "HTTP_OK, source format not verified"),
            (403, b"", b'table-list', "ACCESS_DENIED"),
            (429, b"", b'table-list', "RATE_LIMIT"),
            (302, b"", b'table-list', "REDIRECT (not followed)"),
            (503, b"", b'table-list', "HTTP_ERROR"),
            (200, b'<title>Just a moment</title>', b'table-list', "CHALLENGE"),
        )
        for status, body, marker, expected in fixtures:
            self.assertEqual(mod.describe(status,h,body,marker),expected)

    def test_transport_timeout_only_once_no_secret_print(self):
        class FakeOpener:
            def __init__(self):
                self.calls=0
            def open(self,request,timeout=None):
                self.calls+=1
                self.timeout=timeout
                raise TimeoutError()
        opener=FakeOpener()
        result,elapsed=mod.run_one(mod.TARGETS[0],opener=opener)
        self.assertEqual(result,"TRANSPORT_OR_TIMEOUT")
        self.assertEqual(opener.calls,1)
        self.assertEqual(opener.timeout,mod.TIMEOUT_SECONDS)
        self.assertGreaterEqual(elapsed,0)

if __name__ == "__main__":
    unittest.main()
