#!/usr/bin/env python3
"""One release only: promote the immutable candidate from staging run #5."""
from __future__ import annotations

import os
import subprocess

from deploy_magnetra_auto_pause_once import ROOT, Stop, UUID, snapshot, stable, wait_for, _wrangler_deploy
from release_magnetra_20261028 import candidate_baseline, critical_binding_guard, rollback_if_safe
from release_magnetra_hide_anime_mikan import catalog_guard
from release_magnetra_ro_it_12 import verify_all_assets, verify_public_with_html_settle

REVIEWED = "658f114278ff9576ed1c2ff4f7c2b940f89cf11b"
NEW = "d5e515bd-f286-4c93-8b0e-7124ee75620c"
APP_BLOB = "67b22972d586207ffe7b2bfcea877542e5521d39"
ACTION = "PROMOTE_REVIEWED_309"
DEPLOYED_PATHS = ("web", "worker/src", "worker/wrangler.jsonc")

def git(*args):
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True,
                                       stderr=subprocess.DEVNULL, timeout=15).strip()
    except (OSError, subprocess.SubprocessError):
        raise Stop("REVIEWED_SOURCE_NOT_VERIFIED") from None

def source_guard():
    git("merge-base", "--is-ancestor", REVIEWED, "HEAD")
    if git("diff", "--name-only", REVIEWED, "HEAD", "--", *DEPLOYED_PATHS):
        raise Stop("DEPLOYED_SOURCE_CHANGED_AFTER_STAGE")
    if git("hash-object", "web/app.js") != APP_BLOB:
        raise Stop("REVIEWED_APP_MISMATCH")

def run(action, expected_old):
    if action not in ("READ_ONLY", ACTION):
        raise Stop("NO_RELEASE_ACTION")
    source_guard()
    deployment, split = snapshot()
    old = candidate_baseline(split)
    if NEW == old:
        raise Stop("CANDIDATE_ALREADY_LIVE")
    if action == ACTION and (not UUID.fullmatch(expected_old) or old != expected_old):
        raise Stop("ACTIVE_VERSION_CHANGED_OR_NOT_APPROVED")
    critical_binding_guard(old)
    critical_binding_guard(NEW)
    catalog_guard(None)
    stable(deployment, split)
    print("REVIEWED_309_BASELINE:" + old + "@100")
    print("REVIEWED_309_CANDIDATE:" + NEW + "@0")
    if action == "READ_ONLY":
        return

    wrote_canary = False
    try:
        zero = {old: 100, NEW: 0}
        if split != zero:
            wrote = _wrangler_deploy([old+"@100%", NEW+"@0%"], "Magnetra #309: zero traffic verification")
            deployment = wait_for(deployment, split, zero, wrote)
        verify_all_assets(NEW, deployment, zero)
        catalog_guard(NEW)
        stable(deployment, zero)

        canary = {old: 95, NEW: 5}
        wrote_canary = True
        wrote = _wrangler_deploy([old+"@95%", NEW+"@5%"], "Magnetra #309: 5% canary")
        deployment = wait_for(deployment, zero, canary, wrote)
        verify_all_assets(NEW, deployment, canary)
        catalog_guard(NEW)
        stable(deployment, canary)

        full = {old: 0, NEW: 100}
        wrote = _wrangler_deploy([old+"@0%", NEW+"@100%"], "Magnetra #309: promote verified candidate")
        deployment = wait_for(deployment, canary, full, wrote)
        verify_public_with_html_settle(deployment, full)
        catalog_guard(None)
        stable(deployment, full)
        print("MAGNETRA_309_LIVE_VERIFIED:" + NEW)
    except (Stop, ValueError, KeyError, TypeError, OSError):
        if wrote_canary:
            rollback_if_safe(old, NEW)
        raise

if __name__ == "__main__":
    try:
        run(os.environ.get("RELEASE_ACTION", ""), os.environ.get("EXPECTED_OLD", ""))
    except (Stop, ValueError, KeyError, TypeError, OSError) as e:
        print("MAGNETRA_309_STOP:" + (str(e) if isinstance(e, Stop) else type(e).__name__))
        raise SystemExit(1) from None
