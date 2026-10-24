#!/usr/bin/env python3
"""One-shot owner URL 0Magnet read-only differential. Never logs torrent data.

Exactly one public search GET, one original same-source GET, one production
metadata-only /api/resolve POST, unless a stop condition occurs. No redirects
followed automatically, no retries, no .torrent, no Flud/Shield commands.
"""
from __future__ import annotations

from html.parser import HTMLParser
import json
import os
import re
from urllib.parse import urlencode, urlsplit, parse_qs
from urllib.request import Request, HTTPRedirectHandler, build_opener
from urllib.error import HTTPError, URLError
import sys

SOURCE="https://9mag.net/!lxbV"
PROD="https://index.alexlab.media"
SEARCH="Little.House.on.the.Prairie.2026"
APPROVAL="OWNER_EXACT_0MAGNET_LXBV_READONLY_20261024"
MAX=900_000
UA="Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36"
BROWSER_UA="Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1"


class Stop(Exception):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch_once(url, *, payload=None, source=False):
    # Hosts and paths are fixed by the caller. The worker POST never downloads.
    method="POST" if payload is not None else "GET"
    headers={"Accept":"text/html,application/xhtml+xml" if source else "application/json",
             "User-Agent":UA if source else BROWSER_UA,"Accept-Encoding":"identity",
             "Cache-Control":"no-store"}
    if payload is not None:
        headers["Content-Type"]="application/json"
    req=Request(url, method=method, headers=headers,
                data=json.dumps(payload).encode() if payload is not None else None)
    try:
        with build_opener(NoRedirect).open(req, timeout=20) as r:
            return r.status, r.headers.get("content-type",""), r.read(MAX+1), None
    except HTTPError as e:
        # HTTP 4xx/5xx response body may contain a safe classifiable JSON error.
        # Read and hold locally; never print the payload.
        body=e.read(MAX+1) if not source else b""
        return e.code,e.headers.get("content-type",""),body,e.headers.get("location")
    except (URLError,TimeoutError,OSError):
        return 0,"",b"",None


def infohash(magnet):
    if not isinstance(magnet,str) or not magnet.startswith("magnet:?") or len(magnet)>12000:
        return None
    xt=parse_qs(magnet.partition("?")[2]).get("xt",[])
    if len(xt)!=1:
        return None
    result=re.fullmatch("urn:btih:([a-f0-9]{40}|[a-z2-7]{32})",xt[0],re.I)
    return result.group(1).lower() if result else None


