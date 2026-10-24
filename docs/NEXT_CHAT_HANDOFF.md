# AlexLab Magnetra — New-chat engineering handoff


## LATEST MANDATORY CHECKPOINT — 24 OCT 2026 04:06 EUROPE/ROME — THERARBAG ROOT JSON CORRECTED, IPHONE E2E STILL OPEN

**This heading supersedes historical latest-status sections below. Historical sections are preserved for provenance.** Do not interpret older live versions, stale URLs or proposed workflows as current status.

### Next-session P1 diagnostic work — NOT DEPLOYED (24 Oct 2026)
- A separate branch `diagnostics/therarbag-iphone-optin-20261024` adds owner opt-in tracing for the existing same-card TheRarBg resolver. When the iPhone URL explicitly contains `?magnetra_diag=1`, only TheRarBg `/api/resolve` requests include a bounded diagnostic header; default PWA behavior and all other providers remain unchanged.
- The Worker response includes finite HTML/JSON stages, diagnostic build label, a truncated SHA-256 of the validated details URL and bounded elapsed milliseconds. These appear in the diagnostic error text only in opt-in mode. No original BTIH, magnet, raw details URL, request body, credentials or upstream HTML are added to diagnostic output or logs. The existing source-owned HTML/JSON resolution and request counts are unchanged.
- This is **instrumentation, not a demonstrated bug fix**. Do not merge, enable any traffic, modify immutable Cloudflare percentages or claim iPhone success without four green CI gates, fresh bindings/deployment audit, explicit owner rollout approval and an actual iPhone test. The former `36019925@100 / c201cbf9@0` Cloudflare split remains a historical observation pending GET-only verification.
- A response saying `Worker fără raport` in opt-in mode indicates this debugging code did not answer the request; this alone cannot identify the exact Cloudflare version. Compare selected URL fingerprint and finite stages from the same card to differentiate client/request mismatch from source variability. The real Genshin detail link remains unverified.

### Repository and current deployment
- Public GitHub: https://github.com/Zuzuitu/AlexLab-Magnetra; production PWA: https://index.alexlab.media; current main immediately before this documentation update: 04dac669191ff647b5494216ff78e3cbfd39b1ab, PR #152 merged on 24 Oct. Deploy Magnetra PWA was SKIPPED on merge (run #40052634151). Code merged DOES NOT imply code activated.
- Last independent Cloudflare audit, run https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/40052525794: immutable 36019925-2308-4f99-8223-13854012d372 serves 100% normal production traffic; new PR152 code c201cbf9-2080-4a5b-9e40-723a8714d94c is staged at 0% ordinary traffic. Re-audit percentages before action; not guaranteed for all future times.
- All four required binding names/types audited on both versions: ASSETS (assets), BTDIGG_GATEWAY_TOKEN and MAGNETRA_GATEWAY_TOKEN (secret), FLUD_RELAY (service). Never print their values. The prior Flud Companion version 4e4730a1 was superseded by 36019925 after PR #151; run #40035839690 confirmed 100%, 46 catalog and bindings. A PR #151 squash commit inadvertently contained the [deploy-pwa] marker, triggering a 100% rollout. NEVER repeat a release marker in a non-release merge message.
- Original Android/API provider inventory: 46/46 adapters preserved; PWA only 12 visible / 34 intentionally hidden, Romanian default, Italian optional. Do not resurrect the hidden sources or delete provider IDs. BTDigg Rock64 source has intermittent 504/timeout and later recovery; do not claim permanent repair. Preserve BTDigg gateway 8796, central magnetra gateway 8798, existing tunnel, DNS, Cloudflare secrets and service, no paid infrastructure. Flud queued/relay HTTP success is not physical Shield ACK.

### User incident, real source URL and release work in this session
- iPhone user saw TheRarBg DETAIL_NO_BTIH on Obtain Magnet and Share; in web/app.js Share/Copy invokes ensureMagnet, so that error is the same resolver failure, not an independently proven share bug. Prior 22 Oct Genshin 93.2 MB FLAC card failed; its exact detail URL remains UNVERIFIED. Never borrow a Cyberpunk hash for Genshin.
- User-supplied Cyberpunk exact detail URL: https://therarbg.com/post-detail/95bf8b/2026-10-20-cyberpunk-edgerunners-2-original-series-soundtrack-flac-44-1khz-24bit/ . Screenshot on original site shows Magnet Download, .torrent File, Copy Magnet and Info Hash.
- Read-only exact HTML run #40033086217: HTTP 200, 160985 bytes, one original Info Hash label, one magnet href, zero input-value BTIH. Therefore the input-value hypothesis for this exact page is NOT SUPPORTED; PR #149 stays DRAFT and must not be merged as a fix.
- PR #140 exact bounded no-leak HTML diagnosis MERGED as a88cbdc75354c623f8ab56ead7f0ba8b0336c1ca. PR #150 Worker HTML-shape diagnostic stays DRAFT; remote-preview failed initialization, no Cloudflare live proof from it.
- Real Cloudflare workerd test discovered HTMLRewriter returns magnet href retaining &amp; query delimiters; PR #151 normalizes HTML ampersand entities only for source-owned TheRarBg magnets. Merged as 3cd418221bc29e113abd48d85b44bd25704d56ec; all 4 CI green. BUT iPhone still reported failure afterward; do not equate this patch with full DETAIL_NO_BTIH fix.
- Original-source GitHub read-only comparison run #40037986215: original HTML-labelled BTIH, original magnet and same-detail ?format=json infohash all agree. The TheRarBg public frontend uses Axios res.data.info_hash: Axios res.data is the HTTP JSON BODY, not a JSON object named data. Earlier proposed fallback incorrectly required payload.data.info_hash.
- Owner Rock64 first original JSON GET: HTTP 200 / application/json / data object false / error field false. Nested-only INFO HASH VALID false was a BAD TEST of the correct field; it did not show root infohash missing. The real Cloudflare egress V2 diagnostic #40048285028 also saw HTTP 200 valid JSON but MISSING_DATA_OBJECT due to nested-only assumption.
- Confirmed real Cloudflare egress V3 #40052397701: immutable V3 marker verified, HTTP 200, JSON_ROOT_BTIH_VALID. This demonstrates original root-level infohash exists from Cloudflare itself.
- PR #152 corrects fallback AFTER HTML resolution fails: one same-origin exact detail ?format=json bounded GET; accept strict original 40-hex BTIH at root or wrapped data if non-conflicting; reject mismatches with already fetched original HTML hash/magnet, redirects, invalid JSON, foreign host, oversized payload and challenge; no torrent download or alternate indexer. Unit tests and real workerd fixture passed all four required PR CI checks. Merged as 04dac669191ff647b5494216ff78e3cbfd39b1ab. This CODE is not yet live on the 100% version.
- New PR152 immutable candidate staged at 0% in run #40052525794: c201cbf9-2080-4a5b-9e40-723a8714d94c, all four bindings verified, production 36019925 remains 100%, source JSON hash matching candidate magnet. But legacy production ALSO returned magnet correctly on that GitHub runner.
- **Final user Rock64 exact two-version test on 24 Oct around 04:06 Europe/Rome**: 
  SURSA ORIGINALA: 200 True
  ACTUALA HTTP: 200 MAGNET VALID: True HASH CORECT: True COD: OK
  NOUA HTTP: 200 MAGNET VALID: True HASH CORECT: True COD: OK
  Thus both current production and zero-traffic candidate resolved this same Cyberpunk URL correctly FROM ROCK64. This is NOT evidence of a differential or a completed fix for intermittent iPhone PWA failure. Real iPhone same-card acceptance is still OPEN.
- Python default-UA HTTP 403 was an ingress client classification, not necessarily TheRarBg source. Fixed-origin six-request test #40047996718: default Python 403 for /api/health; browser-UA /api/health 200 and invalid details /api/resolve 400 on both version selections. Browser-User-Agent enables version attributed diagnostics; do not confuse edge 403 and Worker source 403.

### Mandatory action plan for next chat
P0. Read current main, AGENTS.md, docs/PROJECT_STATE.md, docs/NEXT_CHAT_HANDOFF.md and config/project-invariants.json; recheck deployment GET-only. Main commit and 100/0 version are observations at this checkpoint. Respect active 100% current version; do not promote candidate solely from Rock64 tests since baseline was also successful.
P1. Investigate iPhone PWA exact failing result end-to-end: ensureMagnet item provider and details/magnetSource, JSON POST URL/body, HTTP response/error stage, source record ID, optional service-worker/iOS cached JS, and Share/Copy/Get Magnet route behavior. Compare EXACT same item.details and network path with Rock64 successful request. No assumed cache bug; add minimal explicit opt-in privacy-safe diagnostics only if necessary, no hash/token/raw HTML output. For prior Genshin failure do not invent detail URL.
P2. Reproduce intermittent DETAIL_NO_BTIH under controlled single requests; classify status, source HTML/JSON shape and exact immutable Worker invoked. Validate UI labels and fallback errors without silently substituting other provider BTIH. Test genuine iPhone PWA once a candidate is safely exposed via approved canary; distinguish screenshot failure before or after new code activation.
P3. If a verified cause remains, make minimal branch/PR with tests: valid JSON root/wrapped, conflicts, malformed/error envelopes, same-origin redirects and SSRF guards, original same-detail fallback, Share/Copy absent-magnet UI, old/new timing. Do not claim success from only unit tests or unrelated GitHub-runner successes.
P4. Only with owner authorization and fresh Cloudflare metadata canary new reviewed immutable version 0% -> 5% -> 100%, fail closed on any binding, catalog, PWA assets, BTDigg, Flud synthetic relay or E2E regression; preserve last 100% immutable version as rollback at 0%. No stale release markers, no generic wrangler deploy, no accidental [deploy-pwa] in commit messages, no DNS/Tunnel/Rock64 change. Code-only docs/checkpoint updates must not deploy.
P5. After actual owner iPhone success verify Genshin exact original too if available, then update checkpoint and clean up obsolete branch-only diagnostics without removing audit evidence. Keep BTDigg intermittent timeout and Flud physical Shield ACK distinct, unverified issues.

### Hard engineering invariants
- Public repo GitHub Actions standard runners can run without purchasing private-repo minute quotas; preserve existing free/cost protections.
- Material code via branch + PR and all four checks: PWA/provider contracts, technical invariants, Android Debug, Android Staging. Documentation updates in guarded PR too; never direct-main.
- Do not remove 46 provider identities or activate the 34 hidden sources; RO default, IT optional, existing UX. No open proxy, paid sources, CAPTCHAs or anti-bot bypass, unsafe redirects, unrestricted retries, guessed or cross-source hashes, real torrents or private magnet logs, tokens in client, new tunnels, Rock64 service modifications, PWA cache purge without proof.
- Record evidence provenance: exact user screenshots, Rock64 output, GitHub Actions run IDs, Cloudflare immutable percentage/binding audits. Do not conflate code merge, staged 0%, GitHub HTTP 200, mobile E2E or source availability.

---


## LATEST INCIDENT / MANDATORY HANDOFF — 22 OCT 2026 18:56 EUROPE/ROME — THE RARBG STILL FAILS AFTER a088

**Outcome: FUNCTIONAL FAILURE CONFIRMED ON OWNER'S IPHONE. NO FURTHER SPECULATIVE RELEASE.**

