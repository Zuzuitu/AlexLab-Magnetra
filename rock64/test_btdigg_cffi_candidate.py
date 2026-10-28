#!/usr/bin/env python3
"""Offline contract tests for isolated browser-like HTTP transport candidate.

Never accesses BTDigg, installs a dependency or runs the production gateway.
"""
import importlib.util
import pathlib
import unittest

PATH=pathlib.Path(__file__).with_name("btdigg_cffi_candidate.py")
SPEC=importlib.util.spec_from_file_location("btdigg_cffi_candidate",PATH)
candidate=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(candidate)


class FakeResponse:
    def __init__(self,status=200,body=b"<!doctype html><html><div class='one_result'>original row</div></html>",headers=None):
        self.status_code=status
        self.content=body
        self.headers={"content-type":"text/html; charset=utf-8"} if headers is None else headers
        self.closed=False
    def iter_content(self,chunk_size=65536):
        for i in range(0,len(self.content),chunk_size):
            yield self.content[i:i+chunk_size]
    def close(self):
        self.closed=True


class FakeClient:
    def __init__(self,response=None,error=None):
        self.calls=[]
        self.response=response or FakeResponse()
        self.error=error
    def get(self,url,**kwargs):
        self.calls.append((url,kwargs))
        if self.error:
            raise self.error
        return self.response


class TransportCandidateTests(unittest.TestCase):
    def test_one_fixed_origin_request_with_bounded_parameters(self):
        c=FakeClient()
        code,html=candidate.fetch_one("The Dog Stars 2026",client=c)
        self.assertEqual(code,200)
        self.assertIn(b"one_result",html)
        self.assertEqual(len(c.calls),1)
        url,opts=c.calls[0]
        self.assertEqual(url,"https://btdig.com/search")
        self.assertEqual(opts["params"],{"q":"The Dog Stars 2026"})
        self.assertEqual(opts["timeout"],12)
        self.assertEqual(opts["impersonate"],"chrome")
        self.assertFalse(opts["allow_redirects"])
        self.assertEqual(set(opts),{"params","impersonate","timeout","allow_redirects","stream"})
        self.assertTrue(opts["stream"])
        self.assertTrue(c.response.closed,"stream response must close even on success")

    def test_bad_query_is_rejected_before_any_network_action(self):
        c=FakeClient()
        for query in ["", "x", "a"*181, "abc"+chr(0)+"bad", chr(9)+"url"]:
            with self.subTest(query=repr(query)):
                with self.assertRaises(ValueError):
                    candidate.fetch_one(query,client=c)
        self.assertEqual(c.calls,[])

    def test_upstream_429_is_preserved_and_not_retried(self):
        c=FakeClient(response=FakeResponse(status=429))
        self.assertEqual(candidate.fetch_one("ubuntu",client=c),(429,b""))
        self.assertEqual(len(c.calls),1)

    def test_403_redirects_and_provider_failures_are_not_browser_results(self):
        for status in [302,307,401,403,500,503]:
            c=FakeClient(response=FakeResponse(status=status))
            with self.subTest(status=status):
                self.assertEqual(candidate.fetch_one("ubuntu",client=c),(503,b""))
                self.assertEqual(len(c.calls),1)

    def test_network_error_is_redacted_without_hidden_retry(self):
        c=FakeClient(error=RuntimeError("secret cookie or private query"))
        self.assertEqual(candidate.fetch_one("ubuntu",client=c),(504,b""))
        self.assertEqual(len(c.calls),1)

    def test_stream_has_hard_three_megabyte_limit_and_closes(self):
        c=FakeClient(response=FakeResponse(body=b"<html>"+b"x"*(candidate.MAX_RESPONSE_BYTES+1)))
        self.assertEqual(candidate.fetch_one("ubuntu",client=c),(502,b""))
        self.assertTrue(c.response.closed)
        self.assertEqual(len(c.calls),1)

    def test_stream_failure_cannot_expose_raw_exception(self):
        class ErrorResponse(FakeResponse):
            def iter_content(self,chunk_size=65536):
                raise OSError("secret source exception with private network path")
                yield b""
        c=FakeClient(response=ErrorResponse())
        self.assertEqual(candidate.fetch_one("ubuntu",client=c),(504,b""))
        self.assertTrue(c.response.closed)
        self.assertEqual(len(c.calls),1)

    def test_html_content_only_and_no_challenges(self):
        failures=[
            FakeResponse(body=b'<!doctype html><html>Just a moment</html>'),
            FakeResponse(body=b'<!doctype html><html>Checking your browser</html>'),
            FakeResponse(body=b'{"results":[]}',headers={"content-type":"application/json"}),
            FakeResponse(body=b"missing html"),
            FakeResponse(body=b"<html>"+b"x"*(candidate.MAX_RESPONSE_BYTES+1)),
            FakeResponse(headers={"content-type":"text/html","content-length":"4000000"}),
        ]
        for resp in failures:
            code,body=candidate.fetch_one("ubuntu",client=FakeClient(response=resp))
            self.assertIn(code,(502,503))
            self.assertEqual(body,b"")


if __name__=="__main__":
    unittest.main()
