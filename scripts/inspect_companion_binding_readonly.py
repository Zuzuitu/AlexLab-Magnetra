#!/usr/bin/env python3
"""Fail-closed, GET-only Cloudflare account/production-binding audit for Companion.

Does not print secrets, raw API bodies or user pairing data; never deploys.
Uses the existing account-scoped GitHub Actions Cloudflare credentials.
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

from deploy_magnetra_zero_percent import _get_api, _current_deployment, _shares
from inspect_magnetra_fix_stage import binding_pairs

ROOT = Path(__file__).resolve().parents[1]
ACCOUNT = re.compile(r"^[a-f0-9]{32}$", re.I)
WORKERS = frozenset({"alexlab-magnetra", "flud-remote-relay"})
EXPECTED = {
    "ASSETS": {"assets"},
    "BTDIGG_GATEWAY_TOKEN": {"secret_text", "secret_key"},
    "MAGNETRA_GATEWAY_TOKEN": {"secret_text", "secret_key"},
}


class Stop(Exception):
    pass


def validated_source():
    cfg = json.loads((ROOT / "worker/wrangler.jsonc").read_text("utf-8"))
    if (cfg.get("name") != "alexlab-magnetra"
        or cfg.get("main") != "src/index.mjs"
        or cfg.get("routes") != [{"pattern": "index.alexlab.media", "custom_domain": True}]
        or cfg.get("assets") != {"directory": "../web", "binding": "ASSETS"}
        or cfg.get("services") != [{"binding": "FLUD_RELAY", "service": "flud-remote-relay"}]):
        raise Stop("SOURCE_CONFIG_NOT_REVIEWED")
    return cfg


def verify_account_scripts(data):
    result = data.get("result") if isinstance(data, dict) and data.get("success") is True else None
    scripts = result if isinstance(result, list) else (
        result.get("scripts") if isinstance(result, dict) else None
    )
    if not isinstance(scripts, list):
        raise Stop("ACCOUNT_WORKER_LIST_UNVERIFIED")
    found = {x.get("id") or x.get("name") for x in scripts if isinstance(x, dict)}
    if not WORKERS.issubset(found):
        raise Stop("BOTH_WORKERS_SAME_ACCOUNT_NOT_PROVEN")


def audit_version_and_deployment(version_data, deployments):
    dep = _current_deployment(deployments)
    shares = _shares(dep)
    active = [version for version, percent in shares.items() if percent == 100]
    if len(active) != 1 or len(shares) > 2:
        raise Stop("SINGLE_ACTIVE_100_PERCENT_NOT_VERIFIED")
    version_id = active[0]
    if (not isinstance(version_data, dict)
        or version_data.get("success") is not True
        or (version_data.get("result") or {}).get("id") != version_id):
        raise Stop("ACTIVE_VERSION_METADATA_UNVERIFIED")
    pairs = binding_pairs(version_data)
    for name, allowed in EXPECTED.items():
        if not any((name, typ) in pairs for typ in allowed):
            raise Stop("ACTIVE_BINDING_UNVERIFIED_" + name)
    # Report only existence; do not claim an inactive draft is already installed.
    bound = ("FLUD_RELAY", "service") in pairs
    return version_id, dep.get("id"), bound


def account_list():
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
    account = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
    if not token or not ACCOUNT.fullmatch(account):
        raise Stop("CLOUDFLARE_READONLY_CREDENTIALS_MISSING")
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/accounts/{account}/workers/scripts?per_page=100",
        headers={"authorization": "Bearer " + token, "accept": "application/json"},
        method="GET"
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            raw = response.read(1_500_001)
        if not raw or len(raw) > 1_500_000:
            raise Stop("CLOUDFLARE_RESPONSE_SIZE_INVALID")
        return json.loads(raw)
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError):
        raise Stop("CLOUDFLARE_ACCOUNT_READ_FAILED") from None


def run():
    validated_source()
    verify_account_scripts(account_list())
    deployment = _get_api("/deployments")
    record = _current_deployment(deployment)
    shares = _shares(record)
    active = [v for v, percentage in shares.items() if percentage == 100]
    if len(active) != 1:
        raise Stop("LIVE_100_PERCENT_UNVERIFIED")
    version = _get_api("/versions/" + active[0])
    version_id, deployment_id, bound = audit_version_and_deployment(version, deployment)
    again = _current_deployment(_get_api("/deployments"))
    if again.get("id") != deployment_id or _shares(again) != shares:
        raise Stop("CONCURRENT_DEPLOYMENT_CHANGED_DURING_AUDIT")
    print("BOTH_WORKERS_SAME_ACCOUNT: PASS")
    print("SOURCE_SERVICE_BINDING_CONFIG: PASS")
    print("EXISTING_THREE_BINDINGS: PASS")
    print("ACTIVE_IMMUTABLE_VERSION: " + version_id)
    print("ACTIVE_FLUD_RELAY_BINDING: " + ("PRESENT" if bound else "NOT_YET_DEPLOYED"))
    print("DEPLOYMENT_SPLIT_SINGLE_100_PERCENT: PASS")
    print("READ_ONLY: no deployment, upload, secret readout, pairing requests or magnet sends")


def main():
    try:
        run()
        return 0
    except (Stop, ValueError, KeyError, TypeError, urllib.error.URLError, OSError):
        print("COMPANION_ACCOUNT_PREFLIGHT: STOP_UNVERIFIED (details withheld)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
