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
import time
import urllib.error
import urllib.request

from deploy_magnetra_auto_pause_once import (
    Stop, ROOT, UUID, bindings, current, stable, snapshot,
    wait_for, uploaded_version_id, _wrangler_deploy, static_get,
)
from resume_magnetra_auto_pause_c86c import verify_assets

ACTIVE = "6dadc612-9660-4195-aeed-cdb658b22cf8"
OLDER_ROLLBACK = "9bbb227f-7f2a-4a9b-acac-ce8cae620c51"
INITIAL = {ACTIVE: 100, OLDER_ROLLBACK: 0}
ACTION = "CONFIRM_RO_IT_12_PICKER_20261021"
ORIGIN = "https://index.alexlab.media"
OLD_JS_SHA_PREFIX = "85969467f08d21ee"
EXPECTED_SECRETS = ["BTDIGG_GATEWAY_TOKEN", "MAGNETRA_GATEWAY_TOKEN"]


def identity_guard():
    config = json.loads((ROOT / "worker/wrangler.jsonc").read_text(encoding="utf8"))
    if (config.get("name") != "alexlab-magnetra"
        or config.get("main") != "src/index.mjs"
        or config.get("routes") != [{"pattern": "index.alexlab.media", "custom_domain": True}]
        or config.get("assets") != {"directory":"../web", "binding":"ASSETS"}):
        raise Stop("WORKER_ROUTE_AND_ASSET_ORIGIN_MISMATCH")
    app = (ROOT / "web/app.js").read_text(encoding="utf8")
    html = (ROOT / "web/index.html").read_text(encoding="utf8")
    i18n = (ROOT / "web/i18n.js").read_text(encoding="utf8")
    sw = (ROOT / "web/sw.js").read_text(encoding="utf8")
    memory = json.loads((ROOT / "config/project-invariants.json").read_text(encoding="utf8"))
    curated = memory.get("pwa_indexer_curation",{})
    bilingual = memory.get("bilingual_curated_release",{})
    hidden = set(curated.get("hidden_ids",[]))
    required = {"bangumimoe","btsow","dmhy","linuxtracker","mypornclub",
                "nekobt","sukebeinyaa","ytsmx","anilibria","blueroms",
                "epublibre","megapeer","rutorinfo","xxxtracker","fitgirlrepacks"}
    if (curated.get("hidden_from_picker_and_pwa_search_count") != 34
        or curated.get("visible_picker_count") != 12
        or len(hidden) != 34 or not required.issubset(hidden)
        or "btdigg" in hidden
        or bilingual.get("ui_languages") != ["ro","it"]
        or bilingual.get("default_language") != "ro"
        or 'const hiddenIndexerIds=new Set([' not in app
        or '"torrent9","oxtorrent"' not in app
        or 'const preferred=["btdigg","knaben","torrentscsv","thepiratebay","internetarchive"]' not in app
        or 'const valid=new Set(selectableProviders().map(p=>p.id))' not in app
        or 'const visibleFailures=failures.filter(f=>!hiddenIndexerIds.has(f.provider))' not in app
        or '<html lang="ro">' not in html
        or 'id="languageSelect"' not in html
        or 'src="/i18n.js"' not in html
        or 'src="/app.js"' not in html
        or 'const languages=["ro","it"]' not in i18n
        or 'const KEY="magnetra.language.v1"' not in i18n
        or 'const CACHE="alexlab-magnetra-v6"' not in sw
        or '"/i18n.js"' not in sw):
        raise Stop("REVIEWED_12_INDEXER_RO_IT_SOURCE_UNVERIFIED")
    return config


def active_asset_guard():
    """Allow only known prior live JS and exactly expected active versions."""
    digest = hashlib.sha256(static_get("/app.js")).hexdigest()
    if not digest.startswith(OLD_JS_SHA_PREFIX):
        raise Stop("LIVE_APP_JS_NOT_PREVIOUS_VERIFIED_6DAD_RELEASE")
    print("PREVIOUS_ACTIVE_JS_SHA_PASS:" + digest[:16])



