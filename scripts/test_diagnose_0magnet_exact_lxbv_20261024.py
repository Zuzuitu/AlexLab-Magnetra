import io
import json
import os
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch
import diagnose_0magnet_exact_lxbv_20261024 as d

HASH="0123456789abcdef0123456789abcdef01234567"
MAGNET="magnet:?xt=urn:btih:"+HASH
HTML=('<input type="text" id="input-magnet" value="'+MAGNET+'&amp;dn=fixture">').encode()

class ExactOwnerTests(unittest.TestCase):
    def test_fixed_allowlisted_exact_url(self):
        self.assertEqual(d.SOURCE,"https://9mag.net/!lxbV")
        self.assertEqual(d.PROD,"https://index.alexlab.media")
        self.assertEqual(d.origin_redirect_kind("https://9mag.net/!another"),"SAME_ORIGIN")
        self.assertEqual(d.origin_redirect_kind("/!relative"),"SAME_ORIGIN_RELATIVE")
        self.assertEqual(d.origin_redirect_kind("https://evil.example/token"),"OUTSIDE_ORIGIN")

    def test_original_static_input_and_btih(self):
        outcome,h=d.html_classify("text/html",HTML)
        self.assertEqual((outcome,h),("SOURCE_INPUT_MAGNET_VALID",HASH))
        self.assertEqual(d.html_classify("text/html",b'<input id="input-magnet">')[0],
                         "SOURCE_INPUT_VALUE_MISSING")
        self.assertEqual(d.html_classify("text/html",b'<input id="input-magnet" value="bad">')[0],
                         "SOURCE_INPUT_VALUE_INVALID")
        self.assertEqual(d.html_classify("text/html",b'<span>no input</span>')[0],
                         "SOURCE_INPUT_MISSING")
        self.assertEqual(d.html_classify("text/html",HTML+HTML)[0],
                         "SOURCE_INPUT_DUPLICATED")
        self.assertEqual(d.html_classify("application/json",HTML)[0],"SOURCE_NOT_HTML")

    def test_production_502_classification_without_raw_strings(self):
        body=json.dumps({"error":"Provider could not resolve magnet: provider HTTP 403","secret":MAGNET}).encode()
        self.assertEqual(d.response_class(502,"application/json",body)[0],"UPSTREAM_HTTP_403")
        body=json.dumps({"error":"Provider could not resolve magnet: provider details page contains no supported magnet link"}).encode()
        self.assertEqual(d.response_class(502,"application/json",body)[0],"MAGNET_NOT_FOUND_IN_HTML")
        self.assertEqual(d.response_class(200,"application/json",json.dumps({"magnet":MAGNET}).encode()),
                         ("VALID_MAGNET",HASH))
        self.assertEqual(d.response_class(200,"text/html",HTML)[0],"NON_JSON")

    def test_exact_result_identity_no_fuzzy_fallback(self):
        rows=[{"provider":"0magnet","details":"https://9mag.net/!another","magnet":MAGNET},
              {"provider":"0magnet","details":d.SOURCE,"magnet":None}]
        self.assertEqual(d.exact_record_count("application/json",json.dumps({"results":rows}).encode()),
                         ("ONE","ABSENT","ABSENT"))
        self.assertEqual(d.exact_record_count("application/json",json.dumps({"results":rows[:1]}).encode()),
                         ("ZERO","ABSENT","ABSENT"))
        with self.assertRaisesRegex(d.Stop,"DUPLICATE_EXACT_CARD"):
            d.exact_record_count("application/json",json.dumps({"results":rows[1:]*2}).encode())

    def test_no_calls_without_approval(self):
        with patch.object(d.sys,"argv",["script"]),patch.object(d,"fetch_once") as req:
            self.assertEqual(d.main(),2)
            req.assert_not_called()

    def test_one_owner_card_one_source_one_worker_never_echo_values(self):
        records={"results":[{"provider":"0magnet","details":d.SOURCE,"magnet":None,"name":"SECRET_TITLE"}]}
        def fake(url,*,payload=None,source=False):
            calls.append((url,payload,source))
            if "/api/search?" in url:
                return 200,"application/json",json.dumps(records).encode(),None
            if url==d.SOURCE:
                return 200,"text/html",HTML,None
            if url==d.PROD+"/api/resolve":
                self.assertEqual(payload,{"provider":"0magnet","details":d.SOURCE})
                return 200,"application/json",json.dumps({"magnet":MAGNET}).encode(),None
            self.fail("unexpected request")
        calls=[]
        out=io.StringIO()
        with patch.dict(os.environ,{"MAGNETRA_0MAGNET_EXACT_APPROVAL":d.APPROVAL}),\
             patch.object(d,"fetch_once",fake),redirect_stdout(out):
            self.assertEqual(d.execute(),0)
        self.assertEqual(len(calls),3)
        self.assertIn("EXACT_SOURCE_AND_WORKER_BTih_EQUAL: YES",out.getvalue())
        for secret in (MAGNET,HASH,d.SOURCE,"SECRET_TITLE","!lxbV"):
            self.assertNotIn(secret,out.getvalue())

    def test_direct_http429_stops_before_resolver(self):
        calls=[]
        def fake(url,*,payload=None,source=False):
            calls.append(url)
            if "/api/search" in url:return 200,"application/json",b'{"results":[]}',None
            if url==d.SOURCE:return 429,"",b"",None
            self.fail("Unexpected retry or resolver POST after rate limit")
        with patch.dict(os.environ,{"MAGNETRA_0MAGNET_EXACT_APPROVAL":d.APPROVAL}),\
             patch.object(d,"fetch_once",fake),redirect_stdout(io.StringIO()):
            self.assertEqual(d.execute(),0)
        self.assertEqual(len(calls),2)

if __name__=="__main__":unittest.main()
