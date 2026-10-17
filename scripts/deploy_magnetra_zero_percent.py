#!/usr/bin/env python3
"""Exactly one Cloudflare Worker 100% old / 0% candidate deployment, with guarded rollback.

MUTATING script: run ONLY via the owner-confirmed manual GitHub Actions workflow.
Never prints Cloudflare API responses, CLI output, credentials or magnet URIs.
Zero is mandatory; there is NO fallback to 0.01%.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

from inspect_cloudflare_version import VERSION, ROLLBACK, UUID, audit

ACCOUNT = re.compile(r"^[a-fA-F0-9]{32}$")
WORKER = "alexlab-magnetra"


def _get_api(path: str) -> dict:
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
    account = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
    if not token or not ACCOUNT.fullmatch(account):
        raise ValueError("GitHub Cloudflare API credentials missing or malformed")
    root = f"https://api.cloudflare.com/client/v4/accounts/{account}/workers/scripts/{WORKER}"
    req = urllib.request.Request(
        root + path,
        headers={"Authorization": "Bearer " + token, "Accept": "application/json"},
        method="GET",
    )
    # Never print the exception: URL, headers or response body may be sensitive.
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            body = response.read(1_500_001)
        if len(body) > 1_500_000:
            raise ValueError("Cloudflare metadata size guard")
        return json.loads(body)
    except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError("Cloudflare read-only metadata GET failed") from None


def _current_deployment(deployments: dict) -> dict:
    if not isinstance(deployments, dict) or deployments.get("success") is not True:
        raise ValueError("Cloudflare deployment API did not confirm success")
    result = deployments.get("result")
    candidates = result.get("deployments") if isinstance(result, dict) else None
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("Cloudflare deployment list absent")
    candidates = [d for d in candidates if isinstance(d, dict)
                  and isinstance(d.get("created_on"), str)
                  and isinstance(d.get("versions"), list)]
    if not candidates:
        raise ValueError("Deployment list missing required metadata")
    return max(candidates, key=lambda d: d["created_on"])


def _shares(deployment: dict) -> dict[str, float]:
    versions = deployment.get("versions")
    if not isinstance(versions, list) or not 1 <= len(versions) <= 2:
        raise ValueError("Unexpected Cloudflare deployment version count")
    shares = {}
    for entry in versions:
        if not isinstance(entry, dict):
            raise ValueError("Unexpected Cloudflare deployment entry")
        version_id, percentage = entry.get("version_id"), entry.get("percentage")
        if (not isinstance(version_id, str) or not UUID.fullmatch(version_id)
                or type(percentage) not in (float, int) or not 0 <= percentage <= 100
                or version_id in shares):
            raise ValueError("Invalid Cloudflare deployment percentages")
        shares[version_id] = percentage
    if abs(sum(shares.values()) - 100) > 0.00001:
        raise ValueError("Deployment percentages do not total 100")
    return shares


def _wrangler_deploy(specs: list[str], message: str) -> bool:
    cmd = [
        "npx", "--yes", "wrangler@4.102.0", "versions", "deploy",
        *specs, "--config", "worker/wrangler.jsonc",
        "--name", WORKER, "--message", message, "--yes",
    ]
    # Deliberately withhold Wrangler stdout/stderr (diagnostic text may contain IDs).
    try:
        proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, timeout=180, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return False
    return proc.returncode == 0


def _is_old_only(shares: dict[str, float], old: str) -> bool:
    return shares == {old: 100}


def _is_target(shares: dict[str, float], old: str) -> bool:
    # Explicitly demand both versions in the active deployment, including 0%.
    return shares == {old: 100, VERSION: 0}


def _recover(old: str) -> bool:
    """Rollback is authorized only when current versions are known to be ours."""
    try:
        observed = _shares(_current_deployment(_get_api("/deployments")))
    except ValueError:
        print("CRITICAL: cannot inspect deployment for rollback; manual intervention.")
        return False
    if _is_old_only(observed, old):
        print("SAFE: old version is already the only 100% deployment.")
        return True
    if not set(observed).issubset({old, VERSION}):
        print("CRITICAL: concurrent/unknown deployment detected; refusing destructive rollback.")
        return False
    print("ATTEMPTING_ROLLBACK: restoring previous version to 100%.")
    _wrangler_deploy([old + "@100%"], "Magnetra safety rollback after zero-traffic preflight")
    try:
        status = _shares(_current_deployment(_get_api("/deployments")))
    except ValueError:
        print("CRITICAL: rollback state could not be read.")
        return False
    if _is_old_only(status, old):
        print("ROLLBACK_VERIFIED: previous version back to 100%.")
        return True
    print("CRITICAL: rollback not confirmed; inspect Cloudflare immediately.")
    return False


def execute() -> int:
    if os.environ.get("MAGNETRA_EXPLICIT_ZERO_PERCENT_APPROVAL") != "CONFIRM_OLD_100_NEW_0":
        print("STOP: manual zero-percent deployment approval absent.")
        return 2
    version = _get_api("/versions/" + VERSION)
    before_api = _get_api("/deployments")
    messages, safe = audit(version, before_api)
    if not safe:
        print("STOP: candidate secret/assets or old-only 100% preflight failed.")
        for line in messages:
            if line.endswith("UNVERIFIED") or line.endswith("FAIL") or line.endswith("NOT_CONFIRMED"):
                print(line)
        return 2
    before = _current_deployment(before_api)
    shares = _shares(before)
    if len(shares) != 1:
        print("STOP: unexpected preflight version count.")
        return 2
    old = next(iter(shares))
    if not old.startswith(ROLLBACK) or old == VERSION or not _is_old_only(shares, old):
        print("STOP: rollback version mismatch.")
        return 2
    print("PRECHECK_PASS: candidate + all three bindings, only rollback serves 100%.")
    print("ZERO_PERCENT_ONLY: never use a fallback of 0.01%.")
    # Second read narrows the time-of-check/time-of-use window.
    current = _current_deployment(_get_api("/deployments"))
    if current.get("id") != before.get("id") or not _is_old_only(_shares(current), old):
        print("STOP: deployment changed during preflight; no write attempted.")
        return 2

    print("APPLYING: older version 100%, exact candidate 0%, version-only deploy.")
    success = _wrangler_deploy([old + "@100%", VERSION + "@0%"],
                               "Magnetra authorized E2E slot: old 100%, candidate 0%")
    # Cloudflare may take seconds to propagate; API metadata checked after CLI.
    try:
        latest = _shares(_current_deployment(_get_api("/deployments")))
    except ValueError:
        print("CRITICAL: postflight deployment metadata unreadable.")
        _recover(old)
        return 1
    if success and _is_target(latest, old):
        print("POSTFLIGHT_PASS: exact old 100% and candidate 0% verified by API.")
        print("OVERRIDE_SLOT_READY: no provider E2E tests or production promotion performed.")
        return 0
    if not success:
        print("STOP: Wrangler rejected or failed the zero-percent deployment; raw output withheld.")
    else:
        print("STOP: postflight percentages differ from approved 100/0 configuration.")
    if _is_target(latest, old):
        print("STATE_SAFE_BUT_CLI_UNVERIFIED: exact 100/0; manual review before E2E.")
        return 1
    _recover(old)
    return 1


def main() -> int:
    try:
        return execute()
    except ValueError:
        print("STOP: fail-closed Cloudflare metadata/preflight error (response withheld).")
        return 2


if __name__ == "__main__":
    sys.exit(main())
