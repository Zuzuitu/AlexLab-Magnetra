#!/usr/bin/env python3
"""Evidence-only probe of 1 exact TheRarBg detail's HTML and same-origin JSON.
No hash, magnet, title, HTML, source URL, API body or exception printed.
No redirects, retries, other hosts or torrent downloads.
"""
from __future__ import annotations
from html.parser import HTMLParser
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError, URLError
import json
import re
import sys

DETAIL="https://therarbg.com/post-detail/95bf8b/2026-10-20-cyberpunk-edgerunners-2-original-series-soundtrack-flac-44-1khz-24bit/"
JSON_DETAIL=DETAIL+"?format=json"
HEADERS={"User-Agent":"Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36",
         "Accept-Language":"en-US,en;q=0.9","Accept":"text/html,application/xhtml+xml,application/json"}
MAX=3_000_000
HEX=re.compile(r"^[0-9a-fA-F]{40}$")
BTIH=re.compile(r"^magnet:\?xt=urn:btih:([0-9a-fA-F]{40})(?:&|$)",re.I)
LABELED=re.compile(r"\bInfo\s*Hash\s*:\s*([0-9a-fA-F]{40})\b",re.I)

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args):return None

class Shape(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hide=0
        self.words=[]
        self.magnetHashes=set()
        self.magnetCount=0
    def handle_starttag(self,tag,attrs):
        if tag in ("script","style","noscript","template"):self.hide+=1
        if tag=="a":
            href=dict(attrs).get("href","")
            if href.startswith("magnet:?"):
                self.magnetCount+=1
                m=BTIH.match(href)
                if m:self.magnetHashes.add(m[1].lower())
    def handle_endtag(self,tag):
        if tag in ("script","style","noscript","template"):self.hide=max(0,self.hide-1)
    def handle_data(self,txt):
        if not self.hide:self.words.append(txt)
    def hashes(self):
        txt=" ".join(" ".join(self.words).split())
        return {m.group(1).lower() for m in LABELED.finditer(txt)}

def fetch_once(target):
    # Constants only: no user-controlled destination or open proxy
    assert target in (DETAIL,JSON_DETAIL)
    opener=build_opener(NoRedirect())
    try:
        with opener.open(Request(target,headers=HEADERS,method="GET"),timeout=12) as response:
            status=response.status
            content_type=response.headers.get("content-type","").split(";",1)[0].lower()
            data=response.read(MAX+1)
    except HTTPError as e:
        return ("SOURCE_HTTP_"+str(e.code) if e.code in (403,404,429,500,502,503,504) else "SOURCE_HTTP_OTHER",None,None)
    except (URLError,TimeoutError,OSError):
        return ("SOURCE_NETWORK",None,None)
    if status!=200:return ("SOURCE_HTTP_OTHER",None,None)
    if len(data)>MAX:return ("SOURCE_OVERSIZE",None,None)
    return ("OK",content_type,data)

def json_hash(data):
    try: obj=json.loads(data)
    except (ValueError,UnicodeError):return "INVALID_JSON",set()
    root=obj.get("data") if isinstance(obj,dict) and isinstance(obj.get("data"),dict) else obj
    if not isinstance(root,dict):return "JSON_OBJECT_UNEXPECTED",set()
    h=root.get("info_hash")
    if isinstance(h,str) and HEX.fullmatch(h):return "JSON_INFO_HASH_VALID",{h.lower()}
    return ("JSON_INFO_HASH_ABSENT" if h is None else "JSON_INFO_HASH_INVALID"),set()

def main():
    html_status,html_type,html=fetch_once(DETAIL)
    html_hashes=set()
    magnet_hashes=set()
    anchor_count=0
    if html_status=="OK" and html_type in ("text/html","application/xhtml+xml"):
        parser=Shape()
        try:parser.feed(html.decode("utf-8"))
        except UnicodeError:html_status="SOURCE_ENCODING"
        else:
            html_hashes=parser.hashes()
            magnet_hashes=parser.magnetHashes
            anchor_count=parser.magnetCount
    elif html_status=="OK":
        html_status="SOURCE_NOT_HTML"
    print("ORIGINAL_HTML_STATUS:",html_status)
    print("ORIGINAL_LABELLED_BTIH_UNIQUE:",len(html_hashes))
    print("ORIGINAL_MAGNET_ANCHOR_COUNT:",anchor_count)
    print("ORIGINAL_MAGNET_BTIH_UNIQUE:",len(magnet_hashes))
    print("ORIGINAL_VISIBLE_AND_LINK_AGREE:",
          len(html_hashes)==len(magnet_hashes)==1 and html_hashes==magnet_hashes)

    status,ct,body=fetch_once(JSON_DETAIL)
    json_state="NOT_AVAILABLE"
    hashes=set()
    if status=="OK" and ct in ("application/json","text/json"):
        json_state,hashes=json_hash(body)
    elif status=="OK" and ct in ("text/html","application/xhtml+xml"):
        json_state="HTML_NOT_JSON"
    else:json_state=status if status!="OK" else "NON_JSON_CONTENT_TYPE"
    print("SAME_ORIGIN_JSON_STATUS:",json_state)
    print("SAME_ORIGIN_JSON_INFO_HASH_VALID:",len(hashes)==1)
    print("JSON_HASH_MATCHES_ORIGINAL:",
          len(hashes)==len(html_hashes)==1 and hashes==html_hashes)
    print("DIAGNOSTIC_COMPLETED_READ_ONLY:",True)
    return 0
if __name__=="__main__":sys.exit(main())
