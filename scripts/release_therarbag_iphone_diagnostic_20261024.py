#!/usr/bin/env python3
"""Owner-approved TheRarBg iPhone opt-in diagnostic: immutable 0 -> 5 -> 100 release.

The owner confirmed this is a single-user production PWA and explicitly
authorized testing on index.alexlab.media on 24 Oct 2026. Version-only
deployment; never use generic Wrangler deploy or upload, mutate secrets,
settings, DNS, Rock64, Shield/Flud, or send any magnet to a device.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

from deploy_magnetra_auto_pause_once import (
    Stop, ROOT, NoRedirect, snapshot, current, stable, wait_for, _wrangler_deploy,
)
from deploy_magnetra_zero_percent import _get_api
from inspect_companion_binding_readonly import (
    validated_source, account_list, verify_account_scripts,
    Stop as AccountStop,
)
from stage_therarbag_iphone_20261024 import (
    ACTIVE, PREVIOUS_ZERO, EXPECTED_SPLIT, validate_source, verify_binding_payload,
)

NEW = "139d97f7-4048-4bbb-8e90-80585f1f4b26"
ACTION = "CONFIRM_IPHONE_DIAGNOSTIC_PRODUCTION_0_5_100_20261024"
SLOT = {ACTIVE: 100, NEW: 0}
CANARY = {ACTIVE: 95, NEW: 5}
FULL = {ACTIVE: 0, NEW: 100}
BASE = "https://index.alexlab.media"
ORIGINAL = ("https://therarbg.com/post-detail/95bf8b/"
            "2026-10-20-cyberpunk-edgerunners-2-original-series-soundtrack-flac-44-1khz-24bit/")
TEST_HEADER = "owner-opt-in-20261024-v1"
MAX_BYTES = 1200000
STATES = ("HTML_NOT_FETCHED", "HTML_FETCHED", "HTML_ANCHOR_VALID",
          "HTML_NO_ANCHOR", "HTML_METADATA_VALID", "HTML_NO_BTIH")
UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) "
      "AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1")


def before_any_write():
    validated_source()
    validate_source()
    verify_account_scripts(account_list())
    before = current(EXPECTED_SPLIT)
    for version in (ACTIVE, PREVIOUS_ZERO, NEW):
        verify_binding_payload(version, _get_api("/versions/" + version))
    stable(before, EXPECTED_SPLIT)
    if NEW in EXPECTED_SPLIT:
        raise Stop("CANDIDATE_MUST_NOT_BE_ACTIVE_IN_BASELINE")
    print("PRECHECK_ORIGIN_ACCOUNT_FOUR_BINDINGS_AND_SPLIT: PASS", flush=True)
    return before


def http(path, version=None, body=None, diagnostic=False):
    if path not in ("/app.js", "/api/health", "/api/providers", "/api/resolve"):
        raise Stop("UNAPPROVED_RELEASE_PROBE_PATH")
    if body is not None and path != "/api/resolve":
        raise Stop("UNAPPROVED_POST_PATH")
    headers = {
        "User-Agent": UA, "Cache-Control": "no-cache, no-store",
        "Accept-Encoding": "identity", "Accept": "application/json"
        if path.startswith("/api/") else "application/javascript",
    }
    if version:
        if version not in (ACTIVE, NEW):
            raise Stop("UNAPPROVED_VERSION_OVERRIDE")
        headers["Cloudflare-Workers-Version-Overrides"] = (
            'alexlab-magnetra="' + version + '"'
        )
    data = None
    if body is not None:
        data = json.dumps(body, separators=(",", ":")).encode("utf-8")
        if len(data) > 1200:
            raise Stop("BOUNDED_PROBE_BODY_TOO_LARGE")
        headers["Content-Type"] = "application/json"
        headers["Origin"] = BASE
        if diagnostic:
            headers["x-magnetra-resolve-diagnostic"] = TEST_HEADER
    req = urllib.request.Request(BASE + path, headers=headers,
                                 data=data, method="POST" if data else "GET")
    opener = urllib.request.build_opener(NoRedirect())
    try:
        with opener.open(req, timeout=30 if data else 18) as response:
            status = response.status
            mime = response.headers.get("content-type", "")
            raw = response.read(MAX_BYTES + 1)
    except urllib.error.HTTPError as exc:
        status = exc.code
        mime = exc.headers.get("content-type", "")
        raw = exc.read(MAX_BYTES + 1)
    except (urllib.error.URLError, TimeoutError, OSError):
        raise Stop("RELEASE_FIXED_ORIGIN_TRANSPORT_UNVERIFIED") from None
    if not raw or len(raw) > MAX_BYTES:
        raise Stop("RELEASE_FIXED_ORIGIN_SIZE_UNVERIFIED")
    if path == "/app.js":
        if status != 200 or "javascript" not in mime.lower():
            raise Stop("VERSIONED_APP_JS_HTTP_OR_TYPE_UNVERIFIED")
        return raw
    if "application/json" not in mime.lower():
        raise Stop("RELEASE_JSON_HTTP_OR_TYPE_UNVERIFIED")
    try:
        record = json.loads(raw)
    except ValueError:
        raise Stop("RELEASE_JSON_MALFORMED") from None
    if not isinstance(record, dict):
        raise Stop("RELEASE_JSON_SHAPE_UNVERIFIED")
    return status, record


def version_checks(version):
    js = http("/app.js", version=version)
    reviewed = (ROOT / "web/app.js").read_bytes()
    if hashlib.sha256(js).digest() != hashlib.sha256(reviewed).digest():
        raise Stop("NEW_VERSION_APP_JS_SHA_MISMATCH")
    status, health = http("/api/health", version=version)
    if status != 200 or health.get("ok") is not True or (health.get("total"),
                      health.get("ported")) != (46, 46):
        raise Stop("NEW_VERSION_HEALTH_PARITY_FAILED")
    status, body = http("/api/providers", version=version)
    providers = body.get("providers")
    if status != 200 or not isinstance(providers, list) or len(providers) != 46:
        raise Stop("NEW_VERSION_CATALOG_UNVERIFIED")
    ids = [p.get("id") for p in providers if isinstance(p, dict)]
    if len(ids) != 46 or len(set(ids)) != 46 or not {"btdigg", "oxtorrent",
                                                   "torrent9", "therarbag"}.issubset(ids):
        raise Stop("NEW_VERSION_CATALOG_IDENTITIES_CHANGED")
    print("NEW_VERSION_ASSET_SHA_HEALTH_CATALOG_46: PASS", flush=True)


def diagnostic_checks(version):
    # A single owner-provided original-source detail; no alternate items,
    # .torrent fetch, real device token or real magnet delivery.
    status, body = http("/api/resolve", version=version,
                        body={"provider": "therarbag", "details": ORIGINAL},
                        diagnostic=True)
    trace = body.get("diagnostic")
    if (status not in (200, 502) or not isinstance(trace, dict)
        or trace.get("build") != "THERARBAG_IPHONE_DIAG_V1"
        or not isinstance(trace.get("htmlStage"), str)
        or trace["htmlStage"] not in STATES
        or not isinstance(trace.get("jsonStage"), str)
        or not re.fullmatch(r"[A-Z0-9_]{3,40}", trace["jsonStage"])
        or not isinstance(trace.get("elapsedMs"), (int, float))
        or not (0 <= trace["elapsedMs"] <= 30000)
        or not isinstance(trace.get("detailFingerprint"), str)
        or not re.fullmatch(r"[a-f0-9]{12}|unavailable",
                            trace["detailFingerprint"])):
        raise Stop("IMMUTABLE_WORKER_OPTIN_DIAGNOSTIC_UNVERIFIED")
    if status == 200 and not str(body.get("magnet", "")).startswith("magnet:?xt=urn:btih:"):
        raise Stop("IMMUTABLE_WORKER_MAGNET_INVALID")
    if status == 502 and body.get("code") not in (
        "DETAIL_NO_BTIH", "SOURCE_HTTP_403", "SOURCE_HTTP_429",
        "SOURCE_HTTP_404", "SOURCE_HTTP_503", "SOURCE_HTTP_502",
        "SOURCE_HTTP_504", "SOURCE_FETCH_FAILED", "SOURCE_CHALLENGE",
        "SOURCE_BAD_HTML", "SOURCE_HTTP_OTHER",
    ):
        # Source-error codes can differ by environment. A fully validated trace
        # remains sufficient instrumentation proof; no success claim for magnet.
        print("THE_RARBG_ORIGINAL_SOURCE_ERROR: source outcome not used as fix proof", flush=True)
    print("NEW_IMMUTABLE_OPTIN_DIAGNOSTIC: PASS; source magnet not asserted as repaired", flush=True)


def public_checks():
    reviewed = (ROOT / "web/app.js").read_bytes()
    for attempt in range(8):
        got = http("/app.js")
        if hashlib.sha256(got).digest() == hashlib.sha256(reviewed).digest():
            break
        # Cache propagation may return valid HTTP 200 with previous bytes;
        # refuse concurrent percentage changes during the bounded wait.
        rec, shares = snapshot()
        if shares != FULL:
            raise Stop("UNEXPECTED_POST_RELEASE_TRAFFIC_PERCENTAGE")
        if attempt == 7:
            raise Stop("PUBLIC_APP_JS_NOT_YET_NEW")
        time.sleep(5)
    status, health = http("/api/health")
    if status != 200 or (health.get("total"), health.get("ported")) != (46, 46):
        raise Stop("PUBLIC_HEALTH_PARITY_FAILED")
    print("PUBLIC_PRODUCTION_APP_JS_SHA_AND_HEALTH_46: PASS", flush=True)


def transition(before, source, target, label):
    stable(before, source)
    spec = [ACTIVE + "@" + str(target[ACTIVE]) + "%",
            NEW + "@" + str(target[NEW]) + "%"]
    if not _wrangler_deploy(spec, "Magnetra owner approved iPhone opt-in diagnosis " + label):
        raise Stop("IMMUTABLE_VERSION_DEPLOY_COMMAND_FAILED_" + label)
    after = wait_for(before, source, target, True)
    stable(after, target)
    print("IMMUTABLE_TRAFFIC_" + label + ": PASS", flush=True)
    return after


def rollback_if_known():
    try:
        dep, split = snapshot()
        if split == EXPECTED_SPLIT or split == SLOT:
            print("PRODUCTION_PRIOR_VERSION_ALREADY_AT_100: PASS", flush=True)
            return
        if split not in (CANARY, FULL):
            print("CRITICAL_UNKNOWN_SPLIT_NO_AUTOMATIC_ROLLBACK", flush=True)
            return
        verify_binding_payload(ACTIVE, _get_api("/versions/" + ACTIVE))
        verify_binding_payload(NEW, _get_api("/versions/" + NEW))
        stable(dep, split)
        if not _wrangler_deploy(
            [ACTIVE + "@100%", NEW + "@0%"],
            "Magnetra iPhone trace safety rollback, restore prior active 100"
        ):
            print("ROLLBACK_COMMAND_FAILED_MANUAL_AUDIT_REQUIRED", flush=True)
            return
        after = wait_for(dep, split, SLOT, True)
        stable(after, SLOT)
        print("AUTOMATIC_ROLLBACK_PRIOR_ACTIVE_100: PASS", flush=True)
    except (Stop, ValueError, KeyError, TypeError, OSError):
        print("ROLLBACK_NOT_VERIFIED_MANUAL_AUDIT_REQUIRED", flush=True)


def release():
    before = before_any_write()
    # Check the prior active public assets have NOT already changed.
    active_js = http("/app.js")
    if hashlib.sha256(active_js).digest() == hashlib.sha256(
        (ROOT / "web/app.js").read_bytes()).digest():
        raise Stop("PRODUCTION_ALREADY_HAS_CANDIDATE_SOURCE_STOP")
    stable(before, EXPECTED_SPLIT)

    # New version already exists; only the deployment record changes.
    slot = transition(before, EXPECTED_SPLIT, SLOT, "ZERO_SLOT")
    version_checks(NEW)
    diagnostic_checks(NEW)
    stable(slot, SLOT)
    print("ZERO_SLOT_IMMUTABLE_DIAGNOSTIC_VERIFIED: PASS", flush=True)

    canary = transition(slot, SLOT, CANARY, "CANARY_5")
    version_checks(NEW)
    stable(canary, CANARY)

    full = transition(canary, CANARY, FULL, "FULL_100")
    public_checks()
    stable(full, FULL)
    print("OWNER_IPHONE_TEST_READY: https://index.alexlab.media/?magnetra_diag=1", flush=True)
    print("PREVIOUS_VERSION_PRESERVED_0_PERCENT_FOR_ROLLBACK: " + ACTIVE, flush=True)
    print("THE_RARBG_IPHONE_ROOT_CAUSE_STILL_AWAITS_OWNER_REAL_SAME_CARD_TEST", flush=True)
    return 0


def main():
    if os.environ.get("MAGNETRA_IPHONE_DIAGNOSTIC_RELEASE_ACTION") != ACTION:
        print("EXPLICIT_OWNER_PRODUCTION_APPROVAL_MISSING")
        return 2
    try:
        return release()
    except (Stop, AccountStop, ValueError, KeyError, TypeError, OSError):
        print("IPHONE_DIAGNOSTIC_RELEASE_STOP_SAFE_GUARDS: no success claimed", flush=True)
        rollback_if_known()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