def verify_reviewed_assets(version, deployment, shares):
    """Require the entire existing JS/CSS/HTML gate plus the separate offline locale bundle."""
    verify_assets(version, deployment, shares)
    expected=(ROOT / "web/i18n.js").read_bytes()
    got=static_get("/i18n.js",version)
    if hashlib.sha256(got).digest() != hashlib.sha256(expected).digest():
        raise Stop("I18N_SHA_MISMATCH")
    print("REVIEWED_I18N_PASS: /i18n.js sha="+hashlib.sha256(expected).hexdigest()[:16])


def settle_public(deployment,full):
    """Bounded HTML-200 propagation only; no retry for HTTP failures/429/504."""
    for attempt in range(6):
        try:
            verify_reviewed_assets(None,deployment,full)
            return
        except Stop as error:
            if str(error)!="HTML_NOT_REVIEWED_SOURCE_OR_KNOWN_CLOUDFLARE_BEACON" or attempt==5:
                raise
            stable(deployment,full)
            print("HTML_200_SHA_PENDING: bounded 8s wait "+str(attempt+1)+"/5")
            time.sleep(8)


def upload_version(config):
    """Upload an immutable 0%-traffic version, preserving existing secrets."""
    config = dict(config)
    config["secrets"] = {"required": EXPECTED_SECRETS}
    tmp = ROOT / "worker/.wrangler-ro-it12-20261021.jsonc"
    if tmp.exists():
        raise Stop("TEMPORARY_CONFIG_ALREADY_EXISTS")
    tmp.write_text(json.dumps(config, indent=2) + "\n", encoding="utf8")
    os.chmod(tmp, 0o600)
    try:
        try:
            p = subprocess.run(
                ["npx", "--yes", "wrangler@4.102.0", "versions", "upload",
                 "--config", str(tmp), "--keep-vars",
                 "--message", "Magnetra 12 selectable RO/IT indexers; 46 original adapters retained"],
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
            "Magnetra curated indexer guarded rollback to proven 6dad"
        )
        if not ok:
            print("ROLLBACK_UNVERIFIED: Wrangler deployment rejected")
            return
        wait_for(current_record, shares, slot, ok)
        print("ROLLBACK_POSTFLIGHT_PASS: prior active version 100%, uploaded candidate 0%")
    except (Stop, ValueError, TypeError, KeyError, OSError):
        print("ROLLBACK_UNVERIFIED: inspect immutable traffic split manually")


def publish():
    config = identity_guard()
    first = current(INITIAL)
    bindings(ACTIVE)
    bindings(OLDER_ROLLBACK)
    active_asset_guard()
    stable(first, INITIAL)
    print("BASELINE_PASS: 6dad100/9bbb0, 3 required bindings each")

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
        verify_reviewed_assets(candidate, zero_deployment, slot)
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
        verify_reviewed_assets(candidate, canary_deployment, canary)
        stable(canary_deployment, canary)
        print("CANARY_FIVE_PERCENT_POSTFLIGHT_PASS")

        full = {ACTIVE: 0, candidate: 100}
        print("RELEASE_ONE_HUNDRED_PERCENT: old0/new100; previous preserved")
        ok = _wrangler_deploy(
            [ACTIVE + "@0%", candidate + "@100%"],
            "Magnetra 12-indexer Romanian Italian PWA 100 percent; 6dad rollback"
        )
        full_deployment = wait_for(canary_deployment, canary, full, ok)
        settle_public(full_deployment, full)
        catalog_guard(None)
        bindings(ACTIVE)
        bindings(candidate)
        stable(full_deployment, full)
        print("RO_IT12_PUBLIC_RELEASE_PASS: candidate100/6dad0; version=" + candidate)
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
