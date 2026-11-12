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

**Exact URL supplied by owner and shown working in iPhone Safari/Chrome:**
`https://btdig.com/search?order=0&q=The+Dog+Stars+2026`.
The original Chromium pilot omitted the `order=0` parameter and therefore
did not test the exact same URL. Its owner-initiated BTDigg navigation now
uses this fixed first-page sort parameter, with a regression test for
the exact encoded URL. This is **not** evidence that adding the
parameter alone resolves the missing-results discrepancy.

The existing 429 from curl_cffi is still genuine. HTTP 200 from Chromium
proves the top-level browser navigation worked, **not** that it returned
torrent results or that this method will remain available.

**Diagnostic next action, if owner decides to run a new single search:**
Use a reasonably broad title and year, e.g. `The Dog Stars 2026`,
rather than an entire release string with codec, resolution and group.
Do not automatically issue an additional query after a 429; the pilot
never loops or retries. Genuine results must still be validated locally
for title, release group, codec and quality before being classified as PSA.

## Rock64 Chromium HTTP 200 with zero real DOM selectors (12 Nov 2026)

Owner's latest **one-shot** normal Chromium test for `The Dog Stars 2026`,
using the verified exact BTDigg URL `/search?order=0&q=The+Dog+Stars+2026`,
reported: navigation HTTP 200; 0 genuine `.one_result` DOM blocks,
0 title links, 0 BTIH magnets, and **one blocked external script**.

By contrast, normal iPhone browser screenshots show thousands of real source
results for that query and genuine magnets while on home Wi-Fi. This rules
out a missing-title explanation. A 200 response does **not** prove full
search access or genuine server-rendered result HTML.

**Do not presume the blocked script is causal.** Independent HTML adapters
parse `one_result` markup from BTDigg without running JavaScript; an
external verification/analytics script may be unrelated to result rendering.
Do not disable the allowlist, bypass CAPTCHA/verification or fake results.

A read-only next revision adds *metadata only*, from the **same, already
loaded navigation response** and the existing blocked requests:
- `response_html_chars`, `response_is_html`;
- `response_markup_result_marker` and `response_search_form_marker`;
- `response_verification_marker` (presence of known verification strings
  is **not** conclusive evidence of blocking);
- `blocked_script_categories` grouped as verification/static_cdn/other.

No raw HTML, blocked URLs/hosts, queries, magnets, tokens, source headers,
or cookies are printed; no additional BTDigg request or second page load
is introduced. TPB scope and existing Cloudflare/Flud services are unchanged.
Only after the owner inspects this single response can we decide whether
the browser is getting a soft-block page, a search shell or missing markup.

## Evidence: BTDigg serves Google reCAPTCHA assets to Rock64

The 12 November 2026 owner-run probe for the **exact** BTDigg URL
`https://btdig.com/search?order=0&q=The+Dog+Stars+2026` observed
`navigation_status=200`, `response_html_chars=59181`,
`response_markup_result_marker=false`,
`response_search_form_marker=false`,
`response_verification_marker=true`, all genuine DOM counts zero, and
`blocked_script_categories.verification=1`. The pilot's `verification`
classification is **not generic**: it recognizes only Google reCAPTCHA
paths on the official `www.google.com`, `www.gstatic.com` or
`recaptcha.google.com` hosts. Thus one real **Google reCAPTCHA resource**
was requested and blocked by the pilot. This is strong evidence of a
verification/interstitial response instead of real search HTML. It does
**not** prove that the response uses a particular reCAPTCHA variant or
that completing a verification guarantees subsequent programmatic access.

### Opt-in normal Google resources — experimental, NOT production

The original default continues to block all third-party assets, including
reCAPTCHA. This revision adds an explicit **owner-invoked test mode**:
`--allow-recaptcha-assets`. For BTDigg **only**, it permits HTTPS paths
under `/recaptcha/` on exactly the three official hosts above. Other
Google services, third-party trackers, scripts/CDNs, nonstandard ports,
insecure HTTP, redirected page navigations, TPB and all eight other PWA
indexers remain outside this exception.

This is **not** a CAPTCHA solver, challenge bypass, fingerprint
spoofing, cookie/session replay, proxy, IP rotation or search API. It
does not persist sessions. A visible human challenge cannot be solved
through this headless diagnostic; such an outcome must remain
`no_rows_unverified` and must never become fabricated results. One
top-level, owner-triggered navigation only; ordinary reCAPTCHA
subresources and external verification requests may be made by the page.

Optional after code merge and offline tests PASS:

    cd "$HOME/magnetra-cffi-live-20261028"
    "$HOME/.venvs/magnetra-browser/bin/python" rock64/browser_sources_pilot.py --provider btdigg --category movies --allow-recaptcha-assets

Enter `The Dog Stars 2026` once. Inspect
`recaptcha_assets_mode`, `recaptcha_subresources`,
`response_recaptcha_script_marker`,
`response_recaptcha_widget_marker`,
`response_recaptcha_invisible_marker`,
`response_verification_marker` and
`verified_dom_result_pairs`. Do **not** repeat after an upstream
429/403 or treat a successful CAPTCHA-resource load as a successful
source search.

If the site requires a human challenge, a future mode would have to be
explicitly interactive and respect the site's access policy. Until then,
regular iPhone Safari/Chrome manually copying a magnet into the existing
Magnetra Flud Companion action is the proven workaround.

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
