#!/usr/bin/env python3
"""Read-only, exact-version live canary E2E; no BTDigg probes or torrent downloads.

Explicit owner-triggered GitHub workflow only. Check Cloudflare metadata, force
old and candidate Worker versions via the documented version-override header,
then make one original-source HTML search and one deferred magnet resolution per
OxTorrent/Torrent9. Optional explicit EZTV positive probe, never BTDigg.
"""
from __future__ import annotations

import importlib.util
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

from deploy_magnetra_zero_percent import _get_api, _current_deployment, _shares
from inspect_cloudflare_version import VERSION, ROLLBACK, audit as binding_audit

SCRIPT = Path(__file__).with_name("check-magnetra-candidate-e2e.py")
_spec = importlib.util.spec_from_file_location("magnetra_staged_source_checks", SCRIPT)
if _spec is None or _spec.loader is None:
    raise RuntimeError("Missing original candidate E2E validators")
_source = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _source
_spec.loader.exec_module(_source)

RUN_HTML = "RUN_READONLY_HTML"
RUN_HTML_EZTV = "RUN_READONLY_HTML_EZTV"


class Stop(Exception):
    """Sanitized refusal; never print source bodies, magnets, credentials or URLs."""


def deployment():
    version = _get_api("/versions/" + VERSION)
    deployments = _get_api("/deployments")
    lines, _ = binding_audit(version, deployments)
    for binding in ("BTDIGG_GATEWAY_TOKEN", "MAGNETRA_GATEWAY_TOKEN", "ASSETS"):
        if binding + ": PASS" not in lines:
            raise Stop("CANDIDATE_BINDING_UNVERIFIED_" + binding)

    latest = _current_deployment(deployments)
    shares = _shares(latest)
    old_ids = [v for v in shares if v != VERSION and v.startswith(ROLLBACK)]
    if (len(shares) != 2 or len(old_ids) != 1 or
            shares.get(VERSION) != 5 or shares.get(old_ids[0]) != 95):
        raise Stop("EXPECTED_EXACT_95_5_CANARY_NOT_CONFIRMED")
    if not isinstance(latest.get("id"), str) or not latest["id"]:
        raise Stop("DEPLOYMENT_ID_UNVERIFIED")
    print("CANARY_DEPLOYMENT_GATE: PASS (old 95%, candidate 5%; 3 bindings PASS)")
    return old_ids[0], latest["id"]


def old_route_status(old_version):
    """Force the known 95%-old immutable version, not a random 95/5 request."""
    if not old_version.startswith(ROLLBACK) or old_version == VERSION:
        raise Stop("UNSAFE_OLD_VERSION_ID")
    req = urllib.request.Request(
        _source.BASE + "/api/recovery-plan",
        headers={
            "User-Agent": "AlexLab-Magnetra-CanaryGate/1.0",
            "Accept": "application/json",
            "Cache-Control": "no-store",
            "Cloudflare-Workers-Version-Overrides":
                _source.WORKER + '="' + old_version + '"',
        },
        method="GET",
    )
    try:
        with urllib.request.build_opener(_source.NoRedirect).open(req, timeout=18) as resp:
            return resp.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except (urllib.error.URLError, TimeoutError, OSError):
        raise Stop("OLD_VERSION_OVERRIDE_TRANSPORT_UNVERIFIED") from None


def exact_version_fingerprint(old_version):
    # Old and candidate requests are both explicitly version-selected.
    if old_route_status(old_version) != 404:
        raise Stop("OLD_VERSION_FINGERPRINT_NOT_404")
    status, candidate = _source.request_api("/api/recovery-plan", candidate=True)
    if (status != 200 or not isinstance(candidate, dict)
            or not isinstance(candidate.get("providers"), list)
            or len(candidate["providers"]) != 46):
        raise Stop("CANDIDATE_VERSION_FINGERPRINT_NOT_46")
    print("EXACT_VERSION_OVERRIDE_GATE: PASS (old 404, candidate 200 and 46 IDs)")


def verify_not_changed(deployment_id, old_version):
    current = _current_deployment(_get_api("/deployments"))
    current_shares = _shares(current)
    if (current.get("id") != deployment_id or
            current_shares != {old_version: 95, VERSION: 5}):
        raise Stop("CLOUDFLARE_DEPLOYMENT_CHANGED_DURING_E2E")
    print("CANARY_POSTCHECK: PASS (unchanged 95/5)")


def execute():
    scope = os.environ.get("MAGNETRA_CANARY_E2E_CHOICE", "")
    if scope not in (RUN_HTML, RUN_HTML_EZTV):
        raise Stop("EXPLICIT_READONLY_CANARY_E2E_APPROVAL_REQUIRED")

    old, deployment_id = deployment()
    exact_version_fingerprint(old)
    _source.check_catalog()

    for provider in ("oxtorrent", "torrent9"):
        items = _source.validate_search(provider, "ubuntu")
        _source.check_resolve(provider, items)

    if scope == RUN_HTML_EZTV:
        if not _source.check_eztv_positive():
            raise Stop("EZTV_POSITIVE_SOURCE_UNVERIFIED")
    else:
        print("EZTV_LIVE_RETEST: SKIPPED (earlier E2E evidence remains historical)")

    print("BTDIGG_LIVE_RETEST: SKIPPED (no new source probe authorized)")
    verify_not_changed(deployment_id, old)
    print("CANARY_SOURCE_E2E_GATE: PASS (candidate version-selected 95/5 slot; no torrent download)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(execute())
    except (Stop, _source.Stop) as exc:
        print("CANARY_SOURCE_E2E_GATE: STOP " + str(exc))
        print("READ_ONLY: no retry; no deployment, torrent download or raw secrets.")
        sys.exit(1)
    except Exception:
        print("CANARY_SOURCE_E2E_GATE: STOP UNEXPECTED_FAILURE (details withheld)")
        sys.exit(1)
