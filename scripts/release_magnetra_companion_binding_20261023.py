#!/usr/bin/env python3
"""Owner-authorized immutable Magnetra Flud relay Service Binding release.

Single-purpose and fail-closed: verified current 100/0 baseline, upload new
version without traffic, stage exact 0%, verify internal binding via a fake
token (401), verify unchanged public assets/catalog, promote 5%, then 100%.
No real credentials, torrent downloads, user magnet, DNS or Shield changes.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

from deploy_magnetra_auto_pause_once import (
    Stop, ROOT, UUID, NoRedirect, bindings, current, stable, snapshot,
    wait_for, uploaded_version_id, _wrangler_deploy,
)
from release_magnetra_therarbag_cache_link_20261022 import (
    verify_all_assets, verify_public_with_html_settle,
)
from release_magnetra_hide_anime_mikan import catalog_guard
from inspect_companion_binding_readonly import (
    validated_source, account_list, verify_account_scripts, Stop as InspectorStop,
)
from deploy_magnetra_zero_percent import _get_api
from inspect_magnetra_fix_stage import binding_pairs

ACTIVE = "a088fa41-233d-48d3-bd4c-52be6194fda8"
ROLLBACK = "056d8394-79b0-459a-b93e-b5f5a8a7295d"
INITIAL = {ACTIVE: 100, ROLLBACK: 0}
APPROVAL = "CONFIRM_COMPANION_BINDING_RELEASE_20261023"
ORIGIN = "https://index.alexlab.media"
SECRETS = ("BTDIGG_GATEWAY_TOKEN", "MAGNETRA_GATEWAY_TOKEN")
EXPECTED = {
    "ASSETS": {"assets"},
    "BTDIGG_GATEWAY_TOKEN": {"secret_text", "secret_key"},
    "MAGNETRA_GATEWAY_TOKEN": {"secret_text", "secret_key"},
    "FLUD_RELAY": {"service"},
}
TEST_DEVICE = "MAGNETRA_DIAG_NOTREAL_1234"
TEST_TOKEN = "TEST_TOKEN_NOT_REAL_12345678901234567890"


def reviewed_config():
    config = validated_source()
    if config.get("services") != [
        {"binding": "FLUD_RELAY", "service": "flud-remote-relay"}
    ]:
        raise Stop("SERVICE_BINDING_TARGET_MISMATCH")
    code = (ROOT / "worker/src/index.mjs").read_text(encoding="utf-8")
    if ('env?.FLUD_RELAY.fetch' in code
        or not (
            'await env.FLUD_RELAY.fetch(new Request(url,outboundOptions))' in code
            or (
                'const outbound=new Request(url,outboundOptions)' in code
                and 'upstream=await env.FLUD_RELAY.fetch(outbound)' in code
                and 'x-alexlab-companion-probe' in code
            )
        )
        or 'return companion(request,"status",env)' not in code
        or 'return companion(request,"magnet",env)' not in code):
        raise Stop("COMPANION_RELAY_SOURCE_NOT_REVIEWED")
    return config


def verify_version(version_id, require_service=False):
    if not UUID.fullmatch(version_id):
        raise Stop("VERSION_UUID_REJECTED")
    bindings(version_id)  # Preserve all three existing binding names/types.
    response = _get_api("/versions/" + version_id)
    if (not isinstance(response, dict) or response.get("success") is not True
        or (response.get("result") or {}).get("id") != version_id):
        raise Stop("VERSION_DETAILS_UNVERIFIED")
    pairs = binding_pairs(response)
    expected = EXPECTED if require_service else {
        name: kinds for name, kinds in EXPECTED.items() if name != "FLUD_RELAY"
    }
    for name, types in expected.items():
        if not any((name, kind) in pairs for kind in types):
            raise Stop("REQUIRED_BINDING_NOT_PRESENT_" + name)
    if require_service:
        bindings_info = (response.get("result") or {}).get("resources", {}).get("bindings", [])
        service_records = (binding for binding in bindings_info if isinstance(binding, dict)
                           and binding.get("name") == "FLUD_RELAY") if isinstance(bindings_info, list) else []
        # Cross-account authorization and runtime service resolution are separately
        # tested by the real staged 401 probe; never infer them from metadata alone.
        if not any(True for _ in service_records) and not isinstance(bindings_info, dict):
            raise Stop("SERVICE_BINDING_METADATA_MISSING")
    print("REQUIRED_VERSION_BINDINGS_PASS:" + version_id[:8] + (":4" if require_service else ":3"))


def upload(config):
    cfg = dict(config)
    cfg["secrets"] = {"required": list(SECRETS)}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonc", prefix="magnetra-companion-",
                                 dir=ROOT / "worker", delete=False, encoding="utf-8") as f:
        path = Path(f.name)
        f.write(json.dumps(cfg, indent=2) + "\n")
    try:
        os.chmod(path, 0o600)
        command = [
            "npx", "--yes", "wrangler@4.102.0", "versions", "upload",
            "--config", str(path), "--keep-vars",
            "--message", "Magnetra Flud Companion internal relay binding only; no frontend changes",
        ]
        try:
            process = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                                     timeout=220, check=False)
        except (OSError, subprocess.TimeoutExpired):
            raise Stop("IMMUTABLE_VERSION_UPLOAD_UNVERIFIED") from None
        if process.returncode:
            raise Stop("IMMUTABLE_VERSION_UPLOAD_FAILED")
        ident = uploaded_version_id(process.stdout + "\n" + process.stderr)
        if ident in INITIAL:
            raise Stop("IMMUTABLE_VERSION_COLLISION")
        print("NEW_COMPANION_CANDIDATE:" + ident)
        return ident
    finally:
        path.unlink(missing_ok=True)


def fake_status_probe(version):
    """Real staged Worker to relay, but with impossible fake credentials."""
    if not UUID.fullmatch(version):
        raise Stop("UNREVIEWED_VERSION_OVERRIDE")
    payload = json.dumps({"deviceId": TEST_DEVICE, "token": TEST_TOKEN}).encode()
    headers = {
        "Origin": ORIGIN, "Content-Type": "application/json",
        "Accept": "application/json", "Accept-Encoding": "identity",
        "Cache-Control": "no-store",
        "Cloudflare-Workers-Version-Overrides": 'alexlab-magnetra="' + version + '"',
    }
    req = urllib.request.Request(ORIGIN + "/api/companion/status",
                                 data=payload, headers=headers, method="POST")
    opener = urllib.request.build_opener(NoRedirect())
    try:
        with opener.open(req, timeout=24) as resp:
            status = resp.status
            raw = resp.read(1025)
    except urllib.error.HTTPError as exc:
        status = exc.code
        raw = exc.read(1025)
    except (urllib.error.URLError, OSError, TimeoutError):
        raise Stop("STAGED_INTERNAL_STATUS_TRANSPORT_UNVERIFIED") from None
    try:
        result = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        raise Stop("STAGED_INTERNAL_STATUS_RESPONSE_NOT_JSON") from None
    if status != 401 or not isinstance(result, dict) or result.get("error") != "Unauthorized":
        raise Stop("STAGED_INTERNAL_STATUS_NOT_AUTHENTICATED_401")
    print("STAGED_INTERNAL_RELAY_REACHABLE:PASS_401_FAKE_TOKEN")


def restore_if_safe(candidate):
    if not candidate or not UUID.fullmatch(candidate):
        return
    try:
        dep, shares = snapshot()
        target = {ACTIVE: 100, candidate: 0}
        canary = {ACTIVE: 95, candidate: 5}
        full = {ACTIVE: 0, candidate: 100}
        if shares in (INITIAL, target):
            print("ROLLBACK_UNNECESSARY_OLD_100")
            return
        if shares not in (canary, full):
            print("ROLLBACK_STOP_CONCURRENT_OR_UNKNOWN_DEPLOYMENT")
            return
        verify_version(ACTIVE)
        verify_version(candidate, True)
        stable(dep, shares)
        ok = _wrangler_deploy(
            [ACTIVE + "@100%", candidate + "@0%"],
            "Companion Service Binding safe rollback: prior production 100%",
        )
        if not ok:
            print("ROLLBACK_WRITE_FAILED_MANUAL_AUDIT_REQUIRED")
            return
        wait_for(dep, shares, target, ok)
        print("ROLLBACK_OLD_100_NEW_0_PASS")
    except (Stop, InspectorStop, ValueError, KeyError, TypeError, OSError):
        print("ROLLBACK_UNVERIFIED_MANUAL_AUDIT_REQUIRED")


def run():
    config = reviewed_config()
    verify_account_scripts(account_list())
    before = current(INITIAL)
    verify_version(ACTIVE)
    verify_version(ROLLBACK)
    stable(before, INITIAL)
    print("READONLY_PREFLIGHT_SAME_ACCOUNT_AND_OLD_100_PASS")
    candidate = None
    try:
        candidate = upload(config)
        verify_version(candidate, True)
        stable(before, INITIAL)

        slot = {ACTIVE: 100, candidate: 0}
        written = _wrangler_deploy(
            [ACTIVE + "@100%", candidate + "@0%"],
            "Magnetra Flud Companion internal binding stage: zero traffic",
        )
        staged = wait_for(before, INITIAL, slot, written)
        verify_version(candidate, True)
        verify_all_assets(candidate, staged, slot)
        catalog_guard(candidate)
        fake_status_probe(candidate)
        stable(staged, slot)
        print("COMPANION_ZERO_PERCENT_PASS")

        canary = {ACTIVE: 95, candidate: 5}
        written = _wrangler_deploy(
            [ACTIVE + "@95%", candidate + "@5%"],
            "Magnetra Flud Companion binding canary: 5%",
        )
        staged5 = wait_for(staged, slot, canary, written)
        verify_all_assets(candidate, staged5, canary)
        catalog_guard(candidate)
        fake_status_probe(candidate)
        stable(staged5, canary)
        print("COMPANION_CANARY_5_PASS")

        full = {ACTIVE: 0, candidate: 100}
        written = _wrangler_deploy(
            [ACTIVE + "@0%", candidate + "@100%"],
            "Magnetra Flud Companion binding 100%, prior immutable version rollback",
        )
        deployed = wait_for(staged5, canary, full, written)
        verify_public_with_html_settle(deployed, full)
        catalog_guard(None)
        fake_status_probe(candidate)
        verify_version(candidate, True)
        stable(deployed, full)
        print("COMPANION_PRODUCTION_100_PASS:" + candidate)
        print("IPHONE_REAL_PAIRING_AND_PHYSICAL_ACK_STILL_OWNER_ACCEPTANCE")
        return 0
    except (Stop, InspectorStop, ValueError, KeyError, TypeError, OSError):
        print("COMPANION_RELEASE_ABORTED_FAIL_CLOSED")
        restore_if_safe(candidate)
        return 1


def main():
    if os.environ.get("MAGNETRA_COMPANION_RELEASE_ACTION") != APPROVAL:
        print("STOP_OWNER_RELEASE_AUTHORIZATION_REQUIRED")
        return 2
    try:
        return run()
    except (Stop, InspectorStop, ValueError, KeyError, TypeError, OSError):
        print("COMPANION_PREFLIGHT_STOP_NO_WRITES_VERIFIED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
