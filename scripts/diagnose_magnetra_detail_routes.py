#!/usr/bin/env python3
"""One bounded read-only Magnetra production diagnosis of HTML detail-route shapes.

Never prints item titles, full URLs, detail IDs, hashes, magnet URIs, tokens,
response bodies or source HTML. Does not resolve/download/dispatch torrents.
No BTDigg/EZTV calls. Owner-triggered workflow only; no automatic retries.
"""
from __future__ import annotations

from collections import Counter
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from deploy_magnetra_zero_percent import _current_deployment, _get_api, _shares
from inspect_cloudflare_version import ROLLBACK, VERSION

BASE = "https://index.alexlab.media"
ACTION = "RUN_READONLY_2026_DETAIL_SHAPES"
SOURCES = {
    "oxtorrent": "www.oxtorrent.co",
    "torrent9": "www7.torrent9.to",
}
DETAIL = re.compile(r"^/torrent/[0-9]{1,12}/[A-Za-z0-9][A-Za-z0-9._-]{0,180}$")
QUERY = "2026"
MAX_BYTES = 900_000


class Stop(Exception):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def route_shape(provider: str, raw: object) -> str:
    """Mimic Worker route allowlist using non-sensitive URL *shape* only."""
    if provider not in SOURCES:
        return "UNKNOWN_PROVIDER"
    if not isinstance(raw, str) or not raw:
        return "MISSING_DETAIL"
    if len(raw) > 750:
        return "URL_TOO_LONG"
    try:
        parsed = urllib.parse.urlsplit(raw)
        port = parsed.port
    except (TypeError, ValueError):
        return "MALFORMED_URL"
    if (parsed.scheme != "https" or parsed.hostname != SOURCES[provider] or
            port is not None or parsed.username is not None or
            parsed.password is not None):
        return "NONCANONICAL_ORIGIN"
    if parsed.fragment:
        return "FRAGMENT"
    if parsed.query:
        return "QUERY_PARAMETERS"
    path = parsed.path
    if DETAIL.fullmatch(path):
        return "CANONICAL_DETAIL"
    if path.endswith("/") and DETAIL.fullmatch(path[:-1]):
        return "TRAILING_SLASH"
    if "%" in path:
        return "PERCENT_ENCODED_PATH"
    if re.match(r"^/torrent/[0-9]{1,12}/", path):
        return "UNEXPECTED_DETAIL_SLUG"
    if path.startswith("/torrent/"):
        return "DIFFERENT_TORRENT_ROUTE"
    return "OTHER_PATH_TEMPLATE"


def confirm_current_release() -> str:
    deployment = _current_deployment(_get_api("/deployments"))
    shares = _shares(deployment)
    old = [v for v in shares if v.startswith(ROLLBACK) and v != VERSION]
    if (len(shares) != 2 or len(old) != 1 or shares.get(VERSION) != 100
            or shares.get(old[0]) != 0 or not deployment.get("id")):
        raise Stop("EXPECTED_100_PERCENT_CANDIDATE_DEPLOYMENT_NOT_CONFIRMED")
    print("DEPLOYMENT_GATE: PASS (candidate 100%, previous version retained 0%)")
    return str(deployment["id"])


def get_production_search() -> dict:
    params = urllib.parse.urlencode({
        "q": QUERY,
        "providers": "oxtorrent,torrent9",
        "category": "all",
    })
    req = urllib.request.Request(
        BASE + "/api/search?" + params,
        method="GET",
        headers={
            "Accept": "application/json",
            "Cache-Control": "no-store",
            "User-Agent": "AlexLab-Magnetra-DetailRouteDiagnostic/1.0",
        },
    )
    try:
        with urllib.request.build_opener(NoRedirect).open(req, timeout=32) as response:
            if response.status != 200:
                raise Stop("PRODUCTION_SEARCH_NOT_HTTP_200")
            if "application/json" not in response.headers.get("content-type", ""):
                raise Stop("PRODUCTION_SEARCH_NOT_JSON")
            body = response.read(MAX_BYTES + 1)
    except urllib.error.HTTPError:
        raise Stop("PRODUCTION_SEARCH_HTTP_ERROR") from None
    except (urllib.error.URLError, OSError, TimeoutError):
        raise Stop("PRODUCTION_SEARCH_TRANSPORT_UNVERIFIED") from None
    if len(body) > MAX_BYTES:
        raise Stop("PRODUCTION_SEARCH_BODY_TOO_LARGE")
    try:
        parsed = json.loads(body)
    except (ValueError, UnicodeDecodeError):
        raise Stop("PRODUCTION_SEARCH_MALFORMED_JSON") from None
    if not isinstance(parsed, dict) or not isinstance(parsed.get("results"), list):
        raise Stop("PRODUCTION_SEARCH_MALFORMED_RESULTS")
    return parsed


