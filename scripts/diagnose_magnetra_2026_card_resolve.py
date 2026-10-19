#!/usr/bin/env python3
"""Single read-only production 2026 card-to-Resolve diagnostic for OxTorrent/Torrent9.

Bounded source requests: one /api/search and at most one /api/resolve
for each provider (plus at most one distinct CANONICAL preferred source URL
per provider). No BTDigg, EZTV, .torrent, magnet output, Flud, or deployment.
Never emit source URL/title/item ID/magnet/token/provider HTML in logs.
"""
from __future__ import annotations

from collections import Counter
import importlib.util
import os
from pathlib import Path
import sys
import urllib.parse

DIRECTORY = Path(__file__).resolve().parent


def load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, DIRECTORY / filename)
    if spec is None or spec.loader is None:
        raise RuntimeError("missing diagnostic dependency")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


_exact = load("magnetra_exact_resolve_helper", "diagnose_magnetra_exact_oxtorrent_resolve.py")
_routes = load("magnetra_route_shape_helper", "diagnose_magnetra_detail_routes.py")

ACTION = "RUN_BOUNDED_2026_CARD_RESOLVE"
PROVIDERS = ("oxtorrent", "torrent9")
QUERY = "2026"
MAX_ROWS = 200
ALLOWED_TYPES = frozenset({
    "CANONICAL_DETAIL", "MISSING_DETAIL", "URL_TOO_LONG", "MALFORMED_URL",
    "NONCANONICAL_ORIGIN", "FRAGMENT", "QUERY_PARAMETERS", "TRAILING_SLASH",
    "PERCENT_ENCODED_PATH", "UNEXPECTED_DETAIL_SLUG",
    "DIFFERENT_TORRENT_ROUTE", "OTHER_PATH_TEMPLATE",
})


class Stop(Exception):
    pass


def shape(provider, raw):
    status = _routes.route_shape(provider, raw)
    return status if status in ALLOWED_TYPES else "UNCLASSIFIED"


def records(body):
    rows = body.get("results")
    if not isinstance(rows, list) or len(rows) > MAX_ROWS:
        raise Stop("SEARCH_RESULTS_SCHEMA_OR_LIMIT_INVALID")
    buckets = {name: [] for name in PROVIDERS}
    for row in rows:
        if not isinstance(row, dict):
            raise Stop("SEARCH_ROW_NOT_OBJECT")
        provider = row.get("provider")
        if provider not in buckets:
            raise Stop("SEARCH_PROVIDER_ATTRIBUTION_MISMATCH")
        buckets[provider].append(row)
    return buckets


def report(provider, rows):
    """Count only public field presence and fixed URL-shape enum, no raw text."""
    count = Counter()
    for row in rows:
        detail = row.get("details")
        source = row.get("magnetSource")
        preferred = source or detail
        count["total"] += 1
        count["detail_" + shape(provider, detail)] += 1
        if isinstance(source, str) and source:
            count["magnetSource_present"] += 1
            count["magnetSource_" + shape(provider, source)] += 1
            if source != detail:
                count["magnetSource_overrides_details"] += 1
        if isinstance(row.get("torrentFile"), str) and row["torrentFile"]:
            count["torrentFile_present"] += 1
        if isinstance(row.get("magnet"), str) and row["magnet"].startswith("magnet:?"):
            count["magnet_present"] += 1
        if shape(provider, preferred) != "CANONICAL_DETAIL":
            count["pwa_preferred_noncanonical"] += 1
    return count


def choose_sample(provider, rows):
    """Prefer a user-observed 2026 title, otherwise first unresolved valid detail."""
    eligible = [
        row for row in rows
        if not row.get("magnet") and shape(provider, row.get("details")) == "CANONICAL_DETAIL"
    ]
    if not eligible:
        return None, "NONE"
    for row in eligible:
        name = row.get("name")
        if isinstance(name, str) and "toy.story.5.2026" in name.lower().replace(" ", "."):
            return row, "SCREENSHOT_TITLE"
    return eligible[0], "FIRST_VALID_DETAIL"


def probe(provider, row):
    if row is None:
        print("LIVE_RESOLVE_" + provider + ": NOT_ATTEMPTED_NO_CANONICAL_UNRESOLVED_CARD")
        return
    details = row.get("details")
    preferred = row.get("magnetSource") or details
    print("PWA_PREFERRED_" + provider + ": " +
          ("MAGNET_SOURCE" if row.get("magnetSource") else "DETAILS"))
    print("PWA_PREFERRED_SHAPE_" + provider + ": " + shape(provider, preferred))
    print("PWA_PREFERRED_MATCHES_DETAILS_" + provider + ": " +
          ("YES" if preferred == details else "NO"))

    # Resolve only a path already accepted by the strict route-shape allowlist,
    # not a link with ads, redirects, new hosts, query or fragments.
    status, body = _exact.request_json("/api/resolve", payload={
        "provider": provider, "details": details
    })
    print("CANONICAL_DETAIL_RESOLVE_" + provider + ": " +
          _exact.classify_resolve(status, body))

    if preferred != details and shape(provider, preferred) == "CANONICAL_DETAIL":
        status, body = _exact.request_json("/api/resolve", payload={
            "provider": provider, "details": preferred
        })
        print("PWA_PREFERRED_RESOLVE_" + provider + ": " +
              _exact.classify_resolve(status, body))
    else:
        print("PWA_PREFERRED_RESOLVE_" + provider + ": " +
              ("SAME_AS_DETAILS" if preferred == details else
               "SKIPPED_NONCANONICAL_PREFERRED_LINK"))


def execute():
    if os.environ.get("MAGNETRA_2026_CARD_DIAGNOSTIC_APPROVAL") != ACTION:
        raise Stop("EXPLICIT_OWNER_DIAGNOSTIC_APPROVAL_REQUIRED")
    before = _exact.gate()
    print("PRODUCTION_GATE: CANDIDATE_100_OLD_0_VERIFIED")
    params = urllib.parse.urlencode({
        "q": QUERY, "category": "all", "providers": ",".join(PROVIDERS),
    })
    status, body = _exact.request_json("/api/search?" + params)
    if status != 200:
        raise Stop("PRODUCTION_SEARCH_NOT_HTTP_200")
    buckets = records(body)

    failures = body.get("errors")
    if not isinstance(failures, list):
        raise Stop("SEARCH_ERROR_SCHEMA_INVALID")
    for provider in PROVIDERS:
        errors = sum(
            isinstance(x, dict) and x.get("provider") == provider for x in failures
        )
        if errors:
            print("SEARCH_" + provider + ": PROVIDER_ERROR_PRESENT")
        sample_rows = buckets[provider]
        summary = report(provider, sample_rows)
        for key in sorted(summary):
            print("FIELD_" + provider + "_" + key.upper() + ": " +
                  str(summary[key]))
        row, selection = choose_sample(provider, sample_rows)
        print("SAMPLE_" + provider + ": " + selection)
        probe(provider, row)

    if _exact.gate() != before:
        raise Stop("CLOUDFLARE_DEPLOYMENT_CHANGED_DURING_DIAGNOSTIC")
    print("DIAGNOSTIC_PASS: no torrent downloads, magnet output, BTDigg, EZTV, Flud, writes or retries.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(execute())
    except (Stop, _exact.Stop) as err:
        print("DIAGNOSTIC_STOP: " + str(err))
        sys.exit(1)
    except Exception:
        print("DIAGNOSTIC_STOP: UNEXPECTED_FAILURE (raw data withheld)")
        sys.exit(1)
