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


    def test_diagnostic_is_single_record_and_contains_no_query_or_exception(self):
        records = []
        secret = "PRIVATE_SEARCH_TERM_DO_NOT_LOG"
        class CurlLikeError(Exception):
            def __init__(self, code):
                super().__init__("sensitive URL, token and cookie " + secret)
                self.code = code
        for code, expected in [
            (6, "dns_resolution_failed"), (7, "connect_failed"),
            (28, "pre_headers_timeout_unresolved"),
            (35, "tls_handshake_failed"), (60, "tls_certificate_failed"),
            (56, "receive_failed"), (99, "pre_headers_failed_unclassified")
        ]:
            with self.subTest(code=code):
                records.clear()
                c = FakeClient(error=CurlLikeError(code))
                self.assertEqual(candidate.fetch_one(secret, client=c, report=records.append), (504, b""))
                self.assertEqual(len(c.calls), 1, "no background retry")
                self.assertEqual(len(records), 1)
                item = records[0]
                self.assertEqual(item["event"], "btdigg_cffi_transport")
                self.assertEqual(item["gateway_status"], 504)
                self.assertEqual(item["source_status"], None)
                self.assertEqual(item["phase"], "pre_headers")
                self.assertEqual(item["failure"], expected)
                self.assertEqual(item["curl_code"], code if code in candidate.CURL_FAILURES else None)
                self.assertGreaterEqual(item["duration_ms"], 0)
                text = str(item)
                self.assertNotIn(secret, text)
                self.assertNotIn("cookie", text)
                self.assertNotIn("btdig.com", text)

    def test_real_cffi_intenum_error_codes_are_recognized(self):
        from enum import IntEnum
        class CurlCode(IntEnum):
            DNS = 6
            TCP = 7
            TIMEOUT = 28
        class CffiStyleError(Exception):
            def __init__(self, value):
                self.code = value
                super().__init__("private URL and cookies")
        for value,expected in [(CurlCode.DNS,"dns_resolution_failed"),
                               (CurlCode.TCP,"connect_failed"),
                               (CurlCode.TIMEOUT,"pre_headers_timeout_unresolved")]:
            with self.subTest(code=value):
                rows=[]
                code,body=candidate.fetch_one("PSA 1080p", client=FakeClient(error=CffiStyleError(value)),
                                              report=rows.append)
                self.assertEqual((code,body),(504,b""))
                self.assertEqual(rows[0]["failure"],expected)
                self.assertEqual(rows[0]["curl_code"],int(value))
                self.assertIs(type(rows[0]["curl_code"]),int)

    def test_cffi_generic_timeout_cannot_be_falsely_attributed_to_tcp(self):
        reports = []
        candidate.fetch_one("other terms", client=FakeClient(error=TimeoutError("sensitive")),
                            report=reports.append)
        self.assertEqual(reports[0]["failure"], "pre_headers_timeout_unresolved")
        self.assertIsNone(reports[0]["curl_code"])

    def test_body_stream_timeout_is_distinct_from_timeout_before_headers(self):
        class CurlLikeError(Exception):
            code = 28
        class LateFailure(FakeResponse):
            def iter_content(self, chunk_size=65536):
                raise CurlLikeError("secret full URL")
                yield b""
        rows=[]
        value=candidate.fetch_one("search phrase",client=FakeClient(response=LateFailure()),
                                  report=rows.append)
        self.assertEqual(value,(504,b""))
        self.assertEqual(rows[0]["failure"],"body_timeout")
        self.assertEqual(rows[0]["phase"],"body")
        self.assertEqual(rows[0]["source_status"],200)

    def test_diagnostic_on_http_429_and_genuine_success_preserves_status(self):
        for status, expected in [(429,"http_429"),(200,"none")]:
            rows=[]
            c=FakeClient(response=FakeResponse(status=status))
            code,content=candidate.fetch_one("terms",client=c,report=rows.append)
            self.assertEqual(code,status)
            self.assertEqual(rows[0]["gateway_status"],status)
            self.assertEqual(rows[0]["source_status"],status)
            self.assertEqual(rows[0]["failure"],expected)
            self.assertEqual(len(c.calls),1)
            if status==200:self.assertIn(b"one_result",content)

    def test_journal_serializer_emits_only_numeric_or_fixed_public_keys(self):
        import json
        from unittest.mock import patch
        with patch("builtins.print") as output:
            candidate._journal({"event":"btdigg_cffi_transport","failure":"none",
                                "gateway_status":200,"source_status":200,
                                "phase":"body","curl_code":None,"duration_ms":10})
        payload=output.call_args.args[0]
        self.assertEqual(json.loads(payload)["event"],"btdigg_cffi_transport")
        self.assertEqual(output.call_args.kwargs.get("flush"),True)

    def test_diagnostic_reporter_failure_does_not_break_real_source_output(self):
        def broken_report(record): raise RuntimeError("log system unavailable")
        status, body=candidate.fetch_one("ubuntu",client=FakeClient(),report=broken_report)
        self.assertEqual(status,200)
        self.assertIn(b"one_result",body)


if __name__=="__main__":
    unittest.main()
