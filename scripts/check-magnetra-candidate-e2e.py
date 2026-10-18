#!/usr/bin/env python3
"""Bounded live Worker version-override E2E audit. No downloads or raw magnet logging.

Cloudflare is never mutated. Fail closed unless the active deployment is
exact old 100% / candidate 0% AND a candidate-only API fingerprint is observed.
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from deploy_magnetra_zero_percent import _get_api, _current_deployment, _shares
from inspect_cloudflare_version import VERSION, ROLLBACK, audit as binding_audit

BASE = "https://index.alexlab.media"
WORKER = "alexlab-magnetra"
OVERRIDE = WORKER + '="' + VERSION + '"'
MAGNET = re.compile(r"^magnet:\?xt=urn:btih:(?:[a-f0-9]{40}|[a-z2-7]{32})(?:&|$)", re.I)
MAX_BYTES = 750_000


class Stop(Exception):
    """Fail without leaking transport errors or upstream response bodies."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def request_api(path, *, candidate: bool, method="GET", body=None):
    if not path.startswith("/api/") or path.startswith("//") or "//" in path:
        raise Stop("Unsafe API path")
    if method not in ("GET", "POST") or (method == "POST") != (body is not None):
        raise Stop("Unapproved HTTP method/body")
    if body is not None and len(body) > 3500:
        raise Stop("Request body too large")
    headers = {
        "User-Agent": "AlexLab-Magnetra-CandidateE2E/1.0",
        "Accept": "application/json",
        "Cache-Control": "no-store",
    }
    if candidate:
        headers["Cloudflare-Workers-Version-Overrides"] = OVERRIDE
    if body is not None:
        headers["Content-Type"] = "application/json"
        headers["Origin"] = BASE
    req = urllib.request.Request(BASE + path, data=body, headers=headers, method=method)
    opener = urllib.request.build_opener(NoRedirect)
    try:
        with opener.open(req, timeout=32) as resp:
            raw = resp.read(MAX_BYTES + 1)
            status = resp.status
            ctype = resp.headers.get("content-type", "")
    except urllib.error.HTTPError as e:
        status, raw, ctype = e.code, b"", ""
    except (urllib.error.URLError, TimeoutError, OSError):
        raise Stop("PUBLIC_WORKER_TRANSPORT_ERROR") from None
    if len(raw) > MAX_BYTES:
        raise Stop("PUBLIC_WORKER_RESPONSE_TOO_LARGE")
    if status != 200:
        return status, None
    if "application/json" not in ctype:
        raise Stop("PUBLIC_WORKER_UNEXPECTED_CONTENT_TYPE")
    try:
        payload = json.loads(raw)
    except (UnicodeDecodeError, ValueError):
        raise Stop("PUBLIC_WORKER_INVALID_JSON") from None
    if not isinstance(payload, dict):
        raise Stop("PUBLIC_WORKER_UNEXPECTED_JSON")
    return status, payload


def check_deployment():
    # Specific candidate bindings were already verified by GET audit #1.
    version = _get_api("/versions/" + VERSION)
    deployment = _get_api("/deployments")
    lines, _ = binding_audit(version, deployment)
    for name in ("BTDIGG_GATEWAY_TOKEN", "MAGNETRA_GATEWAY_TOKEN", "ASSETS"):
        if name + ": PASS" not in lines:
            raise Stop("CANDIDATE_BINDING_UNVERIFIED_" + name)
    record = _current_deployment(deployment)
    shares = _shares(record)
    if len(shares) != 2 or shares.get(VERSION) != 0:
        raise Stop("ZERO_PERCENT_DEPLOYMENT_NOT_CONFIRMED")
    old = [v for v in shares if v != VERSION]
    if len(old) != 1 or not old[0].startswith(ROLLBACK) or shares[old[0]] != 100:
        raise Stop("OLD_VERSION_100_PERCENT_NOT_CONFIRMED")
    print("CLOUDFLARE_VERSION_SLOT: PASS (old 100%, candidate 0%, bindings PASS)")


def check_routing_fingerprint():
    path = "/api/recovery-plan"
    base_status, base = request_api(path, candidate=False)
    new_status, new = request_api(path, candidate=True)
    # A successful request does NOT prove version override was respected.
    # Require an observable candidate-only endpoint before any source probing.
    if base_status != 404:
        raise Stop("OVERRIDE_ATTRIBUTION_UNVERIFIED_BASELINE_NOT_404")
    if new_status != 200 or not isinstance(new.get("providers") if new else None, list):
        raise Stop("OVERRIDE_ATTRIBUTION_UNVERIFIED_CANDIDATE")
    if len(new["providers"]) != 46:
        raise Stop("CANDIDATE_RECOVERY_PLAN_NOT_46")
    print("OVERRIDE_ROUTING_FINGERPRINT: PASS (baseline 404, candidate 200 + 46 entries)")


