#!/usr/bin/env python3
"""Non-mutating exact-540b 0%-slot acceptance: asset attribution and two sources.

Requires *prior separately approved* Cloudflare slot 249d@100% / 540b@0%.
Uses immutable version override for the staged Worker. Never makes BTDigg/EZTV
requests, opens magnet URI, follows ad links, or downloads .torrent files.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from deploy_magnetra_zero_percent import _current_deployment, _get_api, _shares
from inspect_magnetra_fix_stage import STAGED, ACTIVE, EXPECTED, binding_pairs
from diagnose_magnetra_detail_routes import route_shape

ACTION = "RUN_READONLY_540B_FIX_E2E"
WORKER = "alexlab-magnetra"
BASE = "https://index.alexlab.media"
OVERRIDE = WORKER + '="' + STAGED + '"'
PROVIDERS = ("oxtorrent", "torrent9")
MAGNET = re.compile(r"^magnet:\?xt=urn:btih:(?:[a-f0-9]{40}|[a-z2-7]{32})(?:&|$)", re.I)
MAX_BYTES = 800_000
MAX_RESULTS = 200


class Stop(Exception):
    """Sanitized diagnostic failure."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def deployment_gate() -> str:
    version = _get_api("/versions/" + STAGED)
    if (not isinstance(version, dict) or version.get("success") is not True
            or not isinstance(version.get("result"), dict)
            or version["result"].get("id") != STAGED):
        raise Stop("EXACT_STAGED_VERSION_UNVERIFIED")
    pairs = binding_pairs(version)
    for name, valid_types in EXPECTED.items():
        if not any((name, kind) in pairs for kind in valid_types):
            raise Stop("STAGED_BINDING_UNVERIFIED_" + name)
    deployment = _current_deployment(_get_api("/deployments"))
    shares = _shares(deployment)
    if shares != {ACTIVE: 100, STAGED: 0}:
        raise Stop("EXPECTED_EXACT_249D100_540B0_SLOT_MISSING")
    if not isinstance(deployment.get("id"), str) or not deployment["id"]:
        raise Stop("DEPLOYMENT_ID_UNVERIFIED")
    print("STAGED_0_PERCENT_GATE: PASS (249d 100%, 540b 0%, all three bindings).")
    return deployment["id"]


def http_get(path: str, *, staged: bool, payload: dict | None = None):
    if not path.startswith("/") or path.startswith("//") or "\\" in path:
        raise Stop("UNSAFE_FIXED_PUBLIC_PATH")
    method = "POST" if payload is not None else "GET"
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8") if payload is not None else None
    if body is not None and len(body) > 1200:
        raise Stop("RESOLVE_PAYLOAD_TOO_LARGE")
    headers = {
        "User-Agent": "AlexLab-Magnetra-Resolve540bE2E/1.0",
        "Cache-Control": "no-store",
        "Accept-Encoding": "identity",
        "Accept": "application/json" if path.startswith("/api/") else "text/javascript,application/javascript",
    }
    if staged:
        headers["Cloudflare-Workers-Version-Overrides"] = OVERRIDE
    if body is not None:
        headers["Origin"] = BASE
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=body, method=method, headers=headers)
    try:
        with urllib.request.build_opener(NoRedirect).open(req, timeout=32) as resp:
            status, mime = resp.status, resp.headers.get("content-type", "")
            result = resp.read(MAX_BYTES + 1)
    except urllib.error.HTTPError as e:
        # No body/error details are echoed to logs.
        raise Stop("PUBLIC_WORKER_HTTP_" + str(e.code)) from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise Stop("PUBLIC_WORKER_TRANSPORT_UNVERIFIED") from None
    if status != 200 or len(result) > MAX_BYTES or not result:
        raise Stop("PUBLIC_WORKER_RESPONSE_UNVERIFIED")
    if path.startswith("/api/"):
        if "application/json" not in mime:
            raise Stop("PUBLIC_WORKER_NOT_JSON")
        try:
            parsed = json.loads(result)
        except (UnicodeDecodeError, ValueError):
            raise Stop("PUBLIC_WORKER_MALFORMED_JSON") from None
        if not isinstance(parsed, dict):
            raise Stop("PUBLIC_WORKER_JSON_SHAPE")
        return parsed
    if "javascript" not in mime:
        raise Stop("PUBLIC_APP_JS_MIME_UNVERIFIED")
    return result


