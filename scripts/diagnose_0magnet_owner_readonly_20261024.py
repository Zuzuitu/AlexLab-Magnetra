#!/usr/bin/env python3
"""Owner 0Magnet (9mag.net) read-only diagnostic; no torrent, Flud or download.

At most two different bounded PWA searches, one direct original-source detail
GET, and one PWA resolver POST (a metadata-only lookup, not a magnet dispatch).
No request retries. Never print titles, full URLs, BTIH, magnets, response
bodies, auth data, cookies, or source HTML.
"""
from __future__ import annotations

from html.parser import HTMLParser
import json
import os
import re
import sys
from urllib.parse import urlencode, urlsplit, parse_qs
from urllib.request import Request, HTTPRedirectHandler, build_opener
from urllib.error import HTTPError, URLError

PROD = "https://index.alexlab.media"
PROVIDER = "0magnet"
ORIGIN = "https://9mag.net"
EXPECTED = "little.house.on.the.prairie.2026"
SEARCHES = ("2026", "Little.House.on.the.Prairie.2026")
LIMIT = 950_000
APPROVAL = "OWNER_0MAGNET_READONLY_20261024"
UA = ("Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36")


class Stop(Exception):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def request_once(url, *, payload=None, accept="application/json"):
    headers = {"User-Agent": UA, "Accept": accept,
               "Accept-Encoding": "identity", "Cache-Control": "no-store"}
    method = "POST" if payload is not None else "GET"
    if payload is not None:
        headers["Content-Type"] = "application/json"
    req = Request(url, data=json.dumps(payload).encode() if payload is not None else None,
                  headers=headers, method=method)
    try:
        with build_opener(NoRedirect()).open(req, timeout=24) as response:
            status = response.status
            media = response.headers.get("content-type", "").lower()
            body = response.read(LIMIT + 1)
    except HTTPError as exc:
        # Never log the upstream error body, query, Location, or request URL.
        return (exc.code, "", b"")
    except (URLError, OSError, TimeoutError):
        return (0, "", b"")
    if len(body) > LIMIT:
        return (-1, "", b"")
    return (status, media, body)


def same_source_detail(raw):
    if not isinstance(raw, str) or len(raw) > 1500:
        return False
    try:
        u = urlsplit(raw)
        return (u.scheme == "https" and u.netloc == "9mag.net"
                and u.username is None and u.password is None and not u.fragment
                and bool(u.path) and u.path != "/")
    except ValueError:
        return False


def owner_card(item):
    if not isinstance(item, dict) or item.get("provider") != PROVIDER:
        return False
    name = item.get("name")
    if not isinstance(name, str):
        return False
    # Bound to the same title shown in owner's screenshot, not a different item.
    compact = re.sub(r"[^a-z0-9]+", ".", name.lower()).strip(".")
    return EXPECTED in compact and same_source_detail(item.get("details"))


def choose_owner(payload):
    if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
        raise Stop("PRODUCTION_SEARCH_SCHEMA")
    rows = payload["results"]
    if len(rows) > 500:
        raise Stop("PRODUCTION_SEARCH_TOO_MANY_ROWS")
    matches = [row for row in rows if owner_card(row)]
    if len(matches) > 1:
        # Different releases of one show must never share an assumed magnet.
        matches = [x for x in matches if
                   "2.26" in str(x.get("size", "")) and
                   str(x.get("size", "")).lower().replace(" ", "").endswith("gb")]
    if len(matches) != 1:
        return None
    return matches[0]


def btih(magnet):
    if not isinstance(magnet, str) or len(magnet) > 12000 or not magnet.startswith("magnet:?"):
        return None
    pairs = parse_qs(magnet.partition("?")[2], keep_blank_values=True)
    xt = pairs.get("xt", [])
    if len(xt) != 1:
        return None
    m = re.fullmatch(r"urn:btih:([a-f0-9]{40}|[a-z2-7]{32})", xt[0], re.I)
    return m.group(1).lower() if m else None


