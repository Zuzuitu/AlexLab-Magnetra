#!/usr/bin/env python3
"""Read-only check for a REAL browser-testable Cloudflare Worker Version URL.

Only official fixed Cloudflare API GETs and bounded GETs to an exact, verified
*.workers.dev host. Never changes DNS, Worker settings, previews, deployments,
secrets or traffic, and never sends a torrent or magnet.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import urllib.error
import urllib.request

from deploy_magnetra_zero_percent import _get_api, _current_deployment, _shares
from deploy_magnetra_auto_pause_once import Stop, NoRedirect, ROOT
from stage_therarbag_iphone_20261024 import (
    ACTIVE, PREVIOUS_ZERO, EXPECTED_SPLIT, EXPECTED_BINDINGS,
    verify_binding_payload,
)

VERSION = "139d97f7-4048-4bbb-8e90-80585f1f4b26"
ACTION = "CONFIRM_READ_ONLY_IPHONE_VERSION_URL_AUDIT_20261024"
ACCOUNT = re.compile(r"^[a-f0-9]{32}$", re.I)
SUBDOMAIN = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")


def api_get(path):
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
    account = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
    if not token or not ACCOUNT.fullmatch(account):
        raise Stop("CLOUDFLARE_READONLY_CREDENTIALS_UNVERIFIED")
    if path not in ("/workers/subdomain",
                    "/workers/scripts/alexlab-magnetra/subdomain"):
        raise Stop("CLOUDFLARE_ENDPOINT_NOT_ALLOWLISTED")
    url = "https://api.cloudflare.com/client/v4/accounts/" + account + path
    req = urllib.request.Request(
        url, method="GET",
        headers={"Authorization": "Bearer " + token, "Accept": "application/json"},
    )
    try:
        with urllib.request.build_opener(NoRedirect()).open(req, timeout=20) as res:
            if res.status != 200:
                raise Stop("CLOUDFLARE_GET_HTTP_NOT_200")
            raw = res.read(65537)
    except (urllib.error.URLError, OSError, TimeoutError):
        raise Stop("CLOUDFLARE_GET_FAILED") from None
    if not raw or len(raw) > 65536:
        raise Stop("CLOUDFLARE_RESPONSE_SIZE_REJECTED")
    try:
        payload = json.loads(raw)
    except (ValueError, TypeError):
        raise Stop("CLOUDFLARE_INVALID_JSON") from None
    if not isinstance(payload, dict) or payload.get("success") is not True:
        raise Stop("CLOUDFLARE_RESPONSE_UNVERIFIED")
    if not isinstance(payload.get("result"), dict):
        raise Stop("CLOUDFLARE_RESULT_UNVERIFIED")
    return payload["result"]


def preview_host(account_result, script_result):
    if script_result.get("previews_enabled") is not True:
        return None
    name = account_result.get("subdomain")
    if not isinstance(name, str) or not SUBDOMAIN.fullmatch(name):
        raise Stop("CLOUDFLARE_SUBDOMAIN_UNVERIFIED")
    return VERSION[:8] + "-alexlab-magnetra." + name + ".workers.dev"


def fixed_preview_get(host, path, *, accept, max_bytes):
    if not host or not host.endswith(".workers.dev") or not path in (
        "/api/health", "/api/providers", "/app.js"
    ):
        raise Stop("PREVIEW_PATH_NOT_ALLOWED")
    req = urllib.request.Request(
        "https://" + host + path,
        headers={
            "Accept": accept, "Accept-Encoding": "identity",
            "Cache-Control": "no-store", "Pragma": "no-cache",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1",
        }, method="GET",
    )
    try:
        with urllib.request.build_opener(NoRedirect()).open(req, timeout=18) as res:
            status = res.status
            mime = res.headers.get("content-type", "")
            raw = res.read(max_bytes + 1)
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, TimeoutError):
        raise Stop("PREVIEW_GET_UNAVAILABLE") from None
    if status != 200 or not raw or len(raw) > max_bytes:
        raise Stop("PREVIEW_RESPONSE_UNVERIFIED")
    return mime, raw


def proof():
    before = _current_deployment(_get_api("/deployments"))
    if _shares(before) != EXPECTED_SPLIT:
        raise Stop("LIVE_TRAFFIC_SPLIT_CHANGED")
    verify_binding_payload(VERSION, _get_api("/versions/" + VERSION))
    account = api_get("/workers/subdomain")
    script = api_get("/workers/scripts/alexlab-magnetra/subdomain")
    again = _current_deployment(_get_api("/deployments"))
    if again.get("id") != before.get("id") or _shares(again) != EXPECTED_SPLIT:
        raise Stop("CONCURRENT_TRAFFIC_CHANGE_REFUSED")
    print("CANDIDATE_BINDINGS_FOUR: PASS", flush=True)
    print("UNMODIFIED_100_0_SPLIT: PASS", flush=True)
    if script.get("previews_enabled") is not True:
        print("CLOUDFLARE_VERSION_URLS: DISABLED", flush=True)
        print("NO_CHANGE: preview settings not altered", flush=True)
        return False
    host = preview_host(account, script)
    if not host:
        raise Stop("VERSION_URL_NOT_VERIFIED")
    mime_health, raw_health = fixed_preview_get(host, "/api/health",
                                                  accept="application/json", max_bytes=4096)
    if "application/json" not in mime_health.lower():
        raise Stop("VERSION_URL_HEALTH_MIME_INVALID")
    try:
        health = json.loads(raw_health)
    except ValueError:
        raise Stop("VERSION_URL_HEALTH_JSON_INVALID") from None
    if health.get("ok") is not True or health.get("ported") != 46 or health.get("total") != 46:
        raise Stop("VERSION_URL_HEALTH_PARITY_FAILED")
    mime_js, raw_js = fixed_preview_get(host, "/app.js",
                                       accept="text/javascript,application/javascript",
                                       max_bytes=900000)
    if "javascript" not in mime_js.lower():
        raise Stop("VERSION_URL_JS_MIME_INVALID")
    expected = (ROOT / "web/app.js").read_bytes()
    if hashlib.sha256(raw_js).digest() != hashlib.sha256(expected).digest():
        raise Stop("VERSION_URL_PWA_CONTENT_MISMATCH")
    after = _current_deployment(_get_api("/deployments"))
    if after.get("id") != before.get("id") or _shares(after) != EXPECTED_SPLIT:
        raise Stop("CLOUDFLARE_TRAFFIC_CHANGED_AFTER_PROBE")
    print("IPHONE_VERSION_URL_HEALTH_46: PASS", flush=True)
    print("IPHONE_VERSION_URL_JS_SHA256: PASS", flush=True)
    print("IPHONE_VERSION_URL_VERIFIED: https://" + host + "/?magnetra_diag=1", flush=True)
    print("NORMAL_PRODUCTION_TRAFFIC_UNCHANGED: PASS", flush=True)
    return True


def main():
    if os.environ.get("MAGNETRA_THERARBAG_PREVIEW_AUDIT_ACTION") != ACTION:
        print("OWNER_READONLY_ACTIVATION_NOT_PRESENT")
        return 2
    try:
        proof()
        return 0
    except (Stop, ValueError, TypeError, KeyError, OSError):
        print("VERSION_URL_READONLY_AUDIT_STOP: no Cloudflare changes attempted")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