1. User's fresh iPhone screenshot at **18:56 Europe/Rome, 22 October 2026**, after the new guarded cache-link fallback release, shows the first **TheRarBg** hit again: `[2026.10.21] 原神 Genshin Impact ... A Lyght of the Mone for Thee [FLAC 48kHz 24bit]`, **93.2 MB, 157 seeders, 85 peers**, from `index.alexlab.media`. Clicking **„Obține magnet”** still shows exactly **„Pagina de detalii TheRarBg nu conține un magnet acceptat sau un hash unic verificabil.”** This maps to `DETAIL_NO_BTIH`. Earlier screenshots around **03:17**, **04:29** (generic fallback) and **07:40** (first `DETAIL_NO_BTIH` on prior `056d`) document repeated failures. **Latest `a088` also FAILS for this same card.**
2. Verified real GitHub Actions production rollout [#39732674576](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39732674576) = `SUCCESS`; staged 0% -> 5% -> 100%. As last read in the release log, **Cloudflare active `a088fa41-233d-48d3-bd4c-52be6194fda8@100%`; rollback `056d8394-79b0-459a-b93e-b5f5a8a7295d@0%`**. The three immutable bindings, public PWA assets and 46 original provider identities passed release gates. Current GitHub `main` before this documentation PR: **`464b4dbfd61c3345c0dcf3135666a7982c89b310`** (PR #138 merged; main push PWA auto-deploy correctly skipped). Do **not** confuse CI/release success with a valid magnet on this card or infer current Cloudflare traffic without re-reading it before any future promotion.
3. **Observed vs unknown:** `DETAIL_NO_BTIH` means the Worker received a fetch considered successful by its existing guards and the resolver found no accepted magnet or uniquely trusted BTIH in that returned HTML. It does **not prove** that the authentic browser-visible detail page lacks hash/magnet or that a specific iTorrents link is present. Exact card `Detalii ↗` URL, final server response HTML, mobile/dynamic page structure, copied event attributes and relationship between result and detail have **NOT** been independently inspected. An unrelated source-owned card did resolve with `RESOLVED_MAGNET` in read-only GitHub run [#39710746214](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39710746214); this is not acceptance for the failed card. Earlier diagnostic [#39708239432](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39708239432) stopped before resolve with outer 403; it says nothing about TheRarBg upstream 403.
4. Technical paths: `worker/src/legacy-adapters.mjs` (`legacySearch`, `safeProviderHtml`, `resolveLegacy`, `magnetFromTheRarBgInfoHash`, `magnetFromTheRarBgSourceMetadata`), `worker/src/legacy-specs.mjs` (`therarbag` fixed host `https://therarbg.com`, listing path template), `worker/src/request-headers.mjs` (bounded HTTPS same-origin redirect), `worker/src/index.mjs` (`POST /api/resolve`), `worker/src/therarbag-resolve-errors.mjs` (safe `DETAIL_NO_BTIH` classification), `worker/src/providers.mjs` (listing normalization), `web/app.js` (`ensureMagnet`, `magnetFailureText`), `web/i18n.js`, `worker/test/therarbag-source-owned-hash-resolve.test.mjs` and `worker/test/therarbag-resolve-stage-codes.test.mjs`. Review original Kotlin upstream selectors/contracts before changing semantics.
5. Work completed this session: **PR #127** checkpoint reconcile successful Android CI; **#128** owner-approved read-only diagnostic; **#129** fail-closed diagnosis + outer 403 categories; **#130** successful alternate-card diagnostic checkpoint; **#131** RO/IT detailed error codes + identical repeated infohash; **#132** immutable stage release scaffold; **#133** activation -> `056d…@100%` (run [#39719146924](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39719146924)); **#134** checkpoint; **#135** strict same-detail `itorrents.org/torrent/<40hex>.torrent` link extraction (NO cache request, conflicting hashes rejected); **#136** guarded `056d` baseline release scaffold; **#137** activation -> `a088…@100%` (run #39732674576); **#138** checkpoint. All these PRs merged. Both of the latest live versions have failed on the owner's card; no claim of permanent TheRarBg repair.
6. **NEXT ACTION, HIGHEST PRIORITY:** obtain exact original detail link **via the failing card's `Detalii ↗` control**. On iPhone the owner can long-press Detalii and copy/share the link, or open the original website and copy URL. Do not accept guessed title->URL mappings. With exact URL, confirm HTTPS and approved fixed host `therarbg.com` and `/post-detail/` pattern before a **single bounded read-only** source detail fetch/diagnostic. Inspect sanitized structure: HTTP status, final same-origin URL, challenge detection, content type, byte size, presence/count of literal `magnet:?` hrefs, `Info Hash` labels in text/attributes/inputs, exact source-linked `.torrent File` href host/path and relative markup, `data-clipboard-text`, onclick/JS-rendered attributes, mismatch between listing and detail title. Never emit full hash, full magnet, tokens, HTML bodies or private URLs in logs. If user chooses to share exact page URL explicitly, use it only for source-owned audit.
7. **Implement a fix only after cause is reproduced in a constrained fixture from that exact page** (safe redacted structural fixture; avoid downloading torrent data). Maintain allowlist, HTTPS, SSRF protections, max body/timeout, one original-source request, no automatic repeated retries, no hash guessing/other indexer substitution, no CAPTCHA/Cloudflare bypass. Test valid, malformed, adversarial, mismatched, redirected, JS-only, missing metadata cases; confirm one actual E2E same-card success before claiming fixed.
8. **Production/release rules:** original 46 API/Android adapters stay intact; 34 hidden and 12 visible in PWA, RO default and IT optional, no test labels or hidden-provider reactivation. BTDigg intermittent TCP timeout NOT solved; one positive iPhone search is not reliability proof. Flud Companion Shield physical ACK and full delivery remain unverified. Rock64 credentials, gateway, DNS, IPv6, Tunnel, Cloudflare secrets/bindings must not be touched without independent evidence and explicit need. GitHub PR/CI first, all 4 checks green; deploy ONLY by newly reviewed unique one-shot activation after reading current Cloudflare split and hashes; immutable 0% -> 5% -> 100%, previous active kept at 0% for rollback; never reuse stale version IDs or 20261021/old 20261022 release activation scripts.
9. This note **supersedes historical sections below** where older branches were labelled `PENDING`, `NOT YET DEPLOYED` or `E2E untested`. Current definitive state: deployment succeeded, exact Genshin card E2E **FAILED at 18:56**, source structure **UNVERIFIED**, production **a088@100 / 056d@0 as last confirmed**, no next release justified without fresh evidence.

---


## PRODUCTION RELEASE CONFIRMED — 22 OCT 2026 — THE RARBG SOURCE-CACHE HASH FALLBACK

- New source-owned parser PR #135 was merged at `bebf1a92015cf94987396d5316a63c2b2a27b7ae`; guarded release package PR #136 merged at `de78d133d81971dde82ed91305eb0ff7abde3474`; unique activation PR #137 squash merge `243cccc94e41c5f11f7ea089c0a66f1a564e4eb7`.
- **Real production release SUCCESS:** GitHub Actions [#39732674576](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39732674576). Cloudflare active `a088fa41-233d-48d3-bd4c-52be6194fda8@100%`, immutable rollback `056d8394-79b0-459a-b93e-b5f5a8a7295d@0%`. Preflight verified prior split `056d@100/8c4e@0`, expected old JS `adbd2f21c2803a1e`, CSS `71ea60a9eaf7c03e`, i18n `2c0b099a3a840d78`, and 3 immutable bindings. Candidate independently validated after stage 0%, canary 5%, full 100%, 46/46 original provider identities and correct static assets.
- Source-owned fallback: after exactly one successful, safe same-origin `therarbg.com` detail fetch, accept either a unique labelled infohash OR a single vetted original `.torrent File` link with URL `https://itorrents.org/torrent/<40hex>.torrent` from the `Torrent:` action row, adjacent to `Info Hash:`; reject disagreements, mixed hashes and unsupported/foreign links. **No cache fetch or .torrent download**, no search in another provider, no fabricated hash. Existing original magnet paths remain untouched. 136+ source/provider tests PASS.
- **The exact Genshin 93.2 MB card has NOT been retested since `a088` release.** User's 07:40 local screenshot on earlier 056d release showed `DETAIL_NO_BTIH`, proving that earlier patch did not solve it. Do NOT claim this new source-cache fallback is E2E confirmed for that card until one owner iPhone `Obține magnet` attempt succeeds. If still `DETAIL_NO_BTIH`, the actual HTML likely lacks both accepted source-owned indicators; request the direct `Detalii ↗` URL for exact structural audit instead of more speculative releases.
- Old version IDs must not be reused for a new release; latest rollback is now `056d`, **not 8c4e**. The iPhone PWA uses RO default, IT optional, 12 visible indexers and 46 API identities. BTDigg, Rock64, Flud Companion Shield ACK, DNS and Tunnel untouched.

---


## 22 OCT 2026 — GUARDED 056d TO SOURCE-CACHE LINK RELEASE PREPARED (NOT DEPLOYED)

- PR #135 merged into `main` at `bebf1a92015cf94987396d5316a63c2b2a27b7ae`, after PWA + invariants + debug/staging CI PASS. Adds the strictly source-linked `https://itorrents.org/torrent/<40hex>.torrent` fallback extracted only from validated original TheRarBg detail HTML, alongside cross-validation against any labelled 40-hex original `Info Hash`. Does not fetch/download torrents or use other indexers.
- Release package uses **new** script `scripts/release_magnetra_therarbag_cache_link_20261022.py`, offline safety tests `scripts/test_release_magnetra_therarbag_cache_link_20261022.py`, workflow `.github/workflows/magnetra-therarbag-cache-link-one-shot.yml`. Unique activation marker `[magnetra-therarbag-cachelink-publish-20261022]` and release-event path `docs/release-events/therarbag-cache-link-20261022.md`. The activation file MUST be a separate approved PR: normal merges must NEVER deploy.
- Last **verified** live version `056d8394-79b0-459a-b93e-b5f5a8a7295d@100%`, with rollback `8c4e0f6a-dc7a-4f72-9954-ba9cdd91392f@0%`. Expected old `/app.js` SHA prefix `adbd2f21c2803a1e`, `/i18n.js` `2c0b099a3a840d78`, `/styles.css` `71ea60a9eaf7c03e`. Preflight must re-read Cloudflare actual deployment, hashes, 3 bindings and exact distribution; any difference stops before upload.
- Candidate release stages 0% (asset, language, HTML and 46-provider catalog), 5% canary, 100% public verification, previous 056d preserved at 0% for rollback; no DNS/Tunnel/Rock64/BTDigg/Flud/secret changes and no provider searches.
- **NOT YET LIVE.** The previously failing Genshin 93.2 MB card was observed `DETAIL_NO_BTIH` after 056d release, and the new source-cache link fallback is not yet E2E validated against its actual details HTML. Successful stage promotion must be followed by one fresh iPhone same-card test. Do not report a fixed magnet without this acceptance.

---


## 22 OCT 2026 — THE RARBG EXACT IPHONE CARD FAIL AFTER 056d RELEASE

- User repeated same first Genshin Impact music result (93.2 MB) at 07:40 Europe/Rome after release `056d8394-79b0-459a-b93e-b5f5a8a7295d`@100%. The new RO toast was **"Pagina de detalii TheRarBg nu conține un magnet acceptat sau un hash unic verificabil."** This maps to actual API `DETAIL_NO_BTIH` from an HTTP-200 detail HTML that lacked the previous parser's accepted `<a href="magnet:?">` or `Info Hash: <40 hex>` text. **The 056d release did not fix this card**; the diagnosis is no longer a generic 502/unknown origin. Do not claim success or repeat the previous duplicate-hash assumption.
- A publicly accessible TheRarBg own detail example exposes a `Torrent: Magnet Download .torrent File Copy Magnet Info Hash: <40 hex>` action row. Its `.torrent File` link goes to an iTorrents cache, documented URL form `https://itorrents.org/torrent/<40hex>.torrent` embeds the BTIH. This is evidence of a **source-linked metadata path**, not authority to use a different search indexer or infer hashes from titles.
- New narrow `magnetFromTheRarBgSourceMetadata` fallback, invoked ONLY after a successful original TheRarBg same-origin detail HTML fetch: accepts labelled original 40hex text OR exactly one strict `https://itorrents.org/torrent/<40hex>.torrent` link whose anchor is `.torrent File` in the same first-party `Torrent:` row followed by an `Info Hash:` label. If text hash and cache URL disagree, reject; if multiple different hashes appear, reject; disallow malicious lookalike hosts, non-HTTPS, credentials, queries, fragments, scripts, comments and unlabelled related links. It **does not fetch iTorrents or any .torrent file** and does not query another indexer; the output is a canonical BTIH derived only from that record's first-party HTML. Other 45 provider adapters unaffected.
- Added offline regression tests for source-linked cache hash, missing text hash, contradictions, phishing URLs, origin checking and one-request original-resolver behavior. **Not proven for the actual Genshin record until a new guarded release and iPhone retest.** Existing PWA 056d remains active and old 8c4e at 0% for rollback until then. Do not use old hardcoded 8c4e baseline release script after any new rollout.

---


## FINAL RELEASE CONFIRMATION — 22 OCT 2026 — THE RARBG STAGE DIAGNOSTICS LIVE 100%

- **Published successfully** via unique one-shot GitHub Actions [#39719146924](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39719146924), activated by reviewed PR #133 squash merge `d9215159dfc8e7466961abb8b1f21aa0981a77d6`. Workflow conclusion: **SUCCESS**; actual guarded release code, not just mocked unit tests, logged all three traffic stages.
- **Cloudflare live:** `056d8394-79b0-459a-b93e-b5f5a8a7295d @100%`. **Immutable rollback:** `8c4e0f6a-dc7a-4f72-9954-ba9cdd91392f @0%`. Snapshot and unchanged share verified by release's postflight. Previous `60112...` was the old rollback before the release; it is no longer the current 0% rollback and must **NOT** be targeted by a historic release script.
- Old baseline preflight verified 8c4e@100/60112@0, three immutable bindings for each, public old `/app.js` SHA prefix `67775b388e3239e2`, old `/styles.css` SHA `71ea60a9eaf7c03e`, old `/i18n.js` SHA `5b09171b28a75a81`. Candidate uploaded `056d8394...`; checks passed at 0%, 5% and full 100%.
- Verified *new* public `/app.js` SHA prefix `adbd2f21c2803a1e`, `/styles.css` `71ea60a9eaf7c03e`, `/i18n.js` `2c0b099a3a840d78`, HTML reviewed source `37865e2eb60ee9f0` (Cloudflare beacon-only delta). `/api/providers`: original **46 IDs**, no provider searches or downloads as part of guarded rollout.
- **Functionality still needs independent iPhone acceptance:** the user's first TheRarBg / Genshin Impact 2026 card previously failed twice on cellular; the source parser now accepts repeated *identical* original hash and the PWA translates finite upstream/HTML/client transport errors. No evidence yet that exact previously failed iPhone card resolves after this release. One single user-triggered search and `Obține magnet` on that card is the next action; use exact new RO error category if it still fails. Do not declare permanent TheRarBg availability or Flud Shield ACK.
- **No further deploy planned or needed** until actual live user outcome. Do not use historical `magnetra-therarbag-magnet-one-shot` or old 20261021 deployment scripts. Preserve 46 original adapters, 12 visible, RO default, IT optional, Rock64/BTDigg gateway, secrets, Flud, DNS and Tunnel unchanged.


---


## 22 OCT 2026 — THE RARBG SAFE ERROR-STAGES RELEASE PACKAGE (PREPARED, NOT YET DEPLOYED)

- PR #131 **merged into main** at `0a0c65546728e834cd9b265c68b5dd26d5a18c4e`; all required PR CI passed. Parser fix accepts multiple copies of the exact same validated source-owned 40-hex `Info Hash`, but rejects different values. `therarbag` only API provides sanitized categorical resolve failure `code`; RO/IT client now distinguishes transport, upstream HTTP, missing hash, redirects and client/network failures. Old iPhone card continued to fail before this change was deployed.
- One-shot release implementation `scripts/release_magnetra_therarbag_error_stages_20261022.py`, offline regression `scripts/test_release_magnetra_therarbag_error_stages_20261022.py`, and guarded workflow `.github/workflows/magnetra-therarbag-error-stages-one-shot.yml`. **Never use historical 20261021 release script against the new baseline**: it targets earlier immutable versions.
- Expected latest documented Cloudflare split before upload: `8c4e0f6a-dc7a-4f72-9954-ba9cdd91392f@100%` and `60112a3d-b478-4071-b087-ab793fbdfd60@0%`. Script must re-read actual Cloudflare deployment and requires exact split + validated static asset SHA prefixes + verified 3 bindings before any upload. Unexpected state = STOP, no new traffic.
- Unique activation path `docs/release-events/therarbag-error-stages-20261022.md`; marker `[magnetra-therarbag-stages-publish-20261022]`; no normal merge triggers release. Guarded immutable upload preserves existing secrets, staged 0% asset and 46 ID check, 5% canary verification, 100% public verification, old 8c4e at 0% for rollback, rollback only after inspecting exact known split; no Rock64, DNS, Tunnel, Flud, external torrent downloads, BTDigg source probes, or source-site bypass.
- **Not yet deployed at the time this checkpoint was drafted.** Merge release PR only after CI; activate separately under owner's explicit production-publish authorization. Confirm run deployment ID and exact Cloudflare shares; then one real same-card iPhone test. Do not claim functional fix without that test.


---


### Small functional TheRarBg parser hardening — not proven for owner card

The `magnetFromTheRarBgInfoHash` extractor previously rejected HTML containing two identical `Info Hash: <same 40 hex>` labels because it counted **occurrences**, not distinct values. On a source-owned same-origin successful HTTP 200 detail page, duplicate identical mobile/desktop copies are unambiguous: the parser now permits them; two *different* hashes, malformed labels, off-origin redirects, HTTP errors and oversize documents still fail closed. Added regression test for identical duplicates; earlier conflicting-hash test remains. This is a bounded **potential functional improvement**, not proof that the repeated failing Genshin iPhone card contains duplicate labels; that live HTML has not been inspected and no new release has occurred.



## 22 OCT 2026 — THE RARBG IPHONE REPEATED FAIL, STRUCTURED ERROR STAGES IN CODE (NOT YET LIVE)

- Owner iPhone screenshot at 04:29 Italy on 22 Oct shows the same first **TheRarBg** result (Genshin Impact soundtrack, 93.2 MB, 157 seeders) from the earlier failed session; tapping **Obține magnet** again displays the same generic RO fallback. At least two real iPhone failures; do not call this simply a one-off. Public API diagnostic #39710746214 earlier successfully resolved a sample `2026` card; it did **not** prove the owner clicked identical record, nor did it test the iPhone-to-Worker HTTP POST.
- Current `web/app.js` `api()` discarded the JSON body and code on non-2xx; `magnetFailureText` always displayed the same generic TheRarBg fallback for all errors. Consequently screenshots **cannot distinguish** source HTTP 403/429/502/504, anti-bot, network timeout, missing unique `Info Hash` in genuine source HTML, or an outer non-JSON Cloudflare 403. Do not infer root cause from the previous toast.
- Targeted source-level PR adds `worker/src/therarbag-resolve-errors.mjs` finite, safe classifications *only* for `therarbag` in `/api/resolve` errors; error body never contains raw details URLs, HTML, hashes, titles or tokens. On success API shape remains `{provider,magnet}`. Other 45 adapter identities and errors untouched. `web/app.js` preserves `magnetraCode` for `/api/resolve` only; RO/IT `web/i18n.js` displays the specific stage. Existing `Detalii` still available; no automatic retries, origin change, torrent downloads, Flud, Rock64, proxy, source bypass or secret change.
- This instrumentation is **not a demonstrated functional magnet repair** and requires independently guarded Cloudflare promotion after PR 4/4 CI and an exact live baseline/rollback check. Until published, the screenshot toast does not expose details. After release, a single new same-card tap can distinguish transport vs parsing; only then design a root-cause-specific fix. Do not run full source search stress tests.


---


## THE RARBG — 22 OCT 2026 — REAL PRODUCTION RESOLVE PASS (INTERMITTENCY STILL UNVERIFIED)

- Manual approved read-only GitHub Actions [run #39710746214](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39710746214) at 2026-10-22 02:19 UTC, commit `fbbb6dd298849f47756954491de0519c3f4a8ac1`, **SUCCESS**. New guarded diagnostic was run with explicit source approval. `SEARCH_HTTP_STATUS: 200`, JSON, `SEARCH_CARD_COUNT: 50`, `SEARCH_ERRORS_COUNT: 0`, `SOURCE_CARD_TORRENTFILE_PRESENT: True`, `RESOLVE_HTTP_STATUS: 200`, `RESOLVE_CLASS: RESOLVED_MAGNET`, `DIAGNOSTIC_COMPLETED: RESOLVER_E2E_PASS`; no `cf-mitigated` challenge reported. This proves **one real Worker API → source-owned TheRarBg → valid magnet result** after the fix; it is not merely an offline parser test.
- Prior [run #39708239432](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39708239432) was blocked by outer 403 on search, before resolve. PR #129 corrected the premature `SUCCESS` and added fail-closed classification. The later success is separate evidence, not a retrospective interpretation of the earlier 403.
- **iPhone status remains MIXED:** user screenshot around 03:17 local on 22 October showed a TheRarBg `Obține magnet` failure and RO fallback in the PWA. The later Actions probe selected the first eligible source-owned card in a `2026` search; an exact match to the user-clicked card **was not proven**. The apparent conflict may be due to a distinct card or time-dependent upstream availability, but neither cause is established. Do not mark iPhone E2E PASS and do not claim 100% reliability.
- **Next measured decision:** one user-controlled retry on the same card (no stress searches); if it still fails, capture card-specific, sanitized stage evidence before parser/transport changes. Do not relabel results, guess hashes, bypass CAPTCHA, change Rock64/BTDigg, or redeploy a Worker already proven reachable. Flud Shield ACK remains separate.

---


## THE RARBG 22 OCT 2026 — DIAGNOSTIC 403 FAIL-CLOSED (no Worker release)

- Owner-approved run [#39708239432](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39708239432), main `d3d0040...`: GitHub Actions job concluded `SUCCESS`, but actual public GET `/api/search?q=2026&category=all&providers=therarbag` returned outer HTTP **403**, before the Worker `/api/resolve` request. **The run is INCONCLUSIVE for magnet resolution**. No source HTTP status can be inferred, and 403 is not proof that `therarbg.com` returned 403. On this Worker, ordinary GET search wraps provider errors into JSON HTTP 200.
- Root bug in the diagnostic: `if code != 200: print(...); return` from `main()` gave process exit 0 and a false `SUCCESS`. Corrected diagnostic uses explicit nonzero exit for pre-resolve HTTP block, unusable JSON, missing real TheRarBg card and unclassified resolve errors. It emits finite classifications, response content type, `cf-mitigated` challenge flag and Cloudflare Ray correlation ID when validated (never torrent IDs/URLs/hashes/magnets/tokens). An outer search block permits one harmless GET `/api/health` comparison, using the same diagnostic User-Agent to distinguish route-specific from host-wide blocks; **no extra provider calls**. Only one bounded real search and up to one real resolve when explicitly dispatched.
- Offline regression tests `scripts/test_therarbag_readonly_diagnostic.py` mock HTTP 403 HTML/JSON, health compare, search failure, source allowlist, 502 classified resolution and a successful BTIH response; workflow runs them before any manually approved network request. No GitHub workflow auto-run on merge, no Worker deploy and no Rock64/DNS/BTDigg/Flud changes.
- Next evidence: on manual dispatch of `Diagnose TheRarBg iPhone Resolve (READ ONLY)` with explicit `RUN_ONCE_THE_RARBG_READONLY` input, capture **`SEARCH_BLOCK_CLASS`, `HEALTH_COMPARISON_CLASS`** or **`RESOLVE_CLASS`**. If still outer 403 with Cloudflare metadata, examine Cloudflare Security Events via Ray in the owner's authorized dashboard, no WAF bypass. Do not patch TheRarBg parser or traffic without cause. A GitHub workflow `SUCCESS` after a full probe classifies transport/parser, it is NOT proof of working magnet unless `RESOLVE_CLASS: RESOLVED_MAGNET` and independent iPhone E2E pass.


---


## INCIDENT IPHONE THE RARBG — 22 OCTOMBRIE 2026 — E2E FAIL DUPĂ FIX

- Proprietarul a testat efectiv `https://index.alexlab.media` pe iPhone 5G, căutarea a afișat 51 rezultate și 9 titluri excluse ca nerelevante. Un card marcat **TheRarBg** a afișat **„Obține magnet”** și buton **„.torrent ↗”**. La apăsare, UI a arătat fallbackul nou RO: „TheRarBg nu a putut furniza magnetul. Deschide «Detalii» pentru a încerca direct pe site.” **Verdict: TheRarBg iPhone resolve FAIL după release 8c4e, nu mai este PENDING.** Fallbackul UI RO este confirmat funcțional, nu și rezolvarea magnetului.
- **Cauza upstream vs parser rămâne NECUNOSCUTĂ.** Worker întoarce generic HTTP 502 și pentru erori de request, și pentru `no supported magnet`. O pagină publică TheRarBg examinată separat afișează `Info Hash:`, dar asta nu demonstrează că Worker a primit aceeași pagină la detaliul din iPhone.
- Pregătit diagnostic manual read-only dedicat: `.github/workflows/diagnose-therarbag-iphone-resolve-readonly.yml` și `scripts/diagnose_therarbag_iphone_resolve.py`. Necesită selecția explicită `RUN_ONCE_THE_RARBG_READONLY`, pe `main`; face **maximum o căutare TheRarBg `2026` și un POST resolve dintr-un card cu URL detalii HTTPS allowlisted**, raportează doar categoria sanitară (ex. `UPSTREAM_HTTP_403`, `DETAIL_HTML_NO_MAGNET_OR_HASH`, `FETCH_TIMEOUT`) și dacă linkul .torrent era prezent; nu loghează titluri, URL-uri, hashuri, magneturi sau secrete. **NU este un deploy și NU rulează automat după merge.**
- Nu publica alt fix Worker pe ghicite și nu lărgi origin allowlist; întâi diagnosticul categorial, apoi patch izolat, CI, release guarded și retest efectiv pe iPhone. BTDigg, OxTorrent, Torrent9, Flud, Rock64, DNS, IPv6 și cele 46 adaptoare neatinse.

---


## ACTUALIZARE VERIFICATĂ — 22 OCTOMBRIE 2026 — CI POST-CHECKPOINT

- `main` verificat la `c4f1e5fb90f288c76c026a53e706cd2687c2f90d`; PR #126 rămâne ultimul merge la momentul acestei verificări.
- **Android staging:** GitHub Actions [#39698657719](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39698657719) = `SUCCESS` pe acel `main`. Logul confirmă `:app:assembleStaging`, `BUILD SUCCESSFUL` și uploadul artefactului `torrentsearch-staging.apk` (ID 12392185923). Eșecul anterior #39652018922 pentru `org.jetbrains.kotlin:compose-group-mapping:2.4.20` este ISTORIC, nu statusul ultimului run. Nu s-a aplicat un patch de cod Android în această verificare; nu declara rezolvare garantată permanent.
- **Producție PWA smoke:** [#39698657765](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39698657765) `SUCCESS`; log `PASS: HTTP+TLS OK; HTML, manifest, /api/health, /api/providers OK; 46/46 adapters inventoried as ported`.
- **Teste:** PWA/provider contracts [#39698657715](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39698657715) și technical invariants [#39698657874](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39698657874) = `SUCCESS`.
- **Fără redeploy:** workflow-ul automat Deploy Magnetra PWA [#39698657731](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39698657731) = `SKIPPED`; ultimul release Cloudflare documentat rămâne `8c4e0f6a…@100% / 60112a3d…@0%`, însă această verificare nu a putut citi direct un split actual din API Cloudflare. Nu transforma istoricul în dovadă nouă de trafic LIVE.
- **Încă deschis:** TheRarBg `Obține magnet` real pe iPhone după patch nevalidat; BTDigg reușit măcar o dată E2E dar intermitent; Flud Companion ACK fizic pe Shield nevalidat. Fără query de scraping repetitiv, modificări Rock64 sau schimbări în secrete.

---

## CHECKPOINT AUTORITATIV — 22 OCTOMBRIE 2026 — THE RARBG LIVE / BTDIGG INTERMITENT

**Această stare este mai nouă decât orice secțiune anterioară intitulată «fix pregătit / nepublicat».**

- **Cod:** PR #123 (TheRarBg fallback hash) MERGED, commit 40d4e5c0bb7d5542db0b551c60128a5aa8e135fb. PR #124 (guarded release) MERGED, commit 732848a9ce8d56cc7cee743975a79cfece6e296c, 4/4 CI PASS. PR #125 (activation) MERGED, main commit bdd1270a977653122f234d6b960dbaab120ad7a3.
- **Cloudflare real:** run https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39652018835 SUCCESS. Live `8c4e0f6a-dc7a-4f72-9954-ba9cdd91392f@100%`; rollback vechi `60112a3d-b478-4071-b087-ab793fbdfd60@0%`. Zero-stage / 5%-canary / 100% PASS, 46 provider identities PASS. app.js SHA prefix `67775b388e3239e2`, CSS `71ea60a9eaf7c03e`, HTML `37865e2eb60ee9f0`, i18n.js `5b09171b28a75a81`. Acestea demonstrează succesul release-ului, NU al cardului concret din iPhone.
- **TheRarBg:** utilizatorul a confirmat că «Cererea a eșuat (502)» a apărut la «Obține magnet» pe rezultatul TheRarBg (`therarbag`), nu la BTDigg. Worker `/api/resolve` răspunde HTTP 502 pentru orice excepție, inclusiv parsare/absență magnet, deci codul singur NU demonstrează 502 real upstream. Fix live: din HTML de detalii HTTPS de pe sursa permisă, numai la HTTP 200 și fără ancoră magnet, extrage un unic hash BTIH de 40 hex cu etichetă `Info Hash:` și îl convertește în magnet. Nu ghicește hash, nu folosește alt site, nu repetă agresiv și nu ocolește CAPTCHA. Răspuns upstream 502 real rămâne eroare; UI RO/IT explică și permite butonul Detalii. **Testul efectiv pe iPhone după release este PENDING.**
- **BTDigg Rock64:** PR #105 transport IPv4, CA/SNI TLS, timeouts etapizate, fără proxy/retry; instalat fizic, 99 teste PASS + localhost health PASS. Postinstall două loguri tcp_timeout (~3 sec) cu DNS 3/48ms. `curl -4` HTTP 200 în 0.497s; shell Python TCP PASS 50ms, DNS o singură adresă IPv4 la verificare. Verificatorul real al gateway-ului a produs HTTP 200, 10 rezultate și 10 BTIH, log `total_ms=1094` și `failure=none`. **Utilizatorul a confirmat o căutare BTDigg reușită pe iPhone.** Intermitența NU este declarată reparată permanent. Nu reinstala Rock64, nu ajusta global DNS/IPv6/router/systemd fără probe.
- **Indexere/UI:** catalog original 46 identități/adaptoare în Worker și Android, 34 ascunse numai în interfața PWA, 12 selectabile; priorități BTDigg → Torrent9 → OxTorrent, BTDigg implicit cu fallback. Celelalte vizibile: Knaben, TorrentsCSV, ThePirateBay, Internet Archive, TheRarBg, AudioBookBay, NoNameClub, SubsPlease, 0Magnet. RO implicit, IT alternativ salvat local, texte de audit/test eliminate din UI; păstrează protecțiile și curățarea selecțiilor vechi.
- **Flud Companion:** UI, pair și butonul «Trimite în Flud» nu confirmă livrare fizică. ACK / receipt pe NVIDIA Shield și Android P3 rămâne de verificat. Fără download automat.
- **Android staging separat:** pe push-ul de activare PR #125, jobul `Build staging APK` #39652018922 a eșuat prin dependența Gradle lipsă `org.jetbrains.kotlin:compose-group-mapping:2.4.20` în `:app:composeMappingProducerClasspath`. Debug APK, PWA/provider tests, invariants și smoke PWA au trecut; Cloudflare release a reușit. Aceasta este problemă separată de livrarea PWA; verifică doar când revii la Android.
- **Pași următori:** 1) test iPhone «Obține magnet» pe un rezultat TheRarBg și consemnează exact rezultatul; 2) dacă încă 502, diagnostic sigur pe etapele `/api/resolve` (URL source allowlist, HTTP status upstream, HTML selector / hash) fără a expune tokenuri și fără a relaxa politica sursei; 3) observații BTDigg la apariția naturală a altor timeouturi, diferențiate de erorile TheRarBg; 4) E2E fizic Flud; 5) Android staging dependency separat. **Niciun nou deploy Cloudflare pentru documentare.**

---


## UPDATE 21 OCTOMBRIE 2026 — THE RARBG MAGNET 502: FIX PARSER PREGĂTIT, NU CONFUNDA CU BTDIGG

Utilizatorul a furnizat captură iPhone PWA română unde în cadrul rezultatului **TheRarBg** era butonul „Obține magnet” și toast „Cererea a eșuat (502)”. A clarificat expres că eroarea provine de la **TheRarBg** și este separată de eventualele timeouturi BTDigg. `/api/resolve` este endpointul Worker care întoarce HTTP 502 pentru orice excepție a resolverului, inclusiv parser/no-magnet, deci numai 502 nu dovedește HTTP 502 de la domeniul sursă.

Investigație: adaptorul `therarbag` din `worker/src/legacy-specs.mjs` extrage implicit doar `a[href^='magnet:']`. Pagina TheRarBg, în observare externă, prezintă și `Info Hash: <40 hex>` drept text propriu. Patch izolat în `worker/src/legacy-adapters.mjs`: după încărcarea reușită, validată prin same-origin allowlist/TLS/antibot/size, dacă nu apare ancoră magnet, transformă **numai** un unic infohash cu etichetă `Info Hash:` în `magnet:?xt=urn:btih:<hash>`; niciun retry, torrent download, bypass, redirect, combinație cu alte surse sau hash ghicit. HTTP 502/403 reale rămân erori. Teste noi `worker/test/therarbag-source-owned-hash-resolve.test.mjs`. Pentru un eșec real, interfața PWA afișează RO/IT mesaj specific și indică „Detalii” în locul unui toast 502 generic. All 46 adapters intacte; BTDigg/Rock64/Flud neatins.

Planul de release este separat de parser: workflow unic `.github/workflows/magnetra-therarbag-magnet-one-shot.yml` cu marker `[magnetra-therarbag-magnet-publish-20261021]`, preflight `60112a3d-b478-4071-b087-ab793fbdfd60@100% / 6dadc612-9660-4195-aeed-cdb658b22cf8@0%`, app.js hash vechi `44f1eac85e8550a7`; upload --keep-vars versiune imutabilă nouă, verificare 0%/5%/100% a app.js, i18n.js, CSS, HTML și 46 API IDs, rollback numai pe split cunoscut. **Publicarea și fixul E2E pe iPhone încă nu sunt probate**, până la un run succes și o acțiune efectivă pe iPhone.

---


## 21 OCTOMBRIE 2026 — RO/IT + 12 INDEXERE: PRODUCȚIE 100% CONFIRMATĂ

**Noua stare operațională autoritativă**: [GitHub Actions run #39637878742](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39637878742) = `SUCCESS`. Commit de activare `78a5f72895413b4edd3d7a7926cbae1e292d35bb`. Versiunea Cloudflare Worker+assets `60112a3d-b478-4071-b087-ab793fbdfd60@100%`, versiunea anterioară `6dadc612-9660-4195-aeed-cdb658b22cf8@0%` păstrată pentru rollback. **Nu mai considerați 6dad@100 / 9bbb@0 drept distribuție curentă**; este istoric.

**Dovezi postflight de pe site:** original 6dad100/9bbb0 cu 3 bindinguri verificate; noul upload imutabil cu `--keep-vars`; staging 0% PASS; canary 5% PASS; full100 PASS. Hashuri publice/override verificate `/app.js=44f1eac85e8550a7`, `/styles.css=71ea60a9eaf7c03e`, `/index.html source=37865e2eb60ee9f0` (doar beacon Cloudflare admis), noul `/i18n.js=3ca52c9b10d49502`; `ORIGINAL_PROVIDER_CATALOG_PASS:46`, bindinguri 3/3 PASS; log exact `RO_IT_12_PRODUCTION_100_PASS: 60112a3d-b478-4071-b087-ab793fbdfd60@100 / 6dad@0`.

**Comportament PWA publicat:** 12 indexere vizibile, 34 invizibile și ne-selectabile, păstrate ca originale în Worker/Android (46). Cele 15 ascunse în această sesiune: BangumiMoe, Btsow, Dmhy, LinuxTracker, MyPornClub, NekoBT, Sukebei, YTS, AniLibria, BlueRoms, EpubLibre, MegaPeer, Rutor, XXXTracker, FitGirl Repacks. BTDigg, Torrent9, OxTorrent rămân primele; BTDigg selectat implicit alături de fallback-urile consacrate. Interfața numai **română implicită / italiană opțională**, alegere salvată în browser; fără badge-uri publice `RESULTS THIS SESSION`, audit, `NOT AUDITED`, sau coduri diagnostic pe pagina normală. Avertismentele utile pentru surse încă vizibile rămân. Fără modificări Rock64, Tunnel, DNS, Flud, secrete ori costuri.

**Încă neconfirmat de proprietar:** test vizual direct pe iPhone al celor 12 surse și comutarea RO↔IT; dovada Cloudflare 100% este separată și deja confirmată. Următorul pas poate fi o verificare vizuală rapidă în `https://index.alexlab.media`, fără comenzi SSH.

---


## UPDATE 21 OCTOMBRIE 2026 — CURATED 12 SURSE + RO/IT: LANSARE SECURIZATĂ PREGĂTITĂ

**Ultima cerere explicită a proprietarului:** ascunde suplimentar BangumiMoe, Btsow, Dmhy, LinuxTracker, MyPornClub, NekoBT, Sukebei, YTS, AniLibria, BlueRoms, EpubLibre, MegaPeer, Rutor, XXXTracker și FitGirl Repacks; în total 34 ID-uri ascunse și 12 surse rămase în selector, BTDigg/Torrent9/OxTorrent primele. Întreaga interfață publică PWA este română implicită sau italiană la alegere (limba salvată în browser), fără badge-uri de audit/test. Sunt păstrate toate cele 46 adaptoare Worker și Android, fără modificări Flud, Rock64, secrete, DNS sau Tunnel. Cod UI este în PR #119; testele de regresie pentru traducere și selecții salvate iPhone.

**Lansare pregătită, NU executată de acest PR:** `scripts/release_magnetra_ro_it_12.py`, `.github/workflows/magnetra-ro-it-12-one-shot.yml`, `scripts/test_release_magnetra_ro_it_12.py`. Un viitor commit separat, unic, care modifică numai `docs/release-events/magnetra-ro-it-12-20261021.md` și conține marker `[magnetra-ro-it-12-publish-20261021]` declanșează workflow-ul numai după CI. Preflight fail-closed pe starea `6dadc612-9660-4195-aeed-cdb658b22cf8@100% / 9bbb227f-7f2a-4a9b-acac-ce8cae620c51@0%` și hash live app.js `85969467f08d21ee`. Urmează upload imutabil `--keep-vars`, verificare a JS/CSS/HTML **și i18n.js**, catalog 46 și 3 bindinguri, 0% staging → 5% canary → 100%, 6dad păstrat la 0% pentru rollback. Nu folosi workflow-urile de publicare vechi.

**IMPORTANT:** Faptul că pregătim workflow și că trece CI NU înseamnă publicare. Numai un run de release efectiv cu `PRODUCTION_100_PASS` și verificări de versiune justifică statusul LIVE.

---


## 2026-10-21 — 12 SOURCES VISIBLE, 34 USER-HIDDEN + ONLY ROMANIAN/ITALIAN

Owner specified **15 more original indexers to hide** (retaining original adapters/API IDs): BangumiMoe `bangumimoe`, Btsow `btsow`, Dmhy `dmhy`, LinuxTracker `linuxtracker`, MyPornClub `mypornclub`, NekoBT `nekobt`, Sukebei `sukebeinyaa`, YTS `ytsmx`, AniLibria `anilibria`, BlueRoms `blueroms`, EpubLibre `epublibre`, MegaPeer `megapeer`, Rutor `rutorinfo`, XXXTracker `xxxtracker`, FitGirl Repacks `fitgirlrepacks`. With 19 previously hidden, **34 hidden, 12 selectable**, BTDigg/Torrent9/OxTorrent prioritized; default selection BTDigg plus backup sources. Hidden IDs must not appear in PWA picker, legacy localStorage selections, select-all, alternatives or errors. Original 46 backend/Android adapters remain unchanged.

Owner requested PWA interface **only Romanian (default) and Italian**, select RO/IT from header, persist chosen language in browser storage, no external translation APIs. Static and dynamic text/notifications/Flud pairing/error categories localize. Historical source audit labels, user-visible `TEST`/developer-diagnostic text, old 46-provider debugging summaries and misleading EZTV help removed from public UI. Actual CI tests and safe error reporting remain; no API/Flud/Worker backend changes.

Code branch `ui/magnetra-ro-it-curated-12-20261021`, UI `web/app.js`, `web/index.html`, new offline `web/i18n.js`, `web/manifest.webmanifest`, `web/sw.js`, tests `worker/test/ro-it-localization.test.mjs`, `worker/test/indexer-curation.test.mjs`, invariants and checkpoint. **Do not confuse branch/PR with live Cloudflare publication**. Latest *proven* prior live split `6dadc612-9660-4195-aeed-cdb658b22cf8@100` with `9bbb227f-7f2a-4a9b-acac-ce8cae620c51@0`. Any new deployment needs own exact gated version upload / immutable override static integrity checks including `i18n.js` / 0%, 5%, 100% release and guarded rollback, with no secrets shown, no Rock64/Flud/Tunnel changes. No new costs.

---

## 21 OCTOMBRIE 2026 — ANIMETOSHO / MIKAN ASCUNSE, 27 SELECTABILE: RELEASE FINAL CONFIRMAT

**Stare nouă, autoritativă:** [GitHub Actions #39619753243](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39619753243), `SUCCESS`, activat prin commit `f1a09311e76bb241fd8c8bb28d144d474549f5d7`. Versiunea imutabilă `6dadc612-9660-4195-aeed-cdb658b22cf8@100%` este noua producție; `9bbb227f-7f2a-4a9b-acac-ce8cae620c51@0%` rămâne rollback. **Nu considerați 9bbb@100 sau statusul primei tentative drept actual**. Prima lansare #39610721257 a eșuat pe HTML postflight și a revenit corect la 9bbb@100/6dad@0; reluarea reușită din #39619753243 este verdictul ulterior.

Dovezi log final live: `RESUME_PREFLIGHT_PASS: 9bbb100 / 6dad0`, `RESUME_STAGED_SOURCE_PASS`, `RESUME_CANARY_PASS`, `RESUME_FULL_100`, `REVIEWED_ASSET_PASS /app.js sha=85969467f08d21ee`, `/styles.css sha=1c7080d499b00207`, `REVIEWED_HTML_PASS EXACT_PLUS_CLOUDFLARE_BEACON source_sha=717d75204dafdc9e`, `ORIGINAL_PROVIDER_CATALOG_PASS:46`, `RESUME_CURATED_PUBLIC_PASS: 6dad100/9bbb0`. Testele CI 4/4 PASS, rollback disponibil, nu s-a făcut upload nou și nu s-a modificat Rock64, DNS, Tunnel, tokenuri, API provideri sau Flud.

**PWA acum publicat:** 19 indexere ascunse complet din picker, bulk, selecții persistente, paused și mesajul `indexers unavailable`: sunt incluse AnimeTosho (`animetosho`) și Mikan (`mikanproject`). Sunt 27 selectabile, BTDigg/Torrent9/OxTorrent primele, BTDigg implicit selectat cu surse backup; toate 46 adaptoare încă în cod/API și Android. Avertismentul rămâne vizibil pentru erorile surselor încă selectabile. **Acceptarea vizuală pe iPhone a noului selector încă așteaptă confirmarea proprietarului**, distinct de postflight Cloudflare confirmat.

---


## 2026-10-21 — 27-PICKER INITIAL FULL RELEASE STOPPED; VERIFIED ROLLBACK; BOUNDED RESUME READY

Initial launch [run #39610721257](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39610721257) FAILED on unversioned HTML postflight immediately after 100% promotion, **not** at source code build, JS, CSS or catalog. New immutable version **`6dadc612-9660-4195-aeed-cdb658b22cf8`** uploaded with all 3 correct bindings. At 0% and 5%, reviewed JS `85969467f08d21ee`, CSS `1c7080d499b00207`, HTML source `717d75204dafdc9e` (Cloudflare beacon allowed), provider catalog 46, all PASS. Immediately after 100% JS/CSS PASS then HTML NOT VERIFIED. Safe rollback output `ROLLBACK_POSTFLIGHT_PASS` verified **actual target `9bbb227f…@100% / 6dadc612…@0%`** in guard code; inherited print text `c86c100` was stale/wrong and has been corrected in source. Do NOT claim new 27-picker live while rollback remains.

Prepared **version-only resume** (no new upload) `scripts/resume_magnetra_hide_anime_mikan.py`; if owner-action workflow finds exactly `9bbb@100/6dad@0`, verify both 3 binding types and candidate JS/CSS/HTML+46 provider catalog via immutable override GET, move to 5% and then 100%. For final public `/index.html`-equivalent root HTML, allow bounded wait **only for valid HTTP 200 HTML SHA/beacon mismatch**, checking no concurrent Cloudflare deployment and sleeping 8s, up to 5 waits. Other failures, 429/504, network errors NEVER retried. A failed known-state canary/full resumes safe rollback to 9bbb@100/6dad@0; unknown split aborts without destructive writes. Guard workflow `.github/workflows/magnetra-resume-anime-mikan-one-shot.yml` triggers only after future explicit unique approval marker `[magnetra-resume-anime-mikan-20261021]` and file `docs/release-events/resume-anime-mikan-20261021.md` on main. No Rock64, Tunnel, Flud, DNS, providers or secret mutation.

**Status:** initial first release FAILED + rollback PASS; resume PR pending, not executed; iPhone visual acceptance pending. Never repeatedly rerun old upload job.

---


## 2026-10-21 — PREPARED SAFE DEPLOY FOR 27-VISIBLE CURATED INDEXERS (pending)

The owner requested hiding AnimeTosho and Mikan as well as the earlier 17 problematic sources, bringing the PWA to 27 visible / 19 hidden, all original 46 Worker adapter IDs retained. The PWA errors banner filters hidden sources, but continues showing real failures from still-selectable providers.

Prepared a separate one-shot immutable Cloudflare release guard: `scripts/release_magnetra_hide_anime_mikan.py`, workflow `.github/workflows/magnetra-hide-anime-mikan-one-shot.yml` gated by a future **new activation-only** push to `docs/release-events/hide-anime-mikan-20261021.md` and exact marker `[magnetra-hide-anime-mikan-publish-20261021]`. Release must start from exact verified split `9bbb227f...@100%` / `c86c9a32...@0%`, verify live old JS SHA prefix `0945914b2f7bf266`, both existing binding name/types, original domain/ASSETS, then immutable upload with `--keep-vars`, 0% version-override JS/CSS/HTML SHA, catalog 46, canary 5%, full 100% only after checks. Previous 9bbb version retained at 0% as rollback. No Worker backend or Rock64/Flud changes. No torrent search during release.

**Unmerged deployment source or GitHub PR is not a live release.** Wait for 4/4 CI and activation workflow result and hash postflight. If an unexpected traffic split or SHA is found, STOP without blind retries.

---


## 21 OCTOMBRIE 2026 — EXTINDERE PWA CURATION: AnimeTosho și Mikan

Utilizatorul a cerut ascunderea suplimentară a indexerelor **AnimeTosho** (ID `animetosho`) și **Mikan** (ID `mikanproject`), după erori reale observate pe iPhone. Sunt ascunse împreună cu cele 17 surse de dinainte: **19 ascunse și 27 vizibile** în PWA. Nu se șterg adaptoarele: catalogul original de **46** indexere rămâne în Worker/Android. BTDigg, Torrent9 și OxTorrent rămân prioritare; BTDigg păstrează selecția implicită și fallback-urile existente.

Filtrare inclusiv a selecțiilor vechi și a pauzelor persistate, comenzilor bulk, fallback-ului și avertismentului `indexers unavailable`; dacă doar cele două surse ascunse ar fi eșuat, panoul de avertizare nu apare. Avertismentul rămâne legitim pentru eventuale *alte* surse vizibile cu erori; nu se ascund defecțiuni reale ale BTDigg. Nu există bypass de reclame/CAPTCHA, requesturi agresive, descărcări sau modificări Flud.

**Publicarea e separată de commit:** producția anterioară verificată era `9bbb227f-7f2a-4a9b-acac-ce8cae620c51@100%`, rollback `c86c9a32-31fd-4952-86ed-b35f1763b342@0%`, după run `39605883294`. O nouă lansare sigură trebuie să păstreze aceste versiuni exacte ca bază și să confirme din nou calea completă 0% → 5% → 100%, fără reutilizarea workflow-ului vechi legat de c86c.

---


## 21 OCTOMBRIE 2026 — CURATED PICKER PUBLICAT: CLOUDflare 100% PASS

**Release efectiv executat:** [GitHub Actions #39605883294](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39605883294), `SUCCESS`, din `main` commit `6a832487dc75cc8694f324dfbb24a9764e503369`. Versiunea nouă Cloudflare `9bbb227f-7f2a-4a9b-acac-ce8cae620c51` la **100%**, versiunea anterioară stabilă `c86c9a32-31fd-4952-86ed-b35f1763b342` la **0% (rollback disponibil)**. Nu mai presupune că c86c@100% este live: aceea e stare istorică. Versiunea 136c a rămas disponibilă în istoricul Cloudflare, nu în actualul split.

**Verificare efectivă prin API și origin:** preflight live c86c100/136c0 și hash public `9998e0130b19ece9` PASS; new version uploaded cu `--keep-vars` și trei bindinguri autentificate nume/tip PASS; 0% stage, 5% canary, 100% full PASS; hash public/override `/app.js` `0945914b2f7bf266`, CSS `1c7080d499b00207`, HTML sursă `9658b96cf24f27f2` cu doar beacon Cloudflare permis PASS; original `/api/providers` încă **46 identități** PASS. Nu s-au făcut interogări torrent, schimbări secrete, Rock64, DNS, Tunnel, Flud sau costuri noi.

**Comportament PWA publicat:** 17 indexere expres numite de proprietar ascunse și ne-selectabile în interfață; 29 vizibile; BTDigg, Torrent9, OxTorrent primele, BTDigg selectat implicit alături de fallback-urile existente pentru instalările noi; selecțiile salvate pe iPhone care conțineau indexere ascunse se filtrează la load. Toate 46 adaptoare Worker/Android intacte. Torrentz este doar ascuns, nu șters. **Acceptarea vizuală pe iPhone a pickerului nou încă nu e confirmată**; solicită o captură cu `Indexers` și `29` vizibile, nu revendica asta ca test de iPhone realizat.

**În continuare:** test iPhone doar Indexers/default și funcționare căutare obișnuită; Flud Companion manual E2E separat, fără auto-download. BTDigg poate rămâne intermitent deși E2E pozitiv pe iPhone a fost raportat explicit de proprietar înainte de acest rollout.

---


## 21 OCTOMBRIE 2026 — PUBLICARE CURATED PICKER AUTORIZATĂ; GATE 0% → 5% → 100% (ÎN PREGĂTIRE)

Utilizatorul a autorizat explicit publicarea pe `index.alexlab.media` a selectorului din PR #109 (17 ascunse, 29 vizibile, BTDigg implicit primul, Torrent9 și OxTorrent prioritare; 46 ID-uri originale păstrate în API). A fost pregătit un **workflow nou, unic, activat exclusiv prin commit-ul marker `[magnetra-curated-publish-20261021]` pe fișierul `docs/release-events/curated-picker-20261021.md`**; merge-ul PR-ului de infrastructură nu publică nimic.

Safety: preflight versiuni c86c@100/136c@0 (doar ultima stare confirmată istoric), hash SHA256 JS live verificat `9998e0130b19ece9`, trei bindinguri nume/tip pentru versiunile vechi/noi, protecție nume/route/assets, upload versiune numai cu `--keep-vars` și verificare exactă la 0% a JS/CSS/HTML Cloudflare beacon și catalog 46; canary 5%, apoi 100% numai dacă toate gates trec. Versiunea c86c rămâne rollback la 0%; rollback automat permis numai din procentaj cunoscut 95/5 sau 0/100, cu verificare. Nu se fac căutări torrent în release, nu se modifică Rock64, tunel, DNS, tokenuri sau Flud.

**Status: publicarea NU este încă dovedită.** Actualizează numai după workflow PASS și controlul live. Un rezultat STOP poate lăsa 0%-slot sau produce rollback; nu declara site-ul actualizat fără dovadă.

---


## 2026-10-21 — OWNER-APPROVED PWA SOURCE CURATION (PR pending; not live until separately published)

Owner asked the iPhone PWA to **hide 17 specific consistently failing indexers so they cannot be seen or selected**, including bulk actions and stale browser saved preferences. UI-only exclusion; **all original 46 adapters and source IDs remain in Worker API and Android**; no provider data is deleted. Names and exact IDs: AniRena=anirena, BT4G=bt4g, BitSearch=bitsearch, Ext=extdotto, Eztv=eztvx, FileMood=filemood, LimeTorrents=limetorrents, Nyaa=nyaasi, 1337x=1337x, TokyoToshokan=tokyotoshokan, TorrentDatabase=torrentdatabase, TorrentDownload=torrentdownloadinfo, TorrentDownloads=torrentdownloads, TorrentKitty=torrentkitty, UIndex=uindex, XXXClub=xxxclub, Torrentz=torrentz. Torrentz remains retained in original code for possible later restoration if genuinely functional. These error observations are not a claim that the websites are permanently offline.

Display first: **BTDigg → Torrent9 → OxTorrent → Knaben → TorrentsCSV → ThePirateBay → Internet Archive**; thereafter other nonhidden original sources sorted by saved audit/session observations. BTDigg already defaults selected for new devices; retain four default backups and existing custom selected visible IDs. Saved hidden IDs are silently removed on load; missing all active IDs falls back to safe defaults. The bulk buttons and error recovery flow cannot resurrect hidden IDs. Picker total becomes **29 selectable of original 46 retained**. Historical 46-entry audit and public API remain unchanged. Never weaken Cloudflare provider redirects, anti-bot protections, source attribution, Flud pairing or BTDigg Rock64.

**Deployment boundary:** This UI feature remains only in branch/PR until 4/4 CI and an explicitly safe Cloudflare rollout with immutable version checks; do not trigger old historical promotion workflows or assume a merge is live. Latest validated previous production split c86c100/136c0; no production update yet proven for this UI change.

---


## UPDATE 21 OCTOMBRIE 2026 — BTDigg ORIGINAL: ROCK64 LOCAL HTTP 200 CU 10 MAGNETURI BTIH CONFIRMAT

**Local Rock64: HTTP 200 confirmat, cu 10 rezultate originale și 10 magneturi BTIH.** După instalarea fizică verificată în PR #107, utilizatorul a rulat o singură dată `sudo python3 /opt/magnetra-btdigg/check-btdigg.py` și a trimis dovada: `Local Rock64 HTTP: 200`, `Real BTDigg search page rows: 10`, `Magnet links found: 10`, `PASS: real BTDigg result HTML reached Rock64 gateway.` Logul **aceluiași proces gateway instalat**: `total_ms=1094`, `dns_ms=430`, `tcp_ms=483` (cumulativ; TCP ≈53 ms), `tls_ms=865` (cumulativ), `open_ms=1013`, `read_ms=80`, `failure=none`, `family=IPv4`. Nu expune tokenuri/IP-uri/magneturi.

**Incidente post-patch, încă reale:** două căutări iPhone au raportat `BTDIGG_SOURCE_TIMEOUT`; jurnalul noului gateway a înregistrat de două ori `failure=tcp_timeout`, `total_ms=3052/3007`, `dns_ms=48/3`, `tcp_ms=null`. Separat, `curl -4` a obținut HTTP 200 în 0.497 s, iar un test Python de conectare TCP prin contul shell a reușit în 50 ms cu un singur IPv4 DNS returnat la momentul respectiv. Acum inclusiv serviciul real, în context `systemd DynamicUser=yes`, a înregistrat HTTP 200 și 10 BTIH. Nu mai există motiv probat pentru schimbarea DNS/IP/IPv6, a limitelor `systemd` sau a transportului TLS; cauza intermitenței nu este încă demonstrată. **Acest PASS unic nu dovedește fiabilitate continuă ori dispariția timeouturilor.**

**Acțiunea următoare, numai pe iPhone:** în https://index.alexlab.media reactivează doar BTDigg în `Indexers` dacă a fost auto-suspendat și efectuează o căutare normală `ubuntu`, lăsând-o să termine, pentru verificare end-to-end browser → Worker → Tunnel → Rock64 → BTDigg. Nu lansa teste repetate agresiv, nu ocoli 429. Capturile precedente cu erorile 3→1 sunt compatibile cu auto-pause, dar validarea separată a listei active pe a doua căutare rămâne de confirmat. Textul UI `about 12 seconds` nu reflectă în mod necesar cele două timeouturi reale TCP de circa 3 s; orice corecție UX separat, fără rollout neaprobat.

**Alte servicii și producția neschimbate:** Cloudflare PWA c86c100 / 136c0 (ultima verificare workflow #39516593949), 46 indexere originale păstrate, Flud transfer manual, fără deploy/restart suplimentar. Istoricul anterior cu „postinstall source search pending” se referă la starea de DINAINTEA acestui test pozitiv.

---


## UPDATE 21 OCTOMBRIE 2026 — CONFIRMAT PRIN SSH: BTDigg Rock64 PATCH INSTALAT

**Instalat pe Rock64: CONFIRMAT.** Proprietarul a executat updaterul `rock64/update-btdigg.sh` din checkout-ul imutabil `9c3930f406078ee744e0473b2093ded9b91cead7` și a furnizat outputul terminalului: `Ran 99 tests in 11.187s — OK`; `PASS: Magnetra gateway responded to authenticated localhost health check.`; `PASS: Magnetra gateway upgraded; existing tunnel and secrets untouched.` Instalarea fizică și pornirea/health local sunt astfel dovedite; NU repeta updaterul.

**Distincție critică:** Nu există încă o căutare reală post-instalare în BTDigg și nici loguri noi DNS/TCP/TLS din procesul actual. Nu declara disponibilitate stabilă sau timeout rezolvat permanent. Următorul pas P0: pe iPhone la https://index.alexlab.media, reactivează *numai BTDigg* în Indexers dacă a fost auto-paused; fă o singură căutare normală până la final și observă rezultatele/erorile BTDigg. Fără loop de retry 429/504. Dacă persistă eroarea, citește o singură intrare sanitizată `btdigg_upstream_timing` din jurnalul dedicat și clasifică faza. P1: confirmă apoi că după o căutare completă indexerele cu erori rămân deselectate la a doua căutare. Nu confunda bannerul de erori al primei căutări cu lista activă pentru a doua.

**Restul neschimbat:** Worker Cloudflare c86c@100% / 136c@0% (ultima confirmare reală run #39516593949), 46 de adaptere originale păstrate, Flud manual și neconfirmat E2E, fără alte redeploy-uri/proiecte/tuneluri/tokenuri modificate. PR #105 și #106 MERGED. Secțiunile istorice cu „instalare neconfirmată” de mai jos descriu starea ÎNAINTE de acest output SSH și sunt depășite.

---



## READ FIRST — CANONICAL CHECKPOINT 21 OCT 2026 ~13:13 CEST: BTDigg PR105 merged; physical Rock64 install UNKNOWN

**FULL MASTER PROMPT to copy into a fresh chat: docs/MAGNETRA_MASTER_PROMPT_2026-10-21.md.** This is the CURRENT handoff, replacing the 2026-10-19 master prompt reference and superseding ALL historical stages below. Historical data is preserved, not deleted.

**GitHub:** https://github.com/Zuzuitu/AlexLab-Magnetra . Last validated CODING baseline main SHA **9c3930f406078ee744e0473b2093ded9b91cead7** — PR **#105** MERGED 2026-10-21 UTC, 4/4 PR CI PASS; after-merge main CI also succeeded (Technical invariants #39545284573, PWA/provider contracts #39545284466, PWA production smoke #39545284514, Android debug #39545284517, Android staging #39545284411). PWA deploy run #39545284540 was intentionally **SKIPPED**. A later docs-only checkpoint merge may change main SHA without changing code; never require clone main SHA=9c3930 after that. For a physical install use git fetch PINNED immutable 9c3930 and guarded update-btdigg.sh.

**PRODUCTION unchanged:** Worker alexlab-magnetra, https://index.alexlab.media, Cloudflare immutable c86c9a32-31fd-4952-86ed-b35f1763b342 **100%** / rollback 136c1425-0070-48db-b995-5708bd35bb75 **0%**. Owner-approved real full deploy and postflight [run #39516593949](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39516593949), verified immutable binding types and reviewed JS/CSS/HTML (Cloudflare Insights script exception). No new Worker deploy for PR105. DO NOT re-run previous Cloudflare promotion workflows.

**User's indexer goal:** keep search results relevant; don't spend endless cycles reviving blocked providers. Authentic 46 original source IDs remain in catalog/code. Existing c86c PWA automatically deselects only sources that emitted genuine errors after each completed, noncancelled search, then saves selections per browser; 0 matches with successful response stays enabled. If every source fails the selection is not emptied. Manual re-check can recover paused sources; BTDigg may need manual re-check after local patch installation. The screenshots' 18 unavailable are an observation from that query, not 18 permanently dead indexers; previous error accordion may remain visible as history. iPhone confirmation across two completed searches of automatic selection remains partially pending. No proxy open, source forgery, CAPTCHA bypass or bulk 429/504 retries.

**BTDigg P0, source patch merged but NOT INSTALLED/NOT PROVEN ON ROCK64.** PR #105 https://github.com/Zuzuitu/AlexLab-Magnetra/pull/105; coding commit immutable **9c3930f406078ee744e0473b2093ded9b91cead7**. Change is ONLY rock64/btdigg_gateway.py, offline tests, invariant checker and README/checkpoint. It replaces urllib upstream fetch with a single IPv4 socket/TCP/TLS to original btdig.com:443, valid CA/SNI, ALPN HTTP/1.1, one original GET, no fallback IP/retry/redirect, bounded 12s target with TCP3/TLS3/HTTP6 stage ceilings. Gateway auth localhost:8796, tunnel, 5s rate protection, 20min RAM result cache and Flud unaffected. Sanitized DNS/TCP/TLS/HTTP-phase timings. This is a targeted change and better diagnostics, NOT proof an intermittently failing source is permanently fixed. Owner has **NOT SENT** the terminal result of the previously proposed update-btdigg.sh action. Do not mark physical deployment successful before output.

**Owner's real evidence:**
- Rock64 journal: failure total_ms=12852 and 12753, open_ms=null, read_ms=null, failure=transport; single success total_ms=5734, open_ms=5654, read_ms=80, failure=none.
- Fixed original HTTPS curl at home: BTDigg source HTTP 200, total 1.134972s; DNS 0.547974s, TCP 0.601254s, TLS 0.892791s, TTFB 1.055795s (cumulative).
- Python DNS/TCP: DNS 0.164s, IPv4 TCP OK 0.056s, IPv6 immediate error; IPv4 is first in DNS. No proof IPv6 itself caused the former timeout.
- One independent public original BTDigg diagnostic [run #39529234338](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39529234338) PASS: 6465ms, 10 raw results, 7 relevant actual BTIH magnets, 0 errors. Intermittent means sometimes fine, sometimes timeout.
- Original service resource controls: 127.0.0.1:8796, dedicated token (never paste), systemd magnetra-btdigg.service, dedicated tunnel. Keep independent of the 8797/8798 gateways and all other AlexLab services.

**NEXT ACTION immediately (no more generic repeated diagnostics):** first ask whether owner ALREADY executed the updater after PR105. If yes, request ONLY sanitized terminal output and verify it. If no, give ONE pinned-checkout + guarded updater block (also in current master prompt) that fetches commit 9c3930f via git fetch --depth=1 origin FULL_SHA into temporary directory, verifies SHA, runs sudo bash [temp]/repo/rock64/update-btdigg.sh. It performs backup, local Python tests, only service restart, authenticated local health, and rollback on failed start. DO NOT use old example of cloning current main and requiring HEAD to equal 9c3930 — docs-only main will have moved. It is NOT a Cloudflare release and does not change Router, DNS, global IPv6, other tunnels, Plex, YouTube, NexaPanel or CalciDatum.

**AFTER INSTALL:** seek PASS: Magnetra gateway upgraded (or already matches source), and optionally check the service is active and sanitized phase logs; perform one natural approved BTDigg source query with no retry on 429/504. If the new failures persist classify dns/tcp/tls/headers/read from stage measurements. Claim success only for observed tests, not permanent future uptime. Re-enable BTDigg checkbox on iPhone if auto-paused. No user action in GitHub required now.

**Known technical caution:** the patch applies per-operation socket deadlines when each phase begins and a 12s remaining budget check; unbounded getaddrinfo or multiple operations can still extend absolute wall-clock. Review only if actual postinstall timeouts remain; do not promise a mathematically enforced hard overall deadline without further measurement. Preserve source/auth security and no aggressive retries.

**Canonical sources:** docs/PROJECT_STATE.md (latest appended 2026-10-21 code checkpoint), this file's newest top section, docs/MAGNETRA_MASTER_PROMPT_2026-10-21.md, config/project-invariants.json, rock64/README.md. Keep old sections below for archaeology only.

---

## READ FIRST: LATEST PRODUCTION 2026-10-21 01:41 CEST — c86c100 / 136c0 SUCCESS

**Most recent actual Cloudflare deployment confirmed by [owner-authenticated manual workflow run #39516593949](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39516593949):** immutable `c86c9a32-31fd-4952-86ed-b35f1763b342@100%` (new auto-pause failing sources PWA) + immutable `136c1425-0070-48db-b995-5708bd35bb75@0%` (known working title relevance PWA rollback). Owner selected `CONFIRM_RESUME_VERIFIED_C86C_100` on reviewed `main` commit `ddd0628c14fb8c226db0350294dc99bc298e002f`. **REAL workflow conclusion SUCCESS**, not just mocked unit tests: immutable 3 bindings checked for both IDs, reviewed staged /app.js SHA prefix `9998e0130b19ece9`, /styles.css `1c7080d499b00207`, source `web/index.html` `6e6e2ca3388a5ce7` verified exactly modulo ONLY known Cloudflare Insights JS injection before `</body>`, ONE version-only deploy 136c0/c86c100, then full unoverridden public asset/postflight confirmation `RESUME_FULL_POSTFLIGHT_PASS`. No re-upload of preexisting immutable c86c, no Rock64/Flud/provider requests. This latest state overrides every older c86c0/136c100 and 136c100/540b0 checkpoint in the file below.

**End user iPhone acceptance still PENDING for client selection logic**, unlike successful backend 100% release. On first fully completed noncancelled iPhone search, already-observed real provider errors cause respective source IDs to be deselected for following searches and selections persist per browser (`magnetra.providers.v1`, `magnetra.paused-indexers.v1`). Cleanly responding providers with 0 titles remain selected; all-fail situation does not empty selections. Status banner identifies number paused. All 46 adapters remain permanently in catalog and can be reenabled manually; no source retries, no CAPTCHA bypass, no background probes, no paid services, no Flud auto-send. Source intermittency, BTDigg 429 and EZTV year-only query still separate. Owner was tired of manual steps and explicitly wanted to keep only sources that work; ask only one completed search, then optionally compare provider count on subsequent search. Do not require any more deployment.

**Rollback** (ONLY upon demonstrated regression and explicit owner action): the same `.github/workflows/magnetra-auto-pause-resume-c86c.yml` with `CONFIRM_RESTORE_136C_FROM_C86C_100`, initial state must still be exactly c86c100/136c0. Never auto rollback. Do not repeat original one-action release that uploaded a candidate and aborted with /index.html redirect: [#39510888059](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39510888059). The temporary fix PR #103 `fix/magnetra-auto-pause-resume-c86c` has been merged and validated, 4/4 CI, main `ddd0628c14fb8c226db0350294dc99bc298e002f`. Next source-only checkpoint PR `docs/auto-pause-c86c-100-production-checkpoint` updates canonical invariants and docs with live 100/0, must wait for all CI; merge intentionally skips PWA deployment. The new c86c version is live regardless of checkpoint PR state.

---

## LATEST 2026-10-20 23:05 UTC — c86c already uploaded/staged 0%; resume, NEVER reupload

**Authoritative live Cloudflare split:** `136c1425-0070-48db-b995-5708bd35bb75@100%` (working relevance PWA) and new `c86c9a32-31fd-4952-86ed-b35f1763b342@0%` (reviewed auto-pause/indexer failure-only PWA), **both immutable with three required bindings**. Original user-dispatched [one-action release #39510888059](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39510888059) concluded **FAILURE** after successful upload and one 0%-slot write; verified candidate `/app.js` SHA prefix 9998e0130b19ece9 and `/styles.css` 1c7080d499b00207. **No 100%-traffic promotion occurred. DO NOT re-run original upload workflow.** 540b is historically stored but no longer present in active pair.

Actual blocker: Cloudflare redirects `/index.html` to `/` (HTTP 307), and dynamically injects Cloudflare Insights/beacon into root HTML before closing body; ordinary SHA cannot match unmodified GitHub `web/index.html`. Authenticated READ ONLY [run #39511274282](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39511274282) classified route/status/versions, and [run #39511936377](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39511936377) proved **reviewed HTML bytes match exactly except known tightly constrained Cloudflare beacon script** at tail (specific `static.cloudflareinsights.com/beacon.min.js`, `data-cf-beacon`, `/cdn-cgi/`, only script tags, bounded length); no other modifications. This is a verified root cause, not a need for new Worker upload, code change to search filters, tunnel or Rock64.

**Next source PR code only** branch `fix/magnetra-auto-pause-resume-c86c`: adds `scripts/cloudflare_html_asset_guard.py`, `scripts/resume_magnetra_auto_pause_c86c.py`, `scripts/test_magnetra_auto_pause_resume.py`, default-CANCEL `.github/workflows/magnetra-auto-pause-resume-c86c.yml`, updated canonical invariants/docs. Exact `136c100/c86c0` and deployment ID guard, immutable source/bindings, real `c86c` override JS/CSS byte SHA, `/` reviewed HTML modulo only Cloudflare Insights. Manual `CONFIRM_RESUME_VERIFIED_C86C_100` then performs ONE Wrangler version-only write `136c0/c86c100`, public JS/CSS/HTML postflight and retains original 136c @0 for strict manual rollback. Separate `CONFIRM_RESTORE_136C_FROM_C86C_100` only from exact known post-promotion split. No Worker uploads in resume, no new source queries, extra 429 retry, torrent operations or Flud. CI must pass 4/4 before PR merge; no automatic deploy. GitHub connector does not expose workflow dispatch; user must choose action from manual workflow after merge (ONLY ONE more manual run).

**User preference:** zero fuss. User's last 136c iPhone search accepted title filtering (182 matches, 163 off-topic excluded) and reported 18 unresponsive sources. New c86c PWA after completed noncancelled search automatically pauses *only genuine error sources* on that browser, preserving clean zero-match responders, keeping fallback when ALL fail and all 46 original adapter identities available for manual re-enable. No permanent source deletion. Do not claim this feature live before full new version postflight and user retest. BTDigg 429, EZTV TV-title year semantics and Flud status remain independent.

See newest appended section of `docs/PROJECT_STATE.md`. All prior 136c100/540b0 “current state” records below are historical, superseded by 136c100/c86c0.

---

## READ FIRST — 2026-10-21 iPhone 136c accepted; auto-pause failed sources SOURCE ONLY

**Owner's intent:** After live iPhone query `the good dinosaur 2015` showed **182 MATCHES, 163 off-topic excluded, 18 unavailable indexers**, user accepted 136c relevance and requested very few manual interventions. If sources are externally blocked/unreliable, keep only working selections. Do NOT permanently delete the 46 adapter identities: a zero-result response to a specific title is not failure. Latest independently verified production still **136c100/540b0**.

**New code:** `fix/magnetra-auto-pause-unavailable-indexers`. In the PWA after a **fully completed non-cancelled search**, auto-pause precisely those selected IDs observed to fail from genuine API/provider or transport errors. Persist reduced IDs locally under `magnetra.providers.v1`, and paused IDs `magnetra.paused-indexers.v1`; display an accessible count under picker. HTTP success with 0 title matches stays active; if all selected fail do NOT silently zero out the list. Manual indexer checkbox and Select all 46 restore any original ID. Session-observed successful providers now preferred for the "Search with available" action instead of hard-coded potentially 429 sources. No new provider call, retry, proxy, anti-CAPTCHA workaround, Worker adapter change, BTIH, BTDigg pacing, Rock64, secret or Flud change.

**One owner-action release prepared, not executed:** `.github/workflows/magnetra-auto-pause-single-action.yml`, default CANCEL, action `CONFIRM_AUTO_PAUSE_SINGLE_ACTION_RELEASE`. Gate starts only from exact current immutable 136c100/540b0, reviews 4 CI checks, uploads a new Cloudflare immutable version, verifies three binding names/types and PWA source bundles in genuine zero-percent slot 136c100/new0, then one guarded version-only promotion to 136c0/new100 and public JS/CSS/HTML SHA check. Old 136c retained 0% rollback; manual restore choice `CONFIRM_AUTO_PAUSE_MANUAL_RESTORE` requires exact new immutable version ID and split. Stop safely on version mismatch, blocked transport, unknown split or races; no repeated version write or source requests. Protected Node UI tests, Python offline deployment tests, config and project state accompany source PR; merge only 4/4 CI green without [deploy-pwa]. GitHub connector cannot dispatch; user needs **one** manual workflow run after merge. Do NOT use generic direct Wrangler deploy to shortcut guarded stages.

**Next:** complete and merge PR, then one manual release. Verify actual Cloudflare traffic and ask owner to complete a search so failed indexers are automatically deselected on the iPhone. Current screenshot 18 unavailable is user-observed, not proof every failing source is permanently dead. BTDigg 429, EZTV title-only semantics and Flud offline separately unresolved. Older entries below are historical.

---

## READ FIRST — ACTUAL LATEST 2026-10-20 21:30 UTC: 136c LIVE 100%; 540b rollback 0%

**PRECEDENCE: this latest entry supersedes ALL historical 95/5, 0% and “not yet dispatched” snapshots below.** Current real Cloudflare Worker `alexlab-magnetra`, production `https://index.alexlab.media`: `136c1425-0070-48db-b995-5708bd35bb75@100%` (title/year relevance fix), `540b3417-f845-47e8-96bd-856ccc9f1350@0%` (guarded rollback retained). User manually triggered full `CONFIRM_RELEVANCE_136C_FULL_100` [GitHub run #39500459736](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39500459736) on reviewed commit `4f12f36e62831f6eb78fc234a7ecd4731fb433f5`. **Real release SUCCESS:** immutable 136c JS sha prefix `ca9c44f311aa00f0`, authentic original Knaben/TorrentsCSV query **89 matched/1 excluded**, Torrent9/OxTorrent/YTS **4 matched/70 excluded** (0 error objects at release preflight), one version-only Wrangler change **540b95/136c5 → 540b0/136c100**, Cloudflare 100% postflight PASS, normal public `app.js` hash PASS. **Do not invoke 95/5 full workflow again**; its initial-state gates should refuse. Prior full run #39495655870 failed PRE-write because Torrent9 and OxTorrent timed out; PR #100 corrected only release gate for truthfully attributed source `TIMEOUT` with a positive match, with no proxy/retry/adapter code changes.

Separate **authenticated read-only, no override, true public production** [run #39500843622](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39500843622) SUCCESS verified exact **136c100/540b0**, all required version binding names/types, public `/app.js` SHA prefix **`ca9c44f311aa00f0` / 28,637 bytes** matched reviewed source; **46 original adapter IDs** registered. Public `the good dinosaur 2015` from five real providers: **93 relevant titles, 71 off-topic original rows excluded, 0 errors**, per-source **Knaben 77, TorrentsCSV 12, Torrent9 0, OxTorrent 0, YTS 4**, all retained rows satisfy query tokens+release year; exact per-source total/provenance verified. Two sources returned no matching titles but no errors *in this test*, not proof of stable health. No BTDigg or EZTV request made during this public acceptance. Full user iPhone new relevance PWA UX is **NOT YET ACCEPTED**; request owner to reload site and retest `the good dinosaur 2015` and see MATCHES/exclusions. Results counts vary by source and time.

Checkpoint follow-up is SOURCE/DOCS ONLY `docs/relevance-136c-full-production-checkpoint`, adding protected canonical `config/project-invariants.json`, `scripts/check-project-invariants.py`, `docs/PROJECT_STATE.md` plus new owner-manual read-only `.github/workflows/verify-relevance-136c-full-public-readonly.yml` / `scripts/verify_relevance_136c_full_public_readonly.py`. Follow 4 CI checks then merge; this must not trigger `[deploy-pwa]` or change any Cloudflare traffic. For any genuine future regression, guarded **manual** choice `CONFIRM_RESTORE_540B_FROM_136C_FULL_100` in `.github/workflows/magnetra-relevance-136c-full-100.yml` requires exact 136c100/540b0 to restore known state 540b100/136c0; **no auto rollback**.

Next engineering priorities separate from relevance: source availability 19–21 user-screenshot indexer errors, BTDigg intermittent 429/timeouts (origin/rate-limits on 8796), EZTV title/IMDb semantics (year 2026 alone zero results), iPhone Flud Companion unavailable. Preserve no extra retry after 429/504, no CAPTCHA bypass or generic proxy, all 46 authentic indexer IDs, original BTIH magnets, manual Flud send, no paid service or Rock64 high-memory changes. See latest `docs/PROJECT_STATE.md` appended section for full references. When discussing successful release, distinguish 5 validated providers from entire provider uptime.

---

## LATEST 2026-10-20 22:55 Rome — FULL 136c PROMOTION ABORTED BEFORE ANY WRITE

**Actual live state remains `540b@95%` / `136c@5%`.** Owner launched `CONFIRM_RELEVANCE_136C_FULL_100` in [run #39495655870](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39495655870); result **FAILURE**, no `RELEVANCE_FULL_APPLY_ONCE` in live step, hence NO Cloudflare deployment or 100% release. Authentic 136c JS SHA `ca9c44f311aa00f0`, and live original Knaben/TorrentsCSV 89 matching/1 excluded/0 errors passed. Screenshot-source group aborted. Authenticated READ ONLY diagnostic [#39496009852](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39496009852) confirmed live 95/5, **Torrent9 TIMEOUT, OxTorrent TIMEOUT, YTS 4 valid matches**, 2 actual source errors, 0 leaked off-topic titles. No retry or Worker writes. Root cause of release abort is **flaky provider availability conflated with relevance correctness**, NOT a demonstrated search filter failure. Separate network/Rock64 uptime issues remain.

Source-only branch `fix/relevance-full-timeout-isolation` adjusts full-release screenshot-source gate to allow ONLY truthful, attributed `TIMEOUT` errors with `stats.ok=false`/zero counts **while at least one other original provider supplies a real matching release**, preserving names/metadata/errors, validating all source counts and year/title terms. Fail closed for unknown error code (including 429), forged counts, all provider failures, off-topic rows, unknown version IDs, deployment race or JS hash mismatch. No additional provider calls, no retries, no PWA/code change and no deploy. Offline positive/negative tests added, checkpoint updated. **Next:** PR -> four CI PASS -> merge source code only; user triggers the EXISTING manual `.github/workflows/magnetra-relevance-136c-full-100.yml` choice `CONFIRM_RELEVANCE_136C_FULL_100` once after merge; verify live 136c100/540b0 and ordinary iPhone search. Never rerun outdated branch or old 249d/540b release workflow. 540b kept as separate manual restore at 0% on successful promotion.

---

## LATEST checkpoint 2026-10-20 ~21:30 Rome — 136c@5% LIVE; guarded full release prepared only

Confirmed actual owner-triggered [canary #39482838883](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39482838883) **SUCCESS**: production Cloudflare `540b3417-f845-47e8-96bd-856ccc9f1350@95%` (safe older) / `136c1425-0070-48db-b995-5708bd35bb75@5%` (new relevance). New `web/app.js` SHA prefix `ca9c44f311aa00f0`; 3 version bindings validated. Independent authenticated READ ONLY post-canary [#39484084015](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39484084015) PASS: exact deployed 95/5; 46 adapter IDs; five original providers queried once for `the good dinosaur 2015` with immutable 136c override: Knaben+TorrentsCSV **89 matching/1 off-topic excluded/0 errors**, Torrent9+OxTorrent+YTS **4 matching/70 excluded/0 errors**. All accepted titles genuinely match `good` + `dinosaur` + `2015`, and counters are truthful. NOT a test of all 46 provider live health, and NOT owner iPhone new filter UX acceptance.

The next new code is `feat/relevance-136c-full-100-manual`: manual workflow `.github/workflows/magnetra-relevance-136c-full-100.yml`, explicit choice `CONFIRM_RELEVANCE_136C_FULL_100` (default CANCEL), guarded 540b95/136c5 -> **540b0/136c100**, two full immutable binding/JS checks, **one authentic original query per five providers**, no 429 retry, stable Cloudflare deployment identity and single pinned version-only deploy; bounded metadata plus public static asset hash verification to tolerate short edge-cache lag without a second deploy. Separate choice `CONFIRM_RESTORE_540B_FROM_136C_FULL_100` restores 540b100/136c0 ONLY from exact known full 100 state. Both workflows use existing `magnetra-production-traffic-change` concurrency. No automatic deployment on merge. **At this checkpoint this workflow is not merged, approved, dispatched, or executed**; wait for PR four CI PASS then merge source; human manual GitHub dispatch required due to connector limitation. Do not tell user site is already fully fixed. After actual promotion, inspect genuine Cloudflare live 0/100 and test ordinary public iPhone query.

Older 249d is stored only, not in active two-version split. Do not reuse historical a9df/249d/540b release workflows. Preserve 46 identities, original source provenance, magnet BTIH and manual Flud, no paid services, no generic proxy/CAPTCHA/rate-limit bypass. BTDigg intermittent 429 and 19–21 separate source errors, EZTV show-title behavior, Flud Companion connection unavailable are unrelated. Canonical full explanation at very end of `docs/PROJECT_STATE.md`, newest entry.

---

## LATEST 20 OCT 2026 evening — Verified 136c0 genuine relevance, prepare manual 5% canary

**LIVE cloudflare distribution:** `540b3417-f845-47e8-96bd-856ccc9f1350@100%` and `136c1425-0070-48db-b995-5708bd35bb75@0%`. The prior 249d is still immutable/stored but not in active version pair. Owner manually dispatched [slot #39475416019](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39475416019); Cloudflare 100/0 postflight PASS but workflow finished FAILURE at immediate 136c public JS SHA mismatch; **do not repeat the slot write**. Two independent authenticated READ ONLY diagnostics then PASS, no other deployment: [#39475837891](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39475837891) and [#39476148621](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39476148621). New 136c source JS SHA prefix **ca9c44f311aa00f0** 28,637 bytes; old 540b/public **6fe7ac5e60ab9f72** 28,097 bytes; 136c override and cache-busted request exactly match `web/app.js`. One-shot owner query `the good dinosaur 2015`: Knaben + TorrentsCSV **89 relevant / 1 excluded / 0 errors**, and Torrent9 + OxTorrent + YTS **4 relevant / 70 off-topic excluded / 0 errors**. Both E2E PASS with genuine source attribution and title/year gate. This is NOT proof all 46 providers are healthy and not full 100% release.

**Next manual option PREPARED IN CODE, NOT EXECUTED:** `feat/relevance-136c-5-percent-canary` and its reviewed PR (check latest main) add `.github/workflows/magnetra-relevance-136c-canary-5.yml`. Only after four CI PASS and merge can user select `CONFIRM_RELEVANCE_136C_CANARY_5` to set exact `540b95/136c5`. Default `CANCEL`, production-traffic-change concurrency lock, exact immutable version/3 binding/asset SHA/starting deployment gates and ONE Wrangler write with bounded metadata verification. Separate option `CONFIRM_RESTORE_540B100_136C0` is explicit/manual known-state rollback only. No automatic release or rollback from PR merge; no BTDigg/EZTV, ads, proxy, source retries, Flud or Rock64 modifications. **No full 136c@100 workflow yet.** After canary, live postflight + iPhone query and safe 100% promotion planning. See newest `docs/PROJECT_STATE.md`.

---

## LATEST 2026-10-20 17:44 Europe/Rome — relevance fix version 136c STAGED, NO DEPLOY

**Live Cloudflare remains `540b3417-f845-47e8-96bd-856ccc9f1350@100%` / `249d6767-f4dc-4f4d-bbf7-f57bea2e5554@0%`.** Previously merged screenshot-driven query title/year filter PR #96, main commit `83e1659538e037a12f4bf8044d2cb52f89e72d7f`, all four CI PASS. User launched stage workflow [#39450609144](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39450609144) SUCCESS. Authentic immutable version ID **`136c1425-0070-48db-b995-5708bd35bb75`** uploaded (3 static assets). Separate authenticated read-only Cloudflare [#39451169718](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39451169718) PASS for exact version+all three binding names/types and unchanged live split. Attempted staged /app.js override was **NOT_MATCHED_OR_NOT_ROUTABLE**, because 136c is NOT in deployed version pair. Never report staged E2E passed.

Manual-only 0% slot + bounded exact-source E2E prepared in `feat/relevance-136c-zero-slot-e2e`: workflow `.github/workflows/magnetra-relevance-136c-zero-slot.yml` default `CANCEL`, explicit action `CONFIRM_540B100_136C0_SLOT_AND_READONLY_E2E`, script `scripts/deploy_magnetra_relevance_136c_slot.py` with tests. After PR+four CI PASS and merge, owner can manually choose action. Exact starting split 540b100/249d0 required; guarded one version-only deploy to **540b100/136c0** (old 249d remains stored). Then version-specific `app.js` SHA, catalog 46 and one `the good dinosaur 2015` Knaben/TorrentsCSV public search verifies only matching release titles and source-truthful counts; provider errors/inconclusive zero not hidden. No BTDigg/EZTV requests, Flud, auto retries, tunnel, Rock64, costs. No traffic to 136c users at 0%. Do NOT use old 249d/540b workflows for promotion or rollback. 136c production full promotion is **NOT prepared or executed**; keep 540b for safe rollback once this new slot validates. Code PR merge alone must skip deploy.

---

## NEWEST ENGINEERING TASK — 2026-10-20 iPhone OFF-TOPIC RESULTS (FIX STAGED, NOT DEPLOYED)

Owner searched `the good dinosaur 2015` with all **46** indexers selected, PWA reported **345 results** plus 19–21 unavailable indexers; screenshots show unrelated `Knock Knock (2015)`, `The Hateful Eight (2015)`, and `Good Luck Have Fun Don't Die (2026)` among genuinely matching original release titles. Main code bug confirmed: Worker merged `found` rows into public JSON without checking title relevance; PWA sorted these misleading entries by seeder count. The new guarded fix branch `fix/magnetra-query-relevance-guard` adds `worker/src/query-relevance.mjs` and end-to-end tests so *all 46* sources are subject to a conservative Unicode-token/all-terms/year-in-title gate. Exact IMDb and BTIH hash queries remain supported. API reports matching `total`/`stats` and separately `excludedOffTopic` without confusing off-topic rows with source failures; PWA shows `MATCHES` and explanatory excluded count. No source substitution, extra request, automatic retry, restart, Flud sends, or change to 46 providers. All changes are SOURCE ONLY pending branch → PR → four CI PASS → merge → separately guarded new Cloudflare version upload and release. Prior verified production **540b 100%** stays active until separately authenticated deployment. DO NOT claim this patch already fixed the live iPhone. Check `docs/PROJECT_STATE.md` newest section for exact evidence, limitations and test fixtures. BTDigg intermittence, EZTV year semantics, other provider errors and Flud unavailable are separate.

---

## READ FIRST — LATEST VERIFIED 2026-10-20 00:56 EUROPE/ROME: 540b LIVE 100%, PUBLIC RESOLVE PASS

**This section supersedes the older READ FIRST 540b@5% paragraph and every historical deploy snapshot below.** Latest authenticated production and GitHub code supersede even this observation. Main repository: `Zuzuitu/AlexLab-Magnetra`, site `https://index.alexlab.media`.

**Confirmed Cloudflare version split:** fix `540b3417-f845-47e8-96bd-856ccc9f1350` serves **100%**, previous `249d6767-f4dc-4f4d-bbf7-f57bea2e5554` retained at **0%** as guarded manual rollback slot. Owner explicitly approved 100% on 20 October 2026. Reviewed PR #94 merged at `d819a54704df139e6a1a500b957ce22f97e3b8d5`, all four PR and main CI checks passed, default PWA deploy skipped. Owner dispatched `CONFIRM_PROMOTE_FIX_540B_100` in [run #39337836125](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39337836125). Version-only Cloudflare write **took effect**, but release workflow concluded **FAILURE** at first public `/app.js` hash check; do not falsely report that run SUCCESS. No auto-rollback or second deploy.

**Separate later genuine LIVE verification:** read-only [run #39338307381](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39338307381), job `118353253206`, ended **SUCCESS**. Verified exact 249d0/540b100 live deployment, fixed `web/app.js` local SHA256 prefix `6fe7ac5e60ab9f72` and 28,097 bytes identical to both 540b override, normal public `/app.js` and cache-busted public `/app.js`; old 249d override differed, prefix `80fead40b472e563` and 27,644 bytes. HTTP edge reported `CF-Cache-Status: HIT`. The earlier public mismatch had disappeared **without another Cloudflare write**. Temporary asset propagation/cache is plausible, physical cause NOT proven. PUBLIC no-override catalog **46 original IDs** and real **OxTorrent 50 + Torrent9 20** original unresolved canonical results, and a successful redacted BTIH **/api/resolve for each provider** were confirmed. This does not prove all 46 source providers healthy.

**New release guard:** `scripts/deploy_magnetra_fix_full_100.py` has bounded read-only retries **only** for HTTP-200 static `app.js` hash mismatch, never retries 429/504/provider requests or deploys again; CI offline tests. `.github/workflows/magnetra-public-postflight-diagnostic.yml` is **manual read-only**, executes `scripts/diagnose_magnetra_public_postflight.py` without Cloudflare writes. Current checkpoint is canonical in `docs/PROJECT_STATE.md` and `config/project-invariants.json`. Older a9df/249d release workflow must NOT be used to promote 540b; 540b is already 100%. The existing full 100% workflow would fail closed if the starting 95/5 split is no longer present; use a separately approved rollback only if a genuine regression requires it.

**Pending:** owner's actual iPhone Resolve button UX is still **NOT VERIFIED by user**. BTDigg intermittent 429/`BTDIGG_SOURCE_TIMEOUT` remains independent unsolved P0, and no BTDigg/EZTV request or Rock64 change was made in the 100% postflight. Preserve 46 identities, exact original provenance, free cost limits, restricted routes/secrets, and manual Flud Companion integration. Do not accidentally push `[deploy-pwa]` on checkpoint merge. Branch → PR → 4 CI → merge; no direct main.

---


## READ FIRST — LATEST VERIFIED 2026-10-19 23:00 EUROPE/ROME: RESOLVE FIX LIVE 5%, NOT 100%

**Supersedes older chronological READ FIRST/checkpoint snapshots below, which are historical and NOT current deployment instructions.** GitHub `main`, live Cloudflare deployment and full current checkpoint `docs/PROJECT_STATE.md` are canonical. Complete copy-ready Senior/Staff prompt: **[`docs/MAGNETRA_MASTER_PROMPT_2026-10-19.md`](MAGNETRA_MASTER_PROMPT_2026-10-19.md)**. Verified `main` immediately BEFORE this docs PR: `10818d487facbcf1ba66d7f92322926e9b76508a`; refetch after merge.

**Current EXACT Cloudflare Worker pair:** previous `249d6767-f4dc-4f4d-bbf7-f57bea2e5554` at **95% traffic**, new fixed `540b3417-f845-47e8-96bd-856ccc9f1350` at **5% traffic**. Uploaded by [run #39298077357](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39298077357); 3 binding names/types `BTDIGG_GATEWAY_TOKEN`, `MAGNETRA_GATEWAY_TOKEN`, `ASSETS` verified [run #39303873161](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39303873161); zero-slot created [#39310908577](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39310908577), source/asset E2E at 0% passed [#39311804881](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39311804881). **Owner-approved 5%-canary REAL deployment [#39323736403](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39323736403) ended `CANARY_POSTFLIGHT_PASS: old 249d 95%, fix 540b 5%`.** The separate read-only **LIVE** canary E2E [#39324007635](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39324007635) ended `FIX_540B_CANARY_E2E: PASS`: exact old-vs-new PWA `app.js` versions distinguished by immutable version override, new fixed assets match reviewed GitHub source while old differs; 46/46 provider IDs, OxTorrent **50** + Torrent9 **20** authentic `2026` search results, original deferred BTIH magnet successfully resolved for one card from each provider; Cloudflare 95/5 unchanged at postflight. Offline unit fixture 1+1 lines in log are not the genuine source sample. No BTDigg/EZTV requests, Flud magnet transmissions, downloads, or automatic replay.

**Proven failure and fix:** On iPhone search `2026`, all 70 OxTorrent/Torrent9 results produced `Noncanonical source HTML route refused` because `web/app.js` chose `magnetSource || details`. Real field audit [#39286786842](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39286786842) found `magnetSource` noncanonical in **70/70**, `details` canonical **70/70**, original magnets BTIH valid per source. PR #89 fixed `ensureMagnet` to use exclusively source-owned canonical `item.details` for ONLY these two indexers; keeps all other 44 providers' precedence, original provenance, strict origin/path allowlists, and automatic Flud sending disabled. New fix is available to **only 5% ordinary users**, so random iPhone request may hit old 249d and still fail; no iPhone end-user acceptance confirmed.

**Full promotion to 100% is PREPARED ONLY IN THE GUARDED CODE/PR; NOT APPROVED OR EXECUTED.** The new `.github/workflows/magnetra-resolve-fix-full-100.yml` and scripts/tests are prepared via `feat/magnetra-540b-manual-100-promotion` for PR+CI review, with no deployment. The future `CONFIRM_PROMOTE_FIX_540B_100` manual-only action would change exactly 249d95/540b5 to 249d0/540b100 only after immutable version/binding+asset proof and bounded original-source E2E. Separate `CONFIRM_RESTORE_249D_FROM_FIX_540B_100` would restore 249d100/540b0 from exact promoted slot; default `CANCEL` makes no network calls. Actual owner consent, 100% activation and iPhone acceptance remain FALSE. The existing `magnetra-resolve-fix-canary-5.yml` supports `CONFIRM_RESTORE_249D_100` for an exact known 95/5 rollback; its rollback path was offline-tested, not executed live. Historical `release-magnetra-candidate-100.yml` hardcodes a9df/249d and **must not** be used to promote new 540b. Immediate new chat task: verify current state again, PREPARE via branch/PR/tests a manual-only exact `249d@95,540b@5` -> `249d@0,540b@100` workflow with explicit owner consent, immutable binding/assets and race/postflight gates, guarded rollback. **Never dispatch a traffic change without a new explicit approval.** After authorized promotion verify real logs/versions/catalog/magnets and real iPhone Resolve on both sources.

**BTDigg separate P0 still open:** iPhone `RATE_LIMIT` / HTTP 429 observed, provenance local 8796 five-second throttle vs original source HTTP 429 unproven. Historical `BTDIGG_SOURCE_TIMEOUT` / 504 (~12 seconds) and second iPhone search after approximately one minute returning results also remain true, as does BTDigg differential 10 genuine results for each version in [run #39134428856](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39134428856). No permanent fix demonstrated. Rock64 original-only `btdig.com`, 8796, min gap 5s, 12s upstream timeout, singleflight, 20min success-only RAM cache max 4 entries / 6MB; 16s Worker transport timeout; 5500ms frontend gap. Separate `READ_ONLY_ROCK64_DNS_TCP_TLS_TTFB_BODY_TIMING` only after owner approval. DO NOT retry 429, open arbitrary proxy, change DNS/tunnels/systemd/other Rock64 services or re-label other indexers as BTDigg.

**Project architecture:** `app/` original Kotlin upstream; `web/` iOS/Android PWA; `worker/` Cloudflare Worker `alexlab-magnetra` with 46 upstream indexer IDs, three private bindings, fixed HTTPS host allowlists; Rock64 **BTDigg 8796**, **EZTV 8797**, **shared Magnetra dispatcher 8798** (`eztvx,oxtorrent,torrent9` only); Flud Companion separately relayed by fixed `https://flud-remote.alexlab.media` only upon explicit user action. Free tier, unapproved recurring spend €0, no secrets/keys/private DNS changes, no 46/46 live availability claims. Historic complete 46-provider audit 13 Oct #38373699387 was 13 results / 12 zero/unverified / 21 errors, not today's uptime.

**Release contract:** AGENTS.md first, read latest real code and GitHub Actions; branch → PR → 4 CI groups green → merge; no direct main. `Deploy Magnetra PWA` must remain SKIPPED for checkpoint/code-source PR unless separately approved, and DO NOT include `[deploy-pwa]` marker in commit. New owner approved canary run does NOT authorize 100% promotion. Never deploy via old ID-hardened workflow, never send magnets automatically to Flud, no paid service or deletion of indexers.

**Next:** Prepare controlled exact 540b 100% promotion (not execute) after verifying canary 95/5; separate BTDigg 429 provenance analysis after release. The full master prompt contains the complete engineering plan, constraints, proof run IDs and rollback.

---


_Historical synchronization record from 2026-10-12 (sha `8969b9fe6758f859ac072bea984a5f9c9c59597f`). **Superseded by 2026-10-19 current checkpoint above**. Always refetch GitHub main._

## HISTORICAL snapshot — superseded 2026-10-12 operational state (DO NOT follow as current)

**Never reopen the rejected BTDigg Safari/bookmarklet/clipboard flow.** The owner wants genuine **automatic** BTDigg results when searching *inside* Magnetra. Any manual BTDigg import UI was intentionally deleted by PR #19. Generic paste-magnet → Flud remains. Preserve the original 46 providers and Flud Companion; changes must be BTDigg-only. Never disguise independent DHT results, Bitmagnet, Knaben or another index as BTDigg; no new costs, proxies or CAPTCHA/rate-limit bypass.

**GitHub vs production are different revisions:**
- **GitHub main verified before handoff PR:** `8969b9fe6758f859ac072bea984a5f9c9c59597f` (PR #19 merged, BTDigg browser import removed). PR #18 Rock64 optional gateway merged earlier as `2863b3b52ec54b2a882900316ad1c2615ce47c94`. At the last query there were no open PRs. Latest main CI PWA, invariants, Android Debug/Staging and production smoke passed.
- **Latest successfully deployed PWA:** `239098ba3b1ff3b6a7a5a6021e2cdf3553d784d3`, GitHub deploy run `37980229044`, October 9. The newer `8969b9fe...` production deploy was **SKIPPED** (run `38313083432`) because there was no new release marker/explicit approval. This means the hosted website can still show the old rejected bookmark UI even though it no longer exists in main. Do **not** claim its removal is live. The historical 2026-10-09 full production audit in run `37980229044` had **11 results / 12 empty-or-unverified / 23 provider errors / 0 request errors**, and **BTDigg TIMEOUT**. Old snapshots (12/15/19 etc.) do not supersede this last verified complete audit.
- **Rock64 private gateway is SOURCE CODE ONLY, not a running service proven reachable.** Python gateway `rock64/btdigg_gateway.py` listens `127.0.0.1:8796`, allows only real `https://btdig.com/search`; `rock64/install-btdigg.sh` is a guarded installer and `rock64/check-btdigg.py` the genuine source proof. Worker module `worker/src/btdigg-rock64.mjs` uses fixed `https://btdigg-rock64.alexlab.media` and only for BTDigg **if** private Worker secret `BTDIGG_GATEWAY_TOKEN` is configured. No proof the owner's Rock64 headless request returns real BTDigg rows/magnets, no proof of dedicated Cloudflare Tunnel, DNS, active systemd unit, credentials, or Worker-to-Rock64 end-to-end search. **Do not invent one.**
- Owner confirmed that the BTDigg *website* works at home and explicitly approved exploring Rock64 automatic search; this does **not** establish that automated HTTP requests from the Rock64 machine work. SearXNG BTDigg and third-party qBittorrent/Jackett plugins are not verified working APIs; DHTcrawler2 and Bitmagnet index independently and do not satisfy true BTDigg provenance.
- **Next priority:** continue BTDigg-only automatic solution: verify actual Rock64 environment read-only; safely run local gateway one-shot source test, respecting BTDigg limits; only if there is a genuine source result, integrate a **separate** authenticated Cloudflare Tunnel and Worker secret after the owner approves the specific activation/deploy. Avoid disrupting the existing CalciDatum runner, NexaPanel, other cloudflared units, all other indexers and Flud Companion. Never put secrets in chat, logs, frontend or repository. Keep unapproved recurring spend at **€0**. Read `rock64/README.md`.

**Historical note:** Older paragraphs in this handoff that propose or retain a browser/bookmarklet fallback are *historical*, not an instruction to restore it. `docs/PROJECT_STATE.md` consolidated section “Consolidated owner-decision checkpoint — 2026-10-12” is authoritative below actual live code, configuration, and CI.

**Authority order:** current `main` source code + actual GitHub Actions/deploy state → `docs/PROJECT_STATE.md` + `config/project-invariants.json` → this handoff → chat context. If contradicted, **stop material changes and reconcile first**. Historical checkpoints are not live infrastructure/providership telemetry.

## Mission / owner constraints

Continue engineering the existing production torrent metasearch PWA **AlexLab Magnetra**, forked from `prajwalch/TorrentSearch`, preserving its Android implementation and upstream mergeability while providing a fast responsive installable PWA. The owner expects end-to-end Senior/Staff engineer ownership: inspect, implement, test, PR, merge, deploy when authorized, and report measured results, without asking them to verify anything accessible via connected tools. The user speaks Romanian.

**No Lovable. No paid services, API, Cloudflare tier upgrades, proxies, headless-browser subscriptions or cost increases without explicit consent; unapproved recurring €0.** No secrets in chat, GitHub code, public assets, logs or URLs. Never assert 46/46 real-time provider availability merely because 46 adapters are coded.

## Canonical assets and repos

- Main repo: `https://github.com/Zuzuitu/AlexLab-Magnetra`; original upstream: `https://github.com/prajwalch/TorrentSearch`, MIT. Production: **`https://index.alexlab.media`**.
- Flud Companion remote-controlled Android client (separate project): `https://github.com/Zuzuitu/flud-companion`; hosted relay fixed origin **`https://flud-remote.alexlab.media`**. Nvidia Shield runs Flud Companion; physical device/owner pairing is *not accessible to tests*.
- PWA frontend `web/index.html`, `web/styles.css`, `web/app.js`, `web/manifest.webmanifest`, `web/sw.js`, `web/icon.svg`. Static vanilla JS/CSS/HTML; service worker offline shell. Browser-local preferences, bookmarks and pairing via `localStorage`.
- Backend `worker/src/index.mjs`: Cloudflare Worker with `assets` binding, served at `index.alexlab.media`; fixed-source routes. `worker/src/catalog.mjs` all **46 upstream builtin indexers** from `app/src/main/kotlin/com/prajwalch/torrentsearch/di/BuiltinSearchProvidersModule.kt`. `worker/src/providers.mjs`, `html-adapters.mjs`, `legacy-specs.mjs`, `legacy-adapters.mjs`, `request-headers.mjs`, `provider-recovery.mjs`, `source-audit.mjs`.
- API: `GET /api/health`, `GET /api/providers`, `GET /api/search?q=&providers=&category=`, `POST /api/resolve`, `POST /api/companion/status`, `POST /api/companion/magnet`. Worker may NOT become an arbitrary proxy.
- CI: `scripts/check-project-invariants.py`, `worker/test/*.test.mjs`, workerd selector test `worker/test/selectors.worker.mjs` with separate config `worker/test/wrangler-selector.jsonc`, `scripts/check-production-smoke.py`, `scripts/audit-live-providers.py`. Android CI Debug/Staging/Release workflows preserved.
- Deployment: `.github/workflows/deploy-pwa.yml`, `worker/wrangler.jsonc`; only manual `workflow_dispatch` or an explicit **`[deploy-pwa]`** marker on `main` may deploy. GitHub Actions secrets already privately configured: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`. Never demand or expose their values. Docs-only merge must not deploy.

## Verified latest checkpoint

- Last inspected `main` at handoff: `94d2b6b40e4a3ad465f0c39e64fc1df4301f9f87`, PR #9 docs-only, **no open PRs**, all 6 main CI checks green (including Debug + Staging and production smoke). Refresh before any work.
- Latest *actual deployed frontend* commit: **`bd09a0eb60b679e9e661f0dc1f34613605db2838`**, PR #8, successful Cloudflare deployment workflow **37827913584**, post-deploy HTTPS/manifest/health/provider checks green. Later docs-only PR #9 did not deploy.
- All **46** upstream source IDs have executable adapters. Workerd validated **35 HTML selector sets syntactically**; it did not verify that third-party site markup still matches. A source may return HTTP 200 but zero *valid* magnet rows; do not mistake that for confirmed functionality.
- Latest complete benign `ubuntu` source audit, run **37827913584**: **12 with results**, **14 empty/unverified**, **20 upstream provider errors**, 0 API transport failures. Sources with results: `audiobookbay`, `dmhy`, `btsow`, `epublibre`, `internetarchive`, `knaben`, `linuxtracker`, `nonameclub`, `thepiratebay`, `therarbag`, `torrentscsv`, `0magnet`. These same 12 had results in the previous full audit. Do not claim that seeders, magnet resolution or transfer on all 12 are verified.
- `worker/src/source-audit.mjs` deliberately retains historical **37816874771** (`ubuntu`, 2026-10-08 17:29 UTC): **12 results / 12 empty / 22 errors**. It is a timestamped UI reference, **not** the latest audit nor an online-now signal. User can choose **Select last-audit results** (12 tested) versus **Select all 46**, or any individually. Existing selections persist.
- Default indexers for *new* PWA sessions and backend API: **Knaben, TorrentsCSV, The Pirate Bay, Internet Archive**. Do not silently bring rate-limited Nyaa back as default.
- BTDigg exists but is **not automatically usable** through Worker: `btdig.com` and `www.btdig.com` returned HTTP **429** from independent GitHub-hosted probes; Cloudflare Worker reported `TIMEOUT` (6.5-second fast fail). Nyaa `RATE_LIMIT` 429. Other sites return 403 (including anti-bot challenges), 520/530, or origin-limited redirects. Latest TokyoToshokan correctly reports `ACCESS_DENIED` 403, not prior `UNCLASSIFIED`. **Do not defeat CAPTCHA, hammer 429, invent a reliable BTDigg API, or proxy via unrelated sources**.
- Recovery UI displays human-readable typed provider errors, **Open source search** on fixed provider-owned HTTPS URL (not automatic scraping), **Search with available indexers** as a separately and correctly attributed query, and **Paste magnet → Flud** for a manually copied magnet when browser-only sites block the Worker.
- Flud Remote pairing works through Device ID + token or fragment-bearing QR link imported locally; PWA has **Test Shield connection** (read-only), optional Auto-start and `requestId` deduplication. A Relay `202 queued` is NOT a Shield acknowledgement or download. Status `lastResult.id` must match before reporting actual Shield/Bridge acknowledgement; completed torrent download requires separate evidence. **Real iPhone → Remote Relay → Shield/Flud test NOT yet performed.**

## Past bugs and non-negotiable protections

- Android CI needed separate JetBrains Runtime **21** for Gradle daemon, alongside Temurin 17 for Java source/target; upstream minSdk 25/targetSdk 37 and app ID remain untouched.
- GitHub invariants run before protected build/deploy; JBR 21 check must apply only to workflows actually invoking Gradle (not Node-only CI).
- HTML selectors must be checked in dedicated **workerd** test config and validate proper JSON `ok: true`, `checked: 35`, no invalid selectors; an HTTP 200 from PWA index HTML once gave a false positive.
- Swarm fields missing from upstream must remain `null`; `Number(null)` incorrectly displayed zero before regression fix.
- PWA had stale cache-first `alexlab-magnetra-v1` assets: now `alexlab-magnetra-v2` service worker with network-first scripts/styles/manifest, offline shell, never caching `/api/` or pairing token commands. Preserve SW upgrade tests.
- "Select working" previously selected all 46 just because `ported: true`. Corrected in PR #8 with separate dated-audit selection and all-46 selection. Distinguish historical test results from real-time uptime.
- Source fetch UA pinned to upstream Android Chrome 141 UA and only **one HTTPS redirect staying in same origin** allowed; do not enable generic arbitrary URL/cross-origin redirects.
- All decisions that alter invariants must update `docs/PROJECT_STATE.md`, `config/project-invariants.json`, affected code and tests/guard in the **same PR**.
- Strict no-cost, no-Lovable, no-secret rules. Android code/source/upstream history untouched unless explicitly justified. No direct main code changes.

## Prioritized next work (material product work, not mere documentation)

**P0 — establish newest truth and independently measure actual functionality.**
1. Fetch GitHub main PRs/runs/deploy, read `AGENTS.md`, `docs/PROJECT_STATE.md`, `config/project-invariants.json`, `docs/PROVIDER_AVAILABILITY.md` and the implementations.
2. Verify external production endpoints with smoke plus catalog source identities. Decide a minimally invasive test strategy for each provider, and test source-specific parsing on *known benign, lawful media* and fixtures. A `results` state only means a query returned rows; inspect title, source, hash/magnet URI, `details`, size, seed/peer and invalid/duplicate result handling. Never indiscriminately send magnets to the Shield.
3. Triage 20 actual provider error origins (last complete audit), distinguishing real code defects (incorrect URL, selector, resolver, parsing) from 403/429/CAPTCHA/520/530 external blocks. Add provider fixtures and CI. Audit with low concurrency and don't repeatedly poll 429 sites.

**P1 — verify real Companion handoff safely.**
4. Re-check `Zuzuitu/flud-companion` Remote API code (do not assume status schema or Android logic from old chat). Pair PWA using existing owner-local Remote QR; owner can press **Test Shield connection** and report non-secret status only. Verify the result status: queued, online, matching `lastResult.id`, accepted/failed, then actual appearance of **one lawful test torrent** in Flud. Test offline, invalid pairing, Auto-start and duplicate commands. Never collect credentials in chat or automate real magnet sends without the owner's informed test action.

**P2 — improve quality + source failure UX.**
5. For BTDigg, independent validation of 429 means short timeout and direct-source/browser/magnet fallback are implemented, NOT automatic recovery. A truly functional programmatic adapter needs upstream official/allowed API or another owner-approved compliant architecture; don't invent one or spend money. Improve other providers only with evidence; avoid spoofed successes.
6. Polish mobile-first iOS and Android PWA usability, accessibility, scroll/search performance, install/update, share/copy, `.torrent`, bookmark behavior, link safety and browser/localStorage boundaries. Measure, test and ship fixes through PR.

**P3 — release evidence and checkpoint.**
7. Run `python3 scripts/check-project-invariants.py`, `node --test worker/test/*.test.mjs`, JS syntax, Wrangler dry-run and CI Debug/Staging. PR → green CI → merge. Include explicit `[deploy-pwa]` only for an **approved** production release, then run smoke and 46-source audit; compare results with their actual prior runs and preserve source IDs.
8. Update `docs/PROJECT_STATE.md` with any definitive technical decision, regression root cause, external limit and evidence; update config/guards only when critical invariant truly changed. Keep this handoff subordinate to current code/checkpoint.

## Definition of done

The project is NOT 'fully complete' merely because the PWA is online. Progressively demonstrate: stable installable UI and service worker behavior, source-specific correct result/magnet actions, honest per-provider health, safe production deployment, and a **real, owner-confirmed** one-tap magnet appearing on the Nvidia Shield in Flud. For blocked third-party sites, communicate the limitation or safe fallback rather than fabricating 46 live results.

## How to resume in a new chat

1. Connect or use existing GitHub integration for `Zuzuitu/AlexLab-Magnetra`.
2. Confirm fresh `main` and read `AGENTS.md`, `docs/PROJECT_STATE.md`, `config/project-invariants.json`, `docs/PROVIDER_AVAILABILITY.md` and this handoff.
3. Do useful work immediately on a feature/fix branch; don't ask the owner to inspect things the connector can inspect.
4. Deliver actionable result: PR/commit URLs, tests + CI evidence, deployment status if approved, live measurements and remaining external blockers.

## 2026-10-08 follow-up engineering PR #11 (post-checkpoint, pending merge/deployment)

- Fresh repository inspection confirmed `main` `db5e2d58fa9c3af8277878b4c731856272b7996e` and clean open-PR state **before** this work. Five primary main CI checks and production smoke were green. The latest approved deployed PWA remains historical `bd09a0eb60b679e9e661f0dc1f34613605db2838`; a docs-only merge did not publish code.
- PR **https://github.com/Zuzuitu/AlexLab-Magnetra/pull/11** on `fix/pwa-progress-and-companion-idempotency`: eliminates frontend batch head-of-line blocking with a sliding maximum-three search pool, enables cancellation and ignores late responses; prevents repeat-send races and reuses a canonical magnet's `requestId` for 110 seconds. This preserves relay's genuine 120-second duplicate window, verified from the separate Flud Companion source. No physical Shield transfer was attempted.
- Tests added in `worker/test/pwa-interactions.test.mjs` simulate one blocked provider, cancellation with a late reply, and concurrent/repeated send actions. The regression suite caught and repaired a case-insensitive `XT` magnet parameter bug. Source and architectural details are in the final section of `docs/PROJECT_STATE.md`. Confirm latest PR CI, merged SHA and production authorization before declaring this milestone shipped.
- BTDigg Android implementation is byte-for-byte identical to upstream `BTDigg.kt`; URL and CSS selectors match the Worker. Independent 429/Cloudflare timeout evidence still limits automatic availability. The PWA does **not** support upstream's user-configurable Torznab feature; there is no approved arbitrary endpoint proxy/security model.
- **No release permission implied:** merge of ordinary code without `[deploy-pwa]` must not deploy; retain production snapshot **12 results / 14 empty / 20 provider errors** until a new evidenced full audit. Physical Companion confirmation requires an owner-initiated lawful test.

## 2026-10-08 provider API redirect hardening (PR #12)

- Following PR #11's green CI and merge as commit `0d2df80b1002e594981de01e65bc4d26210f912e`, a distinct source audit found the JSON API adapters and Nyaa HTML adapter still implicitly following external redirects. The protected source-origin rule had been enforced in other adapters but was inconsistent here.
- The new PR `fix/provider-api-origin-redirect-guard` changes only `worker/src/providers.mjs` to reuse the already validated one-hop same-origin HTTPS redirect helper. Six targeted tests exercise allowed and disallowed redirects, POST preservation and no rate-limit retry. Check current GitHub PR/CI/merge state before claiming integrated.
- No production deployment, provider audit, external bypass, physical magnet send, or new service was authorized by this hardening. Historical production source audit remains 12 results / 14 unverified / 20 errors.

## 2026-10-09 BTDigg iPhone browser-import release approval

Owner explicitly authorized Cloudflare deployment via `Fa eploy si gata`. Latest merged feature commit immediately before this release request: `3d2b02b6f895373f1284f13334701aafde53f855` (PR #15). The workflow `.github/workflows/deploy-pwa.yml` runs only on manual dispatch or main commit message containing `[deploy-pwa]`; this release-only PR exists so its squash commit can carry that marker after green PR CI. **Do not claim release success** unless the resulting GitHub Actions deploy run really succeeded and the production smoke is green. The protected workflow will also run the full 46-indexer audit. Keep the genuine BTDigg bookmarklet + optional clipboard fallback labeled as manual import, not a repaired automatic BTDigg API. No paid services or new components authorized. Record actual final release SHA/run from current GitHub state.


## 2026-10-09 Rock64-only automatic BTDigg search candidate

Owner confirms their home connection opens BTDigg and explicitly approves creating a proper **automatic** search path from Magnetra through Rock64 (no manual Safari bookmark). This DOES NOT verify a headless Python BTDigg search on Rock64. Candidate GitHub branch `feat/btdigg-rock64-private-gateway` contains an authenticated, loopback-only Python HTML gateway; only the original BTDigg provider may use the Worker-side fixed `https://btdigg-rock64.alexlab.media` Tunnel origin after protected `BTDIGG_GATEWAY_TOKEN` is set. Python listens `127.0.0.1:8796`, uses fixed `https://btdig.com/search`, bounded requests and no redirects/retries; original Cloudflare BTDigg adapter remains the default when the secret is absent. Other 45 providers and Flud remote are untouched. A separate Cloudflare Tunnel + systemd service and root-owned token are needed, but **none is deployed/installed by GitHub merging code**. See `rock64/README.md` for staged Rock64 preflight, local proof (`check-btdigg.py`), Cloudflare route, secured Worker secret activation, rollback. Do not affect existing CalciDatum runner or NexaPanel service. Do not mark BTDigg recovered until real Rock64 HTML search AND Worker-to-tunnel-to-PWA live results are demonstrated. CI includes `rock64/test_btdigg_gateway.py` and `worker/test/btdigg-rock64.test.mjs`; protected invariant `btdigg_residential_gateway` fixes origins and auth. No paid features or bypasses; check current branch/main PR before claims of integration.

## 2026-10-12 owner removal of BTDigg manual importer

Owner explicitly rejected any Safari, bookmarklet, URL-fragment or clipboard-based BTDigg workflow, and requested its removal from all current application code. Current cleanup branch deletes `web/btdigg-bridge.js`, BTDigg tutorial and handlers, their tests and CSS; updates PWA service-worker cache to v5, and keeps a privacy-only scrub for historical magnet-bearing URL fragments. Preserve the user's generic Flud paste-magnet button, all 46 indexers and existing Companion integration. Prevent a BTDigg error from advertising the discarded manual search route. SearXNG and galaris qBittorrent plugin still fetch BTDigg's HTML and are not verified to work in the user's Cloudflare hosting; reports show HTTP 429. Use only the existing genuine-source, optional Rock64 path and require a real end-to-end proof before claiming automatic BTDigg availability. No production release permission was implied by this source-code cleanup.


## 2026-10-12 session handoff verification record

Current working project state was reconfirmed from GitHub, not inferred from older chat: the main SHA was `8969b9fe6758f859ac072bea984a5f9c9c59597f` before this documentation-only checkpoint PR. Closed/merged PRs: #18 (authenticated BTDigg-only Rock64 backend staged; **no physical installation**) and #19 (remove ALL dedicated BTDigg browser/bookmarklet import UI and tests, preserve generic magnet paste and all 46 providers). Last public release remains Oct 9 `239098ba3b1ff3b6a7a5a6021e2cdf3553d784d3`, run `37980229044` success. The Oct 12 main deploy `38313083432` skipped. Last real deploy's full audit: **11 results, 12 empty-or-unverified, 23 source errors, 0 request errors; BTDigg TIMEOUT**. Regular production smoke checks can pass even when the latest main code is not deployed.

Decisions preserved: avoid Safari/clipboard for BTDigg forever absent new explicit instruction; only automate genuine BTDigg data; do not mutate other 45 providers; no dummy/fake source results; optional fixed-origin private Rock64 gateway must be tested on actual device before declaring functional; no paid services or API credits without permission; no broad hostname proxy or CAPTCHA bypass; no unrelated changes to CalciDatum, NexaPanel, router, Shield or Flud Companion; maintain GitHub branch→green CI→PR→squash workflow and explicit production release approval. Keep the existing search cancellation/sliding 3-source concurrency, Flud repeat-send ID safety and same-origin redirect guards. Owner asked for a detailed Senior/Staff developer master prompt to resume this context in a fresh chat; supply the precise latest status instead of re-asking for already-known project decisions.

For the next engineer: **do not stop at a design proposal**. Check current repo state, inspect the Rock64 runbook and critical Python/Worker gateway code for failure modes, prepare safe one-command verification as applicable, and provide concise terminal instructions *only when actual SSH access is unavailable*. Never claim a service started from code on GitHub. Confirm upstream BTDigg's status and rate-limit policy before any actual automated search, avoid frequent test calls, and explicitly distinguish “browser works” from “headless fetch verified”. Preserve protected cost/CI/runtime rules.

## 2026-10-13 real Rock64 BTDigg HTML verified; activation not yet installed

The owner just successfully ran `SearchProvider.fetch("ubuntu")` from `rock64/btdigg_gateway.py` on the physical Rock64, returning **HTTP 200, 10 literal `one_result` occurrences and 20 literal `magnet:?xt=urn:btih:` occurrences**. This proves the Python fetch works through the home egress, but is not yet a parsed end-to-end PWA result, installed systemd service, Cloudflare Tunnel or Worker secret. User asked to deploy already merged code as needed and requested an exhaustive fresh-chat Senior/Staff software engineering master prompt. Code main at the start of this request was `7b33dc425f3586bd27e45862f44f8c34d8207ad2` (check current state anew). Manual BTDigg bookmarklet UI is already removed from main by PR #19 and protected against reintroduction. Rock64 code was merged by PR #18. All 45 other indexers and Flud Companion must remain intact.

Next actions after confirming successful release: (1) on Rock64, guarded service install `sudo bash rock64/install-btdigg.sh` from a fresh **verified main** checkout; (2) `sudo python3 /opt/magnetra-btdigg/check-btdigg.py` and demand real source evidence; (3) provision a **separate** no-port-forward Cloudflare Tunnel `btdigg-rock64.alexlab.media` → `http://127.0.0.1:8796`, preserving other `cloudflared` units and CalciDatum/NexaPanel; (4) create identical strong token locally at Rock64 and secret `BTDIGG_GATEWAY_TOKEN` in production Cloudflare Worker by approved secure operation; (5) end-to-end search `/api/search?q=ubuntu&providers=btdigg`, confirm honest source/magnets and normal Flud actions without autonomous sends. Keep zero additional costs and do not expose token. Code deployment success alone is not end-to-end success; update this checkpoint with exact release run and audit once observed.

## Latest operational release — 2026-10-13

**Deployed:** PR #21 → `eb37a7ca5c605a125e4a858525991d82a7867db3`, Cloudflare GitHub Actions run **38316637704** succeeded with 48/48 Node tests, production smoke passed (46/46 coded adapters), and 46-source real audit: **12 results / 14 empty-or-unverified / 20 provider errors / 0 request errors**. BTDigg remains TIMEOUT from public Worker because the Rock64 Tunnel and Worker secret have NOT been provisioned. On physical Rock64 owner proved `SearchProvider.fetch("ubuntu")` HTTP 200 with 10 `one_result` occurrences and 20 `magnet:?xt=urn:btih:` prefix occurrences. Next priority: guarded install on Rock64 + protected source proof, create isolated tunnel without changing existing cloudflared/CalciDatum/NexaPanel, configure matching Worker-only secret and genuine full-path PWA search. Beware Cloudflare same-zone error 1042; test before touching global flags. Do NOT claim automatic BTDigg recovered until end-to-end checks pass. No manual bookmarklet fallback, substitute DHT indexes, paid API/proxy, secret disclosure or forced magnet send. Source remains the only original BTDigg provider; other 45 stay unchanged.

## 2026-10-13 LIVE OPERATIONAL OVERRIDE — Rock64 tunnel working, PWA search error

**This is newer than all preceding "not installed"/"pending tunnel" notes.** Repository main before checkpoint PR: `4204c283da9a6622c006c58140f7a86c56dabe3b`; production-code deploy remains successful `eb37a7ca5c605a125e4a858525991d82a7867db3`, run `38316637704`. On the real Rock64, `magnetra-btdigg.service` was active and bound exclusively to `127.0.0.1:8796`. `sudo python3 /opt/magnetra-btdigg/check-btdigg.py` reported **HTTP 200, 10 parsed BTDigg HTML result rows, 10 valid magnet links, PASS** for `ubuntu`.

The user installed `cloudflared` 2026.10.0 at **`/usr/local/bin/cloudflared`** (not `/usr/bin/cloudflared`), created isolated `magnetra-btdigg-tunnel.service` with its ExecStart path adapted and confirmed **tunnel active / gateway active**. The new Cloudflare route `btdigg-rock64.alexlab.media` must use **HTTP** upstream `http://127.0.0.1:8796` (initial origin HTTPS gave 502). Public HTTPS `/healthz` without bearer subsequently returned **401**: reachable and secured. Owner entered matching Rock64 gateway secret as production Cloudflare Worker **Secret** `BTDIGG_GATEWAY_TOKEN`; after initially reporting success, they **reported BTDigg search returns no results and an error in the test**. End-to-end search is **not confirmed working**. A previously shared assistant test link accidentally used `%26` rather than literal `&` as the query-parameter separator; use exactly `/api/search?q=ubuntu&providers=btdigg` and inspect `errors`/`stats` in sanitized JSON before changes.

**Evidence limit:** the independent assistant-side production probe could not resolve DNS in its environment. Owner demonstrated on-device service, real gateway source and publicly reachable protected route, but later reports the PWA BTDigg search errors; there was no captured independent authenticated JSON response, 46-source post-activation audit or physical Flud-send verification. Do not invent those. No external paid services, global Worker fetch compat flags, indexer substitutions or other service changes. No reason to reinstall gateway/tunnel; future tasks should focus on regression-free monitoring and specifically evidenced bugs. Never expose either tunnel/gateway token. All 46 original providers remain coded; manual BTDigg importer remains intentionally removed.

### 2026-10-13 API evidence and pending magnet sanitization patch

The owner uploaded valid public search JSON proving `/api/search?q=ubuntu&providers=btdigg` returns **10 BTDigg records**, `stats[0].ok=true`, `errors=[]`, `total=10` for `ubuntu`. This confirms the Worker search pipeline for this query despite an earlier ambiguous PWA error report. Their independent Python `urllib` request from Rock64 returned non-JSON **HTTP 403**; its cause (potential Cloudflare client/WAF behavior) is not yet verified; do not conflate this with the successful JSON API response or weaken global protections without evidence. The originally shared assistant test hyperlink incorrectly percent-encoded `&` to `%26`, which may explain part of the conflicting test output.

The uploaded API JSON exposed literal `&amp;` sequences in BTDigg magnets (`&amp;dn`, `&amp;tr`). PR #23 adds a **BTDigg-only** one-layer fix to `worker/src/html-adapters.mjs`, a Node URL parameter regression test, and an actual Cloudflare workerd HTMLRewriter fixture using escaped href separators to protect Flud-compatible magnet parameters. This code fix must clear CI and receive explicit release approval before deployment. Do not reconfigure the already active Rock64 gateway/tunnel or send any magnet automatically. PWA UI and Flud delivery still need explicit user-facing acceptance evidence.

## 2026-10-13 latest production receipt — BTDigg LIVE (verified by GitHub Actions)

**This overrides the historical pre-activation BTDigg TIMEOUT summaries.** Explicit owner approval to deploy PR #23's BTDigg-only magnet HTML entity normalization. A guarded release-marker PR #24 was merged as commit `62a30d7b25da1ebcb6e6d35e27b840ba3dee8aac`, triggering successful GitHub Actions deploy run `38361367716`. Cloudflare Worker `alexlab-magnetra` custom-domain version ID: `b0375998-666b-4160-8390-987f62457f01`. Actual post-deployment HTTPS/PWA smoke PASS; all 46 adapters present.

**Full live 46-source `ubuntu` audit:** 13 returned results, 14 empty-or-unverified, 19 provider errors, zero transport request errors. **BTDigg specifically returned 10 results** from the public Worker API, confirming real Rock64 tunnel integration after the old hosted-Cloudflare TIMEOUT. The previously observed literal `&amp;dn`/`&amp;tr` magnet entity issue is fixed in released Worker code and passes Node + real workerd regression tests. There is **no separate captured raw live magnet sample or physical Shield/Flud transmission test** after release; preserve this distinction.

Physical Rock64 gateway/tunnel are already operational and must not be reinstalled merely to test. Cloudflare tunnel public HTTPS `/healthz` intentionally returns 401 without bearer. Owner-supplied browser JSON from before the last release established 10 authentic results; a separate Python urllib HTTP 403 is a client-path discrepancy, not evidence that the browser-visible API is down. Do not modify the other 45 sources, replace authentic BTDigg with different DHT indexes, re-add manual Safari bookmarks, expose credentials, change globally scoped Cloudflare compatibility flags, or trigger torrents to Flud without owner action. The release required no paid service or new API.

## 2026-10-13 intermittent live PWA BTDigg failure after successful deploy

The owner reports that genuine BTDigg `ubuntu` results were visible via the PWA, but approximately ten minutes later the identical search returned **0 results**, a single unavailable indexer and generic UI message **"This provider could not complete the search."** The prior successful Cloudflare release audit `38361367716` found BTDigg **10 real results**, and Rock64 installed gateway/tunnel had been validated, so **do not describe BTDigg as permanently recovered or permanently down**. This is an intermittent live failure. The screenshot does **not** include the API `errors[].error` or `errors[].code` fields; the precise cause (upstream HTTP 504 timeout, Cloudflare edge fetch rejection, tunnel connectivity, etc.) remains unverified.

Current Rock64 gateway limits: fixed BTDigg-only source, single active request, 5s minimum interval, success cache for only 30s, upstream timeout 8s; Worker gateway timeout 10s. A success ten minutes ago does not guarantee a later request can reach BTDigg. A Worker connector bug currently masks ALL fetch exceptions as generic "gateway is unreachable" and the gateway's HTTP 504 is not typed as timeout. The diagnostic-only patch in PR #26 distinguishes gateway HTTP 504/TIMEOUT, Cloudflare same-zone 1042 (when explicitly observed), and other transport failures with safe categorical codes and no automatic retries. It does not claim to fix the intermittent transport cause. **No extra Cloudflare service, network-global fetch flag, paid proxy, IP rotation, automatic reattempt or Flud send is authorized.** Obtain a sanitized copy/screenshot of the exact public `/api/search?q=ubuntu&providers=btdigg` JSON `errors` from a failed browser test to decide any further operational repair.

## 2026-10-13 new stabilization PR and latest 46-provider audit (not yet deployed)

User confirmed the BTDigg PWA search sometimes works without any VPN and fails intermittently for the same `ubuntu` term. This is not proof of a mobile-IP block: BTDigg egress originates from Rock64 at home. Existing Python cache was only 30 seconds and stored only one query; concurrent identical requests could return local 429. Latest GitHub Actions deploy audit 38361367716 (2026-10-13) proved **13 positive / 14 empty-or-unverified / 19 errors / 0 request errors**; BTDigg returned 10 genuine results, even though UI still displayed **08-Oct ERROR IN TEST**. User requested real stabilization and status correction, and discussed removing permanently broken sources; **do not delete original 46 indexers based on a single benign-term audit**.

PR #26 branch `fix/btdigg-intermittent-diagnostics-20261013` is extended with Python success-only 20m/4-entry/6MB in-memory LRU, same-query singleflight, 5s unique-query limit, 12s upstream / 16s Worker gateway budget, safe error diagnostics and no 429/CAPTCHA retries. It replaces the embedded audit with the exact logged 13-Oct 46-source results and tracks separate per-browser-session source outcomes for the provider picker. The snapshot remains historical, never current uptime. Tests and docs/invariant config must pass before merge. No cost, global Cloudflare flag, new indexer backend, credential changes, or Flud sends authorized.

**Not installed/deployed yet**: after CI/squash merge, Rock64 code update and guarded restart must be done explicitly by owner (no SSH connector to this machine), while Worker/UI require separately approved Cloudflare deployment. Preserve the existing production SHA/version until deployment is confirmed. Do not quietly replace a running service by copying files without unit validation and backup. Do not alter CalciDatum, NexaPanel, router, other tunnels or Flud Companion. Source audit is a one-time observation, not grounds for deleting 19 error-status or 14 unverified providers.

## 2026-10-13 Rock64 gateway upgrade succeeded; cleanup fix follow-up

Owner output from physical Rock64 after installing `dcdfdaa1d4ed53e6212701230c31c9a2b00178e8`: **Ran 7 tests / OK; authenticated localhost health PASS; Magnetra gateway upgraded PASS; magnetra-btdigg.service active; magnetra-btdigg-tunnel.service active**. The final `rm` failure was confined to a root-owned Python `__pycache__` directory inside `/tmp/magnetra-stable.4fzB6aEo/repo`; it occurred only during cleanup of the checkout. It did not roll back the active gateway. The source fix in a subsequent PR uses `python3 -B -m unittest` and no-bytecode `ast.parse` in both guarded install and update scripts. No immediate reinstall is needed. The remaining important activation gate is the independently approved Cloudflare Worker/PWA release for the user-visible audit refresh and the 16-second Worker timeout, followed by live BTDigg verification. Do not conflate merged GitHub code with deployed Cloudflare code. Do not touch any other Rock64 services, tokens, Cloudflare tunnels, other 45 original indexers or Flud Companion.

## 2026-10-13 FINAL verified live stabilization state (supersedes pending-deploy notes)

**Rock64 is ALREADY updated, do not reinstall.** Owner's protected updater output: seven Python tests PASS; authenticated localhost `/healthz` PASS; `magnetra-btdigg.service` and `magnetra-btdigg-tunnel.service` both active. An incidental root-owned `__pycache__` in the temporary cloned checkout prevented only final user-owned cleanup; future installers were fixed in merged PR #27, no reinstallation required.

**Cloudflare Worker/PWA is ALREADY deployed.** Release commit `f7a37b555169c920ad1d2dfd35c31bb76fd3c0ac`, GitHub Actions run `38373699387` **success**, Worker Version ID `58df87fe-0ab8-48cc-9c86-8dd6922b8a3c`, custom domain `https://index.alexlab.media`, production smoke PASS. Post-deploy 46-source audit at ~09:05 UTC: **13 results / 12 empty-unverified / 21 provider errors / zero transport errors**, BTDigg specifically **10 real search results**. The PWA's deliberately historical embedded audit reflects a different **earlier** 13-Oct run (`38361367716`, 13/14/19) and additionally shows current-browser-session observations. Do not equate source adapter presence, historical sample or one successful call with guaranteed uptime.

Stability improvements are live on **both** tiers: Rock64 bounded success-only 20-minute/4-entry/6MB in-memory cache, identical request coalescing, fixed upstream throttling, no automatic anti-bot/CAPTCHA/429 retries; Worker timeout 16s and categorized gateway/transport errors; provider status UI updated. The other 45 original indexers remain untouched and selectable, as does user-initiated Flud Companion dispatch. Do not redeploy without cause; no paid services or system-global Cloudflare compatibility changes. If intermittent failures recur, capture the failed request's JSON `errors[]` code with exact time, and distinguish source 429, 504 timeout, tunnel 1042, transport error or UI client filtering. No physical magnet dispatch to Shield was tested or initiated in this rollout.

## 2026-10-13 new request: BTDigg default, status-ranked 46-indexer selection, rapid search stability

Owner confirmed BTDigg works after prior deployment but can fail after ~3 quick searches; no failed `errors[].code` was captured. The physical Rock64 gateway is already stable/installed, so do not reinstall or bypass source limits. The newer selector PR pins BTDigg first, orders last-audit positives before empty/unverified and errors, and updates ranks based on results genuinely observed in this browser session. All 46 sources remain selectable; **none** are deleted based on isolated failures. The complete verified production 13-Oct run **38373699387** replaces the older embedded audit snapshot (13 results / 12 empty or unverified / 21 provider errors; BTDigg 10 real results).

BTDigg is now part of the 5-source default `[btdigg,knaben,torrentscsv,thepiratebay,internetarchive]` for both PWA and Worker API; only clients storing **exactly** the old 4-source default migrate automatically. Custom choices are preserved. A BTDigg-only abortable 5.5-second UI delay before distinct rapid new searches reduces self-generated Rock64 429s without retries, paid IP services or changing the gateway's 5-second throttle. Repeat verified positive identical query may use the gateway's 20-minute success-only source cache. Source-specific errors remain visible; if failures persist obtain exact API code, not guesses. Flud relay unchanged.

Until a successful CI/merge/deployment receipt is recorded, this is **staged** in GitHub, not live. Release must use the same guarded Cloudflare pipeline with no new paid services, Rock64 service changes or manual Safari BTDigg workflow.

## 2026-10-13 LATEST LIVE UI RELEASE — BTDigg pinned, selected, paced

**Do not repeat release or Rock64 setup.** Owner-approved PR #30 squash main commit `6070b64bb626a65905c3b1604d0ff3df49b2483b` was deployed successfully by GitHub Actions **38387105924** to Cloudflare Worker `alexlab-magnetra` at `index.alexlab.media`, production Version ID **`0ea30e34-7b96-4ce6-a7e6-aaef210ed0d4`**. Post-deploy HTTPS/PWA/API smoke PASS, full 46-source benign `ubuntu` audit 13 results / 13 empty-or-unverified / 20 provider errors / 0 request errors; BTDigg **10 real results**.

The deployed PWA selector pins BTDigg first; ranks other sources by successful date-stamped audit or observed browser-session outcome, then empty/unverified, then errors, alphabetical within groups. All 46 preserved. Browser and Worker default selection is now `btdigg,knaben,torrentscsv,thepiratebay,internetarchive`. Saved exactly old 4-source defaults migrate to add BTDigg; any custom preference is respected. The embedded dated source-audit snapshot in the deployed code still reflects the earlier same-day 13/12/21 run **38373699387**, not the later post-deploy 13/13/20 run. Do not describe either as permanent uptime.

Owner complained BTDigg failed after ~3 quick searches. The browser now delays new, different BTDigg searches to respect gateway 5-second rate limit, with a 5.5s abortable wait; no background retry of 429 or CAPTCHA, no IP rotation or global Cloudflare changes, same-query positive cache allowed. Exact original failing `errors[].code` was not captured, so pacing is a preventive improvement, not a proven cure for unrelated upstream failures. Installed Rock64 Python gateway/tunnel stays unchanged. No Flud Companion magnet send was initiated.

## 2026-10-13 third-search timeout persists after >=10-second pause; investigation

Owner reports recurring BTDigg timeout on roughly the third search even when waiting 10 seconds between clicks. Previous 1.08-second physical Rock64 direct BTDigg `debian` probe, active gateway/tunnel and multiple successful PWA searches indicate intermittent rather than permanent failure. The owner does NOT use a Tailscale exit node; do not claim mobile VPN traffic controls Rock64 egress. **Code has no limit of exactly three searches.** The frontend's 5.5-second wait and gateway 5-second throttle don't explain every `TIMEOUT` after a longer pause.

New diagnosis PR makes `BTDIGG_SOURCE_TIMEOUT` (Rock64 HTTP 504, about 12 s BTDigg fetch/waiter) different from `BTDIGG_TUNNEL_TIMEOUT` (Cloudflare Worker tunnel fetch abort after 16 s); both were formerly `TIMEOUT` and displayed identical mobile text. New codes become visible under BTDigg failed-search detail; tests assert end-to-end API error-code distinction with NO extra retries, no token/private URL leakage. **Not yet proven which cause is occurring in the owner's real failing query; neither actual BTDigg availability nor Tailscale association should be asserted without captured source-specific error.** Do not redeploy this diagnostics patch until owner approves, do not change Rock64, Tailscale, Cloudflare security flags, Flud or the 45 other indexers.

## 2026-10-14 four-provider 403 investigation — read-only Rock64 probe first

The owner asked to restore **1337x, BT4G, Ext and EZTV** after a screenshot showed all four return Cloudflare-origin `ACCESS_DENIED` (HTTP 403), and volunteered that they already subscribe to NordVPN. All four are original 46 adapter IDs `1337x`, `bt4g`, `extdotto`, `eztvx`; current fixed origins `1337x.to`, `bt4gprx.com`, `ext.to`, `eztvx.to`. NordVPN on iPhone doesn't alter Worker egress; using NordVPN globally on Rock64 could break Plex/CalciDatum/NexaPanel/BTDigg. BTDigg-only gateway and authenticated tunnel must remain isolated/unmodified. Official `eztvx.to/api/` API exposes recent results and IMDb-specific search, NOT generic text search.

Added read-only `rock64/probe-blocked-indexers.py` and unit tests. Owner must run **once on physical Rock64** as regular `runner`: `python3 -B rock64/probe-blocked-indexers.py` from checked out approved commit. Probe requests four exact benign search pages plus one official EZTV API test, at most 9s each and 256KB inspected, follows no redirects, doesn't log source content, credentials, magnets or modify system. Await results before implementing source-specific isolated four-provider residential gateway (including deferred magnet resolution). The mere presence of HTTP 200 is insufficient for search/magnets proof. If all residential paths 403, evaluate NordVPN only as per-service isolated egress with explicit owner approval and no credentials in chat/GitHub; no automatic CAPTCHA bypass, fake mirrors, paid infrastructure or global routing change.
## 2026-10-14 staged EZTV official API via TVmaze exact-title resolution

The owner's Rock64 probe demonstrated all four original HTML hosts (`1337x.to`, `bt4gprx.com`, `ext.to`, `eztvx.to`) return HTTP **403**, while `https://eztvx.to/api/get-torrents?limit=2&page=1` returned genuine JSON **200** in 0.18s. This disproves merely proxying the four original HTML URLs through Rock64 as an easy fix. Italian AGCOM's official 2018 DNS-block decision names 1337x, but the cause of the observed 403 for each specific domain is not proven. NordVPN on the phone doesn't fix Cloudflare egress; do NOT put the whole Rock64 under NordVPN or request credentials in chat.

An **unreleased** source-only feature branch adds `worker/src/eztv-official-api.mjs` to preserve the existing EZTV `eztvx` ID, using two free/keyless fixed APIs: TVmaze `/search/shows?q=...` for exact unique show-title-to-IMDb lookup; official EZTV `/api/get-torrents?imdb_id=...&limit=100&page=1` for actual torrent magnet results, rejecting mismatched IMDb IDs/ambiguous metadata and unsupported categories. Direct `tt...` searches skip TVmaze. Explicit CC BY-SA TVmaze attribution in picker; tests simulate genuine verified torrents and source HTTP failures; never blend in TVmaze entries as torrents. This does not restore 1337x/BT4G/Ext, and does not promise live EZTV until Cloudflare-origin tests and owner-authorized release succeed. No VPN, Rock64 gateway or Flud changes.

## Owner-authorized EZTV production release trigger — 2026-10-14

Owner explicitly confirmed release of the merged EZTV exact-title API implementation and preparation of an isolated NordVPN test for the remaining three. This documentation-only commit carries the existing protected `[deploy-pwa]` marker so the canonical GitHub Actions workflow runs tests, wrangler deployment, HTTPS smoke and 46-provider audit. This marker does not alter provider code or deploy other projects. After deployment, check actual `eztvx` API search for a verified IMDb ID and report errors honestly. NordVPN must remain test-only and per-service, with no global routing or credentials committed.

## 2026-10-14 NEW PRODUCTION FAILURE: EZTV official API shape unexpected — canonical checkpoint

Owner independently opened exact production URL `https://index.alexlab.media/api/search?q=tt0460681&providers=eztvx` and provided literal JSON:
```json
{"query":"tt0460681","category":"all","results":[],"stats":[{"provider":"eztvx","count":0,"ok":false}],"errors":[{"provider":"eztvx","error":"EZTV API shape unexpected","code":"PROVIDER_ERROR","message":"This provider could not complete the search.","retryable":false,"openUrl":"https://eztvx.to/search/tt0460681"}],"total":0}
```
This is **hard proof that the newly deployed EZTV official API adapter is NOT working for direct IMDb search**. Do not call it repaired or attribute this error to NordVPN. Deployment itself succeeded via owner-approved PR #35 / GitHub Actions run `38525959541`, Worker version `a9df4429-3ca0-4342-8be6-95fe632ee0ea`, HTTP/PWA/46-provider smoke PASS; generic audit `ubuntu` showed `eztvx` empty/unverified but did not exercise actual IMDb search. Actual source JSON structure/content-type/status from the **Cloudflare Worker egress** has not yet been captured. Current `worker/src/eztv-official-api.mjs` requires `Array.isArray(data.torrents)` and then exact `data.imdb_id` echo; one or both assumptions may be false for the actual API response, including possible API-level errors with HTTP 200. Need evidence-first inspection of safe source shape (field names/types and status only; do not log torrents/magnets) and minimal source-only fix, test realistic response fixtures, and release through canonical `[deploy-pwa]` pipeline with real `tt0460681` production smoke. Keep 45 other providers, Flud, BTDigg gateway and tunnels unchanged. Do not fabricate results or silently substitute TVmaze search results.

Other evidence: Physical Rock64 5 GET read-only probe on 2026-10-14: 1337x HTTP 403 0.10s, BT4G HTTP 403 0.12s, Ext HTTP 403 0.10s, EZTV HTML HTTP 403 0.09s, official EZTV API `/api/get-torrents?limit=2&page=1` HTTP 200 expected marker 0.18s. This 200 did **not** verify `?imdb_id=460681` shape. Latest production audit `ubuntu`: 12 result providers, 16 empty/unverified, 18 errors, 0 transport request errors, BTDigg `BTDIGG_SOURCE_TIMEOUT` once; BTDigg intermittently works, not permanently dead.

NordVPN owner already has subscription and explicitly authorized **isolated test preparation**, NOT global Rock64 VPN installation. PR #36 `diagnostics/nordvpn-isolated-preflight-20261014` prepared read-only `rock64/check-nordvpn-isolated.py` and was OPEN at last check. Ask owner to confirm whether NordVPN account shows **SOCKS5 proxy service / endpoints**, exact server hostname and port **only** if non-secret, supported protocol, whether manual/service credentials are available privately, and whether plan permits use. Never ask to paste password, service password, access token, subscription ID or login. If provider doesn't offer SOCKS5, do not invent endpoint; discuss isolated network namespace/container as separately authorized alternative. SOCKS5 must affect only 1337x/BT4G/Ext dedicated process, not Rock64 default route, BTDigg, Plex, NexaPanel, CalciDatum or Tailscale. Proxy may still return 403; prove via fixed-origin bounded test first. No proxy installed yet.

Next chat priority: (1) fix genuine EZTV API JSON response-shape failure from actual evidence; (2) independent NordVPN proxy availability/readiness check, no global routing; (3) only after both tested, source-specific integration with CI, production smoke, and rollback.

## 2026-10-14 — latest physical EZTV source evidence and isolated gateway proposal

Owner ran the enhanced `rock64/inspect-eztv-api.py` **twice**, identical output:
- IMDb `tt0460681`: HTTP 200 JSON, `declared_torrents_count:0`, no torrents array.
- Recent: HTTP 200, `declared_torrents_count:1092185` global reported by source, `torrents_count:2` loaded and 2 valid magnets.
- Filtered IMDb selected from real recent row: HTTP 200, `declared_torrents_count:15`, `torrents_count:2`, exact root and first-row match, 2 valid magnets.
This proves genuine official EZTV source data through residential Rock64; previous GitHub/Cloudflare 403 remains an independent egress blocker. Do not invent IMDb ID of sampled show: probe intentionally did not print it. PR #40 already merged safe zero-hit parser.

Staged implementation branch `feat/eztv-rock64-isolated-gateway-20261014` prepares distinct authenticated EZTV residential gateway; see `rock64/README_EZTV.md`, `docs/PROJECT_STATE.md`, live branch PR/CI. **No activation**: proposed 127.0.0.1:8797, hostname `eztv-rock64.alexlab.media`, unique Worker Secret `EZTV_GATEWAY_TOKEN`, unique local `MAGNETRA_EZTV_TOKEN`, all must be verified before any live service/tunnel or Cloudflare deploy. Existing BTDigg 8796/tunnel/service and Plex/NexaPanel/CalciDatum/Flud are off limits. No global NordVPN/DNS/Tailscale/firewall; 1337x/BT4G/Ext remain separately blocked and PR #36 for NordVPN is independent.

## 2026-10-14 — EZTV local preflight after PR #41 (physical Rock64)

Owner ran 5/5 Python tests (PASS), `ss -ltn '( sport = :8797 )'` returned no listener, `cloudflared` is at `/usr/local/bin/cloudflared`, BTDigg service is active. Follow-up isolated EZTV PR corrects the dedicated tunnel template from `/usr/bin/cloudflared` to the observed absolute path and adds credential-safe authenticated loopback source proof at `rock64/check-eztv-gateway.py`. No live EZTV service, tunnel, DNS or Worker Secret has been verified or activated. **Do not change any existing cloudflared service or global network routing.** Next owner step (after PR merge and explicitly accepting local installation): guarded `install-eztv.sh`, local health + positive-source proof, only then an isolated Cloudflare tunnel, final controlled deploy and real production check. 1337x/BT4G/Ext/NordVPN remain separate unresolved work.

## 2026-10-14 — EZTV physical install succeeded; smoke check blocked before local health

User ran pin `a51585ef9e27c14da6b7183457491ba11178edca`: gateway installer enabled `magnetra-eztv.service`, reported PASS on `127.0.0.1:8797`, and 5/5 gateway tests passed twice. Immediate `check-eztv-gateway.py` gave generic FAIL *before* `EZTV local authenticated health: PASS`. Root cause unknown. Possible startup race vs auth file mismatch vs health route unavailable, not a proven upstream EZTV error. Gateway may now be running but is not yet validated. Do not reinstall service, change BTDigg, or create Cloudflare tunnel. Follow-up branch `fix/eztv-local-health-readiness-diagnostics-20261014` adds bounded local-listener readiness retries and safe stage/cause output. Obtain `systemctl is-active magnetra-eztv.service`, `ss -ltn '( sport = :8797 )'`, and no-auth health HTTP code (expected 401), then run the updated check. Install/activation must stop until authentic positive result is proven locally.


## 2026-10-15 — EZTV local filtered zero, broader residential provider audit

Physical Rock64 EZTV service at `127.0.0.1:8797` is active, unauthenticated
`/healthz` correctly reports HTTP 401, BTDigg remains active. Updated
authenticated checker printed `EZTV local authenticated health: PASS`,
then `EZTV filtered source rows: 0`, `valid magnet: 0`,
`FAIL stage=local-filtered`. This is an unresolved discrepancy versus the
earlier direct EZTV positive filtered lookup (`limit=2`, two magnets);
the installed EZTV gateway queries `limit=100`. Do not configure
`eztv-rock64.alexlab.media`, set the Worker Secret or deploy production yet.

Owner wants the same Rock64 method considered for Torrentz, UIndex, 1337x,
BT4G, Ext and other failed original adapters. Prior Rock64 1337x/BT4G/Ext
403 means source access needs independent proof before any residential
gateway. Staged two read-only, fixed-origin source diagnostics
(`rock64/probe-more-indexers.py` with optional `--extended`, and
`rock64/diagnose-eztv-filter.py` requiring sudo for an in-memory gateway
credential). They neither modify existing services nor print sensitive
data. See `rock64/README_MULTI_INDEXER_EGRESS.md`, current GitHub main and
current diagnostics PR. Only after the owner supplies actual physical
per-source status and, for positive sources, genuine HTML/magnet evidence,
start a separate guardrailed gateway design. Preserve all 46 provider IDs,
source attribution, all Flud actions, BTDigg's 8796 tunnel, EZTV's 8797
service, other Rock64 projects and no paid/global VPN changes.

## 2026-10-15 — 11-source owner audit + reproducible EZTV filtered mismatch

Latest physical Rock64 11-source read-only `ubuntu` audit:
- Torrentz (`torrentz2.nz`): NETWORK_OR_TIMEOUT in 0.07 s, cause not yet categorized.
- UIndex, 1337x, BT4G, Ext, TorrentDatabase, TorrentDownloads, TokyoToshokan: HTTP 403 **also from residential IP**.
- OxTorrent, Torrent9, BitSearch: HTTP 301 with no redirects followed; determine same-origin vs new host before any adapter change.
- EZTV: recent HTTP 200 and valid magnet candidate, but for the **same sampled IMDb** direct `limit=2`, direct `limit=100`, and authenticated loopback gateway each HTTP 200 exact echo declared 0 / no torrents list. Earlier direct positive filtered IMDb was real at another time/sample; do not infer `limit=100` bug. EZTV service 8797 and BTDigg service both active. No EZTV tunnel/secret/deploy.

Next: merged `rock64/probe-indexer-followup.py` for FOUR targeted original HTML hosts (safe redirect class/destination host, exact Torrentz transport category) plus up to FOUR different genuine recent EZTV IMDb samples, with no IDs or magnets logged. It is read-only, never follows redirect, no network/service changes. Evaluate owner output; do not invent Torrentz replacements or proxy 403 websites. Stage separate canonical-migration patch only if the redirect host/path proves safe and authentic content can be verified.

## 2026-10-15 — EZTV filtered-positive source evidence and redirect destinations

New physical Rock64 read-only report:
`torrentz` has TRANSPORT_FAILURE (no HTTP). OxTorrent HTTP 301 →
`www.oxtorrent.co`, Torrent9 HTTP 301 → `www7.torrent9.to`,
BitSearch HTTP 301 → `bitsearch.eu`, all **OFF_ORIGIN** and none
followed. Do not change catalog/legacy-spec host until authenticity,
HTML rows, safe exact-origin redirects and deferred magnets verified.
Other seven Rock64 HTTP 403 sources remain blocked and untouched.

EZTV official `limit=100` API retrieved matching authentic magnet
results for **three distinct recent IMDb IDs**: 16/16, 31/31 and
100/100 returned records; fourth recent candidate had no filtered
results. This proves the upstream API works, and picking a zero-result
recent candidate is the local smoke's false-negative issue. The
installed private Rock64 `magnetra-eztv.service` at 8797 is
authenticated, but **positive filtered results through it are still
UNVERIFIED**. A scoped PR adjusts only standalone
`rock64/check-eztv-gateway.py` (up to 4 official positive candidates,
then exactly one same-ID authenticated gateway GET) and adds
`rock64/probe-redirect-candidates.py` for the three observed new
hostnames read-only with markers, no redirects. CI must pass, then
owner performs two pinned checks from the Rock64. **No tunnel, secret,
production deploy, service changes, new cost or 403 bypass** until
end-to-end evidence and explicit owner approval.


## 2026-10-15 — decisive same-IMDb Rock64 EZTV gateway 100/100 PASS

Owner ran latest read-only scripts from `35d1b47e406eaf0e4e9deda5d313eae21ca8bdb3`. Source-positive official EZTV API filtered result: `direct filtered rows:100`, `direct matching magnet count:100`. Authenticated independent loopback gateway `127.0.0.1:8797` for the **same hidden IMDb**: `gateway filtered rows:100`, `gateway matching magnet count:100`, exact acceptance `PASS: genuine EZTV magnet metadata reached isolated local gateway`. Both `magnetra-eztv.service` and `magnetra-btdigg.service` active. Local function is proven, **no need for further sampling or gateway code changes**. This is *not* Worker/Tunnel or PWA production success.

Original off-origin 301 target checks from residential Rock64: OxTorrent `www.oxtorrent.co` HTTP 200 / only 3 generic HTML table rows / 0 magnet anchors; Torrent9 `www7.torrent9.to` HTTP 200 / only 4 generic table rows / 0 magnet anchors; BitSearch `bitsearch.eu` HTTP 520. Nothing is verified as a genuine searchable torrent result, and no provider origins or parsers should yet be silently modified. Torrentz transport failed, seven others 403 even on Rock64.

Next practical milestone: request **explicit owner permission to create a NEW Cloudflare-managed tunnel and DNS route** for `eztv-rock64.alexlab.media` to local `http://127.0.0.1:8797`, then separately activate only `magnetra-eztv-tunnel.service` with private tunnel token stored outside GitHub and chat. Existing `/usr/local/bin/cloudflared` must be checked for version 2025.4+ / token-file support per official docs. `rock64/magnetra-eztv-tunnel.service` is a standalone template that uses `LoadCredential=tunnel-token` and `TUNNEL_TOKEN_FILE=%d/tunnel-token`; do not use globally destructive `cloudflared service install`. Monitor Worker-to-Tunnel same-zone 1042 with an isolated test and **never enable global fetch compatibility flags** affecting unrelated projects without explicit approval. Worker `EZTV_GATEWAY_TOKEN` and a protected `[deploy-pwa]` release only after tunnel proof and separate consent; no live tunnel, DNS or Worker secret is known to exist yet. No paid/cloudflare upgrade authorization, no VPN/global routing changes.


## 2026-10-15 — explicit owner GO for independent EZTV Tunnel/DNS, PWA deployment held

Owner replied **Da** to creating a NEW Cloudflare Tunnel plus
`eztv-rock64.alexlab.media` DNS route pointing only to
`127.0.0.1:8797`. Scope strictly excludes production PWA deploy,
Worker Secret provisioning, paid upgrades, global `cloudflared`
service install, shared routes, existing BTDigg, Flud, Plex,
NexaPanel and CalciDatum. The earlier local same-IMDb test PASSED
with 100/100 genuine magnet metadata via authenticated 8797;
BTDigg gateway is also active.

There is no Cloudflare connector or Rock64 SSH in this chat, so
actual account/host changes are not done. A newly staged
`rock64/install-eztv-tunnel.sh` is root-opt-in and prompts
invisibly for only the new dedicated tunnel token, stores it mode
0600 at `/etc/magnetra-eztv/tunnel-token`, refuses overwrites,
checks `/usr/local/bin/cloudflared` version 2025.4.0+,
`--token-file` support, EZTV/BTDigg active and local health 401,
and installs **only** `magnetra-eztv-tunnel.service` from the
existing isolated template. Owner uses Cloudflare Dashboard
Networking > Tunnels > Create Tunnel, name
`Magnetra-EZTV-Rock64`, published application hostname
`eztv-rock64.alexlab.media`, origin
`http://127.0.0.1:8797`, automatic CNAME. Do NOT run
Dashboard `cloudflared service install TOKEN` or paste tokens
into chat/GitHub. Obtain both files from same pinned merged commit,
run manually, verify Cloudflare Tunnel Healthy and HTTPS
unauthenticated `/healthz` HTTP 401; do not claim completion based
on code alone. Optional later Worker/1042/prod integration needs
explicit further approval. Read `rock64/README_EZTV.md`.

Cloudflare official Dashboard workflow: first create tunnel and obtain
its private token; run new separate Rock64 connector installer; after
connector becomes Healthy click Continue and add Published application
route + automatic CNAME. If Dashboard permits route before connector
Healthy, that ordering is also safe; do not assume UI supports it.


## 2026-10-15 — LATEST OVERRIDE: single pre-existing Cloudflare Tunnel for Magnetra

**CRITICAL owner correction:** "nu mai faceam tunnel pt fiecare in parte ... solutie pt toate restul". This supersedes the formerly approved new EZTV-only Cloudflare Tunnel plan. Do **not** follow PR #48 instructions, do **not** execute install-eztv-tunnel.sh or create an EZTV-specific cloudflared unit/token/hostname. Superseding PR removes unused installer/template/test from GitHub only, with no physical changes. The existing local 127.0.0.1:8797 EZTV gateway is proven with direct=100 and authenticated local=100 genuine same-IMDb magnets and must be preserved. Existing BTDigg 8796 and its BTDigg Tunnel must not be stopped or rerouted.

New target documented in docs/SHARED_MAGNETRA_GATEWAY.md: one existing BTDigg Tunnel connector + new one-time Published application magnetra-rock64.alexlab.media pointing to a future fixed-route authenticated Magnetra dispatcher on 127.0.0.1:8798. The original BTDigg hostname remains pointed at 8796. Subsequent provider fixes become dispatcher registrations, NO per-provider Cloudflare Tunnel/route. First owner step: run read-only rock64/check-shared-tunnel.sh from merged pinned commit, and confirm existing BTDigg Tunnel management mode in Cloudflare Dashboard (not token). Then stage central dispatcher and source-specific genuine HTML/magnet tests via PR/CI, with no physical install/production deploy before approval. Seven sources return HTTP 403 even from Rock64; extra Tunnel will NOT fix them. OxTorrent/Torrent9 new-host HTML tables not yet verified as torrent search rows/magnets, BitSearch HTTP 520, Torrentz transport error. PWA still preserves 46 IDs. Worker-to-Tunnel same-zone error 1042 is potential; never globally loosen Worker outbound compatibility or existing Flud/BTDigg paths. No new Tunnel/DNS/secret/host service/proxy/production deploy performed by this step.


## 2026-10-15 — user confirms central 8798 gateway + existing BTDigg Tunnel (no new tunnels)

The owner explicitly agreed to use the **existing** BTDigg Tunnel,
preserving its current hostname->8796 route, then later add **one**
Published application `magnetra-rock64.alexlab.media` ->
`127.0.0.1:8798`. Verify real tunnel's Cloudflare Dashboard
mode/config, physical Rock64 port/service states, and Worker same-zone
1042 before activation. No service/DNS changes yet.

The staged implementation branch adds:
`rock64/magnetra_gateway.py` and separate optional
`rock64/magnetra-gateway.service` template + localhost-only
tests, with exactly one authenticated provider route
`/v1/eztvx/torrents?imdb_id=NNN`; it forwards to the
existing loopback EZTV 8797 using its independently private
`MAGNETRA_EZTV_TOKEN`. Hub uses a **new, different**
`MAGNETRA_GATEWAY_TOKEN`, 8798 loopback only, no open proxy,
no arbitrary provider IDs, no logging identities/magnets/tokens,
no cache/retry/redirect, 1MB response limit and strict IMDb
validation. Worker optional EZTV adapter stages the **central**
origin and new hub secret, never the abandoned EZTV-only hostname;
no PWA release or Cloudflare Worker Secret provisioned.

**First user terminal action** after PR merge: obtain pinned
`rock64/check-shared-tunnel.sh` (not root-required), run on physical
Rock64 and share only high-level states/listener counts/unauth
health codes. Separately verify in Cloudflare Dashboard existing
BTDigg Tunnel's management mode and ability to add Published
application, without clicking save or changing route. Do not run
old EZTV-only tunnel installer from PR #48. No new hub installer
yet; develop after physical preflight. The 46 original providers
and unchanged BTDigg/Flud/Plex/NexaPanel/CalciDatum are protected.


## 2026-10-16 — LATEST VERIFIED CHECKPOINT / USE THIS FIRST IN NEXT CHAT

**User provided physical Rock64 read-only test and Cloudflare Dashboard
screenshots of the REAL EXISTING BTDigg Tunnel.** This overrides prior
speculative instructions to inspect whether the old route exists.

Physical script pinned to PR #50 main commit
`7129adfaa076c7cd2dcc2650913332a3de6f019e` showed:
```text
magnetra-btdigg.service: active
magnetra-btdigg-tunnel.service: active
magnetra-eztv.service: active
magnetra-eztv-tunnel.service: inactive
port_8796_listener_count: 1
port_8797_listener_count: 1
port_8798_listener_count: 0
port_8796_health_http: 401
port_8797_health_http: 401
```
401 unauth is intentional security success. 8798 is FREE, **not
installed**; `magnetra-eztv-tunnel.service: inactive` alone does not
prove it absent. Neither tunnel nor service has been changed.

Cloudflare Dashboard screenshots show tunnel
`magnetra-btdigg-rock64`, **1 active replica**, **1 existing
Published application route**:
`btdigg-rock64.alexlab.media` →
`http://127.0.0.1:8796`, and **Add route** visible on the
existing tunnel. `Type: cloudflared` is shown, but a literal
`Remotely managed` mode LABEL was NOT shown: do not pretend this
was proven. Token rotation is visible but NOT clicked; NEVER rotate,
print or expose tokens. There is no second route or DNS change yet.
The existing route is the live BTDigg dependency and must stay
exactly unchanged.

**Chosen permanent architecture:** reuse only this existing Cloudflare
Tunnel connector; when local proof is ready, add exactly ONE new
Published application route:
`magnetra-rock64.alexlab.media` →
`http://127.0.0.1:8798`. This is a second ROUTE on the SAME tunnel,
not another Cloudflare Tunnel nor one route per indexer. Subsequent
provider paths use the one dispatcher. The previous separate EZTV
tunnel proposal/PR #48 is superseded and its installer/template/test
were removed from GitHub by the subsequent correction. **DO NOT run
any per-indexer tunnel installation.**

**Staged main implementation PR #50**, commit
`7129adfaa076c7cd2dcc2650913332a3de6f019e`:
`rock64/magnetra_gateway.py` strict local 8798 server;
`rock64/magnetra-gateway.service` bounded standalone unit
template; tests `rock64/test_magnetra_gateway.py`. Only
`GET /v1/eztvx/torrents?imdb_id=NNN` and authenticated
`/healthz` allowed. New strong separate hub token
`MAGNETRA_GATEWAY_TOKEN` for requests; private existing EZTV
token `MAGNETRA_EZTV_TOKEN` is used ONLY for local hop
`127.0.0.1:8797`. No arbitrary URL proxy, no redirect,
no query logging, no inaccurate IMDb/magnet rows. 1MB body cap,
8 thread cap, bounded timeouts, no extra cache/retry. Existing
BTDigg port 8796 not used by hub. Cloudflare Worker EZTV adapter
staged for one future shared HTTPS host and NEW opt-in
`MAGNETRA_GATEWAY_TOKEN`, old `EZTV_GATEWAY_TOKEN` ignored.
No Worker Secret set, no Rock64 8798 installer executed, no new
tunnel, no DNS, no production deploy. PR #50 CI passed 76 Node,
55 Python, Android Debug and Staging. Same-zone Worker→Tunnel
Cloudflare 1042 remains untested/risky.

Previous real EZTV source positive proof: official API direct 100/100
matching IMDb magnet entries, authenticated local EZTV 8797 100/100
for SAME hidden IMDb; this proves **8797, NOT 8798**. Preserve all 46
original provider IDs, original Flud/Flood Companion UX, no
substituting other indexers' results. 2026-10-13 provider audit
historical only: 13 with results / 12 empty or unverified / 21
errors. OxTorrent canonical target `www.oxtorrent.co`: HTTP 200
3 generic table rows, no verified magnet; Torrent9 canonical
`www7.torrent9.to`: HTTP 200 4 generic rows, no verified magnet;
BitSearch `bitsearch.eu`: HTTP 520; Torrentz: pre-HTTP
transport failure; UIndex, 1337x, BT4G, Ext, TorrentDatabase,
TorrentDownloads, TokyoToshokan: HTTP 403 even on residential
Rock64. No automatic "proxy fixes all"; verify genuine rows/details
and do not bypass challenges.

**IMMEDIATE NEXT CODER ACTION**: re-fetch real current GitHub
`main`, read `AGENTS.md`,
`docs/PROJECT_STATE.md`, `docs/SHARED_MAGNETRA_GATEWAY.md`,
`config/project-invariants.json`, and latest checkpoint.
Implement a **guarded OPTIONAL 8798 installer and acceptance checker**
via new scoped PR/tests; do not run physically without user
approval. Preflight already PASS. New installer may touch ONLY
`/opt/magnetra-gateway`, `/etc/magnetra-gateway` and
`magnetra-gateway.service`, refuse overwrites/collisions and use
root-only generated hub token different from private EZTV token.
Make a safe same-private-IMDb local acceptance test verifying
`8797 → 8798` positive genuine magnet metadata and 401 for
unauthorized; no token/IMDb/magnet/hash/title logged. 4 core CI
checks (memory invariants, PWA/provider, Android Debug and Staging)
green before merge, **no [deploy-pwa]**. Owner can run new pinned
installer later only after permission. Then the single new
Cloudflare Published application on existing tunnel and isolated
Worker same-zone 1042 tests; NO global fetch compatibility flags,
paid VPN/egress or service restarts. Owner separate go-ahead required
for physical install, route addition, Worker Secret/deploy.

No ChatGPT remote SSH or Cloudflare administrative connector;
owner executes physical commands and Cloudflare UI changes.
Do not conflate staged code/CI green with live runtime. Protect
shared Rock64 host: BTDigg tunnel/8796, EZTV 8797, Plex, Flud,
NexaPanel, CalciDatum, Tailscale, NordVPN, global cloudflared,
firewall/DNS/default route and other unrelated services.


## 2026-10-16 — installer PR handoff (staged, not activated)

Main was verified at `05239e212f75638f93ce3987efbea445ef00f6f6`. The next work is the 8798 installer PR on `feat/rock64-central-8798-installer`: `rock64/install-magnetra-gateway.sh`, `rock64/check-magnetra-gateway.py` and `rock64/test_magnetra_install.py`, with PWA CI syntax/unit guard and updated source-of-truth documentation. These are NOT evidence of a physically installed daemon, live 8798 magnets, a new Cloudflare route, a Worker secret, or a production PWA deploy. Complete CI/PR review before a separate user-approved SSH install. Do not demand screenshots or redo the historical 8796/8797 preflight as a development prerequisite. Physical installer nevertheless must check the protected old services immediately before changing the machine.

After the opt-in install, run `sudo python3 -B /opt/magnetra-gateway/check-magnetra-gateway.py`; it auto-selects a recent legitimate source-owned positive IMDb privately and requires exact source/8797/8798 magnet equality without revealing the IMDb, magnets or credentials. Report PASS/FAIL truthfully. Then only with new approval add `magnetra-rock64.alexlab.media` -> `http://127.0.0.1:8798` on the EXISTING BTDigg tunnel. Preserve 8796 route, existing units, all 46 IDs and zero-new-cost rule. No Worker deploy or global compatibility changes. The old separated EZTV tunnel is deprecated.


## 2026-10-16 — first 8798 installation FAILED; recovery gated

On physical Rock64 the owner ran the pinned checkout at `73b916cdf811f777881a88ae17d9f6b5ae2280bb`: preflight PASS (8796/8797 protected, 8798 free), 18 local tests PASS, `enable --now` succeeded, but the immediate `--smoke` failed with nonspecific authenticated-health error. The installer executed scoped rollback and did NOT continue to the positive same-IMDb original/8797/8798 acceptance. Actual failure stage is UNKNOWN. Code inspection shows the smoke was performed immediately after `Type=simple` activation without wait-for-listener, so a startup race is plausible but NOT confirmed as the root cause.

A separate `fix/rock64-8798-readiness-diagnostics` PR adds a finite loopback-only startup readiness wait for connection-refused and safe stage-specific error output (no IDs, magnets or secrets). After CI green and PR integration, pin the new main SHA, use the guarded installer in a new owner-authorized SSH attempt, and run the genuine positive-source checker. If the new attempt fails, collect only the redacted stage and sanitized central-unit diagnostics; do not assume port 8798 works or change existing tunnel/BTDigg/EZTV units. Keep all Cloudflare/Worker activation gates closed.


## 2026-10-16 — VERIFIED LOCAL 8798 ACCEPTANCE SUCCESS (LATEST; replaces failed-install next step)

Owner supplied real physical Rock64 terminal output for pinned `main` `174d7e09c441f9430e14518b928f5efc4a0812e1` (PR #53 startup/readiness fix integrated). Installer preflight passed for original BTDigg/EZTV, 23 offline tests passed, new systemd 8798 was installed/enabled, and authenticated local smoke passed. On 8798 and 8797: health auth=200, no auth=401; on 8796 no auth=401; BTDigg, its tunnel, and EZTV units reported active. The full **real EZTV positive-magnet** local checker also PASSED: authentic original source 53 magnets, authenticated 8797 53, authenticated 8798 53, **exact multiset equality** for the same internally selected genuine IMDb. No ID, title, magnet, hash or secret printed. Do not claim the old first-install failure persists; its exact original cause remains undetermined, but the patched startup readiness mechanism passed physically.

Canonical source/invariants now mark `gateway_deployed=true` and `physical_8798_acceptance_passed=true` (LOCAL ONLY). Crucially, **no new Cloudflare hostname, DNS/route, Worker Secret or PWA release has been activated**. Next step is **ask owner approval for one new Published application route** on EXISTING `magnetra-btdigg-rock64` tunnel: `magnetra-rock64.alexlab.media` -> `http://127.0.0.1:8798`. Existing BTDigg `btdigg-rock64.alexlab.media` -> `http://127.0.0.1:8796` must be untouched. Do not create a new tunnel, rotate token, add unrelated services, or repeat local 8798 install. After explicit route approval, verify public HTTPS and 401 unauthorized; only afterward evaluate isolated Worker->Tunnel 1042 risk, and obtain further consent before Worker secret and protected production `[deploy-pwa]`. Maintain all 46 indexers.


## 2026-10-16 — CLOUDFLARE ROUTE CONFIRMED; HTTPS 401/TLS PASS; ROCK64 A-RECORD LOOKUP PENDING (LATEST)

With owner approval, the Cloudflare Dashboard now visually confirms TWO published applications on ONE existing `magnetra-btdigg-rock64` tunnel. Old `btdigg-rock64.alexlab.media` -> `http://127.0.0.1:8796` preserved; new `magnetra-rock64.alexlab.media` -> `http://127.0.0.1:8798`. Proxied Cloudflare CNAME entries for both visibly point to the same existing tunnel identifier. User's actual Rock64 `curl --resolve` test, with Cloudflare edge IPv4 `188.114.96.12` and `188.114.97.12`, returned **HTTP 401 and TLS verify 0** for the new hostname on each; old public BTDigg regular IPv4 returned HTTP 401. 8798 loopback remained 401 no-auth. Public host header/TLS and unauthorized response confirmed without using or disclosing any credential. **NOT proven:** public authenticated response or any Worker->Tunnel fetch.

Rock64 resolver `getent ahostsv4` currently returns no IPv4 for new hostname; `getent ahostsv6` returns Cloudflare IPv6 for both hostnames, and IPv6 HTTPS fails equally for both. Cause unknown: distinguish local resolver filtering/caching vs public A-record behavior using READ-ONLY DoH, without changing host DNS, routes, firewall or other projects. `dig` missing; do not install just for this task.

Update invariant status `new_dns_route_created=true`, `public_unauth_https_401_verified=true`; `gateway_deployed=true`, `physical_8798_acceptance_passed=true`, `new_tunnel_installed=false` and `worker_activated=false`. Do not direct the owner to add the route a second time or reinstall 8798. NEXT after DNS diagnosis is a safely **isolated** Worker->Tunnel same-zone/1042 probe, not a production deploy or Worker Secret activation. Existing `worker/src/eztv-rock64.mjs` sends only canonical EZTV filtered calls to the new fixed hostname when `MAGNETRA_GATEWAY_TOKEN` exists; production remains gated. Keep 46 original indexers and all protected services unchanged.


## 2026-10-16 — DNS PUBLIC A/AAAA CONFIRMED; Rock64 default IPv4 lookup still empty (LATEST)

Owner executed a real DNS-over-HTTPS GET from Rock64 straight to Cloudflare 1.1.1.1 using `curl --resolve cloudflare-dns.com:443:1.1.1.1`, checking `magnetra-rock64.alexlab.media` A and AAAA. Both responses had `Status=0`. A-record answer: `188.114.97.7`, `188.114.96.7` (TTL 300). AAAA answer: `2a06:98c1:3121::7`, `2a06:98c1:3120::7` (TTL 300). Ordinary `getent ahostsv4` was still EMPTY on that Rock64 host. Therefore public DNS records **exist**, but the OS resolver path is anomalous; its precise root cause is unconfirmed. Cloudflare shared tunnel route was already visibly correct and no-auth HTTPS `curl --resolve` succeeded with 401/TLS=0 through two Cloudflare IPv4 edges. BTDigg still works; 8798 local source-positive acceptance was 53=53=53 identical magnets.

**Next immediate safe read-only step:** recheck `getent ahostsv4` after TTL, view `/etc/resolv.conf` nameserver configuration or optional `resolvectl` A response. No global DNS/firewall/VPN/Tailscale changes until cause known; no `dig` install needed. Then isolate Worker->Tunnel 1042 feasibility without activating production Worker or exposing bearer credentials. Tunnel routes and existing services must not be changed.


## 2026-10-16 — NORMAL DNS+HTTPS RESTORED; isolated 1042 probe staged, deployment NOT authorized (LATEST)

Latest owner terminal: normal Rock64 `getent ahostsv4 magnetra-rock64.alexlab.media` now returns `188.114.96.12` and `188.114.97.12`. `/etc/resolv.conf` -> `/run/systemd/resolve/stub-resolv.conf`, systemd-resolved DNS `127.0.0.53`. `resolvectl query --type=A` returns both IPs from local cache over `end0` in 9.4 ms. Normal `curl --noproxy '*' -4` new hostname HTTPS `/healthz` produced HTTP **401** via `188.114.97.12` without forcing edge IP. The missing A lookup self-resolved without any user network change; exact original cause unknown. There is **no outstanding DNS fix** or need to reinstall 8798/add tunnel route.

Scoped next-step code staged: `worker/probes/tunnel-1042-probe.mjs`, `worker/test/tunnel-1042-probe.test.mjs`, `worker/probes/README.md` are a standalone **no-secret, unauthenticated, fixed-URL 1042 diagnostic** with offline regression tests. Not imported by PWA; no Wrangler deploy config. Before REAL Worker same-zone execution, owner must explicitly approve a **temporary separately deployed Worker on an unused same-zone hostname**, within accepted plan limits; do not accidentally overwrite production Worker or existing tunnel hostname. The temporary Worker is NOT deployed by GitHub integration. `workers.dev` preview is not conclusive for same-zone 1042 restrictions; 401 only verifies an unauthenticated Worker-to-host call. Cleanup after test. Production `MAGNETRA_GATEWAY_TOKEN`, 46 indexers, deployed PWA and global `global_fetch_strictly_public` remain untouched. After true Worker transport confirmation, separately authorize credential integration and production protected `[deploy-pwa]` release.


## 2026-10-16 — iPhone cannot paste Cloudflare Worker Quick Edit; native Git Builds route staged (LATEST)

Physical user photo shows temporary Cloudflare Worker `magnetra-1042-probe` already created, Quick Edit contains a blank JavaScript line after selecting existing Hello World; Monaco popup: `Unable to read from the browser's clipboard`. Do not ask the owner to repeat long iOS paste. **No real 1042 test has been executed**. An attempt to write a GitHub Actions deployment workflow failed under tool safety controls; do not claim it exists or attempt indirect workarounds. Instead a standalone config `worker/probes/wrangler.jsonc` plus offline contract test/strict invariant guard is being committed to the GitHub repository via PR/CI. Exact config: name `magnetra-1042-probe`, main `tunnel-1042-probe.mjs`, temporary custom domain `magnetra-probe.alexlab.media`, `workers_dev=false`, no production routes/secrets. `worker_1042_git_build_config_staged=true` is staged only.

After green CI + merge, guide the owner on iOS through **Cloudflare Workers & Pages → magnetra-1042-probe → Settings → Builds → Connect**, select GitHub repo `Zuzuitu/AlexLab-Magnetra`, branch main and root `worker/probes` (not root/worker), build/deploy config with `npx wrangler deploy`. Cloudflare may only deploy after a subsequent commit push; require actual log evidence, no guess. If worker Custom Domain `magnetra-probe.alexlab.media` is available, it can be provisioned via reviewed config. Do not touch `index.alexlab.media`, `magnetra-rock64.alexlab.media`, original BTDigg tunnel, or production secrets. After one redacted test, disconnect Git and delete temporary Worker/domain.


## 2026-10-16 — Owner clicked CONNECT for temporary Worker Git Builds; first build requires main push (LATEST)

Latest owner Cloudflare Dashboard screenshots show the newly created temporary Worker `magnetra-1042-probe` Git-connected to `Zuzuitu/AlexLab-Magnetra` branch `main`, root `worker/probes`, deploy command `npx wrangler deploy`, optional build command blank, build variables/secrets empty, preview disabled. Cloudflare explicitly says **"You can now push a commit to your Git repository to start your first build"**. The selected Build API token's label is `calcidatum-build-token`; do not infer its permissions or change another project's settings without a precise build error. **No first build result or 1042 test was supplied yet.**

In-progress owner-approved first-deploy trigger: small checkpoint change to `worker/probes/README.md`, plus canonical docs and guarded config, through PR, all-green GitHub CI and squash merge. A new commit on main should trigger the existing Git-connected *temporary* Cloudflare Worker. Ensure Cloudflare Built/Deployed status and custom domain `magnetra-probe.alexlab.media` are actually confirmed before asking user to query `/probe`. Do not touch production PWA, existing tunnel routes, credential files or 46 indexers. After one redacted test, disconnect Builds/delete temporary Worker and hostname.


## 2026-10-16 — REAL WORKER→TUNNEL 1042 probe PASS, temporary Worker cleanup still pending (LATEST)

Owner proved the temporary custom-domain Cloudflare Worker is live: `curl --noproxy '*' -4 https://magnetra-probe.alexlab.media/probe` from Rock64 returned HTTP 200, TLS verify result 0, JSON content-type and 50-byte body. Sanitized parsed JSON: `{"result":"PASS_UNAUTHENTICATED_401","status":401}`. DNS A returned `104.21.62.69`, `172.67.221.15`. This is **actual no-auth Worker→existing tunnel→gateway 8798 /healthz reachability within alexlab.media without error 1042**, not a mock. Earlier Safari `probe.txt` looked empty, but Rock64 test resolves that question. Earlier separate physical local original EZTV → 8797 → 8798 proved identical 53/53 magnet multisets. Neither test proves **authenticated Worker source-fetch** yet. DO NOT change protected production Worker based only on unauthorized test.

The **owner has NOT reported disconnecting the temporary Worker's Git Builds or deleting the temporary Worker/custom-domain**. Next step: guide owner on iPhone to `magnetra-1042-probe` Settings → Builds → Disconnect, then delete ONLY temporary Worker `magnetra-1042-probe` and ensure its single custom domain `magnetra-probe.alexlab.media` is removed, without touching `alexlab-magnetra`, `index.alexlab.media`, `magnetra-rock64.alexlab.media`, `btdigg-rock64.alexlab.media` or existing tunnel. The checkpoint PR documenting success is deliberately **left unmerged until cleanup** to avoid auto-redeploying the Git-connected temporary Worker with another main push. Thereafter merge once CI green and owner confirms cleanup. Status: live unauth 1042 probe PASS; authenticated Worker fetch NOT tested; Worker production secret/deploy NOT activated. Further secret+production activation requires separate explicit approval and safe test.


## 2026-10-16 — owner reports temporary probe teardown DONE; proceed to guarded auth plan (LATEST)

In direct response to instructions to (1) disconnect Git Builds for temporary `magnetra-1042-probe`, (2) remove only temporary `magnetra-probe.alexlab.media` domain, and (3) delete only `magnetra-1042-probe`, the owner answered **"Gata"**. Mark teardown as **owner-confirmed**, not independently Cloudflare-verified. Hence `worker_1042_git_connected=false` and `worker_1042_temporary_worker_cleanup_confirmed=true` in canonical guard; `worker_1042_live_test_passed=true` keeps successful live no-auth result. Do not re-create temporary Worker or reuse its old URL. The real evidence was 200/TLS0 at `/probe`, JSON `PASS_UNAUTHENTICATED_401`/401, showing no 1042 on this path. Earlier Rock64 exact authentic 53/53 multiset equality remains separate. **Authenticated Worker-to-8798 source fetch remains NOT tested.**

Now merge the latest checkpoint PR after all required CI passes, then obtain **new explicit user approval** for production secret setup and the safe staged authenticated Worker test. Never print/copy the bearer token to chat, shell logs, GitHub repository, frontend or public temporary workers. Preserve current production `alexlab-magnetra` Worker and 46 original indexers unless activation and its deployment are separately authorized. Existing BTDigg tunnel remains unchanged. The same-zone no-auth test is not proof of final EZTV magnet parity from the Worker.


## 2026-10-16 — user authorized GENERAL 46-indexer recovery; Phase 1 universal engine staged (LATEST)

Explicit user correction: **do NOT stop after getting EZTV working**. The objective is to recover as many as technically/legitimately verifiable of the original 46 indexers directly within the Magnetra PWA, without manual browser handoff; owner said "Da-i drumul atunci" to proceed with generalized work.

GitHub Phase 1 PR `feat/provider-wide-recovery-triage-v1` stages `worker/src/recovery-strategy.mjs`, `scripts/recovery-plan.mjs`, complete tests, guarded config and `docs/PROVIDER_RECOVERY_PLAN.md`. Plan covers exact 46 current catalogue IDs, uses dated 13/12/21 one-query snapshot rather than inventing uptime, and adds per-source read-only triage metadata and `GET /api/recovery-plan` (NOT yet in production). It explicitly classifies BitSearch/OxTorrent/Torrent9 redirect candidates, physical Rock64 403 sites 1337x/BT4G/Ext, Torrentz transport failure, rate-limit stop and sample-dependent empty lists. Gateway eligible only BTDigg (independent existing 8796) and EZTV (real local original→8797→8798 53 parity); no credential or physical 8798 route expansion. Both future Worker EZTV authenticated E2E and protected PWA deploy require separate concrete gates; `worker_activated=false`.

Next after green CI/merge: owner-run one read-only pinned checkout `python3 -B rock64/probe-redirect-candidates.py` for exactly three fixed HTTPS candidate hosts (no redirects, no token/magnets, bounded 8s/256KB each), then verify genuine listings/parser/detail handoff. Do not install/restart Rock64 units or tunnel. For providers that Rock64 ALSO blocks, do not pretend a residential gateway helps. Only providers with real positive Rock64-only upstream evidence qualify for future narrowly allowlisted 8798 routes. All original 46 IDs preserved.


## 2026-10-16 — Physical redirect-candidate results, original selector → magnet detail proof next (NOT activated)

Owner ran merged `main` revision `7685641735669ec57e463cf0447f9cac223b4fbb` from physical Rock64. `scripts/check-project-invariants.py` passed. Exact fixed-host, no-redirect `rock64/probe-redirect-candidates.py` output: **OxTorrent `www.oxtorrent.co` HTTP 200 with `LAYOUT_HINT_ONLY`, 3 `<tr>` table rows and 0 direct magnet anchors; Torrent9 `www7.torrent9.to` HTTP 200 with `LAYOUT_HINT_ONLY`, 4 table rows and 0 direct magnet anchors; BitSearch `bitsearch.eu` HTTP 520 `HTTP_ERROR`**. These were real Rock64 results, not a Worker or CI fixture. **Neither OxTorrent nor Torrent9 is yet verified to return source-owned result rows or valid magnets**, and HTTP 520 must not be auto-retried. The original Android implementations for both sites use original `table > tbody > tr`, `td:nth-child(1)>a` search→details and a magnet selector on the **details page** (OxTorrent `div.btn-magnet > a`, Torrent9 `a[href^="magnet:"]`).

This PR stages strictly bounded, read-only `rock64/probe-result-details.py` for **exactly two pinned alternative hostname URLs** (OxTorrent/Torrent9) with benign query `ubuntu`: original-structure first-column result rows; fixed origin and same tested hostname detail URL allowlist; 1 search GET and at most 1 selected details GET per source; no URL/host input, no redirect following, no proxy environment, max 8 seconds and 256 KiB each; a well-formed BTIH magnet anchor is checked in memory without logging names, URLs, hashes, magnets, bodies, or retrieving .torrent files. No source-host origin migration is automatically authorized; a valid magnet-shaped anchor is NOT proof of downloadability. Dedicated offline Python regression tests and existing GitHub gates must pass before owner may execute the one-time physical diagnostic.

**NEXT GATE:** After protected branch CI and merge, owner runs one read-only `python3 -B rock64/probe-result-details.py` on pinned Rock64 GitHub checkout and returns sanitized JSON. Based on real results, implement exact-original provider parsing/origin changes on a separate PR only if source owned valid rows + details magnet are demonstrated; do not make generic 8798 proxy, change either Cloudflare tunnel application or production Worker, activate secret, reroute BitSearch or claim new indexers are healthy. Current worker_activated remains false, production provider-audit historical 13/12/21 unchanged.


## 2026-10-16 — OxTorrent + Torrent9 real search→details magnet proof, source-owned 8798 integration STAGED (NOT DEPLOYED)

Owner ran **real Rock64 read-only probe** at pinned GitHub commit `dd4666b04d76ee924df6a9aca0ba8445a9725ec4`. Results: `oxtorrent` alternate `www.oxtorrent.co`: HTTP 200 search, 3 real query-matching `ubuntu` rows, 3 same-source details candidates, first details HTTP 200 and a well-formed BTIH magnet anchor found. `torrent9` alternate `www7.torrent9.to`: exact same 3 query-matched rows/3 detail candidates/one HTTP 200 details magnet anchor. **No .torrent/magnet download or proof of actual swarm connectivity.** Earlier BitSearch alternate `bitsearch.eu` yielded HTTP 520 and remains excluded; other 44 indexers remain untouched. This evidence *does* justify a guarded new backend for these two sources only.

New staged code: `rock64/magnetra_html_egress.py` defines **two hardcoded HTTPS upstream hosts only**, search paths `/recherche/<encoded q>` and `/search_torrent/<encoded q>.html`, detail paths only `/torrent/<numeric-id>/<slug>`. Unprivileged source traffic has no proxy-env, redirects or retries, max 8 sec and 256 KiB/response, no token forwarding, no magnet/file download, no source HTML or URL logging. `rock64/magnetra_gateway.py` extends the existing **authenticated 8798 dispatcher** from the single EZTV path to exact `/v1/oxtorrent/html` and `/v1/torrent9/html` with `mode=search|detail` strict parameter allowlist. No generic proxy, no additional tunnel or route. Only HTTP 200 genuine HTML pages are relayed; upstream 403/429/504 remain errors. `rock64/upgrade-magnetra-gateway.sh` is **owner-triggered only** and designed for preflight/rollback of the *existing* 8798 script and new module, explicitly preserving 8796/8797 service configurations and credentials. Already installed 8798 must NOT be subjected to the original first-install script.

Worker stage: `worker/src/legacy-specs.mjs` pins the two *physically verified* canonical alternate hosts, leaves original selectors intact; `worker/src/html-rock64.mjs` creates an **optional** source-only fixed URL→8798 mapped fetcher using the existing server-side `MAGNETRA_GATEWAY_TOKEN`, never the frontend. `worker/src/index.mjs` uses it for search **and deferred details→magnet** only for OxTorrent/Torrent9 when secret exists; all other indexers use existing transport. Without a secret, no tunnel request. PWA behavior and 46 source IDs remain unchanged. No production Worker secret is activated, and no protected PWA deployment is tagged in this PR.

State of actual rollout **ON 2026-10-16**: `html_8798_implementation_staged=true`; `html_8798_physical_update_confirmed=false`, `html_authenticated_worker_e2e_passed=false`, `worker_activated=false`, `provider_recovery_v1.production_deployed=false`. Existing physical 8798 is unchanged, current production PWA remains unchanged, historical one-query 13/12/21 audit still the true recorded production snapshot. After 4/4 CI and merge: separately owner-run *pinned reviewed* source-only 8798 upgrade, verify service and source HTML parity, then explicitly approve safe Cloudflare production secret/deployment and test end-to-end before claiming either provider recovered in PWA. No paid upgrades or global Worker compatibility flag changes.


## 2026-10-16 — Physical 8798 upgrade restart race; rollback physically verified; bounded readiness patch staged (LATEST)

Owner ran merged `main` PR #63 commit `f9e57888c579368eee9b86a98c92dc9cba4350ce` via guarded one-time root invocation of `rock64/upgrade-magnetra-gateway.sh --install`. Code/invariant check passed, all **85 Python regression tests** passed, **PREFLIGHT_OK** confirmed unauthed HTTP 401 on original localhost 8796/8797/8798. After `systemctl restart magnetra-gateway.service`, the first immediate post-restart 401 check hit `ConnectionRefusedError: [Errno 111]`, and script triggered its rollback. The original v#63 script used Type=simple and an immediate single HTTP connect, creating a startup readiness race. The traceback does not name the failing port; since only 8798 was restarted, 8798 is the leading explanation, not an absolutely demonstrated root cause.

Owner independently executed read-only post-rollback diagnostic: four services `magnetra-gateway`, `magnetra-eztv`, `magnetra-btdigg`, `magnetra-btdigg-tunnel` all `active`; `NRestarts=0`, `ExecMainStatus=0`, `ActiveState=active`, `SubState=running`; loopback 8796, 8797, 8798 each HTTP 401; `/opt/magnetra-gateway/magnetra_html_egress.py` **ABSENT** (expected post-rollback); last 30 service journal entries only clean start/stop, no traceback. Thus old 8798 and old credential protection are physically intact, no HTML provider rollout completed, and no tunnel/production Worker changes occurred. Do not repeat the old installer.

New `rock64/wait-magnetra-8798.py` stages a strict maximum 12-second **local-only** readiness wait on `127.0.0.1:8798/healthz` accepting only HTTP 401; retries ONLY transient local TCP refused/reset/error while unit binds, immediately fails an unexpected HTTP response, never retries source 403/429 or content. Updated existing one-time upgrade performs this check **after new version restart** and **after rollback restart** (output clearly distinguishes `ROLLBACK_VERIFIED` vs restoration not health verified). Independent old 8796 and 8797 401 gates retained. Offline mocked tests simulate immediate success, two refused connects then 401, hard HTTP 200 failure and persistent refusal/deadline; CI syntax and invariants guard readiness calls. Canonical state: `html_8798_startup_readiness_patch_staged=true`; `html_8798_owner_rollback_verified=true`; `html_8798_physical_update_confirmed=false`; `worker_activated=false`; `html_authenticated_worker_e2e_passed=false`. The new script has NOT been physically run and no production activation or secret setting occurred.

Only after **PR CI green + merge** supply owner a commit-pinned checkout of the updated `--install` script. Do not run old checkout. New upgrade must pass local 401 readiness, both HTML real-source search→details magnet acceptance, and BTDigg/EZTV preserved. If any error, STOP and inspect instead of repeating blindly; keep Cloudflare Worker PWA off until an additional explicit gate.


## 2026-10-16 — PHYSICAL 8798 upgrade successfully installed, 2/2 real source HTML→magnet acceptance PASS (LATEST)

Owner ran the pinned merged GitHub commit `60e2d250e318bf6eca65b5ad7acb55f62d378125` guarded central upgrade on physical Rock64 Armbian. Exact owner-provided terminal evidence:
- `Project invariant check PASSED`; **92 Python unit tests OK**.
- `PREFLIGHT_OK: existing 8796, 8797, 8798 authentication intact`.
- `POST_RESTART_READY: loopback 8798 responded HTTP 401`; this proves the bounded startup-readiness PR #64 patch fixed the practical install-blocking race during the successful attempt.
- `POST_INSTALL_OK: BTDigg 8796, EZTV 8797 and central 8798 each require authentication`; all four service components were protected in the upgrade preflight; no tunnel edits.
- Authenticated physical **8798** acceptor `check-magnetra-html.py` verified both real providers (not mocks): OxTorrent search HTTP 200, **3** query-matching Ubuntu results, selected details HTTP 200, valid BTIH magnet anchor; Torrent9 search HTTP 200, **3** query-matching results, selected details HTTP 200, valid BTIH magnet anchor; final `{"result":"PASS","checked_sources":2}`.
- Installer completed: `PASS: isolated 8798 code upgraded. EZTV/BTDigg/tunnel not changed.` No observed rollback required on this second attempt.
- Three printed `STOP: expected --post-restart or --rollback, read-only.` lines were produced intentionally by negative-argument offline unit test cases, **not** by live installer logic. This PR redirects that expected stderr into the test's capture buffer so future runs show no alarming false STOP text.

Updated machine-readable state: `html_8798_physical_update_confirmed=true`, `html_8798_real_source_acceptance_passed=true`, `html_8798_physical_acceptance_providers=["oxtorrent","torrent9"]`; existing `worker_activated=false`, `html_authenticated_worker_e2e_passed=false`, `provider_recovery_v1.production_deployed=false`, `new_tunnel_installed=false`. Do NOT misrepresent verified backend magnets as end-user PWA recovery yet, nor infer actual torrent download/connectivity.

**NEXT:** Use existing production Cloudflare `alexlab-magnetra` Worker/secret model, without disclosing the live private `MAGNETRA_GATEWAY_TOKEN` to GitHub/chat/commands logs. Production Worker has three optional shared-gateway source adapters (EZTV, OxTorrent, Torrent9) staged on main; secret is still NOT confirmed set, and no `[deploy-pwa]` or `workflow_dispatch` should run until source-specific authenticated Worker→8798 E2E rollout steps and rollback have been reviewed. Production domain `index.alexlab.media`, old BTDigg 8796 cloudflared route, EZTV 8797, other services and original 46 provider IDs must remain protected. Run real end-to-end single-query checks and full 46 provider audit after controlled release. Do not claim 3 providers recovered if checks are missing or stale.


## 2026-10-17 — Cloudflare secret draft saved, controlled **code upload only** prepared (LATEST)

Confirmed from owner's screenshot: active Cloudflare Worker `alexlab-magnetra` version `a9df4429` 100% traffic/0% displayed errors. Owner added central secret `MAGNETRA_GATEWAY_TOKEN` with **Save version**, creating distinct **undeployed secret-only** version `ce808b27`. Only prior `BTDIGG_GATEWAY_TOKEN` existed. **Do not deploy ce808b27**: it may contain old Worker code. Cloudflare `wrangler deploy` would send a new version directly to 100%, so stage the main Worker code instead via `wrangler versions upload`. Preserve existing BTDigg secret and 46 providers.

Implementer staged a **manual-only GitHub Action** `.github/workflows/stage-magnetra-worker.yml` in a PR with the hard guard `cloudflare_worker_stage`. It checks canonical Worker `alexlab-magnetra`, asset binding, the production domain and both secret **names** (not values) in an ephemeral config; tests then `wrangler versions upload --keep-vars`, which creates a version without production traffic. No GitHub Action is executed automatically on merge; owner must manually Run workflow under GitHub Actions on main. Its result, code version ID, and retained binding names must be reviewed before allowing any canary or deployment. If the secret exists only on an undeployed version and does not satisfy Wrangler's required secret binding check, upload fails safely: do NOT bypass the guard.

Previous owner physical Rock64 8798 genuine 2/2 OxTorrent and Torrent9 HTTP 200 search/detail magnet pass is verified; this does **NOT** imply PWA Worker success. Production Worker secret activation, Worker→Tunnel authenticated E2E and all 46 indexer live audit are still UNVERIFIED. State target: current active `a9df4429` must stay 100% until explicit evidence; `ce808b27` remains draft secret-only. Do not touch existing Tunnel/DNS/Btdigg/other services; do not paste secrets.


## 2026-10-17 — Manual Worker versions upload succeeded via GitHub Action; ID and secret bindings UNVERIFIED (LATEST)

Owner uploaded a screenshot of a green completed GitHub Actions run: **Stage Magnetra Worker (NO DEPLOY)**, **run #1**, via manual dispatch, branch **main**, duration **23 seconds**. GitHub connector verified PR #66 merged to main at commit **`2428f0120b213f706d9e6e0ae994c248d80c6c12`**. The merged workflow is manual-only and runs `wrangler@4.102.0 versions upload --keep-vars` after checking original Worker name/route/assets, all Worker tests and the two required **secret binding names**; it never runs production `wrangler deploy`. Thus the screenshot supports a successful **upload-only workflow**, **not** authenticated live Worker→8798, Cloudflare binding details or deployment to production.

Previous owner's Cloudflare screenshots: live rollback/reference version **`a9df4429`** at **100% traffic**, 0% errors displayed before manual action; after **Save version** for secret `MAGNETRA_GATEWAY_TOKEN`, undeployed old-code/secret-only draft **`ce808b27`** was created. **Do not deploy ce808b27**. The production active percentage has NOT been rechecked after latest upload, nor is the new uploaded Worker version's Cloudflare ID visible yet. **Do not invent its ID or claim full PWA activation**.

All Rock64 gateway results remain physically true: port 8798 HTTPS same-tunnel uses authorization; real source OxTorrent & Torrent9 search→details magnet **2/2 PASS**, EZTV separate original→8797→8798 **53 exact**; 8796/8797/8798 unauthed `/healthz` HTTP 401. Protected 46-provider code, BTDigg separate route and tunnel unchanged.

Read detailed owner handoff at **`docs/CHECKPOINT_2026-10-17_CLOUDFLARE_STAGE.md`**. The machine-readable checkpoint explicitly records `worker_code_version_uploaded=true` on screenshot proof, while `new_code_version_cloudflare_id_verified=false`, `new_code_version_required_bindings_verified=false`, `active_100_percent_after_stage_reverified=false`, `worker_code_version_activated=false`, `staged_worker_authenticated_test_passed=false`, `worker_to_tunnel_authenticated_e2e_confirmed=false`, `shared_magnetra_gateway.worker_activated=false`, `provider_recovery_v1.production_deployed=false`.

**Next action requires user's Cloudflare Deployments screenshot after upload**: show current Active deployment version/100% plus the newly uploaded code-version row `Magnetra 46-provider stage: EZTV/OxTorrent/Torrent9 8798, no traffic`. Inspect detail page for new version code/build and binding **names** `BTDIGG_GATEWAY_TOKEN` & `MAGNETRA_GATEWAY_TOKEN` without reading values. Do **NOT** press Deploy on either new version yet. Plan safe canary only after eligibility/capabilities are verified; get explicit approval before percentage shift, preserve rollback `a9df4429`. No old `deploy-pwa.yml` manual dispatch, no automatic `[deploy-pwa]` commit. See checkpoint for entire project.


## 2026-10-17 — Live Cloudflare screenshot + verified staged Version ID (post-PR #67)

GitHub Actions run #1 logs on `main` at SHA `2428f0120b213f706d9e6e0ae994c248d80c6c12` show **Worker Version ID `249d6767-f4dc-4f4d-bbf7-f57bea2e5554`**, with Wrangler 4.102.0 `versions upload --keep-vars`, **96/96 Worker tests PASS** and asset binding `ASSETS` visible at upload. PR #67 documenting earlier staging was merged at `e31f1fac0e30e0a7abbd2f2bc1a01bba9a457aaa`.

User Cloudflare screenshot at ~16:37 local time: deployment `a9df4429` **remains at 100% production traffic**; staged version `249d6767` listed but **not active**; secret-only `ce808b27` still inactive. Second screenshot at ~16:42 local time: **Production Settings lists two secret names** (BTDIGG and MAGNETRA gateway); **this does not verify that both are bound in the specific staged version**. Production `workers.dev` and Preview `workers.dev` are both OFF; the canonical custom production domain `index.alexlab.media` remains. "No connected bindings" in Settings must not be interpreted as proof that `ASSETS` is missing; Worker upload output independently showed `env.ASSETS`.

The new **manual-only, read-only** workflow `.github/workflows/inspect-magnetra-cloudflare-version.yml` uses existing GitHub-held API credentials and two Cloudflare **GET** endpoints to inspect specific version binding *names/types* and current deployment shares. It does not expose raw responses, secrets or magnet URLs, and does not upload/deploy Worker code. **As of this documentation, workflow has NOT yet been executed and version-specific binding verification is NOT PASS.** Its results must be reviewed before a safe isolated E2E plan.

There is no new Rock64 installation, tunnel or DNS change, no change to BTDigg and no production activation. Version URLs remain OFF because public previews would expose another entry point unless secured; do not enable automatically. Retain `a9df4429` as rollback while verified to be live, and never deploy secret-only `ce808b27`.

## 2026-10-17 18:06 Europe/Rome — Worker version binding audit PASS (LATEST)

**GitHub Actions run:** [Inspect Magnetra Cloudflare Version (READ ONLY) #1](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39047958484), manual workflow_dispatch on reviewed `main` commit `8ce9c9b2458dac8a0caa642997467fea48bc6e14`, complete SUCCESS. Job `117440400755` executes the **exact version** Cloudflare GET audit with 6/6 no-leak parser tests passing and no writes. Result lines: `VERSION_ID_MATCH: PASS`, `BTDIGG_GATEWAY_TOKEN: PASS`, `MAGNETRA_GATEWAY_TOKEN: PASS`, `ASSETS: PASS`, `ROLLBACK_ACTIVE_100_PERCENT: PASS`, `CANDIDATE_NO_TRAFFIC: PASS`, `STAGE_METADATA_GATE: PASS`. Candidate exact ID: **`249d6767-f4dc-4f4d-bbf7-f57bea2e5554`**. Thus **specific-version binding names/types verified**, and production deployment still targets historical `a9df4429` 100%. Log `CANDIDATE_HAS_PREVIEW: UNVERIFIED`; owner's previous Cloudflare Domains screenshot shows Preview URL toggle OFF.

**No end-to-end authenticated provider search yet.** `staged_worker_authenticated_test_passed=false`, `worker_to_tunnel_authenticated_e2e_confirmed=false`, `worker_code_version_activated=false`, `production_worker_promotion_completed=false`, `canary_rollout_approved=false`; no provider may be marked production-recovered based on this audit.

**Next gated approach (NOT EXECUTED):** Because Version URLs are OFF, Cloudflare [Version Overrides](https://developers.cloudflare.com/workers/versions-and-deployments/version-overrides/) can select the candidate only when it is included in the currently active deployment. Cloudflare supports a controlled deployment containing `a9df4429` at **100%** and candidate `249d6767` at **0%**, followed by an explicitly targeted `Cloudflare-Workers-Version-Overrides` request. This is a deployment configuration mutation despite 0% normal traffic and **requires explicit owner approval** and exact rollback preflight before use. Version override may not be applied; must verify invoked version, not mistake old Worker results for new candidate. No Preview URL exposure, no new tunnel, no secret output, no auto torrent downloading. If header override cannot be independently verified, STOP. Prepare a scoped E2E plan for authentic EZTV IMDb, OxTorrent/Torrent9 Ubuntu search plus deferred magnet resolution, BTDigg baseline and post-check audit of all 46 providers. If another safer supported isolated test path becomes available, assess first.

**Do not run:** `wrangler deploy`, promote/split, `[deploy-pwa]`, any traffic mutation, router/tunnel/Rock64 modification until separately approved. Preserve rollback `a9df4429` and don't activate secret-only `ce808b27`.


## 2026-10-17 — Explicit authorization for 100% old + 0% candidate E2E slot (NOT YET EXECUTED)

Owner explicitly confirmed the narrowly-scoped Cloudflare operation to create a **two-version deployment** with previous `a9df4429` at **100% normal traffic** and candidate **`249d6767-f4dc-4f4d-bbf7-f57bea2e5554` at exactly 0%**, only for targeted `Cloudflare-Workers-Version-Overrides` E2E testing. This approval does **not** authorize 0.01%, 1%, or any ordinary traffic to the new version, secret changes, other code deployments or general production promotion.

Official Cloudflare documentation at https://developers.cloudflare.com/workers/versions-and-deployments/version-overrides/ explicitly demonstrates a 0% candidate included in current deployment; Wrangler version deploy noninteractive accepts `<old-id>@100%` and `<new-id>@0%`. Cloudflare public API specification displays 0.01 as minimum; **if Cloudflare rejects exactly 0%, STOP safely, do not round up**.

The dedicated GitHub Actions workflow `.github/workflows/configure-magnetra-zero-percent.yml` is strictly **manual-only** on main and requires typed input `CONFIRM_OLD_100_NEW_0`. It revalidates exact Worker version, candidate binding names/types, current 100%-old deployment, full previous UUID retrieved from Cloudflare, then invokes pinned Wrangler 4.102.0 to request 100% old + 0% candidate. Postflight checks both exact percentages; if they deviate, it attempts bounded rollback to old 100%. On any missing proof, token/API error or concurrent deployment it stops rather than mutating/overwriting unrelated versions. Raw API outputs, Wrangler stderr, tokens and magnets are withheld from logs. Tests assert exactly 0% (never 0.01%). **The workflow has not been run yet, and the two-version slot is NOT verified configured.**

Previously [manual exact-version GET audit #1](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39047958484) passed for BTDIGG, MAGNETRA and ASSETS bindings and previous 100%-old only state. The candidate is not yet proven Worker→Tunnel→8798 authenticated, no EZTV/OxTorrent/Torrent9 PWA E2E success, and no production provider recovery can be claimed. Preview workers.dev remains off. Any later activation above 0% requires **new explicit owner approval** and live rollback verification.


## 2026-10-17 19:13 Europe/Rome — zero-percent Cloudflare workflow dispatch #2 skipped (authorization unconfirmed)

Owner triggered `Configure Magnetra 0 Percent E2E Slot (APPROVED)` twice: [#1](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39052675140) and [#2](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39052769455). Both are GitHub `workflow_dispatch` on `main`, completed with **job `configure` = SKIPPED**. GitHub API does not expose selected `confirm_zero_percent` input on these runs. Old job-level gate checked `github.ref == refs/heads/main && inputs.confirm_zero_percent == CONFIRM_OLD_100_NEW_0`; branch main is confirmed, so exact input/conditional evaluation remains unproven. **No Cloudflare step ran, no 100/0 deployment, no E2E.**

A minimal workflow patch moves the input check to an explicit first step so invalid/default `CANCEL` ends with a safe, explanatory error instead of silent SKIPPED; main-only job gating, mandatory `CONFIRM_OLD_100_NEW_0`, Python second guard and all Cloudflare preflight/rollback constraints remain. Run only after this change is merged with CI PASS. No automatic retries or deployment.


## 2026-10-17 19:24 Europe/Rome — authorized exact Cloudflare 100/0 deployment PASS, candidate E2E pending

Owner triggered [GitHub Actions Configure Magnetra 0 Percent E2E Slot #3](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39053562983), workflow_dispatch on main `9bdca3e1753e50d49c46a8e9fb5df5eae3de492c`. Run SUCCESS; real deployment phase (not mock tests) printed `PRECHECK_PASS`, `ZERO_PERCENT_ONLY`, `APPLYING`, `POSTFLIGHT_PASS: exact old 100% and candidate 0% verified by API`, and `OVERRIDE_SLOT_READY`. GitHub step and overall job both succeeded. Previous `a9df4429` remains 100% ordinary traffic; candidate exact `249d6767-f4dc-4f4d-bbf7-f57bea2e5554` is **present at 0% in current deployment**. No public-preview workers.dev, tunnel, secret or Rock64 changes. Invariants now record this actual postflight.

Cloudflare [Version Overrides](https://developers.cloudflare.com/workers/versions-and-deployments/version-overrides/) supports `Cloudflare-Workers-Version-Overrides: alexlab-magnetra="249d6767-f4dc-4f4d-bbf7-f57bea2e5554"` for a version included at 0%. **Override may silently not be applied**: successful HTTP 200 does NOT prove routing to candidate. Its documented safeguards require either per-invocation version observability or a differentiating code behavior. Existing candidate has no version-metadata response binding. Next test will require the legacy 100%-active API to return 404 for `GET /api/recovery-plan`, and override candidate to return 200 with all 46 recovery metadata records. If both return identical responses, STOP and mark `OVERRIDE_ATTRIBUTION_UNVERIFIED`; do not infer which version ran.

A newly staged **manual only, read-only** workflow `.github/workflows/test-magnetra-candidate-e2e.yml` first verifies through Cloudflare GET that the two-version deployment is still precisely 100%/0% and that candidate has `ASSETS` and both gateway secret bindings. Then it requires the candidate-only fingerprint, verifies 46 provider IDs, searches `ubuntu` from `oxtorrent` and `torrent9` (one query each), resolves one genuine same-origin details magnet per provider via `POST /api/resolve`, and checks `eztvx` by canonical IMDb `tt0460681` through the existing 8798 authenticated dispatch. It also makes at most one observational BTDigg query, never retries or downloads torrent payloads, never logs magnet strings, tokens, source HTML, raw upstream error responses or secret values. An absent/blocked upstream response remains **UNVERIFIED**, not fictional PASS; no updates to production source-health snapshot on an incomplete audit.

**The E2E workflow is not yet integrated or executed at this checkpoint.** New CI tests cover the version fingerprint, provider attribution, input approval, no-leak magnet handling, and exact 100/0 gate. No provider E2E is marked PASS yet. Promotion of the candidate above 0% still requires a separate explicit owner approval and guarded rollback.


## 2026-10-18 07:43 Europe/Rome — Real candidate E2E #1 PARTIAL, EZTV known-empty sample

Owner dispatched [Test Magnetra Candidate E2E #1](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39101511577) on reviewed main `1049c5895e9c77e9a32603913372278a9b3884a5`; workflow **FAILURE** only because last tested EZTV IMDb `tt0460681` returned **zero**. Job `117598567653` passed owner authorization, invariants, 9/9 offline tests and LIVE:
`CLOUDFLARE_VERSION_SLOT: PASS` old `a9df4429` 100% / exact candidate `249d6767-f4dc-4f4d-bbf7-f57bea2e5554` 0% plus all three bindings;
`OVERRIDE_ROUTING_FINGERPRINT: PASS` (baseline old /api/recovery-plan HTTP 404 vs candidate HTTP 200 and 46 entries);
`CANDIDATE_PROVIDER_CATALOG: PASS 46/46`;
`SEARCH_PASS_oxtorrent: 3` and `DEFERRED_MAGNET_PASS_oxtorrent`;
`SEARCH_PASS_torrent9: 3` and `DEFERRED_MAGNET_PASS_torrent9`.
Both are **genuine authenticated Cloudflare Worker candidate→8798 Tunnel/Rock64→real HTML source→detail→BTIH magnet PASS**. No raw tokens or magnets printed. No torrents downloaded. **BTDigg NOT tested**, because the old workflow stopped on EZTV first. No production promotion. The production percentage remains 100/0 as verified by that E2E preflight; no later deployment is claimed.

EZTV `tt0460681` (Supernatural) returned `stats.ok=true,count=0`, `errors=[]` at live candidate. This is **expected for the historical source**: physical Rock64 read-only source probe in `docs/PROJECT_STATE.md` (2026-10-14) explicitly saw exact echo IMDb `460681`, `torrents_count=0`, no `torrents` array. Local **53/53 authentic EZTV magnets** (2026-10-16) were proven for a DIFFERENT, genuine recent IMDb ID automatically chosen from source (ID not logged). Requiring positive rows for the known-empty `tt0460681` was a *test fixture / acceptance design error*, NOT evidence that Worker tunnel/auth failed.

Next bounded READ-ONLY workflow patch: treat historical `tt0460681` empty as an honest valid result, attempt one official recent-source GET with no credentials to obtain max two real source-positive IMDb samples; historically GitHub cloud egress was 403, so this can fail without asserting Rock64 is blocked. Fall back to four well-known series IMDb *candidate controls* (NOT guaranteed positive), query only via 0%-candidate header, validate same-source magnets and stop unverified if every exact IMDb sample is empty. Independently run BTDigg observational probe before EZTV. No retries, proxy changes, secret exposure, Worker code upload, production percentage shift or Rock64 changes. The static series IDs must NEVER be represented as observed positive without new live responses.


## 2026-10-18 11:52 Europe/Rome — Live E2E #2 partial: actual 8797 MIN_GAP=3 seconds identified; sanitized error pending

Owner executed [Test Magnetra Candidate E2E #2](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39117038271) on `main` `9f50eb8ac1ebef9684b1d329d663463f72f29cb1`. Job `117644818767` **failed** (not an activation or Worker deployment). Real log:
`CLOUDFLARE_VERSION_SLOT: PASS` old `a9df4429` 100%, candidate `249d6767` 0%; `OVERRIDE_ROUTING_FINGERPRINT: PASS`; `CANDIDATE_PROVIDER_CATALOG: PASS 46/46`; OxTorrent **3 results** plus genuine deferred BTIH magnet PASS; Torrent9 **3 results** plus genuine deferred BTIH magnet PASS. The new BTDigg observational request returned `UNVERIFIED (SEARCH_UPSTREAM_ERROR_btdigg)`. EZTV known-empty `tt0460681` returned a genuine zero without provider errors; the independent **direct original EZTV API on GitHub Actions** returned **two source-positive recent IMDb identifiers with valid magnets**, identities redacted. First recent IMDb through candidate Worker returned `SEARCH_UPSTREAM_ERROR_eztvx`, and the previous diagnostic aborted. Thus authenticated **positive** EZTV and BTDigg are **still not proven**, even though original source recent discovery was positive.

**Code-derived plausible root cause for EZTV:** existing isolated physical `rock64/eztv_gateway.py` implements `MIN_GAP = 3` seconds, enforced by `Provider.search` with **HTTP 429** for a new uncached IMDb too soon after the previous request. The diagnostic first requested the known-empty `tt0460681` and immediately a recent positive IMDb, which can violate the 3-second floor. However the old diagnostic swallowed error `code`, so rate-limit attribution is **HYPOTHESIS, NOT YET CONFIRMED**. No gateway changes, no retries on 429 and no lowering of rate limit is justified. BTDigg failure mechanism also remains unverified.

**Isolated PR patch staged, not deployed:** remove the unnecessary live historically empty sample before positive probe (its real zero was confirmed in #2); select up to two genuine source-owned IMDb samples from a single bounded recent EZTV GET, and only when needed fall back to two *unverified* static TV IDs. For distinct planned samples, wait `3.5` seconds after an empty response before next (not a retry); stop immediately on 429/upstream error. Capture only allowlisted public Worker error codes and bounded HTTP status, never raw strings, links, credentials or magnet values. Default new workflow mode `FOCUSED_GATEWAYS` only checks still-verified Cloudflare version 100/0, 46 catalog entries, one BTDigg observation and source-specific EZTV positive evidence; previously E2E-verified HTML providers will **not** be retested unless manually choosing `FULL_CANARY_AUDIT`. Existing output flags for 100%-old prod and 0%-candidate are maintained; **no promotion is authorized**. New offline tests assert no known-empty prelude, minimum-gap spacing, no auto-retry after 429, safe code sanitization and focused-scope no unnecessary upstream requests.


## 2026-10-18 12:28 Europe/Rome — Candidate E2E #3 SUCCESS: real EZTV 29 magnets; BTDigg source 504 observational

**LATEST authoritative live evidence:** owner manually ran [Test Magnetra Candidate E2E (READ ONLY) #3](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39119359606), GitHub Actions on exact reviewed main SHA **\`78dd5519a7d4d891c4840756b22b6f0f16dfc597\`**. Entire GitHub workflow and all job steps **SUCCESS**. This latest run supersedes previous #2's EZTV positive E2E uncertainty. No Cloudflare deployment mutation occurred.

Actual live job \`117651596145\` log (distinguish from 19 offline unittest fixture lines):
- \`MANUAL_READONLY_E2E_GATE: PASS\`, project invariant PASS and **19/19 offline tests PASS**.
- \`CLOUDFLARE_VERSION_SLOT: PASS (old 100%, candidate 0%, bindings PASS)\`: existing production Worker \`a9df4429\` remains at **100% normal traffic**, candidate exact \`249d6767-f4dc-4f4d-bbf7-f57bea2e5554\` included at **0%**, with required \`ASSETS\`, \`BTDIGG_GATEWAY_TOKEN\`, and \`MAGNETRA_GATEWAY_TOKEN\` bound.
- \`OVERRIDE_ROUTING_FINGERPRINT: PASS (baseline 404, candidate 200 + 46 entries)\`: candidate version override **genuinely selected** rather than silently ignored. \`CANDIDATE_PROVIDER_CATALOG: PASS 46/46\` means 46 IDs in catalog, **NOT** 46 healthy/e2e source providers.
- Test scope \`FOCUSED_GATEWAYS\` intentionally did **NOT** repeat OxTorrent and Torrent9 E2E. Previous real #1 and #2 runs each verified **3 genuine original query results and 1 deferred BTIH magnet per source** through authenticated Worker→tunnel→Rock64 8798.
- **BTDigg**: \`BTDIGG_CANDIDATE_OBSERVATION: UNVERIFIED (SEARCH_UPSTREAM_ERROR_btdigg_BTDIGG_SOURCE_TIMEOUT_HTTP_504)\`. Only **one** BTDigg query; status explains Rock64 BTDigg **source timeout**, **not** demonstrated bad tunnel, token or BTDigg-wide persistent outage. Don't claim BTDigg E2E positive or regress prod. Its prior protected 8796 and tunnel must remain unchanged. No auto retry.
- **EZTV genuine positive:** \`EZTV_RECENT_DISCOVERY: 2 original IMDb IDs with valid source magnets (identities withheld)\`; source-positive recent IMDb selected. The script **does not** query historically empty \`tt0460681\` as a live prelude; it respects the physical 8797 \`MIN_GAP=3\` seconds anti-burst policy (two different planned samples separated by 3.5 seconds only if needed; no retry after 429). Live log: \`SEARCH_PASS_eztvx: real response; 29 source-attributed results\`, \`EZTV_AUTHENTICATED_POSITIVE_GATE: PASS (29 genuine source results; IMDb withheld)\`; 29 genuine validated BTIH magnet-bearing rows through **candidate Cloudflare Worker → existing shared Tunnel → authenticated Rock64 8798 → EZTV service 8797 → official original EZTV API**. A successful later test after pacing is NOT proof the prior specific error was HTTP 429, because the old test redacted the actual error code. \`eztv_rate_limit_as_root_cause_confirmed=false\` remains.
- \`E2E_GATE_RESULT: PASS (stage candidate, scope=FOCUSED_GATEWAYS, NOT normal production traffic)\`. Candidate's **EZTV, OxTorrent and Torrent9** have positive authenticated real E2E evidence; BTDigg still requires separate investigation and full 46-provider functional regression sweep is NOT complete.

Machine-readable stage records \`staged_worker_authenticated_test_passed=true\`, \`worker_to_tunnel_authenticated_e2e_confirmed=true\` specifically because **these three** original providers passed (recorded in \`candidate_e2e_verified_provider_ids\`), not because all 46 were healthy. \`candidate_all_46_providers_e2e_verified=false\` and \`candidate_btdigg_positive_e2e_verified=false\`; \`production_worker_promotion_completed=false\`, \`worker_code_version_activated=false\`, \`canary_rollout_approved=false\`, \`provider_recovery_v1.production_deployed=false\`, and \`shared_magnetra_gateway.worker_activated=false\` remain strictly **FALSE**. Do NOT promote any percentage or alter Rock64, existing BTDigg tunnel, secrets or DNS without separate explicit owner authorization. Best next gate: use read-only, bounded comparison of BTDigg 504 against historic/direct/production behavior with provider-specific source-aware timeout diagnostics; an isolated timeout should not be treated as persistent outage or used to weaken 8796 limits.


## 2026-10-18 — BTDigg restoration gate after candidate EZTV 29 E2E PASS (READ ONLY, NOT EXECUTED)

Owner requests **restoration of genuine automatic BTDigg**, not a substitute indexer, paid service or manual clipboard fallback. Historical actual production evidence in `docs/PROJECT_STATE.md` (13 Oct, live `/api/search?q=ubuntu&providers=btdigg`, audit run `38361367716`) confirms **10 authentic BTDigg results and valid source BTIH magnet links** from Worker→existing private Cloudflare Tunnel→Rock64 8796→`btdig.com`. That real provider intermittently recovered/faltered; not a permanently absent feature. Latest candidate [focused E2E #3](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39119359606) produced `BTDIGG_SOURCE_TIMEOUT_HTTP_504` from a **single** `ubuntu` request through 0%-candidate. This specifically means the dedicated 8796 gateway returned 504 for the upstream source within its **12-second** budget; it does not imply bad bearer credentials, dead tunnel or a Worker-code regression. It also does NOT prove current **old production** BTDigg is failing: same source has intermittent behavior.

Investigated code: original `rock64/btdigg_gateway.py` has bounded 12s upstream, only one in-flight source request, 5s minimum new-query interval, 20-minute success-only RAM LRU cache, 3MB cap, no challenge bypass and no automatic retry. `worker/src/btdigg-rock64.mjs` keeps BTDigg dedicated origin `https://btdigg-rock64.alexlab.media` separate from new shared 8798 Tunnel, and only BTDigg uses its bearer secret. Crucially, current candidate E2E invokes an *observational* one-off search, not a production-vs-candidate controlled comparison.

New *manual*, **read-only** GitHub workflow `.github/workflows/diagnose-btdigg-differential.yml` stages a stronger production-first differential check. It requires an explicit owner choice `COMPARE_OLD_THEN_CANDIDATE` on `main` and rechecks physical Cloudflare exact deployment old `a9df4429` 100% / candidate `249d6767` 0%, three bindings and candidate-only version fingerprint BEFORE upstream. It first performs **ONE** `ubuntu` query on actual old production and validates exact `btdigg` source attribution and real BTIH magnet rows. **On 429, 504, any error or empty response, STOP without an automatic retry or a second candidate request.** Only when old is genuinely positive, query the **same** `ubuntu` once via candidate version-override; the protected gateway's 20-minute success-only RAM cache is then expected to provide the same query without a second upstream hit. Log only status enum and row count; never print tokens, raw JSON, titles, searches beyond static benign query, magnets, hashes or remote source responses. Outcome differentiates shared source/unavailable old vs candidate-only regression vs both healthy. CI offline regression tests enforce no repeats, first-old ordering, fixed origin/query, 429/504 stop, strict result identity/counters and privacy.

At this checkpoint the diagnostic PR is pending CI/merge and the manual workflow has **NOT run**. No gateway, timeout, Rock64 service, tunnel, DNS, secret, other provider, Worker code, deployment or production traffic is changed. Do NOT silently raise 12s timeout, disable 5s gap, restart 8796, or change global network to cure a **single** 504. If old production source 504 persists, next gate requires narrow read-only Rock64 health + DNS/transport timing checks against the fixed original BTDigg host without printing credentials; any service modification requires user explicit approval and rollback. EZTV, OxTorrent, Torrent9 positive candidate E2E remains untouched; promotion of candidate remains not authorized.


## 2026-10-18 16:05 Europe/Rome — REAL BTDigg recovered observation: old and candidate PASS_BOTH 10/10

Owner completed [Diagnose BTDigg Old vs Candidate (READ ONLY) #1](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39134428856) via `workflow_dispatch` on reviewed `main` SHA `4b32da83e1897402d52af6af3e51aa9b32eae1ca`; GitHub workflow `SUCCESS`, job `117695945236` all steps passed. Logs contain **11 mocked offline tests**, but the subsequent *real source-network invocation* also separately logged:
- `CLOUDFLARE_VERSION_SLOT: PASS (old 100%, candidate 0%, bindings PASS)`
- `OVERRIDE_ROUTING_FINGERPRINT: PASS (baseline 404, candidate 200 + 46 entries)`
- `BTDIGG_COMPARISON: same source identity, same query, no retry on failure.`
- `BTDIGG_PRODUCTION: PASS (validated rows=10)`
- `BTDIGG_CANDIDATE: PASS (validated rows=10)`
- `BTDIGG_DIFFERENTIAL: PASS_BOTH (old and candidate verified)`

**Grounded conclusion:** Genuine original `btdig.com` source `ubuntu` search through private authenticated Rock64 8796 gateway, old 100%-deployed Worker, and separately candidate exact 0%-deployed Worker each returned 10 true BTDigg-attributed result records with valid BTIH magnets and matched API counters. The same query was checked old-first; no second upstream fetch was expected because successful 8796 response caches in RAM 20 minutes. No arbitrary proxy, index substitution, DHT crawler, CAPTCHA bypass, magnet transfer or download was performed.

**Limit:** Earlier candidate E2E #3 on 2026-10-18 returned a real `BTDIGG_SOURCE_TIMEOUT_HTTP_504` from ONE source attempt. This and previous reported intermittent errors remain true historical evidence. The current PASS_BOTH establishes recovery at test time and **rules out persistent candidate-only regression for the tested query**, but does not establish 24/7 stability or a unique confirmed cause for the earlier source timeout. No gateway code update occurred and `btdigg_source_timeout_fix_verified=false` stays FALSE to avoid falsely declaring a permanent fix. No follow-up invasive Rock64 testing is justified from a single historical 504 when both Workers are now positive.

**Verified candidate E2E provider allowlist:** BTDigg, EZTV (29 real source magnet results in E2E #3), OxTorrent and Torrent9 (each three results plus deferred original BTIH magnet in E2E #1/#2). **Other 42 providers have NOT received complete, positive E2E proof**; 46/46 catalog IDs ≠ 46/46 healthy sources. Stage `249d6767-f4dc-4f4d-bbf7-f57bea2e5554` still has 0% ordinary traffic, old active `a9df4429` has 100%, no canary/promotion approval. Secret names/bindings stay unchanged; no new Cloudflare deployment, Rock64 service restart, tunnel/DNS edits or device changes.

**Next:** No BTDigg gateway repair/deployment necessary for the now-positive immediate path. Owner may perform one normal BTDigg search within current PWA to verify iPhone UX separately, mindful of 5s rate limit. If future source 504 recurs consistently, collect narrow read-only timestamped status at 8796 and upstream DNS/network timing (without logging query, magnet, auth or source HTML) before proposing a targeted change and rollback. Full 46-provider source regression scan is a separate later gate.


## 2026-10-18 (seara, Italia) — CHECKPOINT COMPLET AL SESIUNII; BTDigg pe iPhone: timeout REAL apoi rezultate

**Noul master prompt complet pentru continuarea într-un chat separat:** [docs/MAGNETRA_MASTER_PROMPT_2026-10-18.md](MAGNETRA_MASTER_PROMPT_2026-10-18.md). Citește-l împreună cu `AGENTS.md`, codul `main`, `config/project-invariants.json` și acest `PROJECT_STATE`. Un handoff vechi din 12 octombrie este păstrat istoric, dar NU mai descrie configurația actuală.

**SHA înainte de prezentul PR de checkpoint:** `46870fc82772974936a73fabf819e27f32a3c7a5` (PR #77 integrat). Un merge nou de documentație trebuie să păstreze `Deploy Magnetra PWA` = `skipped`, fără `[deploy-pwa]` și fără alte modificări de infrastructură.

### Cronologie a deciziilor și dovezilor din această sesiune

1. **Cloudflare slot 100/0 aprobat strict:** după PR #69 audit de bindinguri (run [39047958484](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39047958484)), PR #70 a pregătit manual configurarea. Primele două dispatch-uri au fost `skipped` din cauza condiției de aprobare neîndeplinite/neexpuse; PR #71 a făcut confirmarea fail-closed explicită. Execuția reală [39053562983](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39053562983) a reușit cu `POSTFLIGHT_PASS`: vechea `a9df4429` **100% trafic obișnuit**, candidata exact `249d6767-f4dc-4f4d-bbf7-f57bea2e5554` **0%** (intrată în deployment pentru version override). Versiunea secret-only `ce808b27` nu a fost activată. `BTDIGG_GATEWAY_TOKEN`, `MAGNETRA_GATEWAY_TOKEN` și `ASSETS` au fost verificate pentru candidata exactă. **Niciun canary >0% nu este aprobat.**
2. **PR #72–#74: probe E2E orientate spre dovezi, fără deploy:** atribuire clară candidat (veche `/api/recovery-plan` 404 vs candidată 200 + 46), catalog 46/46 ID-uri, cercetare EZTV pe IMDb autentic nu pe `tt0460681` istoric gol, pacing 8797 `MIN_GAP=3s`, fără retry după rate limit. Fără fetch-uri/magnet downloads automate.
3. **Rezultate reale provider:** OxTorrent + Torrent9 (run [39101511577](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39101511577), reconfirmare în [39117038271](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39117038271)) fiecare **3** rezultate autentice și un magnet BTIH rezolvat din pagina detaliilor; EZTV (run [39119359606](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39119359606)) **29** rezultate originale, cu magneturi BTIH valide prin 8798→8797. Toate prin candidata 0% și autentificare verificată.
4. **BTDigg intermittent vs regression:** primul test focused [39119359606](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39119359606) a raportat un **`BTDIGG_SOURCE_TIMEOUT_HTTP_504`**, nu defect de binding. PR #76 a introdus comparația manuală old-first. Run real [39134428856](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39134428856) a demonstrat `BTDIGG_PRODUCTION: PASS (validated rows=10)`, `BTDIGG_CANDIDATE: PASS (validated rows=10)`, `BTDIGG_DIFFERENTIAL: PASS_BOTH` pentru `ubuntu`, cu rezultate BTDigg originale și magneturi reale. PR #77 a integrat dovezile; **fără modificări în 8796, tunel, secret sau Cloudflare rollout**. Nu există dovadă de regresie exclusivă a candidatei pentru interogarea verificată.
5. **ULTIMA dovadă din interfața utilizatorului, ulterioară PR #77:** pe iPhone, Magnetra a afișat exact `BTDIGG_SOURCE_TIMEOUT` cu mesajul `Rock64 could not complete the BTDigg source request in time (about 12 seconds).`. Utilizatorul a așteptat **aproximativ 1 minut**, apoi următoarea căutare BTDigg **a returnat rezultate afișate în PWA**. **Nu știm dacă a fost același termen sau unul diferit**; acest aspect NU poate fi dedus. Nu s-a efectuat nicio intervenție asupra serviciului, tokenurilor sau tunelului pentru recuperare. Aceasta este o **problemă intermitentă reală**, nu o reparație permanentă.
6. **Clasificare corectă a 504:** `BTDIGG_SOURCE_TIMEOUT` se referă la răspunsul **HTTP 504 al gateway-ului 8796 după bugetul configurat 12s**; este distinct de `BTDIGG_TUNNEL_TIMEOUT` al subrequestului Worker cu 16s. Codul `SearchProvider.fetch` mapează însă în 504 atât un timeout cât și diverse `OSError/URLError` (DNS, conexiune, TLS ori transport). **Cauza fizică exactă nu a fost demonstrată**, deci eticheta tehnică „source timeout” nu garantează server upstream lent. Regulile existente sunt `MIN_SEARCH_INTERVAL=5s`, PWA pacing `5.5s`, cache succes-only `20min/4 intrări/6MB RAM`, un upstream în zbor cu singleflight. Nu elimina protecțiile, nu mări automat timeout, nu adăuga retry repetitiv.

### Verdict operațional / următorul pas

- **Stare corectă:** 4 provideri cu E2E pozitiv pe candidat (**btdigg, eztvx, oxtorrent, torrent9**), catalogul conține **46** indexere originale, dar un full live E2E al tuturor celor 46 nu a fost făcut. Ultimul audit complet istoric de producție (13 oct., run `38373699387`) a fost 13 cu rezultate / 12 zero-neconfirmate / 21 erori; nu reprezintă uptime curent.
- **BTDigg:** produce date originale și pe veche, și pe nouă și pe iPhone, **dar un 504 intermitent poate reapărea**. Nu declara „reparat definitiv” și nu seta `btdigg_source_timeout_fix_verified=true`.
- **NEXT ACTION P0:** numai **diagnostic read-only al timpilor BTDigg Rock64→sursa originală** și o investigație a diferențelor DNS / TCP connect / TLS / TTFB / read, plus sănătatea procesului 8796, fără secrete/loguri raw și fără cereri repetate la 429/504. Începe cu audit de cod și statusuri local read-only, apoi **o singură probă upstream dacă userul autorizează**, nu un bulk-scan. Dacă este nevoie de actualizarea Python, pregătește branch/PR și rollback, apoi cere acord pentru instalarea fizică.
- **Fără deployment:** păstrează Cloudflare old 100% / candidate 0%, `canary_rollout_approved=false`, `production_worker_promotion_completed=false`; fără `[deploy-pwa]`, manual Deploy, schimbări DNS/Tunnel, servicii Rock64 sau Flud. Costuri noi = zero fără acord expres.
