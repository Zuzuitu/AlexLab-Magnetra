# Browser capability pilot — BTDigg and ThePirateBay only

## Scope

Proof-of-capability for a real Chromium browser on Rock64, **ONLY** for BTDigg
and ThePirateBay. The other eight PWA providers and 46 backend adapters, Flud,
Cloudflare production, installed BTDigg cffi module and source ranking are unchanged.

Safari on iPhone working is useful evidence, but does not guarantee Chromium
automation on Rock64 will be accepted. No CAPTCHAs, stealth, proxy/IP rotation,
credential import, anti-bot evasion, background polling or automatic retries.

## Implementation status

- New rock64/browser_sources_pilot.py is NOT a live gateway, does not run as a
  systemd service and is not invoked by Cloudflare Worker.
- One owner-invoked navigation to btdig.com/search for BTDigg, or
  thepiratebay.org/search.php for TPB. The TPB page may naturally call apibay.org;
  the pilot records only its HTTP 429/403 status.
- Incognito Chromium; no cookies retained. Sandbox must remain enabled.
- Fixed HTTPS allowlist: btdig.com alone for BTDigg, and thepiratebay.org
  plus apibay.org for TPB; all external subresources blocked.
- Reports only safe status and DOM row/magnet-link counts, no query, URLs,
  response HTML, individual magnets, titles, secrets, cookies or IPs.
- A HTTP 200 page without verified row selectors is NOT called a successful
  or empty search: the status is no_rows_unverified.
- Unit tests use fake browser objects. No external source request in CI.
- Does not extract result records or replace either production adapter.
  That requires a successful original-browser navigation proof and a separate
  guarded browser gateway design with rollback.

## Safe prerequisite check on Rock64 (no installation)

Run as runner, not root:

    command -v chromium || true
    python3 - <<'PY'
    import importlib.util
    print("PLAYWRIGHT_PRESENT:",importlib.util.find_spec("playwright") is not None)
    PY
    df -h /
    free -h

Debian Trixie distributes Chromium ARM64 and Playwright supports Debian 13
ARM64. Check storage/memory before any installation; the browser is large.

## Offline tests

    cd "$HOME/magnetra-cffi-live-20261028"
    python3 -B -m unittest rock64/test_browser_sources_pilot.py -v

## Optional single, owner-initiated test (only if prerequisites available)

    python3 rock64/browser_sources_pilot.py --provider btdigg --category movies

Enter the test search query on stdin after the prompt. This runs ONE normal
browser navigation, with no retry, and prints only metadata. For TPB replace
the provider with thepiratebay. Do not repeat if the source returns 429/403,
or disable sandbox/protections to force access.

Interpretation:
- rendered_rows — original browser page exposed result/magnet selectors;
- source_http_429 or source_access_denied — origin refused, stop;
- challenge_not_solved — origin requires verification, stop;
- no_rows_unverified — could be JS loading, DOM changes or genuine empty;
- browser_navigation_failed — local browser/prerequisite issue, not zero results.

Only after the Rock64 browser pilot works with genuine user searches should
we connect browser mode to Magnetra and map validated source records.
