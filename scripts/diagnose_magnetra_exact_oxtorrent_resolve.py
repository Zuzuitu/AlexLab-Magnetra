#!/usr/bin/env python3
"""Owner-triggered, source-bounded, read-only OxTorrent Resolve comparison.

Diagnoses one public details URL supplied by the project owner against:
* a single normal PWA search for the title, restricted to OxTorrent;
* the exact /api/resolve request used by the iPhone PWA.

It never logs result names, HTML, original URLs, ID, magnet or BTIH data, and
never downloads/opens magnet/.torrent or contacts Flud. No retry or writes.
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from deploy_magnetra_zero_percent import _current_deployment, _get_api, _shares
from inspect_cloudflare_version import ROLLBACK, VERSION

ACTION = "RUN_EXACT_OXTORRENT_READONLY"
BASE = "https://index.alexlab.media"
PROVIDER = "oxtorrent"
SOURCE_ORIGIN = "https://www.oxtorrent.co"
# Exact owner-shared ordinary OxTorrent result. No client-specified upstream.
OWNER_DETAIL = (
    SOURCE_ORIGIN +
    "/torrent/133995/toy-story-5-2026-multi-ca-1080p-web-h264-supply"
)
QUERY = "toy story 5"
MAX_BYTES = 1_200_000
DETAIL = re.compile(r"^/torrent/[0-9]{1,12}/[A-Za-z0-9][A-Za-z0-9._-]{0,180}$")
BTIH = re.compile(r"^magnet:\?xt=urn:btih:(?:[0-9a-fA-F]{40}|[A-Za-z2-7]{32})(?:&|$)")


class Stop(Exception):
    """A safe diagnostic stop, with no raw source data."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def shape(raw):
    """Report only finite classes, never any source URL or its private parts."""
    if not isinstance(raw, str) or not raw:
        return "ABSENT"
    if len(raw) > 750:
        return "EXCESSIVE_LENGTH"
    try:
        u = urllib.parse.urlsplit(raw)
        port = u.port
    except (TypeError, ValueError):
        return "MALFORMED"
    if (u.scheme != "https" or
            u.hostname != "www.oxtorrent.co" or
            port is not None or
            u.username is not None or u.password is not None):
        return "ORIGIN_REFUSED"
    if u.fragment:
        return "FRAGMENT"
    if u.query:
        return "QUERY"
    if DETAIL.fullmatch(u.path):
        return "CANONICAL_DETAIL"
    if u.path.endswith("/") and DETAIL.fullmatch(u.path[:-1]):
        return "TRAILING_SLASH"
    if "%" in u.path:
        return "ENCODED_PATH"
    return "OTHER_PATH"


def gate():
    data = _current_deployment(_get_api("/deployments"))
    shares = _shares(data)
    old = [v for v in shares if v.startswith(ROLLBACK) and v != VERSION]
    if (len(shares) != 2 or len(old) != 1 or
            shares.get(old[0]) != 0 or shares.get(VERSION) != 100 or
            not isinstance(data.get("id"), str) or not data["id"]):
        raise Stop("PRODUCTION_EXACT_100_PERCENT_VERSION_UNVERIFIED")
    return data["id"]


def request_json(path, *, payload=None):
    if not path.startswith("/api/") or path.startswith("//") or "//" in path:
        raise Stop("API_PATH_NOT_ALLOWED")
    method = "POST" if payload is not None else "GET"
    data = None if payload is None else json.dumps(payload, separators=(",", ":")).encode("utf8")
    if data is not None and len(data) > 600:
        raise Stop("API_PAYLOAD_TOO_LONG")
    headers = {
        "User-Agent": "AlexLab-Magnetra-OwnerExactResolveDiagnostic/1.0",
        "Accept": "application/json",
        "Cache-Control": "no-store",
    }
    if data is not None:
        headers["Origin"] = BASE
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.build_opener(NoRedirect).open(req, timeout=35) as resp:
            status = resp.status
            ctype = resp.headers.get("content-type", "")
            body = resp.read(MAX_BYTES + 1)
    except urllib.error.HTTPError as err:
        status = err.code
        ctype = err.headers.get("content-type", "") if err.headers else ""
        body = err.read(MAX_BYTES + 1)
    except (urllib.error.URLError, TimeoutError, OSError):
        raise Stop("PRODUCTION_TRANSPORT_UNVERIFIED") from None
    if len(body) > MAX_BYTES:
        raise Stop("API_RESPONSE_TOO_LARGE")
    if "application/json" not in ctype:
        raise Stop("API_RESPONSE_NOT_JSON")
    try:
        parsed = json.loads(body)
    except (UnicodeDecodeError, ValueError):
        raise Stop("API_RESPONSE_MALFORMED_JSON") from None
    if not isinstance(parsed, dict):
        raise Stop("API_RESPONSE_NOT_OBJECT")
    return status, parsed