class Input(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.inputs=[]
    def handle_starttag(self,tag,attrs):
        if tag.lower()=="input" and dict(attrs).get("id")=="input-magnet":
            self.inputs.append(dict(attrs).get("value"))


def html_classify(media,body):
    if len(body)>MAX:
        return "SOURCE_HTML_OVERSIZED",None
    if "html" not in media.lower():
        return "SOURCE_NOT_HTML",None
    reader=Input()
    reader.feed(body.decode("utf8",errors="replace"))
    if len(reader.inputs)==0:return "SOURCE_INPUT_MISSING",None
    if len(reader.inputs)>1:return "SOURCE_INPUT_DUPLICATED",None
    if reader.inputs[0] is None:return "SOURCE_INPUT_VALUE_MISSING",None
    h=infohash(reader.inputs[0])
    return ("SOURCE_INPUT_MAGNET_VALID",h) if h else ("SOURCE_INPUT_VALUE_INVALID",None)


def response_class(status,media,body):
    if len(body)>MAX:return "BODY_TOO_LARGE",None
    if "application/json" not in media.lower():return "NON_JSON",None
    try:
        data=json.loads(body)
    except (UnicodeError,ValueError):
        return "INVALID_JSON",None
    if not isinstance(data,dict):return "INVALID_JSON_SHAPE",None
    if status==200:
        h=infohash(data.get("magnet"))
        return ("VALID_MAGNET",h) if h else ("MISSING_MAGNET_IN_SUCCESS",None)
    # Classify only a fixed finite set: do not echo raw error/metadata.
    err=str(data.get("error","")).lower()[:250]
    if "provider http 403" in err:return "UPSTREAM_HTTP_403",None
    if "provider http 401" in err:return "UPSTREAM_HTTP_401",None
    if "provider http 404" in err:return "UPSTREAM_HTTP_404",None
    if "provider http 429" in err:return "UPSTREAM_HTTP_429",None
    if re.search("provider http 5[0-9][0-9]",err):return "UPSTREAM_HTTP_5XX",None
    if "challenge" in err or "browser session" in err:return "UPSTREAM_CHALLENGE",None
    if "redirect" in err:return "UPSTREAM_REDIRECT",None
    if "no supported magnet" in err:return "MAGNET_NOT_FOUND_IN_HTML",None
    if "details url" in err or "allowlist" in err:return "DETAIL_URL_REJECTED",None
    if "timeout" in err or "timed out" in err:return "UPSTREAM_TIMEOUT",None
    if "could not connect" in err:return "UPSTREAM_NETWORK",None
    return "RESOLVE_ERROR_OTHER",None


def exact_record_count(media,body):
    if len(body)>MAX or "application/json" not in media.lower():raise Stop("SEARCH_BODY_UNVERIFIED")
    try: record=json.loads(body)
    except (ValueError,UnicodeError):raise Stop("SEARCH_INVALID_JSON") from None
    if not isinstance(record,dict) or not isinstance(record.get("results"),list):
        raise Stop("SEARCH_INVALID_SCHEMA")
    rows=record["results"]
    if len(rows)>500:raise Stop("SEARCH_TOO_MANY_RESULTS")
    exact=[r for r in rows if isinstance(r,dict) and r.get("provider")=="0magnet" and
           r.get("details")==SOURCE]
    if len(exact)>1:raise Stop("DUPLICATE_EXACT_CARD")
    r=exact[0] if exact else None
    return "ONE" if r else "ZERO", ("PRESENT" if r and infohash(r.get("magnet")) else "ABSENT"), (
        "PRESENT" if r and isinstance(r.get("magnetSource"),str) and r["magnetSource"] else "ABSENT")


def origin_redirect_kind(location):
    if not location:return "NO_LOCATION"
    try:
        parsed=urlsplit(location)
        if parsed.scheme=="https" and parsed.netloc=="9mag.net":
            return "SAME_ORIGIN"
        if location.startswith("/") and not location.startswith("//"):
            return "SAME_ORIGIN_RELATIVE"
        return "OUTSIDE_ORIGIN"
    except ValueError:return "MALFORMED"


def execute():
    if os.environ.get("MAGNETRA_0MAGNET_EXACT_APPROVAL")!=APPROVAL:
        raise Stop("EXPLICIT_OWNER_APPROVAL_REQUIRED")
    path=PROD+"/api/search?"+urlencode({"q":SEARCH,"category":"all","providers":"0magnet"})
    code,media,body,_=fetch_once(path)
    print("EXACT_CARD_SEARCH_HTTP:",code,flush=True)
    if code==200:
        count,mag,aux=exact_record_count(media,body)
        print("EXACT_DETAILS_URL_IN_SEARCH:",count,flush=True)
        print("SEARCH_MAGNET_PRESENT:",mag,flush=True)
        print("SEARCH_AUXILIARY_LINK:",aux,flush=True)
    else:
        print("SEARCH_UNAVAILABLE_CONTINUE_ONLY_WITH_OWNER_URL: YES",flush=True)
    # One direct GET to the exact user-provided URL, do not resolve redirects.
    code,media,body,location=fetch_once(SOURCE,source=True)
    print("EXACT_ORIGINAL_SOURCE_HTTP:",code,flush=True)
    if code in (301,302,303,307,308):
        print("EXACT_ORIGINAL_REDIRECT_ORIGIN:",origin_redirect_kind(location),flush=True)
        # Do not query the resolver after an observed redirect as another 
        # upstream request might constitute a rate-limit circumvent attempt.
        return 0
    if code in (403,429,500,502,503,504) or code==0:
        print("EXACT_ORIGINAL_FETCH_BLOCKED_OR_UNAVAILABLE: YES",flush=True)
        return 0
    if code!=200:
        print("EXACT_ORIGINAL_RESPONSE_OTHER: YES",flush=True)
        return 0
    stage,h=html_classify(media,body)
    print("EXACT_ORIGINAL_HTML:",stage,flush=True)
    code,media,body,_=fetch_once(PROD+"/api/resolve",
                                 payload={"provider":"0magnet","details":SOURCE})
    print("EXACT_PRODUCTION_RESOLVER_HTTP:",code,flush=True)
    outcome,worker_hash=response_class(code,media,body)
    print("EXACT_PRODUCTION_RESOLVER_CLASS:",outcome,flush=True)
    if h and worker_hash:
        print("EXACT_SOURCE_AND_WORKER_BTih_EQUAL:","YES" if h==worker_hash else "NO",flush=True)
    print("DIAGNOSTIC_READONLY_DONE: no torrent, hash, magnet, details URL, title or body exposed",flush=True)
    return 0


def main():
    if sys.argv[1:]!=["--approved-readonly"] or os.environ.get("MAGNETRA_0MAGNET_EXACT_APPROVAL")!=APPROVAL:
        print("STOP: NOT_APPROVED_NO_REQUEST",flush=True)
        return 2
    try:
        return execute()
    except Stop as e:
        print("READONLY_STOP:",str(e),flush=True)
        return 1
    except Exception:
        print("READONLY_STOP: UNEXPECTED_REDACTED",flush=True)
        return 1


if __name__=="__main__":
    raise SystemExit(main())
