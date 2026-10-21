#!/usr/bin/env python3
"""Resume already-uploaded curated 27-indexer release after a safe HTML postflight rollback.

Only known, bound immutable 9bbb/6dad versions are permitted. No upload.
Fail closed on unknown deployment, non-200/429/504 or other errors; bounded
HTML propagation wait ONLY for HTTP-200 content mismatch, never source retries.
"""
from __future__ import annotations

import os
import sys
import time

from release_magnetra_hide_anime_mikan import (
    ACTIVE, Stop, bindings, catalog_guard, current, identity_guard,
    rollback_if_safe, stable, verify_assets, wait_for, _wrangler_deploy
)

NEW = "6dadc612-9660-4195-aeed-cdb658b22cf8"
ACTION = "CONFIRM_RESUME_HIDE_ANIME_MIKAN_20261021"
SLOT = {ACTIVE:100, NEW:0}
CANARY = {ACTIVE:95, NEW:5}
FULL = {ACTIVE:0, NEW:100}
HTML_200_MISMATCH = "HTML_NOT_REVIEWED_SOURCE_OR_KNOWN_CLOUDFLARE_BEACON"


def verify_public_with_html_settle(deployment):
    """Only successful 200 HTML source mismatch may be polled at bounded pace."""
    for n in range(6):
        try:
            verify_assets(None, deployment, FULL)
            return
        except Stop as e:
            # An HTTP error, 429, 504 or unknown mismatch never gets retried.
            if str(e) != HTML_200_MISMATCH or n == 5:
                raise
            stable(deployment, FULL)
            print("HTML_200_SHA_PENDING: controlled propagation wait " + str(n+1) + "/5")
            time.sleep(8)


def resume():
    identity_guard()
    before = current(SLOT)
    bindings(ACTIVE)
    bindings(NEW)
    stable(before, SLOT)
    print("RESUME_PREFLIGHT_PASS: 9bbb100 / 6dad0; immutable names/types verified")
    verify_assets(NEW, before, SLOT)
    catalog_guard(NEW)
    stable(before, SLOT)
    print("RESUME_STAGED_SOURCE_PASS: reviewed JS/CSS/HTML and 46 provider IDs")

    try:
        print("RESUME_CANARY_5: original95/new5")
        wrote = _wrangler_deploy(
            [ACTIVE+"@95%",NEW+"@5%"],
            "Magnetra 27-indexer owner-approved resumed canary 5 percent"
        )
        after5 = wait_for(before, SLOT, CANARY, wrote)
        verify_assets(NEW, after5, CANARY)
        stable(after5, CANARY)
        print("RESUME_CANARY_PASS")

        print("RESUME_FULL_100: previous0/new100")
        wrote2 = _wrangler_deploy(
            [ACTIVE+"@0%",NEW+"@100%"],
            "Magnetra hide AnimeTosho Mikan 27 indexers 100 percent; 9bbb rollback retained"
        )
        after100 = wait_for(after5, CANARY, FULL, wrote2)
        verify_public_with_html_settle(after100)
        catalog_guard(None)
        bindings(ACTIVE)
        bindings(NEW)
        stable(after100, FULL)
        print("RESUME_CURATED_PUBLIC_PASS: 6dad100/9bbb0")
        return 0
    except (Stop, ValueError, KeyError, TypeError, OSError):
        print("RESUME_CURATED_STOP: reviewed source, public assets, or traffic gate")
        # A single guarded rollback; never overwrite concurrent unknown splits.
        rollback_if_safe(NEW)
        return 1


def main():
    if os.environ.get("MAGNETRA_ANIME_MIKAN_RESUME_ACTION") != ACTION:
        print("STOP: explicit unique owner resume marker missing; no Cloudflare access")
        return 2
    try:
        return resume()
    except (Stop, ValueError, KeyError, TypeError, OSError):
        print("RESUME_PREFLIGHT_STOP: candidate/previous version or route not verified")
        return 1


if __name__=="__main__":
    sys.exit(main())
