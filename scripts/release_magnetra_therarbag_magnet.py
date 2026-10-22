#!/usr/bin/env python3
"""Owner-approved, immutable, fail-closed TheRarBg source-owned magnet fix release.

Requires a unique GitHub Actions activation-only marker. Preserves 46 original
API adapters and existing secrets; zero source queries or Rock64 changes.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

from deploy_magnetra_auto_pause_once import (
    Stop, ROOT, UUID, NoRedirect, bindings, current, stable, snapshot,
    wait_for, uploaded_version_id, _wrangler_deploy, static_get,
)
from resume_magnetra_auto_pause_c86c import verify_assets
from release_magnetra_hide_anime_mikan import catalog_guard

ACTIVE = "60112a3d-b478-4071-b087-ab793fbdfd60"
ROLLBACK = "6dadc612-9660-4195-aeed-cdb658b22cf8"
INITIAL = {ACTIVE: 100, ROLLBACK: 0}
ACTION = "CONFIRM_MAGNETRA_THERARBG_MAGNET_20261021"
ORIGIN = "https://index.alexlab.media"
OLD_JS_SHA_PREFIX = "44f1eac85e8550a7"
SECRET_NAMES = ["BTDIGG_GATEWAY_TOKEN", "MAGNETRA_GATEWAY_TOKEN"]


def guard_source():
    config = json.loads((ROOT / "worker/wrangler.jsonc").read_text(encoding="utf8"))
    if (config.get("name") != "alexlab-magnetra" or
        config.get("main") != "src/index.mjs" or
        config.get("routes") != [
            {"pattern": "index.alexlab.media", "custom_domain": True}
        ] or
        config.get("assets") != {"directory": "../web", "binding": "ASSETS"}):
        raise Stop("PRODUCTION_ROUTE_OR_ASSETS_UNVERIFIED")
    app = (ROOT / "web/app.js").read_text(encoding="utf8")
    html = (ROOT / "web/index.html").read_text(encoding="utf8")
    i18n = (ROOT / "web/i18n.js").read_text(encoding="utf8")
    sw = (ROOT / "web/sw.js").read_text(encoding="utf8")
    cfg = json.loads((ROOT / "config/project-invariants.json").read_text(encoding="utf8"))
    picker = cfg["pwa_indexer_curation"]
    locale = cfg["bilingual_curated_release"]
    if (len(picker["hidden_ids"]) != 34 or picker["visible_picker_count"] != 12
        or picker["original_adapter_ids_retained"] != 46
        or not {"bangumimoe", "ytsmx", "fitgirlrepacks", "mikanproject"}.issubset(picker["hidden_ids"])
        or picker["priority_visible_ids"][:3] != ["btdigg", "torrent9", "oxtorrent"]
        or locale["default_language"] != "ro" or locale["ui_languages"] != ["ro", "it"]
        or 'lang="ro"' not in html or 'id="languageSelect"' not in html
        or 'src="/i18n.js"' not in html
        or 'const hiddenIndexerIds=new Set([' not in app
        or 'const visibleFailures=failures.filter(f=>!hiddenIndexerIds.has(f.provider))' not in app
        or 'const ROMANIAN_KEYS=new Map(' not in i18n
        or '"/i18n.js"' not in sw or 'RESULTS THIS SESSION' in app
        or "Select all 46" in html):
        raise Stop("REVIEWED_THERARBG_PICKER_SOURCE_MISMATCH")
    source=(ROOT/"worker/src/legacy-adapters.mjs").read_text(encoding="utf8")
    pwa=(ROOT/"web/app.js").read_text(encoding="utf8")
    i18n=(ROOT/"web/i18n.js").read_text(encoding="utf8")
    if ("export function magnetFromTheRarBgInfoHash(html){" not in source
        or not (
            'if(!magnet&&id==="therarbag")magnet=magnetFromTheRarBgInfoHash(html);' in source
            or (
                'export function magnetFromTheRarBgSourceMetadata(html){' in source
                and 'if(!magnet&&id==="therarbag")magnet=magnetFromTheRarBgSourceMetadata(html);' in source
                and 'url.hostname!=="itorrents.org"' in source
                and 'url.search||url.hash' in source
            )
        )
        or "function magnetFailureText(item,error)" not in pwa
        or '"TheRarBg could not provide this magnet.' not in i18n):
        raise Stop("REVIEWED_THERARBG_SOURCE_FIX_MISSING")
    return config


def old_js_guard():
    actual = hashlib.sha256(static_get("/app.js")).hexdigest()
    if not actual.startswith(OLD_JS_SHA_PREFIX):
        raise Stop("OLD_LIVE_APP_JS_SHA_CHANGED")
    print("VERIFIED_BASELINE_JS_SHA:" + actual[:16])


def upload_version(config):
    data = dict(config)
    data["secrets"] = {"required": SECRET_NAMES}
    tmp = ROOT / "worker/.wrangler-therarbag-magnet-20261021.jsonc"
    if tmp.exists():
        raise Stop("TEMPORARY_RELEASE_CONFIG_ALREADY_EXISTS")
    tmp.write_text(json.dumps(data,indent=2)+"\n", encoding="utf8")
    os.chmod(tmp,0o600)
    try:
        try:
            process = subprocess.run(
                ["npx","--yes","wrangler@4.102.0","versions","upload",
                 "--config",str(tmp),"--keep-vars",
                 "--message","Magnetra TheRarBg source-owned magnet curated PWA; original 46 API identities retained"],
                cwd=ROOT,capture_output=True,text=True,timeout=220,check=False)
        except (OSError,subprocess.TimeoutExpired):
            raise Stop("NEW_IMMUTABLE_UPLOAD_UNVERIFIED") from None
        if process.returncode:
            raise Stop("NEW_IMMUTABLE_UPLOAD_FAILED")
        ident=uploaded_version_id(process.stdout+"\n"+process.stderr)
        if ident in INITIAL:
            raise Stop("CANDIDATE_VERSION_COLLISION")
        print("THERARBG_IMMUTABLE_VERSION_UPLOADED:" + ident)
        return ident
    finally:
        tmp.unlink(missing_ok=True)


def read_i18n(version):
    """One fixed-origin HTTPS read. Never follow off-origin redirects."""
    headers={"Accept-Encoding":"identity",
             "Cache-Control":"no-cache,no-store,max-age=0",
             "Pragma":"no-cache",
             "User-Agent":"MagnetraROITImmutableRelease/1.0"}
    if version is not None:
        if not UUID.fullmatch(version):
            raise Stop("UNVERIFIED_LANGUAGE_ASSET_OVERRIDE_VERSION")
        headers["Cloudflare-Workers-Version-Overrides"] = 'alexlab-magnetra="' + version + '"'
    req=urllib.request.Request(ORIGIN+"/i18n.js",headers=headers,method="GET")
    try:
        with urllib.request.build_opener(NoRedirect()).open(req,timeout=20) as response:
            if response.status!=200 or "javascript" not in response.headers.get("content-type","").lower():
                raise Stop("TRANSLATION_ASSET_STATUS_OR_MIME_INVALID")
            data=response.read(1_200_001)
    except (urllib.error.HTTPError,urllib.error.URLError,OSError,TimeoutError):
        raise Stop("TRANSLATION_ASSET_TRANSPORT_NO_RETRY") from None
    if not data or len(data)>1_200_000:
        raise Stop("TRANSLATION_ASSET_LENGTH_INVALID")
    return data


def verify_all_assets(version, deployment, split):
    # Existing audited SHA / beacon guard (JS, CSS and full root HTML).
    verify_assets(version,deployment,split)
    expected=hashlib.sha256((ROOT/"web/i18n.js").read_bytes()).digest()
    # Only valid HTTP200/javascript with a different content SHA may be polled.
    for attempt in range(12):
        if hashlib.sha256(read_i18n(version)).digest()==expected:
            print("REVIEWED_THERARBG_LANGUAGE_ASSET_PASS: "+
                  hashlib.sha256((ROOT/"web/i18n.js").read_bytes()).hexdigest()[:16])
            return
        stable(deployment,split)
        if attempt==11:
            raise Stop("TRANSLATION_ASSET_SHA_MISMATCH")
        time.sleep(8)


# Cloudflare may briefly serve previous unversioned HTML after full switch.
# Only verified HTTP-200 reviewed-source mismatch may wait; never retry 429/504.
HTML_200_MISMATCH = "HTML_NOT_REVIEWED_SOURCE_OR_KNOWN_CLOUDFLARE_BEACON"


def verify_public_with_html_settle(deployment, full):
    for attempt in range(6):
        try:
            verify_all_assets(None, deployment, full)
            return
        except Stop as e:
            if str(e) != HTML_200_MISMATCH or attempt == 5:
                raise
            stable(deployment,full)
            print("THERARBG_HTML_PROPAGATION_WAIT:" + str(attempt+1) + "/5")
            time.sleep(8)


def rollback_if_safe(candidate):
    if not candidate or not UUID.fullmatch(candidate):
        return
    try:
        previous,shares=snapshot()
    except (Stop,ValueError,KeyError,TypeError):
        print("ROLLBACK_MANUAL_AUDIT_REQUIRED: unknown deployment metadata")
        return
    staged={ACTIVE:100,candidate:0}
    canary={ACTIVE:95,candidate:5}
    full={ACTIVE:0,candidate:100}
    if shares in (INITIAL,staged):
        print("BASELINE_STILL_SERVING: 60112@100")
        return
    if shares not in (canary,full):
        print("ROLLBACK_REFUSED_CONCURRENT_OR_UNKNOWN_SPLIT")
        return
    try:
        bindings(ACTIVE);bindings(candidate)
        stable(previous,shares)
        ok=_wrangler_deploy(
            [ACTIVE+"@100%",candidate+"@0%"],
            "Magnetra TheRarBg fail-closed rollback to proven 6dad at 100 percent"
        )
        wait_for(previous,shares,staged,ok)
        print("GUARDED_ROLLBACK_PASS: 6dad100 / candidate0")
    except (Stop,ValueError,KeyError,TypeError,OSError):
        print("ROLLBACK_UNVERIFIED: manual audit required")


def run():
    config=guard_source()
    before=current(INITIAL)
    bindings(ACTIVE);bindings(ROLLBACK)
    old_js_guard()
    stable(before,INITIAL)
    print("THERARBG_BASELINE_PASS: 60112@100 / 6dad@0")
    candidate=None
    try:
        candidate=upload_version(config)
        bindings(candidate)
        stable(before,INITIAL)

        slot={ACTIVE:100,candidate:0}
        print("THERARBG_STAGING_ZERO_PERCENT")
        ok=_wrangler_deploy([ACTIVE+"@100%",candidate+"@0%"],"Magnetra TheRarBg source-owned magnet indexers: stage immutable 0%")
        staged=wait_for(before,INITIAL,slot,ok)
        verify_all_assets(candidate,staged,slot)
        catalog_guard(candidate)
        stable(staged,slot)
        print("THERARBG_STAGE_PASS: assets and 46 original adapters")

        canary={ACTIVE:95,candidate:5}
        ok=_wrangler_deploy([ACTIVE+"@95%",candidate+"@5%"],"Magnetra TheRarBg source-owned magnet indexers: canary 5%")
        canary_dep=wait_for(staged,slot,canary,ok)
        verify_all_assets(candidate,canary_dep,canary)
        stable(canary_dep,canary)
        print("THERARBG_CANARY_5_PASS")

        full={ACTIVE:0,candidate:100}
        ok=_wrangler_deploy([ACTIVE+"@0%",candidate+"@100%"],"Magnetra TheRarBg source-owned magnet indexers: 100% with 60112 rollback")
        full_dep=wait_for(canary_dep,canary,full,ok)
        verify_public_with_html_settle(full_dep,full)
        catalog_guard(None)
        bindings(ACTIVE);bindings(candidate)
        stable(full_dep,full)
        print("THERARBG_PRODUCTION_100_PASS: "+candidate+"@100 / 6dad@0")
        return 0
    except (Stop,ValueError,KeyError,TypeError,OSError):
        print("THERARBG_ROLLOUT_STOP: bounded review or immutable deployment check failed")
        rollback_if_safe(candidate)
        return 1


def main():
    if os.environ.get("MAGNETRA_THERARBG_RELEASE_ACTION") != ACTION:
        print("STOP: unique owner release marker not present, zero Cloudflare calls")
        return 2
    try:
        return run()
    except (Stop,ValueError,KeyError,TypeError,OSError):
        print("THERARBG_PREFLIGHT_STOP: unchanged production state not verified")
        return 1


if __name__=="__main__":
    sys.exit(main())
