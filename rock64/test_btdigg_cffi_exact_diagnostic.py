#!/usr/bin/env python3
"""Offline exact result ownership verification; zero network traffic."""
from contextlib import redirect_stdout
from io import StringIO
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).parent))
MODULE = Path(__file__).with_name("diagnose_btdigg_cffi_exact.py")
SPEC = importlib.util.spec_from_file_location("diagnose_btdigg_cffi_exact", MODULE)
diag = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(diag)

HASH = "0123456789abcdef0123456789abcdef01234567"
EXACT = "The.Dog.Stars.2026.1080p.10bit.WEBRip.6CH.x265.HEVC-PSA"

def row(title, magnet=True, size=True, wrapper=True):
    name = f'<div class="torrent_name"><a href="/torrent/{HASH}">{title}</a></div>'
    link = f'<div class="torrent_magnet"><a href="magnet:?xt=urn:btih:{HASH}&amp;dn=fixture">Magnet</a></div>' if magnet else ""
    size_html = '<span class="torrent_size">1.73 GB</span>' if size else ""
    body = name + link + size_html
    return '<div class="one_result">' + ('<div>' if wrapper else '') + body + ('</div>' if wrapper else '') + '</div>'

def run(html,status=200):
    log=[]
    with patch.object(diag, "fetch_one", return_value=(status,html.encode())) as fetch:
        result=diag.verify(report=log.append)
        fetch.assert_called_once_with(EXACT,client=None)
    return result, log

class BTDiggRealHTMLProofTests(unittest.TestCase):
    def test_exact_file_with_real_magnet_same_row(self):
        for wrapped in (False,True):
            result, log=run('<html>'+row(EXACT,wrapper=wrapped)+'</html>')
            self.assertTrue(result)
            self.assertEqual(log,["HTTP_STATUS: 200","VALID_SOURCE_ROWS: 1","EXACT_RELEASE_WITH_MAGNET: True"])

    def test_magnet_in_wrong_result_is_not_assigned_to_exact_release(self):
        page='<html>'+row(EXACT,magnet=False)+row("The Dog Stars 2026 720p WEBRip x264 Other",magnet=True)+'</html>'
        result,log=run(page)
        self.assertFalse(result)
        self.assertIn("EXACT_RELEASE_WITH_MAGNET: False",log)
        self.assertIn("VALID_SOURCE_ROWS: 1",log)

    def test_near_match_or_missing_size_or_invalid_magnet_never_counts(self):
        for title,magnet,size in [
          (EXACT.replace("PSA","OTHER"),True,True),
          (EXACT.replace("1080p","2160p"),True,True),
          (EXACT,True,False),
          (EXACT,False,True)
        ]:
            result,log=run(row(title,magnet=magnet,size=size))
            self.assertFalse(result)
            self.assertIn("EXACT_RELEASE_WITH_MAGNET: False",log)

    def test_non_200_fail_closed_without_content_or_secrets(self):
        for status in (429,503,504):
            result,log=run(row(EXACT),status)
            self.assertFalse(result)
            self.assertEqual(log,["HTTP_STATUS: "+str(status),"VALID_SOURCE_ROWS: 0","EXACT_RELEASE_WITH_MAGNET: False"])

    def test_diagnostic_never_prints_magnet_or_file_name(self):
        result,log=run(row(EXACT))
        self.assertTrue(result)
        public="\n".join(log)
        self.assertNotIn(HASH,public)
        self.assertNotIn(EXACT,public)
        self.assertNotIn("magnet:?",public)
        self.assertNotIn("1.73 GB",public)

if __name__=="__main__":
    unittest.main()
