#!/usr/bin/env python3
"""Manual BTDigg production-versus-0%-candidate diagnostic; NO mutations.

Safe policy: inspect exact Cloudflare 100/0 state and candidate override first.
Perform one BTDigg query via OLD production. Only if it succeeds and returns
genuine magnet-bearing rows, query the same term once through the candidate.
A production error/429/504 halts: NEVER repeat upstream after failure.

No Rock64 admin, no credential copies, no raw URLs/JSON/title/hash/magnet logs.
"""
from __future__ import annotations

import importlib.util
import os
import pathlib
import sys

TEST_CODE = pathlib.Path(__file__).with_name("check-magnetra-candidate-e2e.py")
SPEC = importlib.util.spec_from_file_location("magnetra_candidate_e2e", TEST_CODE)
e2e = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = e2e
SPEC.loader.exec_module(e2e)

# Exactly one benign, historically source-positive query; no user-derived
# arbitrary keywords or torrent-specific scraping payloads.
PATH = "/api/search?q=ubuntu&providers=btdigg&category=all"


def check_one_version(*, candidate: bool):
    """Return (kind, count) using only provider-verified structured records."""
    status, body = e2e.request_api(PATH, candidate=candidate)
    if status != 200 or not isinstance(body, dict):
        return ("HTTP_" + str(status) if status in (400, 401, 403, 429, 502, 503, 504)
                else "HTTP_OR_JSON_UNVERIFIED", 0)
    errors, results, stats = body.get("errors"), body.get("results"), body.get("stats")
    if not isinstance(errors, list) or not isinstance(results, list) or not isinstance(stats, list):
        return "INVALID_API_CONTRACT", 0
    if errors:
        return "ERROR_" + e2e.safe_provider_error_code(errors[0]), 0
    if len(stats) != 1 or not isinstance(stats[0], dict):
        return "INVALID_PROVIDER_STATS", 0
    stat = stats[0]
    if stat.get("provider") != "btdigg" or stat.get("ok") is not True:
        return "PROVIDER_STAT_UNVERIFIED", 0
    if not results:
        return "SOURCE_EMPTY_UNVERIFIED", 0
    if len(results) > 100 or any(not isinstance(v, dict) or
                                v.get("provider") != "btdigg" or
                                not isinstance(v.get("name"), str) or not v["name"] or
                                not e2e.valid_magnet(v.get("magnet"))
                                for v in results):
        return "INVALID_OR_FOREIGN_MAGNET_ROWS", 0
    if stat.get("count") != len(results) or body.get("total") != len(results):
        return "RESULT_COUNTER_MISMATCH", 0
    return "PASS", len(results)


def run() -> int:
    if os.environ.get("MAGNETRA_BTDIGG_COMPARE_APPROVAL") != "COMPARE_OLD_THEN_CANDIDATE":
        print("STOP: exact manual authorization missing; no network requests.")
        return 2
    # Validate that the test path remains a fixed benign request.
    if PATH != "/api/search?q=ubuntu&providers=btdigg&category=all":
        print("STOP: diagnostic request not canonical.")
        return 2

    # The current 100/0 slot + exact binding metadata and version fingerprint
    # must pass before even one BTDigg source request is initiated.
    e2e.check_deployment()
    e2e.check_routing_fingerprint()
    print("BTDIGG_COMPARISON: same source identity, same query, no retry on failure.")

    old_status, old_rows = check_one_version(candidate=False)
    print("BTDIGG_PRODUCTION: " + old_status +
          (" (validated rows=" + str(old_rows) + ")" if old_status == "PASS" else ""))
    if old_status != "PASS":
        print("BTDIGG_DIFFERENTIAL: STOP_PRODUCTION_NOT_POSITIVE")
        print("DIAGNOSIS: the old deployed Worker also cannot prove BTDigg right now; "
              "do not blame candidate or mutate Rock64 based on this single observation.")
        return 1

    # After old succeeded, existing 8796 success-only in-memory cache should
    # answer the second identical query, without causing a fresh source fetch.
    new_status, new_rows = check_one_version(candidate=True)
    print("BTDIGG_CANDIDATE: " + new_status +
          (" (validated rows=" + str(new_rows) + ")" if new_status == "PASS" else ""))
    if new_status != "PASS":
        print("BTDIGG_DIFFERENTIAL: STAGED_ONLY_REGRESSION_SUSPECT")
        return 1
    print("BTDIGG_DIFFERENTIAL: PASS_BOTH (old and candidate verified)")
    return 0


def main() -> int:
    try:
        return run()
    except e2e.Stop:
        print("BTDIGG_DIFFERENTIAL: STOP_UNVERIFIED_TRANSPORT_OR_CLOUDFLARE_GATE")
        return 2
    except Exception:
        print("BTDIGG_DIFFERENTIAL: STOP_UNEXPECTED_ERROR (details withheld)")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
