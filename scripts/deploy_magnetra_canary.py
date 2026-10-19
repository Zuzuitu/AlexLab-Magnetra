#!/usr/bin/env python3
"""Manual, fail-closed Cloudflare 5% canary and bounded 100%-old rollback.

Only approved version IDs, only the existing Worker; no source code upload,
secret mutation, tunnel, DNS, or Rock64 changes. Raw API/CLI output is withheld.
"""
from __future__ import annotations

import os
import sys

from deploy_magnetra_zero_percent import (
    _current_deployment, _get_api, _is_target, _is_old_only,
    _recover, _shares, _wrangler_deploy,
)
from inspect_cloudflare_version import VERSION, ROLLBACK, audit

START = "CONFIRM_CANARY_5_PERCENT"
ROLLBACK_ACTION = "CONFIRM_ROLLBACK_OLD_100"


def old_version(shares: dict[str, float]) -> str | None:
    old = [key for key in shares if key.startswith(ROLLBACK) and key != VERSION]
    return old[0] if len(old) == 1 else None


def is_canary(shares: dict[str, float], old: str) -> bool:
    return shares == {old: 95, VERSION: 5}


def unchanged(before: dict, expected: dict[str, float]) -> bool:
    """Refuse a write if another Cloudflare deployment landed during preflight."""
    now = _current_deployment(_get_api("/deployments"))
    return (isinstance(before.get("id"), str) and bool(before["id"])
            and now.get("id") == before["id"]
            and _shares(now) == expected)


def start_canary() -> int:
    version = _get_api("/versions/" + VERSION)
    deployments = _get_api("/deployments")
    messages, safe = audit(version, deployments)
    if not safe:
        print("STOP: candidate binding check or 100/0 safety preflight failed.")
        for line in messages:
            if line.endswith(("UNVERIFIED", "FAIL", "NOT_CONFIRMED")):
                print(line)
        return 2

    before = _current_deployment(deployments)
    shares = _shares(before)
    old = old_version(shares)
    if old is None or not _is_target(shares, old):
        print("STOP: expected exact 100% old / 0% candidate slot not present.")
        return 2
    if not unchanged(before, shares):
        print("STOP: deployment changed during preflight; no writes attempted.")
        return 2

    print("PREFLIGHT_PASS: exact candidate + bindings, old 100%, new 0%.")
    print("APPLYING: old 95%, exact candidate 5%.")
    cli_success = _wrangler_deploy(
        [old + "@95%", VERSION + "@5%"],
        "Magnetra approved bounded canary: old 95%, candidate 5%",
    )
    try:
        observed = _shares(_current_deployment(_get_api("/deployments")))
    except ValueError:
        print("CRITICAL: postflight unreadable; attempting guarded 100% old rollback.")
        _recover(old)
        return 1
    if cli_success and is_canary(observed, old):
        print("CANARY_POSTFLIGHT_PASS: old 95%, candidate 5% confirmed by API.")
        print("NOTE: deployment verified, not yet an end-to-end PWA user acceptance.")
        return 0
    print("STOP: CLI or Cloudflare postflight did not verify exact 95/5.")
    if observed == {old: 100, VERSION: 0} or _is_old_only(observed, old):
        print("NO_TRAFFIC_SHIFT_CONFIRMED: candidate remains at 0%.")
        return 1
    if set(observed).issubset({old, VERSION}):
        print("ATTEMPTING_GUARDED_ROLLBACK: restore old 100%.")
        _recover(old)
    else:
        print("CRITICAL: unknown concurrent deployment; refusing automatic rollback.")
    return 1


def rollback() -> int:
    before = _current_deployment(_get_api("/deployments"))
    shares = _shares(before)
    old = old_version(shares)
    if old is None:
        print("STOP: old version not uniquely identified.")
        return 2
    if _is_old_only(shares, old):
        print("ALREADY_SAFE: old version is 100%; no write.")
        return 0
    if not (is_canary(shares, old) or _is_target(shares, old)):
        print("STOP: rollback allowed only from known 95/5 or 100/0 slot.")
        return 2
    if not unchanged(before, shares):
        print("STOP: deployment changed; no write.")
        return 2
    print("APPLYING_ROLLBACK: restoring old version to 100%.")
    if _recover(old):
        print("ROLLBACK_POSTFLIGHT_PASS: old 100%, candidate 0% of live traffic.")
        return 0
    print("CRITICAL: rollback could not be confirmed; inspect Cloudflare.")
    return 1


def execute() -> int:
    choice = os.environ.get("MAGNETRA_CANARY_ACTION", "")
    if choice == START:
        return start_canary()
    if choice == ROLLBACK_ACTION:
        return rollback()
    print("STOP: explicit manual GitHub workflow action absent.")
    return 2


def main() -> int:
    try:
        return execute()
    except ValueError:
        print("STOP: sanitized Cloudflare metadata error; no verified operation.")
        return 2


if __name__ == "__main__":
    sys.exit(main())
