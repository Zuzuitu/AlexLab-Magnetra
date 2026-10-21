#!/usr/bin/env python3
"""One-shot guarded release of owner-approved Magnetra PWA indexer curation.

Only changes one Worker immutable VERSION and its traffic split, never
Rock64/Tunnels/DNS, source fetch policies, secrets, or Flud Companion.
Requires the unique approved GitHub Actions push marker and reviewed main.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.error
import urllib.request

from deploy_magnetra_auto_pause_once import (
    Stop, ROOT, UUID, bindings, current, stable, snapshot,
    wait_for, uploaded_version_id, _wrangler_deploy, static_get,
)
from resume_magnetra_auto_pause_c86c import verify_assets

ACTIVE = "c86c9a32-31fd-4952-86ed-b35f1763b342"
OLDER_ROLLBACK = "136c1425-0070-48db-b995-5708bd35bb75"
INITIAL = {ACTIVE: 100, OLDER_ROLLBACK: 0}
ACTION = "CONFIRM_CURATED_UI_OWNER_RELEASE_20261021"
ORIGIN = "https://index.alexlab.media"
OLD_JS_SHA_PREFIX = "9998e0130b19ece9"
EXPECTED_SECRETS = ["BTDIGG_GATEWAY_TOKEN", "MAGNETRA_GATEWAY_TOKEN"]


def identity_guard():
    config = json.loads((ROOT / "worker/wrangler.jsonc").read_text(encoding="utf8"))
    if (
        config.get("name") != "alexlab-magnetra"
        or config.get("main") != "src/index.mjs"
        or config.get("routes") != [
            {"pattern": "index.alexlab.media", "custom_domain": True}
        ]
        or config.get("assets") != {
            "directory": "../web", "binding": "ASSETS"
        }
    ):
        raise Stop("WORKER_ROUTE_AND_ASSET_ORIGIN_MISMATCH")
    app = (ROOT / "web/app.js").read_text(encoding="utf8")
    html = (ROOT / "web/index.html").read_text(encoding="utf8")
    if ("const hiddenIndexerIds=new Set([" not in app
            or 'const preferred=["btdigg","knaben","torrentscsv","thepiratebay","internetarchive"]' not in app
            or '"torrentz"' not in app
            or '"torrent9","oxtorrent"' not in app
            or 'Select all available' not in html
            or 'Select all 46' in html):
        raise Stop("REVIEWED_CURATED_SOURCE_NOT_PRESENT")
    return config


def active_asset_guard():
    """Allow only known prior live JS and exactly expected active versions."""
    digest = hashlib.sha256(static_get("/app.js")).hexdigest()
    if not digest.startswith(OLD_JS_SHA_PREFIX):
        raise Stop("LIVE_APP_JS_NOT_PREVIOUS_VERIFIED_C86C_RELEASE")
    print("PREVIOUS_ACTIVE_JS_SHA_PASS:" + digest[:16])


def upload_version(config):
    """Upload an immutable 0%-traffic version, preserving existing secrets."""
    config = dict(config)
    config["secrets"] = {"required": EXPECTED_SECRETS}
    tmp = ROOT / "worker/.wrangler-curated-20261021.jsonc"
    if tmp.exists():
        raise Stop("TEMPORARY_CONFIG_ALREADY_EXISTS")
    tmp.write_text(json.dumps(config, indent=2) + "\n", encoding="utf8")
    os.chmod(tmp, 0o600)
    try:
        try:
            p = subprocess.run(
                ["npx", "--yes", "wrangler@4.102.0", "versions", "upload",
                 "--config", str(tmp), "--keep-vars",
                 "--message", "Magnetra curated 29 indexers; 46 original adapters retained"],
                cwd=ROOT, capture_output=True, text=True, timeout=220,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            raise Stop("WRANGLER_VERSION_UPLOAD_UNVERIFIED") from None
        if p.returncode:
            raise Stop("WRANGLER_VERSION_UPLOAD_FAILED")
        identifier = uploaded_version_id(p.stdout + "\n" + p.stderr)
        if identifier in INITIAL:
            raise Stop("NEW_VERSION_COLLIDES_WITH_APPROVED_BASELINE")
        print("CURATED_VERSION_UPLOADED:" + identifier)
        return identifier
    finally:
        tmp.unlink(missing_ok=True)


def catalog_guard(version: str | None):
    """GET-only fixed origin JSON catalog: all 46 IDs must still be available."""
    headers = {
        "Accept": "application/json", "Cache-Control": "no-store",
        "Accept-Encoding": "identity", "User-Agent": "MagnetraCuratedUiRelease/1.0",
    }
    if version:
        if not UUID.fullmatch(version):
            raise Stop("INVALID_OVERRIDE_VERSION")
        headers["Cloudflare-Workers-Version-Overrides"] = (
            'alexlab-magnetra="' + version + '"'
        )
    req = urllib.request.Request(
        ORIGIN + "/api/providers", method="GET", headers=headers
    )
    opener = urllib.request.build_opener(
        # Do not follow an unexpected off-origin redirect.
        __import__("deploy_magnetra_auto_pause_once").NoRedirect()
    )
    try:
        with opener.open(req, timeout=20) as response:
            if response.status != 200 or "json" not in response.headers.get("content-type", ""):
                raise Stop("CATALOG_HTTP_OR_TYPE_MISMATCH")
            raw = response.read(1_000_001)
        if len(raw) > 1_000_000:
            raise Stop("CATALOG_RESPONSE_TOO_LARGE")
        catalog = json.loads(raw).get("providers")
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, TimeoutError,
            ValueError, TypeError, AttributeError):
        raise Stop("CATALOG_READ_UNVERIFIED") from None
    if not isinstance(catalog, list) or len(catalog) != 46:
        raise Stop("CATALOG_NO_LONGER_46")
    ids = [r.get("id") for r in catalog if isinstance(r, dict)]
    if (len(ids) != 46 or len(set(ids)) != 46
            or not {"btdigg", "torrent9", "oxtorrent", "torrentz", "eztvx"}.issubset(ids)):
        raise Stop("ORIGINAL_PROVIDER_IDENTITIES_NOT_PRESERVED")
    print("ORIGINAL_PROVIDER_CATALOG_PASS:46; no search or torrent requests")


def rollback_if_safe(new: str | None):
    """One bounded rollback attempt after canary/full failure, no guesses."""
    if not new or not UUID.fullmatch(new):
        return
    try:
        current_record, shares = snapshot()
    except (ValueError, Stop, TypeError, KeyError):
        print("ROLLBACK_NEEDS_MANUAL_AUDIT: deployment metadata unavailable")
        return
    canary = {ACTIVE: 95, new: 5}
    full = {ACTIVE: 0, new: 100}
    slot = {ACTIVE: 100, new: 0}
    if shares in (INITIAL, slot):
        print("SAFE_WITHOUT_ROLLBACK: verified old Worker still serves 100%")
        return
    if shares not in (canary, full):
        print("ROLLBACK_REFUSED: unknown or concurrently modified traffic split")
        return
    try:
        bindings(ACTIVE)
        bindings(new)
        # Refuse to replace a deployment that changed after last inspection.
        stable(current_record, shares)
        ok = _wrangler_deploy(
            [ACTIVE + "@100%", new + "@0%"],
            "Magnetra curated indexer guarded rollback to proven c86c"
        )
        if not ok:
            print("ROLLBACK_UNVERIFIED: Wrangler deployment rejected")
            return
        wait_for(current_record, shares, slot, ok)
        print("ROLLBACK_POSTFLIGHT_PASS: known c86c100 / curated0")
    except (Stop, ValueError, TypeError, KeyError, OSError):
        print("ROLLBACK_UNVERIFIED: inspect immutable traffic split manually")


def publish():
    config = identity_guard()
    first = current(INITIAL)
    bindings(ACTIVE)
    bindings(OLDER_ROLLBACK)
    active_asset_guard()
    stable(first, INITIAL)
    print("BASELINE_PASS: c86c100 136c0, 3 required bindings each")

    candidate = None
    try:
        candidate = upload_version(config)
        bindings(candidate)
        stable(first, INITIAL)

        slot = {ACTIVE: 100, candidate: 0}
        print("ZERO_PERCENT_SLOT: old100/new0")
        ok = _wrangler_deploy(
            [ACTIVE + "@100%", candidate + "@0%"],
            "Magnetra curated picker immutable 0 percent verification"
        )
        zero_deployment = wait_for(first, INITIAL, slot, ok)
        verify_assets(candidate, zero_deployment, slot)
        catalog_guard(candidate)
        stable(zero_deployment, slot)
        print("CANDIDATE_STATIC_AND_CATALOG_AT_ZERO_PASS")

        canary = {ACTIVE: 95, candidate: 5}
        print("CANARY_FIVE_PERCENT: old95/new5")
        ok = _wrangler_deploy(
            [ACTIVE + "@95%", candidate + "@5%"],
            "Magnetra curated picker 5 percent canary"
        )
        canary_deployment = wait_for(zero_deployment, slot, canary, ok)
        bindings(candidate)
        verify_assets(candidate, canary_deployment, canary)
        stable(canary_deployment, canary)
        print("CANARY_FIVE_PERCENT_POSTFLIGHT_PASS")

        full = {ACTIVE: 0, candidate: 100}
        print("RELEASE_ONE_HUNDRED_PERCENT: old0/new100; previous preserved")
        ok = _wrangler_deploy(
            [ACTIVE + "@0%", candidate + "@100%"],
            "Magnetra curated picker 29 indexers 100 percent; c86c rollback"
        )
        full_deployment = wait_for(canary_deployment, canary, full, ok)
        verify_assets(None, full_deployment, full)
        catalog_guard(None)
        bindings(ACTIVE)
        bindings(candidate)
        stable(full_deployment, full)
        print("CURATED_PUBLIC_RELEASE_PASS: new100/c86c0; version=" + candidate)
        return 0
    except (Stop, ValueError, TypeError, KeyError, OSError):
        print("CURATED_RELEASE_STOP: guarded Cloudflare asset/version/traffic gate")
        rollback_if_safe(candidate)
        return 1


def main():
    if os.environ.get("MAGNETRA_CURATED_RELEASE_ACTION") != ACTION:
        print("STOP: unique owner-approved release marker absent, no Cloudflare call")
        return 2
    try:
        return publish()
    except (Stop, ValueError, TypeError, KeyError, OSError):
        print("PREUPLOAD_STOP: active production no longer matches verified state")
        return 1


if __name__ == "__main__":
    sys.exit(main())