def check_catalog():
    status, body = request_api("/api/providers", candidate=True)
    if status != 200 or not isinstance(body.get("providers") if body else None, list):
        raise Stop("CANDIDATE_CATALOG_API_FAILURE")
    ids = [p.get("id") for p in body["providers"] if isinstance(p, dict)]
    if len(ids) != 46 or len(set(ids)) != 46:
        raise Stop("CANDIDATE_CATALOG_46_IDS_MISMATCH")
    print("CANDIDATE_PROVIDER_CATALOG: PASS 46/46")


def valid_magnet(value):
    return (isinstance(value, str) and len(value) <= 12000
            and bool(MAGNET.search(value)))


def validate_search(provider, query, *, allow_empty=False):
    path = "/api/search?" + urllib.parse.urlencode({
        "q": query, "providers": provider, "category": "all"
    })
    status, body = request_api(path, candidate=True)
    if status != 200 or not isinstance(body, dict):
        raise Stop("SEARCH_HTTP_OR_JSON_FAIL_" + provider)
    errors = body.get("errors")
    stats = body.get("stats")
    results = body.get("results")
    if not isinstance(errors, list) or not isinstance(stats, list) or not isinstance(results, list):
        raise Stop("SEARCH_RESULT_SCHEMA_FAIL_" + provider)
    if errors:
        # Do not log untrusted provider error strings or full source URLs.
        raise Stop("SEARCH_UPSTREAM_ERROR_" + provider)
    if len(stats) != 1 or stats[0].get("provider") != provider or stats[0].get("ok") is not True:
        raise Stop("SEARCH_PROVIDER_STAT_MISMATCH_" + provider)
    if not results:
        if allow_empty:
            return []
        raise Stop("SEARCH_EMPTY_UNVERIFIED_" + provider)
    for item in results:
        if not isinstance(item, dict) or item.get("provider") != provider or not item.get("name"):
            raise Stop("SEARCH_SOURCE_IDENTITY_MISMATCH_" + provider)
        magnet = item.get("magnet")
        if magnet is not None and not valid_magnet(magnet):
            raise Stop("SEARCH_INVALID_MAGNET_" + provider)
    print("SEARCH_PASS_" + provider + ": real response; " + str(len(results)) + " source-attributed results")
    return results


def check_resolve(provider, items):
    allowed = {"oxtorrent": "https://www.oxtorrent.co/",
               "torrent9": "https://www7.torrent9.to/"}
    details = next((item.get("details") for item in items
                    if isinstance(item.get("details"), str)
                    and item["details"].startswith(allowed[provider])
                    and item.get("magnet") is None), None)
    if details is None:
        details = next((item.get("details") for item in items
                        if isinstance(item.get("details"), str)
                        and item["details"].startswith(allowed[provider])), None)
    if details is None:
        raise Stop("DETAIL_URL_UNVERIFIED_" + provider)
    data = json.dumps({"provider": provider, "details": details}, separators=(",", ":")).encode()
    status, result = request_api("/api/resolve", candidate=True, method="POST", body=data)
    if status != 200 or not isinstance(result, dict) or result.get("provider") != provider:
        raise Stop("DEFERRED_RESOLUTION_HTTP_OR_PROVIDER_FAIL_" + provider)
    if not valid_magnet(result.get("magnet")):
        raise Stop("DEFERRED_MAGNET_INVALID_" + provider)
    print("DEFERRED_MAGNET_PASS_" + provider + ": original-provider detail resolved; magnet BTIH valid (value withheld)")



# Upstream's historic tt0460681 / Supernatural response legitimately returned
# torrents_count=0. A zero must not be mistaken for gateway transport failure.
# Positive verification uses recent original-source IMDb IDs when public source
# access is available and bounded current-series controls otherwise.
EZTV_ZERO_SAMPLE = "tt0460681"
EZTV_CURRENT_SERIES_SAMPLES = ("tt0096697", "tt0413573", "tt0182576", "tt0364845")