def classify_resolve(status, body):
    """No magnet value or untrusted error content is ever returned or logged."""
    if status == 200:
        return ("PASS_VALID_BTIH" if
                isinstance(body.get("magnet"), str) and
                len(body["magnet"]) <= 12_000 and
                BTIH.search(body["magnet"]) else
                "HTTP_200_INVALID_MAGNET")
    error = body.get("error", "")
    if status == 502 and isinstance(error, str):
        if "Noncanonical source HTML route refused" in error:
            return "HTTP_502_NONCANONICAL_WORKER_ROUTE"
        if "Source HTML gateway" in error:
            return "HTTP_502_GATEWAY_ERROR"
        if "provider details page contains no supported magnet link" in error.lower():
            return "HTTP_502_NO_MAGNET_IN_SOURCE"
    return "HTTP_" + str(status) + "_OTHER"


def select_search_record(body):
    results = body.get("results")
    if not isinstance(results, list):
        raise Stop("SEARCH_RESULT_SCHEMA_INVALID")
    matched = []
    for item in results[:100]:
        if not isinstance(item, dict) or item.get("provider") != PROVIDER:
            raise Stop("SEARCH_SOURCE_ATTRIBUTION_MISMATCH")
        if item.get("details") == OWNER_DETAIL:
            matched.append(item)
    if len(matched) > 1:
        raise Stop("DUPLICATE_OWNER_DETAIL_UNVERIFIED")
    return matched[0] if matched else None


def execute():
    if os.environ.get("MAGNETRA_EXACT_RESOLVE_APPROVAL") != ACTION:
        raise Stop("EXPLICIT_OWNER_DIAGNOSTIC_APPROVAL_REQUIRED")
    if shape(OWNER_DETAIL) != "CANONICAL_DETAIL":
        raise Stop("OWNER_DETAIL_STATIC_GATE_FAILED")

    deployment_id = gate()
    print("PRODUCTION_GATE: PASS (exact candidate 100%, old 0%)")
    print("OWNER_DETAIL_STATIC_ROUTE: CANONICAL_DETAIL")

    search = urllib.parse.urlencode({
        "providers": PROVIDER, "q": QUERY, "category": "all"
    })
    search_status, search_body = request_json("/api/search?" + search)
    if search_status != 200:
        raise Stop("EXACT_SEARCH_HTTP_" + str(search_status))
    errors = search_body.get("errors")
    if not isinstance(errors, list):
        raise Stop("SEARCH_ERROR_SCHEMA_UNVERIFIED")
    print("EXACT_SEARCH_PROVIDER_ERROR: " +
          ("PRESENT" if errors else "NONE"))
    record = select_search_record(search_body)
    if record is None:
        print("OWNER_RECORD_IN_BOUNDED_SEARCH: NOT_PRESENT")
    else:
        print("OWNER_RECORD_IN_BOUNDED_SEARCH: FOUND")
        details = record.get("details")
        magnet_source = record.get("magnetSource")
        preferred = magnet_source or details
        print("REPORTED_DETAILS_SHAPE: " + shape(details))
        print("REPORTED_MAGNET_SOURCE_SHAPE: " + shape(magnet_source))
        print("PWA_RESOLVE_PREFERRED_FIELD: " +
              ("MAGNET_SOURCE" if magnet_source else "DETAILS"))
        print("PWA_RESOLVE_URL_EQUALS_OWNER_LINK: " +
              ("YES" if preferred == OWNER_DETAIL else "NO"))
        print("PWA_EXISTING_MAGNET: " +
              ("YES" if isinstance(record.get("magnet"), str) and
               record["magnet"].startswith("magnet:?") else "NO"))

    status, result = request_json("/api/resolve", payload={
        "provider": PROVIDER, "details": OWNER_DETAIL
    })
    print("OWNER_EXACT_RESOLVE: " + classify_resolve(status, result))
    if record is not None:
        preferred = record.get("magnetSource") or record.get("details")
        if (isinstance(preferred, str) and preferred != OWNER_DETAIL and
                shape(preferred) not in ("ORIGIN_REFUSED", "EXCESSIVE_LENGTH", "MALFORMED")):
            # The PWA would submit this same-origin string. One optional
            # comparison call only when it differs from the owner link.
            second_status, second = request_json("/api/resolve", payload={
                "provider": PROVIDER, "details": preferred
            })
            print("PWA_PREFERRED_RESOLVE: " + classify_resolve(second_status, second))
        else:
            print("PWA_PREFERRED_RESOLVE: NOT_DISTINCT_OR_NOT_ELIGIBLE")

    if gate() != deployment_id:
        raise Stop("DEPLOYMENT_CHANGED_DURING_READONLY_DIAGNOSTIC")
    print("DIAGNOSTIC_COMPLETE: no magnet output, downloads, Flud, Rock64, deploy or retries.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(execute())
    except Stop as exc:
        print("DIAGNOSTIC_STOP: " + str(exc))
        sys.exit(1)
    except Exception:
        print("DIAGNOSTIC_STOP: UNEXPECTED_FAILURE (raw details withheld)")
        sys.exit(1)