class InputMagnet(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.found = 0
        self.with_value = 0
        self.values = []
    def handle_starttag(self, tag, attrs):
        if tag.lower() != "input":
            return
        data = dict(attrs)
        if data.get("id") != "input-magnet":
            return
        self.found += 1
        value = data.get("value")
        if isinstance(value, str):
            self.with_value += 1
            if btih(value):
                self.values.append(value)


def page_magnet_shape(body):
    parser = InputMagnet()
    parser.feed(body.decode("utf-8", errors="replace"))
    if parser.found == 0:
        return ("INPUT_MISSING", None)
    if parser.found > 1:
        return ("INPUT_DUPLICATED", None)
    if parser.with_value == 0:
        return ("VALUE_ATTR_MISSING", None)
    if len(parser.values) == 1:
        return ("MAGNET_VALID", parser.values[0])
    return ("VALUE_NOT_VALID_BTIH", None)


def json_body(media, body):
    if "application/json" not in media:
        raise Stop("PRODUCTION_NON_JSON_RESPONSE")
    try:
        value = json.loads(body)
    except (ValueError, UnicodeError):
        raise Stop("PRODUCTION_INVALID_JSON") from None
    if not isinstance(value, dict):
        raise Stop("PRODUCTION_JSON_SCHEMA")
    return value


def safe_error_class(data):
    if not isinstance(data, dict):
        return "UNCLASSIFIED"
    message = str(data.get("error", ""))[:250].lower()
    if re.search(r"provider http 403|provider http 401", message):
        return "SOURCE_HTTP_403_OR_401"
    if re.search(r"provider http 404", message):
        return "SOURCE_HTTP_404"
    if re.search(r"provider http 429", message):
        return "SOURCE_RATE_LIMIT_429"
    if re.search(r"provider http 5[0-9][0-9]", message):
        return "SOURCE_HTTP_5XX"
    if "challenge" in message or "browser session" in message:
        return "SOURCE_CHALLENGE"
    if "redirect" in message:
        return "SOURCE_REDIRECT"
    if "no supported magnet" in message:
        return "SOURCE_NO_SUPPORTED_MAGNET"
    if "details url" in message or "allowlist" in message:
        return "DETAIL_URL_REJECTED"
    if "timed out" in message or "timeout" in message:
        return "SOURCE_TIMEOUT"
    return "OTHER_RESOLVE_FAILURE"


def execute():
    if os.environ.get("MAGNETRA_0MAGNET_DIAGNOSTIC_APPROVAL") != APPROVAL:
        raise Stop("OWNER_APPROVAL_REQUIRED")
    chosen = None
    for index, query in enumerate(SEARCHES, 1):
        path = "/api/search?" + urlencode({"q": query, "category": "all", "providers": PROVIDER})
        code, media, body = request_once(PROD + path)
        print(f"PRODUCTION_SEARCH_{index}_HTTP:", code, flush=True)
        if code != 200:
            raise Stop("PRODUCTION_SEARCH_UNAVAILABLE_NO_RETRY")
        payload = json_body(media, body)
        errors = payload.get("errors", [])
        if not isinstance(errors, list):
            raise Stop("PRODUCTION_SEARCH_ERRORS_SCHEMA")
        # A provider error is NOT a reason to repeat the source request.
        if any(isinstance(x, dict) and x.get("provider") == PROVIDER for x in errors):
            print("PRODUCTION_SEARCH_PROVIDER_ERROR: PRESENT", flush=True)
            raise Stop("PROVIDER_SEARCH_FAILED_NO_RETRY")
        chosen = choose_owner(payload)
        print(f"OWNER_EXACT_CARD_SEARCH_{index}:", "FOUND" if chosen else "NOT_IN_SAMPLE", flush=True)
        if chosen:
            break
    if not chosen:
        print("RESULT: EXACT_CARD_NOT_FOUND_NO_FIX_ASSUMED", flush=True)
        return 0
    if btih(chosen.get("magnet")):
        print("SEARCH_CARD_ALREADY_HAS_MAGNET: YES", flush=True)
    else:
        print("SEARCH_CARD_ALREADY_HAS_MAGNET: NO", flush=True)
    detail = chosen["details"]
    code, media, body = request_once(detail, accept="text/html,application/xhtml+xml")
    print("ORIGINAL_DETAIL_GET_HTTP:", code, flush=True)
    direct = None
    if code == 200 and "text/html" in media:
        shape, direct = page_magnet_shape(body)
        print("ORIGINAL_SERVER_HTML_INPUT:", shape, flush=True)
    else:
        print("ORIGINAL_SERVER_HTML_INPUT: NOT_INSPECTABLE", flush=True)
    # Resolve only the validated same-card source URL, no torrent transfer.
    code, media, body = request_once(PROD + "/api/resolve",
                                     payload={"provider": PROVIDER, "details": detail})
    print("PRODUCTION_RESOLVE_HTTP:", code, flush=True)
    if code in (200, 502, 400):
        try:
            answer = json_body(media, body)
        except Stop:
            print("PRODUCTION_RESOLVE_RESULT: INVALID_JSON", flush=True)
        else:
            resolved = btih(answer.get("magnet"))
            if code == 200 and resolved:
                print("PRODUCTION_RESOLVE_RESULT: VALID_BTIH", flush=True)
                if direct:
                    print("SAME_SOURCE_BTih_MATCH:", "YES" if btih(direct) == resolved else "NO", flush=True)
            else:
                print("PRODUCTION_RESOLVE_RESULT:", safe_error_class(answer), flush=True)
    else:
        print("PRODUCTION_RESOLVE_RESULT: TRANSPORT_OR_EDGE_UNVERIFIED", flush=True)
    print("READ_ONLY_DIAGNOSTIC_DONE: no hash, magnet, title, URL, HTML, torrent or Flud logged", flush=True)
    return 0


def main():
    if sys.argv[1:] != ["--approved-readonly"] or os.environ.get("MAGNETRA_0MAGNET_DIAGNOSTIC_APPROVAL") != APPROVAL:
        print("STOP: OWNER_APPROVAL_REQUIRED_NO_CALL", flush=True)
        return 2
    try:
        return execute()
    except Stop as exc:
        print("READ_ONLY_STOP:", str(exc), flush=True)
        return 1
    except Exception:
        print("READ_ONLY_STOP: UNEXPECTED_FAILURE_REDACTED", flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