def discover_recent_eztv_ids():
    """One GET of genuine official recent EZTV rows; no result contents logged."""
    url = "https://eztvx.to/api/get-torrents?limit=12&page=1"
    req = urllib.request.Request(url, headers={
        "User-Agent": "AlexLab-Magnetra-PositiveSample/1.0",
        "Accept": "application/json",
    }, method="GET")
    try:
        with urllib.request.build_opener(NoRedirect).open(req, timeout=9) as response:
            if response.status != 200 or "application/json" not in response.headers.get("content-type", ""):
                print("EZTV_RECENT_DISCOVERY: UNVERIFIED_CONTENT_TYPE_OR_STATUS")
                return []
            body = response.read(750_001)
        if len(body) > 750_000:
            print("EZTV_RECENT_DISCOVERY: RESPONSE_TOO_LARGE")
            return []
        parsed = json.loads(body)
    except urllib.error.HTTPError as err:
        # HTTP 403 is historically known for cloud egress; it is not proof
        # that Rock64 origin is blocked.
        print("EZTV_RECENT_DISCOVERY: UPSTREAM_HTTP_" + str(err.code))
        return []
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, UnicodeDecodeError):
        print("EZTV_RECENT_DISCOVERY: SOURCE_UNVERIFIED")
        return []
    rows = parsed.get("torrents") if isinstance(parsed, dict) else None
    if not isinstance(rows, list):
        print("EZTV_RECENT_DISCOVERY: NO_ROWS")
        return []
    candidates = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        number = str(row.get("imdb_id", "")).removeprefix("tt")
        if not re.fullmatch(r"[0-9]{5,12}", number) or int(number) == 0:
            continue
        magnet = row.get("magnet_url")
        if not valid_magnet(magnet):
            continue
        imdb = "tt" + number
        if imdb not in candidates and imdb != EZTV_ZERO_SAMPLE:
            candidates.append(imdb)
            if len(candidates) == 2:
                break
    print("EZTV_RECENT_DISCOVERY: " + str(len(candidates)) + " original IMDb IDs with valid source magnets (identities withheld)")
    return candidates


def check_eztv_positive():
    """Separate expected empty vs. genuine positive source-specific magnets."""
    historical = validate_search("eztvx", EZTV_ZERO_SAMPLE, allow_empty=True)
    if historical:
        print("EZTV_HISTORICAL_ZERO_NOW_POSITIVE: " + str(len(historical)) + " original results")
        if any(valid_magnet(item.get("magnet")) for item in historical):
            print("EZTV_AUTHENTICATED_POSITIVE_GATE: PASS")
            return True
    else:
        print("EZTV_KNOWN_EMPTY_SAMPLE: PASS (0 genuine rows, NOT a tunnel failure)")

    discovered = discover_recent_eztv_ids()
    # Fixed true-series IMDb identifiers are only candidate controls; they
    # are NOT labelled known-positive and never substituted across indexers.
    seen = {EZTV_ZERO_SAMPLE}
    count = 0
    for imdb in [*discovered, *EZTV_CURRENT_SERIES_SAMPLES]:
        if imdb in seen:
            continue
        seen.add(imdb)
        count += 1
        if count > 6:
            break
        rows = validate_search("eztvx", imdb, allow_empty=True)
        if rows:
            if not all(valid_magnet(row.get("magnet")) for row in rows):
                raise Stop("EZTV_POSITIVE_ROWS_WITHOUT_VALID_MAGNET")
            print("EZTV_AUTHENTICATED_POSITIVE_GATE: PASS (" + str(len(rows)) + " genuine source results; IMDb withheld)")
            return True
        print("EZTV_SAMPLE_" + str(count) + ": EMPTY_UNVERIFIED")
    print("EZTV_AUTHENTICATED_POSITIVE_GATE: UNVERIFIED (all sampled exact IDs empty)")
    return False


def check_btdigg_observational():
    # A single BTDigg request, with no retry: results/error do not imply historical uptime.
    try:
        results = validate_search("btdigg", "ubuntu")
        print("BTDIGG_CANDIDATE_OBSERVATION: " + str(len(results)) + " results")
    except Stop as exc:
        print("BTDIGG_CANDIDATE_OBSERVATION: UNVERIFIED (" + str(exc) + ")")


def execute():
    if os.environ.get("MAGNETRA_E2E_READONLY_APPROVAL") != "RUN_READONLY_E2E":
        raise Stop("EXPLICIT_E2E_DIAGNOSTIC_INPUT_REQUIRED")
    check_deployment()
    check_routing_fingerprint()
    check_catalog()
    for provider in ("oxtorrent", "torrent9"):
        items = validate_search(provider, "ubuntu")
        check_resolve(provider, items)
    check_btdigg_observational()
    if not check_eztv_positive():
        raise Stop("EZTV_POSITIVE_SOURCE_NOT_PROVEN")
    print("E2E_GATE_RESULT: PASS (staged candidate, NOT normal production traffic)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(execute())
    except Stop as err:
        print("E2E_GATE_RESULT: STOP " + str(err))
        print("No retry, no torrent download, no secret disclosure, no Cloudflare mutation.")
        sys.exit(1)
    except Exception:
        print("E2E_GATE_RESULT: STOP UNEXPECTED_FAILURE (details withheld)")
        sys.exit(1)
