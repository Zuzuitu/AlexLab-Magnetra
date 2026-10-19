#!/usr/bin/env python3
"""Read-only, exact Cloudflare version gate for the Oct 19 Magnetra Resolve fix.

Checks uploaded version bindings and existing production deployment. Never
prints API responses, original requests, secret values or provider data.
This workflow does not create a 0% slot or deploy any code.
"""
from __future__ import annotations

import sys

from deploy_magnetra_zero_percent import _current_deployment, _get_api, _shares
from inspect_cloudflare_version import VERSION as ACTIVE, ROLLBACK, EXPECTED

STAGED = "540b3417-f845-47e8-96bd-856ccc9f1350"
STAGED_COMMIT = "c6867647c10bba33db0361178f3380a7ffa48385"


def binding_pairs(payload: dict) -> set[tuple[str, str]]:
    result = payload.get("result") if isinstance(payload, dict) else None
    resources = result.get("resources") if isinstance(result, dict) else None
    raw = resources.get("bindings") if isinstance(resources, dict) else None
    if isinstance(raw, list):
        return {(b.get("name"), b.get("type")) for b in raw
                if isinstance(b, dict)
                and isinstance(b.get("name"), str)
                and isinstance(b.get("type"), str)}
    if isinstance(raw, dict):
        return {(name, info.get("type")) for name, info in raw.items()
                if isinstance(name, str) and isinstance(info, dict)
                and isinstance(info.get("type"), str)}
    return set()


def audit(payload: dict, deployment_payload: dict) -> tuple[list[str], bool]:
    lines = ["STAGED_VERSION_ID: " + STAGED,
             "STAGED_SOURCE_COMMIT: " + STAGED_COMMIT]
    if not isinstance(payload, dict) or payload.get("success") is not True:
        return lines + ["STAGED_METADATA: UNVERIFIED"], False
    version = payload.get("result")
    if not isinstance(version, dict) or version.get("id") != STAGED:
        return lines + ["STAGED_VERSION_MATCH: FAIL"], False
    lines.append("STAGED_VERSION_MATCH: PASS")
    names = binding_pairs(payload)
    bindings_ok = True
    for name, allowed in EXPECTED.items():
        valid = any((name, kind) in names for kind in allowed)
        lines.append(name + ": " + ("PASS" if valid else "UNVERIFIED"))
        bindings_ok = bindings_ok and valid

    try:
        record = _current_deployment(deployment_payload)
        shares = _shares(record)
    except (ValueError, TypeError, KeyError):
        return lines + ["DEPLOYMENT_METADATA: UNVERIFIED"], False

    previous = [ident for ident in shares if ident.startswith(ROLLBACK)]
    expected = shares == {ACTIVE: 100} or (
        len(previous) == 1 and
        shares == {ACTIVE: 100, previous[0]: 0}
    )
    staged_absent = STAGED not in shares
    lines.append("CURRENT_PRODUCTION_249D_100_PERCENT: " +
                 ("PASS" if expected else "UNVERIFIED"))
    lines.append("NEW_540B_VERSION_NOT_DEPLOYED: " +
                 ("PASS" if staged_absent else "FAIL"))
    if not isinstance(record.get("id"), str) or not record["id"]:
        lines.append("DEPLOYMENT_ID: UNVERIFIED")
        return lines, False
    lines.append("DEPLOYMENT_ID: PASS")
    return lines, bindings_ok and expected and staged_absent


def main() -> int:
    try:
        payload = _get_api("/versions/" + STAGED)
        deployments = _get_api("/deployments")
        lines, ok = audit(payload, deployments)
    except (ValueError, TypeError, KeyError):
        print("STAGE_GATE: STOP_UNVERIFIED (sanitized Cloudflare metadata error)")
        return 2
    print("\n".join(lines))
    print("STAGE_GATE: " + ("PASS" if ok else "STOP_UNVERIFIED"))
    print("READ_ONLY: no deployment, version upload, secrets mutation, source requests or Flud action.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