def diagnose_results(body: dict) -> dict:
    rows = body.get("results")
    if not isinstance(rows, list):
        raise Stop("UNEXPECTED_RESULTS_SCHEMA")
    summary = {provider: Counter() for provider in SOURCES}
    screenshot_matches = {
        "oxtorrent": "toy.story.5.2026",
        "torrent9": "hope.2026",
    }
    matched = {provider: Counter() for provider in SOURCES}
    for row in rows[:200]:
        if not isinstance(row, dict) or row.get("provider") not in SOURCES:
            raise Stop("SOURCE_ATTRIBUTION_UNVERIFIED")
        provider = row["provider"]
        shape = route_shape(provider, row.get("details"))
        summary[provider][shape] += 1
        name = row.get("name")
        if isinstance(name, str) and screenshot_matches[provider] in name.lower():
            matched[provider][shape] += 1
    return {"summary": summary, "matched": matched}


def execute() -> int:
    if os.environ.get("MAGNETRA_DETAIL_DIAGNOSTIC_APPROVAL") != ACTION:
        raise Stop("EXPLICIT_OWNER_READONLY_DIAGNOSTIC_APPROVAL_REQUIRED")
    first_id = confirm_current_release()
    body = get_production_search()
    data = diagnose_results(body)
    errors = body.get("errors", [])
    if not isinstance(errors, list):
        raise Stop("ERROR_SCHEMA_UNVERIFIED")
    print("PRODUCTION_SEARCH: obtained JSON; providers explicitly restricted to OxTorrent and Torrent9.")
    for provider in SOURCES:
        for error in errors:
            if isinstance(error, dict) and error.get("provider") == provider:
                code = error.get("code")
                safe = code if code in ("RATE_LIMIT", "TIMEOUT", "CHALLENGE",
                                       "ACCESS_DENIED", "UPSTREAM_ERROR",
                                       "PROVIDER_ERROR", "REDIRECT_BLOCKED") else "UNCLASSIFIED"
                print("PROVIDER_STATUS_" + provider + ": " + safe)
        totals = data["summary"][provider]
        print("DETAIL_SHAPES_" + provider + ": " +
              ", ".join(key + "=" + str(totals[key]) for key in sorted(totals)))
        matches = data["matched"][provider]
        print("SCREENSHOT_TITLE_SHAPES_" + provider + ": " +
              (", ".join(key + "=" + str(matches[key]) for key in sorted(matches)) or "NOT_IN_SAMPLE"))
        if not totals:
            print("PROVIDER_SAMPLED_" + provider + ": ZERO (not proof of permanent unavailability)")
    final_id = confirm_current_release()
    if final_id != first_id:
        raise Stop("DEPLOYMENT_CHANGED_DURING_DIAGNOSTIC")
    print("READ_ONLY_COMPLETE: no resolves, torrents, magnets, BTDigg, EZTV, deploy, or retries.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(execute())
    except Stop as exc:
        print("READ_ONLY_DIAGNOSTIC: STOP " + str(exc))
        sys.exit(1)
    except Exception:
        print("READ_ONLY_DIAGNOSTIC: STOP UNEXPECTED_FAILURE (details withheld)")
        sys.exit(1)