def verify_asset_override() -> None:
    reviewed = (Path(__file__).resolve().parent.parent / "web" / "app.js").read_bytes()
    live_staged = http_get("/app.js", staged=True)
    live_active = http_get("/app.js", staged=False)
    new_digest = hashlib.sha256(reviewed).digest()
    if hashlib.sha256(live_staged).digest() != new_digest:
        raise Stop("STAGED_VERSION_ASSET_ATTRIBUTION_FAILED")
    if hashlib.sha256(live_active).digest() == new_digest:
        raise Stop("ACTIVE_ASSET_ALREADY_MATCHES_STAGE_OR_OVERRIDE_IGNORED")
    print("STAGED_APP_JS_ATTRIBUTION: PASS (540b matches reviewed fix; 249d differs).")


def valid_magnet(value) -> bool:
    return isinstance(value, str) and len(value) <= 12000 and bool(MAGNET.search(value))


def verify_provider_catalog() -> None:
    body = http_get("/api/providers", staged=True)
    providers = body.get("providers")
    if not isinstance(providers, list):
        raise Stop("STAGED_PROVIDER_CATALOG_UNVERIFIED")
    ids = [p.get("id") for p in providers if isinstance(p, dict)]
    if len(ids) != 46 or len(set(ids)) != 46:
        raise Stop("STAGED_CATALOG_46_UNVERIFIED")
    print("STAGED_PROVIDER_CATALOG: PASS 46/46.")


def verify_original_sources() -> None:
    query = urllib.parse.urlencode({
        "q": "2026", "providers": ",".join(PROVIDERS), "category": "all",
    })
    body = http_get("/api/search?" + query, staged=True)
    rows = body.get("results")
    errors = body.get("errors")
    if not isinstance(rows, list) or not isinstance(errors, list) or len(rows) > MAX_RESULTS:
        raise Stop("STAGED_SEARCH_SCHEMA_UNVERIFIED")
    if errors:
        # Do not echo user/site-controlled error messages or retry on 429.
        raise Stop("STAGED_SEARCH_SOURCE_ERROR")
    selected = {}
    counters = {"oxtorrent": 0, "torrent9": 0}
    for row in rows:
        if not isinstance(row, dict):
            raise Stop("STAGED_SEARCH_ROW_MALFORMED")
        provider = row.get("provider")
        if provider not in PROVIDERS:
            raise Stop("STAGED_SEARCH_SOURCE_IDENTITY_MISMATCH")
        detail = row.get("details")
        if route_shape(provider, detail) != "CANONICAL_DETAIL":
            raise Stop("STAGED_DETAIL_NONCANONICAL_" + provider)
        counters[provider] += 1
        if provider not in selected and not valid_magnet(row.get("magnet")):
            selected[provider] = detail
    for provider in PROVIDERS:
        if not counters[provider] or provider not in selected:
            raise Stop("STAGED_SOURCE_EMPTY_OR_NO_UNRESOLVED_" + provider)
        # Deliberately POSTs original canonical DETAILS, never advertising
        # magnetSource, user-defined URL, download URL, or Flud command.
        resolved = http_get("/api/resolve", staged=True,
                            payload={"provider": provider, "details": selected[provider]})
        if resolved.get("provider") != provider or not valid_magnet(resolved.get("magnet")):
            raise Stop("STAGED_DEFERRED_RESOLVE_UNVERIFIED_" + provider)
        print("STAGED_RESOLVE_PASS_" + provider + ": authentic canonical detail -> valid BTIH (withheld).")
    print("STAGED_SOURCE_SEARCH_PASS: OxTorrent " + str(counters["oxtorrent"]) +
          ", Torrent9 " + str(counters["torrent9"]) + " original results.")


def execute() -> int:
    if os.environ.get("MAGNETRA_FIX_E2E_ACTION") != ACTION:
        raise Stop("EXPLICIT_BOUNDED_E2E_OWNER_APPROVAL_REQUIRED")
    deployment_id = deployment_gate()
    verify_asset_override()
    verify_provider_catalog()
    verify_original_sources()
    if deployment_gate() != deployment_id:
        raise Stop("DEPLOYMENT_CHANGED_DURING_TEST")
    print("STAGED_FIX_E2E_GATE: PASS (no Worker deploy, BTDigg/EZTV, torrent download, magnet output or Flud).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(execute())
    except Stop as exc:
        print("STAGED_FIX_E2E_GATE: STOP " + str(exc))
        sys.exit(1)
    except (ValueError, TypeError, KeyError):
        print("STAGED_FIX_E2E_GATE: STOP_UNVERIFIED (redacted metadata issue)")
        sys.exit(1)
