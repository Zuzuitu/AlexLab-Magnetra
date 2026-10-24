#!/usr/bin/env python3
"""Owner-approved immutable TheRarBg iPhone diagnostic VERSION upload only.

This deliberately does NOT call Wrangler "versions deploy", change a traffic
percentage, send a magnet, contact a torrent source, or modify bindings.
A new version can be used only after a separate guarded owner-approved 0% slot.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from deploy_magnetra_zero_percent import _get_api, _current_deployment, _shares
from deploy_magnetra_auto_pause_once import Stop, ROOT, uploaded_version_id
from inspect_magnetra_fix_stage import binding_pairs
from inspect_companion_binding_readonly import (
    account_list, verify_account_scripts, validated_source,
    Stop as CompanionStop,
)

ACTIVE = "36019925-2308-4f99-8223-13854012d372"
PREVIOUS_ZERO = "c201cbf9-2080-4a5b-9e40-723a8714d94c"
EXPECTED_SPLIT = {ACTIVE: 100, PREVIOUS_ZERO: 0}
ACTION = "CONFIRM_IMMUTABLE_ZERO_TRAFFIC_UPLOAD_20261024"
EXPECTED_BINDINGS = {
    "ASSETS": {"assets"},
    "BTDIGG_GATEWAY_TOKEN": {"secret_text", "secret_key"},
    "MAGNETRA_GATEWAY_TOKEN": {"secret_text", "secret_key"},
    "FLUD_RELAY": {"service"},
}
STAGE_CONFIG = ROOT / "worker/.wrangler-therarbag-iphone-stage-only.jsonc"


def validate_source():
    config = validated_source()
    pwa = (ROOT / "web/app.js").read_text(encoding="utf8")
    worker = (ROOT / "worker/src/index.mjs").read_text(encoding="utf8")
    adapter = (ROOT / "worker/src/legacy-adapters.mjs").read_text(encoding="utf8")
    if (
        "const theRarBgDiagnosticMode=" not in pwa
        or '"x-magnetra-resolve-diagnostic"' not in pwa
        or "THERARBAG_IPHONE_DIAG_V1" not in worker
        or "detailFingerprint:await detailFingerprint(details)" not in worker
        or 'request.headers.get("x-magnetra-resolve-diagnostic")' not in worker
        or 'diagnostic.htmlStage="HTML_NO_BTIH"' not in adapter
        or 'diagnostic.jsonStage="JSON_VALID"' not in adapter
    ):
        raise Stop("REVIEWED_OPTIN_SOURCE_MISMATCH")
    return config


def verify_binding_payload(version, payload):
    if (
        not isinstance(payload, dict)
        or payload.get("success") is not True
        or not isinstance(payload.get("result"), dict)
        or payload["result"].get("id") != version
    ):
        raise Stop("IMMUTABLE_VERSION_UNVERIFIED")
    pairs = binding_pairs(payload)
    for name, allowed in EXPECTED_BINDINGS.items():
        if not any((name, kind) in pairs for kind in allowed):
            raise Stop("REQUIRED_BINDING_UNVERIFIED_" + name)


def read_split():
    dep = _current_deployment(_get_api("/deployments"))
    split = _shares(dep)
    if split != EXPECTED_SPLIT or not isinstance(dep.get("id"), str) or not dep["id"]:
        raise Stop("CLOUDFLARE_BASELINE_CHANGED_NO_UPLOAD")
    return dep


def guard_baseline():
    verify_account_scripts(account_list())
    initial = read_split()
    for version in EXPECTED_SPLIT:
        verify_binding_payload(version, _get_api("/versions/" + version))
    second = read_split()
    if second["id"] != initial["id"]:
        raise Stop("CONCURRENT_DEPLOYMENT_REFUSED")
    print("ACCOUNT_ORIGIN_AND_FLUD_SERVICE: PASS", flush=True)
    print("EXACT_ACTIVE_100_PREVIOUS_ZERO_0: PASS", flush=True)
    print("FOUR_BINDINGS_BOTH_EXISTING_VERSIONS: PASS", flush=True)
    return initial


def upload_only(config):
    if STAGE_CONFIG.exists():
        raise Stop("TEMPORARY_STAGE_CONFIG_ALREADY_EXISTS")
    staged = dict(config)
    staged["secrets"] = {
        "required": ["BTDIGG_GATEWAY_TOKEN", "MAGNETRA_GATEWAY_TOKEN"]
    }
    STAGE_CONFIG.write_text(json.dumps(staged, indent=2) + "\n", encoding="utf8")
    os.chmod(STAGE_CONFIG, 0o600)
    try:
        try:
            process = subprocess.run(
                [
                    "npx", "--yes", "wrangler@4.102.0", "versions", "upload",
                    "--config", str(STAGE_CONFIG), "--keep-vars",
                    "--message", "Magnetra iPhone TheRarBg opt-in trace, immutable upload only, no traffic",
                ],
                cwd=ROOT, capture_output=True, text=True, timeout=220, check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            raise Stop("CANDIDATE_UPLOAD_UNVERIFIED") from None
        if process.returncode != 0:
            raise Stop("CANDIDATE_UPLOAD_FAILED") from None
        version = uploaded_version_id(process.stdout + "\n" + process.stderr)
        if version in EXPECTED_SPLIT:
            raise Stop("NEW_VERSION_COLLIDES_WITH_EXISTING")
        print("NEW_IMMUTABLE_DIAGNOSTIC_VERSION: " + version, flush=True)
        return version
    finally:
        STAGE_CONFIG.unlink(missing_ok=True)


def run():
    config = validate_source()
    before = guard_baseline()
    if read_split()["id"] != before["id"]:
        raise Stop("DEPLOYMENT_CHANGED_BEFORE_UPLOAD")
    # This is the ONLY Cloudflare write: create a version, not a deployment.
    candidate = upload_only(config)
    verify_binding_payload(candidate, _get_api("/versions/" + candidate))
    after = read_split()
    if after["id"] != before["id"]:
        raise Stop("POST_UPLOAD_PRODUCTION_DEPLOYMENT_CHANGED")
    print("NEW_VERSION_FOUR_BINDINGS: PASS", flush=True)
    print("NO_DEPLOYMENT_PERCENTAGES_CHANGED: PASS", flush=True)
    print("IPHONE_PUBLIC_TEST_NOT_YET_ENABLED: needs separately approved zero-slot", flush=True)
    return 0


def main():
    if os.environ.get("MAGNETRA_THERARBAG_IPHONE_STAGE_ACTION") != ACTION:
        print("OWNER_STAGE_ONLY_APPROVAL_NOT_PRESENT")
        return 2
    try:
        return run()
    except (Stop, CompanionStop, ValueError, TypeError, KeyError, OSError):
        print("STAGE_ONLY_STOP_UNVERIFIED: no deliberate traffic change attempted")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
