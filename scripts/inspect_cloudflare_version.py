#!/usr/bin/env python3
"""Read-only Cloudflare version audit. Never print API payloads or secret values."""
import json
import re
import sys
from pathlib import Path

VERSION = "249d6767-f4dc-4f4d-bbf7-f57bea2e5554"
ROLLBACK = "a9df4429"
EXPECTED = {"BTDIGG_GATEWAY_TOKEN": {"secret_text", "secret_key"},
            "MAGNETRA_GATEWAY_TOKEN": {"secret_text", "secret_key"},
            "ASSETS": {"assets"}}
UUID = re.compile(r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$")


def audit(version, deployments):
    output = ["CANDIDATE_VERSION: " + VERSION]
    if not isinstance(version, dict) or version.get("success") is not True:
        return output + ["VERSION_RESPONSE: UNVERIFIED"], False
    item = version.get("result")
    if not isinstance(item, dict) or item.get("id") != VERSION:
        return output + ["VERSION_ID_MATCH: FAIL"], False
    output.append("VERSION_ID_MATCH: PASS")
    metadata = item.get("metadata") or {}
    if isinstance(metadata, dict):
        preview = metadata.get("hasPreview")
        output.append("CANDIDATE_HAS_PREVIEW: " + ("YES" if preview is True else "NO" if preview is False else "UNVERIFIED"))

    resources = item.get("resources")
    bindings = resources.get("bindings") if isinstance(resources, dict) else None
    if isinstance(bindings, list):
        pairs = {(b.get("name"), b.get("type")) for b in bindings
                 if isinstance(b, dict) and isinstance(b.get("name"), str)
                 and isinstance(b.get("type"), str)}
    elif isinstance(bindings, dict):
        pairs = {(name, spec.get("type")) for name, spec in bindings.items()
                 if isinstance(spec, dict)}
    else:
        pairs = set()
    all_bindings_ok = True
    for name, types in EXPECTED.items():
        ok = any((name, kind) in pairs for kind in types)
        output.append(name + ": " + ("PASS" if ok else "UNVERIFIED"))
        all_bindings_ok &= ok

    if not isinstance(deployments, dict) or deployments.get("success") is not True:
        return output + ["DEPLOYMENTS_RESPONSE: UNVERIFIED"], False
    result = deployments.get("result")
    records = result.get("deployments") if isinstance(result, dict) else None
    if not isinstance(records, list) or not records:
        return output + ["DEPLOYMENTS_RESPONSE: UNVERIFIED"], False
    records = [d for d in records if isinstance(d, dict) and isinstance(d.get("created_on"), str)]
    if not records:
        return output + ["DEPLOYMENT_TIMESTAMP: UNVERIFIED"], False
    latest = max(records, key=lambda d: d["created_on"])
    shares = latest.get("versions")
    if not isinstance(shares, list) or not shares:
        return output + ["TRAFFIC_SHARES: UNVERIFIED"], False
    # Cloudflare can return the exact 100% old + 0% candidate slot.
    # A 0% entry is deliberately present for version overrides, not live traffic.
    # Accept ONLY old-only 100% or the known two-version 100/0 slot.
    if len(shares) not in (1, 2) or any(not isinstance(d, dict) for d in shares):
        return output + ["TRAFFIC_SHARES: UNVERIFIED"], False
    compact = [(d.get("version_id"), d.get("percentage")) for d in shares]
    if (not all(isinstance(v, str) and UUID.fullmatch(v)
                and type(p) in (float, int) and 0 <= p <= 100 for v, p in compact)
            or len({v for v, _ in compact}) != len(compact)):
        return output + ["TRAFFIC_SHARES: UNVERIFIED"], False
    if abs(sum(p for _, p in compact) - 100) > 0.001:
        return output + ["TRAFFIC_TOTAL: UNVERIFIED"], False
    shares_by_id = dict(compact)
    old_ids = [v for v in shares_by_id if v.startswith(ROLLBACK)]
    rollback_id = old_ids[0] if len(old_ids) == 1 else None
    old_only = rollback_id is not None and shares_by_id == {rollback_id: 100}
    zero_slot = (rollback_id is not None and
                 shares_by_id == {rollback_id: 100, VERSION: 0})
    candidate_no_traffic = shares_by_id.get(VERSION, 0) == 0
    output.append("ROLLBACK_ACTIVE_100_PERCENT: " +
                  ("PASS" if old_only or zero_slot else "NOT_CONFIRMED"))
    output.append("CANDIDATE_NO_TRAFFIC: " +
                  ("PASS" if candidate_no_traffic else "FAIL"))
    output.append("ZERO_PERCENT_SLOT: " + ("PRESENT" if zero_slot else "ABSENT"))
    return output, all_bindings_ok and (old_only or zero_slot)

def main():
    if len(sys.argv) != 3:
        print("Usage: inspect_cloudflare_version.py <version.json> <deployments.json>")
        return 2
    try:
        v = json.loads(Path(sys.argv[1]).read_text())
        d = json.loads(Path(sys.argv[2]).read_text())
        lines, passed = audit(v, d)
    except (ValueError, OSError):
        print("METADATA_PARSE: UNVERIFIED (raw response withheld)")
        return 2
    print("\n".join(lines))
    print("STAGE_METADATA_GATE: " + ("PASS" if passed else "STOP_UNVERIFIED"))
    print("READ_ONLY: no deployment, no secrets changed; authenticated E2E not yet tested.")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
