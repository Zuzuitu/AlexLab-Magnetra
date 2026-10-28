#!/usr/bin/env python3
"""Owner-approved, one-shot immutable Magnetra online release.

Fail-closed Cloudflare 100/0 -> 95/5 -> 0/100, with old version retained at
0% for rollback. Never changes Rock64, DNS, tunnels, secrets or source requests.
A single guarded rollback is attempted only for OUR two verified versions.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

from deploy_magnetra_auto_pause_once import (
    Stop, ROOT, UUID, bindings, snapshot, stable, wait_for,
    uploaded_version_id, _wrangler_deploy,
)
from deploy_magnetra_zero_percent import _get_api
from inspect_magnetra_fix_stage import binding_pairs
from release_magnetra_ro_it_12 import verify_all_assets, verify_public_with_html_settle
from release_magnetra_hide_anime_mikan import catalog_guard

REVIEWED = "0ae9df97f43bb158c22e0251fc6a3a0c8dedef61"
ACTION = "CONFIRM_MAGNETRA_20261028_ONLINE_OWNER"
EXPECTED_DIFF = {
    ".github/workflows/magnetra-release-20261028.yml",
    "scripts/release_magnetra_20261028.py",
    "scripts/test_release_magnetra_20261028.py",
    "web/app.js",
    "config/project-invariants.json",
    "scripts/check-project-invariants.py",
    "worker/test/indexer-curation.test.mjs",
}
REQUIRED_SECRETS = ("BTDIGG_GATEWAY_TOKEN", "MAGNETRA_GATEWAY_TOKEN")


def source_guard():
    # Only the reviewed #226 deployed baseline and exact 10-indexer curation changes are permitted.
    try:
        subprocess.run(["git", "merge-base", "--is-ancestor", REVIEWED, "HEAD"],
                       cwd=ROOT, check=True, capture_output=True, timeout=10)
        proc = subprocess.run(["git", "diff", "--name-only", REVIEWED, "HEAD"],
                              cwd=ROOT, check=True, capture_output=True,
                              text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        raise Stop("REVIEWED_SHA_ANCESTRY_UNVERIFIED") from None
    actual = set(proc.stdout.splitlines())
    if not actual or not actual.issubset(EXPECTED_DIFF):
        raise Stop("UNREVIEWED_MAIN_CHANGE_SINCE_226")

    config = json.loads((ROOT / "worker/wrangler.jsonc").read_text())
    if (config.get("name") != "alexlab-magnetra"
        or config.get("main") != "src/index.mjs"
        or config.get("routes") != [
            {"pattern": "index.alexlab.media", "custom_domain": True}
        ]
        or config.get("assets") != {"directory": "../web", "binding": "ASSETS"}
        or config.get("services") != [
            {"binding": "FLUD_RELAY", "service": "flud-remote-relay"}
        ]):
        raise Stop("CANONICAL_WORKER_BINDINGS_OR_ROUTE_CHANGED")
    app = (ROOT / "web/app.js").read_text()
    i18n = (ROOT / "web/i18n.js").read_text()
    fallback = (ROOT / "worker/src/release-fallback.mjs").read_text()
    curated = json.loads((ROOT / "config/project-invariants.json").read_text())["pwa_indexer_curation"]
    if (curated.get("visible_picker_count") != 10
        or curated.get("hidden_from_picker_and_pwa_search_count") != 36
        or curated.get("original_adapter_ids_retained") != 46
        or "audiobookbay" not in curated.get("hidden_ids", [])
        or '"subsplease","audiobookbay"]);' not in app
        or "RESULTS_PER_PAGE=50" not in app
        or "release naming" not in app
        or '"release naming"' not in i18n
        or "isLiteralReleaseMatch" not in fallback):
        raise Stop("OWNER_10_INDEXER_RELEASE_SOURCE_UNVERIFIED")
    print("REVIEWED_SOURCE_AND_ROUTE_PASS:#226,10-visible,AudioBookBay-hidden,50-per-page,Flud config")
    return config


def candidate_baseline(shares):
    """Accept only a single 100% active version and optionally one 0% old slot."""
    if not isinstance(shares, dict) or not 1 <= len(shares) <= 2:
        raise Stop("LIVE_SPLIT_NOT_100_PERCENT_BASELINE")
    active = [v for v, pct in shares.items() if pct == 100]
    if len(active) != 1 or any(pct not in (0, 100) for pct in shares.values()):
        raise Stop("LIVE_TRAFFIC_NOT_EXACT_100_0")
    if not UUID.fullmatch(active[0]):
        raise Stop("ACTIVE_VERSION_NOT_IMMUTABLE_UUID")
    return active[0]


def critical_binding_guard(version):
    bindings(version)
    result = _get_api("/versions/" + version)
    names = binding_pairs(result)
    if ("FLUD_RELAY", "service") not in names:
        raise Stop("FLUD_RELAY_SERVICE_BINDING_UNVERIFIED")
    print("FLUD_SERVICE_BINDING_PASS:" + version[:8])


def upload(config, old):
    data = dict(config)
    data["secrets"] = {"required": list(REQUIRED_SECRETS)}
    temporary = ROOT / "worker/.wrangler-owner-20261028.jsonc"
    if temporary.exists() or temporary.is_symlink():
        raise Stop("EPHEMERAL_CONFIG_ALREADY_PRESENT")
    temporary.write_text(json.dumps(data, indent=2) + "\n", encoding="utf8")
    os.chmod(temporary, 0o600)
    try:
        try:
            p = subprocess.run(
                ["npx", "--yes", "wrangler@4.102.0", "versions", "upload",
                 "--config", str(temporary), "--keep-vars",
                 "--message", "Magnetra #226 plus AudioBookBay removal: 10 active source choices"],
                cwd=ROOT, capture_output=True, text=True, timeout=220, check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            raise Stop("IMMUTABLE_STAGE_UPLOAD_UNVERIFIED") from None
        if p.returncode != 0:
            raise Stop("IMMUTABLE_STAGE_UPLOAD_FAILED")
        new = uploaded_version_id(p.stdout + "\n" + p.stderr)
        if new == old:
            raise Stop("NEW_VERSION_EQUALS_LIVE_OLD")
        print("IMMUTABLE_STAGE_UPLOADED:" + new)
        return new
    finally:
        temporary.unlink(missing_ok=True)


def rollback_if_safe(old, new):
    if not new or not UUID.fullmatch(new):
        return
    try:
        before, shares = snapshot()
        slot = {old: 100, new: 0}
        if shares == {old: 100} or shares == slot:
            print("ROLLBACK_NOT_NEEDED:old100")
            return
        if shares not in ({old: 95, new: 5}, {old: 0, new: 100}):
            print("ROLLBACK_REFUSED:concurrent-or-unknown-split")
            return
        critical_binding_guard(old)
        critical_binding_guard(new)
        stable(before, shares)
        wrote = _wrangler_deploy(
            [old + "@100%", new + "@0%"],
            "Magnetra #226 guarded restore of previous verified production",
        )
        wait_for(before, shares, slot, wrote)
        print("ROLLBACK_CONFIRMED:old100-new0")
    except (Stop, ValueError, KeyError, TypeError, OSError):
        print("ROLLBACK_NOT_VERIFIED:manual-inspection-required")


def publish():
    config = source_guard()
    before, existing = snapshot()
    old = candidate_baseline(existing)
    critical_binding_guard(old)
    catalog_guard(None)
    stable(before, existing)
    print("LIVE_PREFLIGHT_PASS:existing-100-percent;rollback-version="+old)
    new = None
    try:
        new = upload(config, old)
        critical_binding_guard(new)
        stable(before, existing)

        zero = {old: 100, new: 0}
        wrote = _wrangler_deploy(
            [old + "@100%", new + "@0%"],
            "Magnetra #226 immutable zero-percent validation",
        )
        zero_dep = wait_for(before, existing, zero, wrote)
        verify_all_assets(new, zero_dep, zero)
        catalog_guard(new)
        stable(zero_dep, zero)
        print("ZERO_PERCENT_STAGE_PASS")

        canary = {old: 95, new: 5}
        wrote = _wrangler_deploy(
            [old + "@95%", new + "@5%"],
            "Magnetra #226 guarded five-percent canary",
        )
        canary_dep = wait_for(zero_dep, zero, canary, wrote)
        verify_all_assets(new, canary_dep, canary)
        critical_binding_guard(new)
        stable(canary_dep, canary)
        print("FIVE_PERCENT_CANARY_PASS")

        full = {old: 0, new: 100}
        wrote = _wrangler_deploy(
            [old + "@0%", new + "@100%"],
            "Magnetra #226 online 100 percent, old retained at zero for rollback",
        )
        full_dep = wait_for(canary_dep, canary, full, wrote)
        verify_public_with_html_settle(full_dep, full)
        catalog_guard(None)
        critical_binding_guard(old)
        critical_binding_guard(new)
        stable(full_dep, full)
        print("MAGNETRA_10_INDEXERS_ONLINE_100_PASS:" + new)
        print("OWNER_IPHONE_SOURCE_TEST_PENDING:does-not-certify-BTDigg-availability")
        return 0
    except (Stop, ValueError, KeyError, TypeError, OSError):
        print("ROLLOUT_STOP:fail-closed-version-or-asset-gate")
        rollback_if_safe(old, new)
        return 1


def main():
    if os.environ.get("MAGNETRA_20261028_RELEASE_ACTION") != ACTION:
        print("NO_EXPLICIT_RELEASE_ACTION:zero-Cloudflare-calls")
        return 2
    try:
        return publish()
    except (Stop, ValueError, KeyError, TypeError, OSError):
        print("PREUPLOAD_STOP:no-production-traffic-changed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
