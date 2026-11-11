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

## Observed real BTDigg result and corrected metrics (11 Nov 2026)

A one-off Rock64 Chromium test for a very specific movie release returned
HTTP 200 and state `no_rows_unverified`. Original pilot code masked the
`rendered_rows` and `magnet_links` counters to **zero** whenever strict
validation failed. Those zeros therefore did NOT prove the page was empty.
This follow-up patch reports bounded raw counts separately:
`raw_dom_result_blocks`, `raw_dom_name_links`,
`raw_dom_magnet_candidates`, `magnet_links`,
`verified_dom_result_pairs`, and the number of external resources/scripts
blocked by the fixed-origin security policy. None contains page text or
magnet URLs. `rendered_rows` means verified pairs for BTDigg, not raw blocks.

The existing 429 from curl_cffi is still genuine. HTTP 200 from Chromium
proves the top-level browser navigation worked, **not** that it returned
torrent results or that this method will remain available.

**Diagnostic next action, if owner decides to run a new single search:**
Use a reasonably broad title and year, e.g. `The Dog Stars 2026`,
rather than an entire release string with codec, resolution and group.
Do not automatically issue an additional query after a 429; the pilot
never loops or retries. Genuine results must still be validated locally
for title, release group, codec and quality before being classified as PSA.

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
