# AlexLab Magnetra — Project State

## 24 Oct 2026 — P1 0Magnet (9mag.net) iPhone "Sursă indisponibilă" investigation, NOT FIXED

- **User evidence**: real Safari screenshots: PWA 0Magnet result "Little.House.on.the.Prairie.2026.S01.720p.10bit.WEBRip.2CH.x265.HEVC-PSA" (2.26 GB) shows "Obține magnet" and then generic "Sursă indisponibilă". The owner visits the original 9mag.net detail page, which visibly displays a magnet and Info Hash. This does not prove what static server HTML reached Cloudflare or what HTTP status the original upstream returned to the Worker.
- **Confirmed implementation**: 0magnet has fixed origin https://9mag.net and an input-type deferred resolver with selector input#input-magnet, reading the value attribute of original detail HTML. This matches the Android ZeroMagnet implementation. The PWA currently collapses multiple failures into the same generic error; the code does NOT establish a failed selector or blocked upstream.
- **Evidence gate staged, not yet run**: scripts/diagnose_0magnet_owner_readonly_20261024.py and workflow .github/workflows/0magnet-owner-readonly-20261024.yml; tests and explicit owner approval file. One-shot bounded read-only: at most 2 distinct production search GETs scoped to original 0magnet, one source-owned same-card detail GET, and one production metadata-only /api/resolve POST. Logs only finite status/class flags, no titles, detail URLs, magnets, hashes, raw HTML, credentials, user cookies or sensitive data. No torrent, download, Flud, Shield, retry on rate limit or challenge bypass. Stop if the source's same card is not available.
- **Next**: inspect genuine action output and only then propose a smallest possible regression-tested source-specific fix with a separately owner-approved controlled immutable release. Preserve the proven TheRarBg fix, existing 46 adapters, 12 visible/34 hidden PWA picker, RO/IT UI, SSRF allowlist, all bindings, existing Cloudflare 100/0 last-proven split, Rock64/Tunnel/DNS/Shield/Flud. This PR is diagnostic and documentation only; automatic general PWA deploy must be skipped.



## LATEST MANDATORY CHECKPOINT — 24 OCT 2026 — OWNER IPHONE SUCCESS REPORTED; THE RARBG MAGNET FIX ACCEPTED

**This section supersedes the previous 24 Oct 2026 "PHYSICAL IPHONE ACCEPTANCE OPEN" wording below; that earlier section and all other investigation history remain unchanged as historical record.**

### Owner physical iPhone result (24 Oct 2026, Europe/Rome)
- After confirmed guarded production release [#40100824187](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/40100824187) and successful [production smoke #40100824081](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/40100824081), the owner returned in the next session with the explicit report **"Ole , functionewza acum!!"** (it works now) immediately following the requested physical iPhone TheRarBg retest. Treat this as **positive owner-reported physical iPhone functional acceptance of the TheRarBg magnet resolver fix**, rather than the earlier GitHub-runner-only verification.
- **Evidence boundary:** the owner's short confirmation did not individually identify whether **Obține magnet, Copiază and Distribuie** were *all three* tested, nor assert actual Flud-to-Shield acknowledgement or a completed torrent download. Do not fabricate per-button or downstream delivery acceptance. The previously reproducible **TheRarBg wrong-link source precedence** incident is resolved according to the owner's functional report. If a specific untested action later fails, diagnose that action separately.
- Last independently evidenced production state remains immutable **`916d0671-b9c5-432d-8724-aed27bc22c4f@100%`** with rollback **`139d97f7-4048-4bbb-8e90-80585f1f4b26@0%`**, as recorded by the successful one-shot rollout. The GitHub `main` baseline before this documentation change was **`263a16d2375b9ccbd3bf72d7a8a3557888942020`**. These percentages are **last proven values**, not a newly performed live Cloudflare API query.
- **No redeploy, rerun or post-acceptance modification** to PWA bundle, Cloudflare version percentages, DNS, tunnels, Rock64 8796/8797/8798, credentials, Companion, Shield or Flud is warranted. Never rerun the one-shot release workflow.
- **Next work, evidence-first (ordered):** (P1) if the original Genshin 93.2 MB TheRarBg issue persists, obtain the exact same-card `details` from fresh PWA search or user's original URL, then investigate only that record; do not assume Cyberpunk's details/fingerprint/hash applies. (P1) independently verify real Flud/Shield remote receipt and matching acknowledgement, distinguishing PWA queue acceptance from Shield ACK and from download, only with owner-provided device evidence/explicit action. (P2) revisit BTDigg intermittent 504 only with new reproduction and bounded read-only timings; do not assume the already deployed IPv4 transport patch permanently eliminated all timeouts. (P2) plan scoped original-provider regression; the 46 IDs/adapters are preserved, but 46/46 catalog is NOT 46/46 live source health. PWA selector remains 12 visible/34 hidden, Romanian default/Italian optional.
- **Change scope:** THIS acceptance checkpoint is **documentation only**. No code, release activation marker, traffic change, bindings, monetized services or provider adapter adjustments. Standard four CI checks must pass before merge; automated PWA deployment must be skipped.



## LATEST MANDATORY CHECKPOINT — 24 OCT 2026 — THE RARBG IPHONE FIX LIVE 100%; PHYSICAL IPHONE ACCEPTANCE OPEN

**This heading supersedes historical latest-status sections below. Historical sections are preserved for provenance.** Do not interpret older live versions, stale URLs or proposed workflows as current status.

### 24 Oct 2026 — VERIFIED LIVE: TheRarBg iPhone details-first fix at 100%; owner acceptance still pending
- **Current production VERIFIED**, NOT a proposed release. Cloudflare guarded immutable one-shot release workflow **#40100824187** COMPLETED SUCCESS on 24 Oct 2026. Immutable corrected version **`916d0671-b9c5-432d-8724-aed27bc22c4f@100%`** live on **https://index.alexlab.media**; prior diagnostic version **`139d97f7-4048-4bbb-8e90-80585f1f4b26@0%`** preserved as immediate rollback. Before release, exact baseline 139d@100 and 36019925@0 verified, all 4 bindings present. Candidate uploaded via pinned `wrangler@4.102.0 versions upload --keep-vars`, staged 0%, passed `/app.js` SHA vs reviewed source and 46/46 health/catalog, resolved the owner-original exact Cyberpunk detail to a VALID MAGNET using original HTML without logging hash; then tested 5% canary and promoted to 100%. Postflight public `/app.js` reviewed SHA, 46/46 catalog and production smoke workflow **#40100824081** all PASS. Workflow logs distinguish offline unittest fixture version 11111111-1111-4111-8111-111111111111 from REAL Cloudflare immutable `916d0671-b9c5-432d-8724-aed27bc22c4f` — do not confuse them.
- **Root cause proven by user real iPhone + source-specific production audits**: first 352.7 MB TheRarBg Cyberpunk soundtrack first card on iPhone failed with `URL b12d9fd36aa0 / HTML_NO_BTIH / JSON_URL_REJECTED`; original owner-clicked details page has genuine magnet and info hash. Read-only run **#40084154928** proved exact original `details` URL has SHA256-12 `3b00bf511347`; run **#40085002856** confirmed same-card `magnetSource` has SHA256-12 **b12d9fd36aa0** (exact failing input) while direct original `details` resolves `VALID_MAGNET / HTML_ANCHOR_VALID`. Client `ensureMagnet()` wrongly prioritized `magnetSource || details` for TheRarBg. **PR #161 code fix** merged as **93f311f12cfb192ba3dfe686e8c27b0f5f162e2a**; details-first choice for TheRarBg only added to existing OxTorrent/Torrent9 rule. All other 43 providers keep prior precedence. Node VM tests run REAL `ensureMagnet` function and cover original source, optional diagnostic, other providers, no-details safety and pre-resolved magnet.
- **PR #162** guarded release script/workflow merged as **4cdf45bd3fff92e5379ee86ac1c4f0ec70e1cfe4** after all four mandatory checks PASS on final PR head `860b8e2bfbb530ebfec2478b414a51045b0edc97`. Previous failed intermediate Python unittest import (`SimpleNamespace` imported from `unittest.mock`) was fixed and ALL FOUR checks reran PASS. Release script `scripts/release_therarbag_details_first_20261024.py`, workflow `.github/workflows/therarbag-details-first-production-20261024.yml`; one-time release already used — NEVER rerun it, because baseline pins are intentionally stale after successful rollout. Automatic generic PWA deploy was skipped for release merge (run **#40100824032**). No Preview URL toggle, DNS, Rock64, Shield/Flud, token or routing change.
- **NEXT P0 user action**: On physical iPhone do fresh Safari search on **https://index.alexlab.media/?magnetra_diag=1**, find SAME original TheRarBg result **352.7 MB**, press **Obține magnet**, then **Copiază** and **Distribuie**; verify success / source-specific trace and screenshots. A GitHub-runner real original magnet success DOES NOT substitute for Safari owner E2E. If user deliberately tests **Trimite în Flud**, confirm separate relay queue vs Shield ACK; never label accepted as downloaded. No need to edit TheRarBg backend or invent hashes; re-investigate only if owner still reproduces failure on new JS version.
- **NEXT P1**: If iPhone fails, inspect exact card details/magnetSource, response headers and frontend script freshness/service worker using opt-in privacy-safe trace; verify actual running version and browser API response; do not assume cache issue. Previous Genshin 93.2 MB source card issue remains UNVERIFIED until its real original detail URL/user reproduction supplied — never copy Cyberpunk infohash. After iPhone success update acceptance/cleanup diagnostics by guarded PR; retain audit history. Recheck Cloudflare immutable percentages before any future change. Current known rollback is `139d97f7-4048-4bbb-8e90-80585f1f4b26`, NOT historical `36019925`, `c201cbf9` or `4e47`.


### 24 Oct 2026 — P1 iPhone TheRarBg source-precedence ROOT CAUSE CONFIRMED; details-first code fix awaiting release
- Owner actual iPhone screenshot (first Cyberpunk Edgerunners 2 Original Series Soundtrack card, 352.7 MB) on new diagnostic PWA proved `THERARBAG_IPHONE_DIAG_V1; URL b12d9fd36aa0; HTML_NO_BTIH; JSON_URL_REJECTED; 55ms` while owner-clicked source details page displayed same item's real Magnet Download, Copy Magnet and Info Hash. Owner final original page URL is `https://therarbg.com/post-detail/95bf8b/2026-10-20-cyberpunk-edgerunners-2-original-series-soundtrack-flac-44-1khz-24bit/`.
- GET-only PR #159 and real workflow #40084154928 verified current 352.7 MB original TheRarBg result has `details` EXACTLY this owner-supplied canonical URL: SHA256-12 `3b00bf511347`, strict JSON route acceptable; the failed iPhone input fingerprint was different.
- **DECISIVE PROOF**: read-only original details-probe PR #160, production workflow #40085002856: SAME original 352.7 MB result has a **DIFFERENT `magnetSource`** property and its SHA256-12 **EXACTLY matches original failed iPhone input `b12d9fd36aa0`**. Direct original `details` on the very same production API returned `VALID_MAGNET`, `HTML_ANCHOR_VALID`, `JSON_NOT_STARTED`, no torrent data or Flud commands. Therefore actual cause is PWA `ensureMagnet` choosing `item.magnetSource || item.details` for TheRarBg, whereas TheRarBg's legitimate magnet is on `details`, not its misleading listing auxiliary link. Do NOT alter HTML/JSON validator or invent a BTIH; they are behaving correctly on the source's correct URL.
- Code-fix branch `fix/therarbag-owner-details-first-20261024`: modify only PWA `web/app.js` to include `therarbag` in existing details-first precedence with OxTorrent/Torrent9. Keep the other 43 adapter precedence rules unchanged, protect missing details from unsafe alternate source, retain owner opt-in trace, all 46 provider identities, 34 PWA-hidden and 12 visible, original RO/IT UX and Flud Companion. Node VM integration tests exercise the real `ensureMagnet` function for source pair and existing other providers. Code merge is NOT production deployment; require all four CI green and a NEW guarded immutable Cloudflare version-only 0->5->100 release from current actual baseline, with exact four bindings and rollback.
- **User real iPhone re-test** of first 352.7 MB card on fresh search remains outstanding until guarded fix is actually live. The successful original-source POST is **server-level proof of fix rationale**, not proof of user-device success.

### 24 Oct 2026 11:04 Europe/Rome — real iPhone diagnosis REPRODUCED; link identity mismatch
- Owner real screenshot after guarded release #40059873546 confirms production diagnostic `THERARBAG_IPHONE_DIAG_V1` and still-failing first TheRarBg Cyberpunk Edgerunners 2 card: 352.7 MB, 78 seeds, 27 peers, `HTML_NO_BTIH`, `JSON_URL_REJECTED`, 55ms, validated details URL SHA256-12 `b12d9fd36aa0`. iPhone failure **NOT FIXED**; runtime instrumentation **CONFIRMED**.
- The previously supplied original-source canonical Cyberpunk URL `https://therarbg.com/post-detail/95bf8b/2026-10-20-cyberpunk-edgerunners-2-original-series-soundtrack-flac-44-1khz-24bit/` hashes to `3b00bf511347`: it is **not the exact same URL string** as current live first-card details. Do not reuse that distinct source URL's hash as same-card evidence.
- `worker/src/legacy-adapters.mjs::theRarBgOriginalJsonHash` sets `JSON_URL_REJECTED` **before JSON fetch** if URL has search params/auth/fragment/incorrect strict path or host; first-level `validateLegacyDetail` accepts same-origin URLs with query/search. This discrepancy is a strong candidate, NOT yet exact cause; no patch until exact same-card shape observed.
- Read-only new PR branch `diagnostics/therarbag-iphone-result-url-shape-20261024` computes first 12hex SHA256 of each exact PWA search `details` value, compares user-supplied fingerprint, logs **only** safe URL shape category. At most two fixed canonical production GET search calls, no POST resolve or mutation. One-shot workflow marker `[magnetra-therarbag-iphone-linkshape-readonly-20261024]`, all CI required before merge. If no matching card, STOP and request exact `Detalii` URL without guessing. Only after evidence fix with regression + reviewed immutable staged release; owner iPhone acceptance still pending.


### 24 Oct 2026 — Owner approves direct production iPhone diagnostic rollout (PENDING RELEASE)
- Owner confirmed Magnetra PWA is currently used only by the owner, and explicitly authorized controlled testing at the canonical `https://index.alexlab.media` address; dedicated Cloudflare Version URLs are disabled as confirmed by GET-only workflow #40058531928. This authorization does not by itself establish production success.
- PR #154 merged as `86e84ff` with opt-in `?magnetra_diag=1`, four CI checks successful; no automatic PWA deployment. PR #155 merged as `5cd950fd`, and guarded Cloudflare version upload run #40058004336 succeeded with immutable version `139d97f7-4048-4bbb-8e90-80585f1f4b26`, four binding checks and unchanged historical 36019925@100/c201cbf9@0 split. PR #156 merged as `b6fef040`, read-only Preview URL check completed and confirmed previews DISABLED; no setup change or new URL.
- Next unique guarded PR `release/therarbag-iphone-diagnostic-100-20261024`: production owner-approved release event file, fail-closed script + tests for staged 0% -> 5% -> 100% with existing version as 0%-rollback. Must re-audit EXACT Cloudflare baseline/bindings and original 46 adapters before any traffic action, verify built JS + finite diagnostic runtime and public postflight; stop/rollback if any gate fails. THIS ENTRY IS NOT PROOF OF EXECUTION. No generic Wrangler deploy, no automatic `[deploy-pwa]` marker, no real Flud/torrent operation.
- After successful GitHub release workflow and live postflight, owner iPhone test URL is `https://index.alexlab.media/?magnetra_diag=1`; get screenshot of same failing TheRarBg card to diagnose `DETAIL_NO_BTIH`. Test outcome and root cause remain UNVERIFIED until that evidence arrives.


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


## 23 OCT 2026 — FLUD COMPANION MAGNETRA FIX LIVE AT 100% (RELEASE VERIFIED)

- **Cloudflare Worker promotion completed successfully:** GitHub Actions [#39985628821](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39985628821) confirmed `EXACT_IMMUTABLE_DEPLOYMENT_PREFLIGHT:PASS`, `TRAFFIC_PROMOTION_PASS:CANARY_5`, `TRAFFIC_PROMOTION_PASS:PRODUCTION_100` and `COMPANION_IMMUTABLE_PRODUCTION_100_PASS`. Immutable new Magnetra version `4e4730a1-3334-4b1a-98da-966f807d5078` serves **100%**; previous `a088fa41-233d-48d3-bd4c-52be6194fda8` is retained at **0%** as safe rollback.
- **Independent root-cause and acceptance evidence:** Owner's synthetic-only Rock64 POST to the exact staged `4e47` version returned HTTP 401 with unique `x-alexlab-companion-probe: upstream-http-401`, proving internal `FLUD_RELAY` Service Binding works. Root cause of previous HTTP 502 was unsupported workerd `Request.redirect = error` causing constructor `TypeError`; patch switched to `redirect:manual` and explicitly refused 3xx, preventing bearer leakage. Real bearer tokens, personal ID, magnets never used in automated tests.
- **No collateral changes:** The production release only changed version traffic percentages, did not upload Worker code or affect DNS, Flud Remote, Shield, Rock64, YouTube or the original 46 indexers. Post-activation GitHub Actions PWA contracts, invariants and public smoke checks are green. Android build checks are independent of this Worker-only release.
- **User acceptance still open:** On iPhone open `https://index.alexlab.media`, use Flud Companion modal with previously saved pairing, select `Verifică legătura Shield`, and confirm actual Online/auto-start-ready status; optional deliberately safe magnet must be checked to Shield ACK separately because relay queue acceptance is not physical delivery. Do not claim real Shield connection verified in Magnetra until owner tests it.
- **Rollback reference:** previous immutable `a088fa41-233d-48d3-bd4c-52be6194fda8` is the exact current rollback version (0% traffic). Roll back only after checking Cloudflare metadata and with owner authorization; never use stale release actions with historical version pins.

## 23 OCT 2026 — OWNER ROCK64 CONFIRMS SERVICE BINDING FIX; GUARDED FULL RELEASE PREPARED

- Definitive user test from Rock64: POST with immutable Cloudflare version override `alexlab-magnetra="4e4730a1-3334-4b1a-98da-966f807d5078"`, fixed synthetic ID/token, `X-AlexLab-Companion-Probe: 20261023-v2`, returned **HTTP 401**, `x-alexlab-companion-probe: upstream-http-401`, JSON `{error:Unauthorized}`. This proves the **exact new immutable version** executed and reached Flud Remote's authorization service through the Service Binding. Real Shield ACK still requires owner's browser acceptance after publication.
- Old immutable version `a088fa41-233d-48d3-bd4c-52be6194fda8` serving 100%; corrected candidate 4e47 at 0% verified by Cloudflare on initial stage. Previous GitHub-runner tests get outer HTTP 403 from public Cloudflare edge and cannot replace the owner-approved Rock64 proof.
- New immutable no-upload promotion script `scripts/promote_companion_fixed_4e47_20261023.py` and one-shot `.github/workflows/companion-4e47-immutable-promotion.yml` are designed to require exact deployment old@100/new@0 and preserved service/asset/secrets bindings, then one-at-a-time metadata-verified old@95/new@5 and old@0/new@100. The new candidate code and original assets cannot change during this pure version-percentage release. Old version remains immutable as 0% rollback. On known error after a write, issue a guarded previous 100% restore; refuse unrecognized or concurrently changed splits. No real tokens, no torrent magnet sends, no Shield, Flud Remote, YouTube, Rock64, DNS or provider changes.
- Activation must be separate, explicit, one-shot release event `docs/release-events/companion-4e47-publish-20261023.md` and commit marker `[magnetra-companion-4e47-publish-20261023]` **after reviewed PR CI**. The script records independent Rock64 test as user attestation; the GitHub runner cannot repeat it reliably. Actual production rollout status MUST be confirmed from Cloudflare job logs; do not infer it from merged source. Owner must ultimately verify real Shield Online in Magnetra and optional benign magnet delivery; relay queue is not a physical ACK.

## 23 OCT 2026 — WORKER REDIRECT FIX STAGED 0%, ROCK64 ACCEPTANCE PENDING

- Conclusive owner Rock64 response from staged 47bbcec3-a4fc-4830-aa5e-33c55356a30b: HTTP 502 with unique probe header binding-request-type_error. New Request constructor threw TypeError before Service Binding fetch. Actual Cloudflare workerd Request Redirect only permits FOLLOW and MANUAL, not prior error mode.
- PR #146 merged as 01be9341940b2c0c70242084e6dea0c10d211571: switch to redirect manual and explicit upstream 300–399 refusal, preserving bearer confidentiality. Tests for redirect mode and blocked redirects added.
- Zero-only Cloudflare diagnostic workflow #39983123904 uploaded fixed candidate 4e4730a1-3334-4b1a-98da-966f807d5078; 4 binding identities PASS, old immutable a088@100 and new 4e47@0 VERIFIED. GitHub-hosted synthetic status lacked the candidate marker and failed closed, consistent with GitHub runner public edge 403 observed earlier. No 5%/100% promotion and no real token or magnet send.
- Required Rock64 acceptance: POST https://index.alexlab.media/api/companion/status using Origin https://index.alexlab.media, Cloudflare-Workers-Version-Overrides alexlab-magnetra="4e4730a1-3334-4b1a-98da-966f807d5078", X-AlexLab-Companion-Probe 20261023-v2, fixed fake device MAGNETRA_DIAG_NOTREAL_1234 and fixed fake token TEST_TOKEN_NOT_REAL_12345678901234567890. Only HTTP 401 + response x-alexlab-companion-probe upstream-http-401 confirms bound relay. If it fails, no release.
- After 401 validation, prepare separately owner-approved immutable version-specific guarded 0/5/100 promotion retaining active a088 rollback; never rerun stale initial one-shot script. Flud, Shield, Rock64, YouTube, DNS, secrets and original 46 adapters unchanged.

## 23 OCT 2026 — WORKER SERVICE BINDING CONSTRUCTOR TYPEERROR IDENTIFIED (FIX CANDIDATE; NOT LIVE)

- Owner performed real Rock64 staged call with version override `47bbcec3-a4fc-4830-aa5e-33c55356a30b` and uniquely gated `X-AlexLab-Companion-Probe: 20261023-v2`. Result: HTTP 502 with `x-alexlab-companion-probe: binding-request-type_error`; this **proves the new immutable version ran**, entered Service Binding branch, and threw TypeError constructing `new Request(url,outboundOptions)` BEFORE `env.FLUD_RELAY.fetch` was called. No real creds were supplied.
- Root cause identified in Cloudflare's actual workerd Request implementation: `Request::Redirect` enum permits `FOLLOW`/`MANUAL` only; `error` is unsupported. The existing `redirect:"error"` caused constructor TypeError. The fix uses `redirect:"manual"`, with explicit 300-399 response refusal before parsing data; unlike `follow`, it cannot forward the Remote bearer token to another origin. Preserve bounded 12s abort, exact allowlisted target, authentication, POST payload and idempotency semantics. Node and workerd tests must pass.
- The previous zero-only stage run [#39981515340](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39981515340) uploaded `47bbcec3-a4fc-4830-aa5e-33c55356a30b` and verified it at 0%; its resource-gate then stopped on an asset verification, leaving prior `a088fa41-233d-48d3-bd4c-52be6194fda8` serving 100% at last confirmation.
- New branch `fix/companion-redirect-mode-workerd-20261023`: stage-only guarded release script requires `a088@100/47bb@0` exactly; uploads a fresh immutable Worker candidate with corrected manual policy; retains old production @100%; verifies all four bindings, assets, 46 providers and fake token `401` plus synthetic diagnostic header. **Never automatically promote to 5% or 100%** or send a magnet. After a verified staged 401, a separate owner-controlled promotion with rollback is required.
- No Shield, Flud Remote, Rock64, YouTube, DNS or real secret/token modifications.

## 23 OCT 2026 — IMMUTABLE COMPANION VERSION OVERRIDE VERIFICATION (PROPOSED; NO PRODUCTION CHANGE)

- User ran actual synthetic-only Rock64 `POST /api/companion/status` with `Cloudflare-Workers-Version-Overrides: alexlab-magnetra="ac71bb51-b681-458b-8f40-980d4621fe62"` and received HTTP 502 `Companion remote relay is unavailable.`. The same body appears in old and candidate code, so this DOES NOT prove the override took effect. Cloudflare explicitly documents that an un-applied version override falls back to weighted traffic without raising a request error.
- GitHub-hosted runner's public Flud status test instead returned HTTP 403 with non-auth JSON, while Rock64 direct Flud status returned HTTP 401 for synthetic credentials; never treat that GitHub 403 as proof of Worker service-binding failure.
- The only safe discriminant is a unique response marker from candidate code, limited to a preagreed fake Device ID, fake token and dedicated header. Diagnostic branch `diagnostic/companion-immutable-v2-finite-stage-20261023` adds synthetic-only `x-alexlab-companion-probe` response header with finite labels, not raw errors or secrets. Normal API behavior is unchanged.
- New owner-triggered `.github/workflows/companion-v2-zero-only-diagnostic.yml` invokes `scripts/stage_companion_v2_diagnostic.py`: require exactly a088@100/ac71@0, verify all original binding names/types and same Cloudflare account, upload a new reviewed immutable version with `FLUD_RELAY` using `--keep-vars`, replace the 0% slot only (a088 remains @100), verify assets/catalog, perform fake-token staged response-marker probe, and require exact unchanged 100/0 afterwards. It explicitly CANNOT promote 5% or 100%. Its result will diagnose whether override routing applied; even success does NOT prove real Shield ACK.
- Do not rerun the previous full release workflow. Do not modify Flud Relay, Shield, YouTube, BTDigg, Rock64, DNS, real credentials or original 46 adapters. Production status still unchanged, pending diagnostic results.

## 23 OCT 2026 — MAGNETRA → FLUD REMOTE STATUS HTTP 502 (PROPOSED INTERNAL BINDING; NOT DEPLOYED)

- **First real owner-authorized release attempt 23 Oct:** PR #141 merged `bd01227d97fb40a5a244e3055113934ac7ae2518`; unique release action [#39977046464](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39977046464) started from activation commit `d5eef34de2455c3992fca2625e6b430728acd50d`. Cloudflare account/old-version preflight PASS; uploaded candidate `ac71bb51-b681-458b-8f40-980d4621fe62` with four binding names/types verified; staged old a088@100%, candidate@0%; reviewed JS/CSS/HTML/i18n and 46 provider catalog PASS. **Staged fake-token internal status failed closed before canary** (`COMPANION_RELEASE_ABORTED_FAIL_CLOSED`, `ROLLBACK_UNNECESSARY_OLD_100`), so NO 5% or 100% promotion and no verified live fix. Exact response status/category was deliberately withheld in first script. New standalone read-only classifier on branch `diagnostic/companion-stage-readonly-20261023` uses direct Flud GET and candidate override Magnetra POST with fake credentials, emits ONLY finite HTTP status+category; requires exact old100/candidate0 unchanged. Do not retry original release blindly. Next decision based on diagnostic result; no real tokens, magnet sends, Flud/Shield/BTDigg/Rock64 changes.

- **Owner requested real production release on 23 October** after confirming two Workers in same account. No paid Github Actions minutes are required for standard GitHub-hosted runners on this public repo. This branch now contains dedicated immutable release `scripts/release_magnetra_companion_binding_20261023.py` and one-shot `.github/workflows/magnetra-companion-binding-one-shot.yml`, owner activation marker `[magnetra-companion-binding-publish-20261023]` in a NEW `docs/release-events/companion-binding-20261023.md` commit only after merge. Exact preflight currently documented active a088@100 / rollback 056d@0; release stops if actual Cloudflare deployment changed. It checks same-account workers, baseline immutable version binding names, uploads with `--keep-vars` and required existing secrets, validates four binding names/types, stages 0%, performs real staged internal GET via Magnetra using **fake bearer credentials** and requires HTTP 401 from Flud Remote, checks unchanged static PWA + i18n and original 46 provider IDs, then validates 5% canary and 100%, preserving the previous immutable version at 0%. Unknown traffic split or failure triggers fail-closed and guarded restore when possible. The staged 401 is a relay-transport proof, **not** a Shield ACK; owner iPhone acceptance still necessary. Workflow must not be triggered automatically by merge; activation must be separately owner-authorized. **No Cloudflare mutation yet; deployment result remains UNVERIFIED until action logs and Cloudflare API show PASS.**

- **Owner confirmation 23 October, screenshot Cloudflare Workers & Pages:** both `alexlab-magnetra` (`index.alexlab.media`) and `flud-remote-relay` (`flud-remote.alexlab.media`) are listed within the same Cloudflare dashboard account. This satisfies the visible prerequisite for the Service Binding, but does not verify the currently deployed version's binding metadata. Cloudflare documentation validates `services:[{binding:"FLUD_RELAY",service:"flud-remote-relay"}]` and `env.FLUD_RELAY.fetch(new Request(...))` for HTTP forwarding. CI at commit `80b067360e0995b8c39b2d5981d3d30a0ce74b72`: 6 checks all PASS, including worker regression, invariants and Android builds. Release remains **NOT DEPLOYED**, PR #141 draft.
- **Added safe staging prerequisite:** `scripts/inspect_companion_binding_readonly.py` and manual GET-only `.github/workflows/inspect-companion-binding-readonly.yml` inspect both Worker names within one Cloudflare account plus exact current immutable Magnetra 100% version and original ASSETS/BTDIGG/MAGNETRA secret binding **name/types only**, without reading/printing secret values. Script recognizes the new optional fourth `FLUD_RELAY` service binding if already active; this workflow never uploads/deploys, sends no pairing requests and no magnets. Offline fixtures in `scripts/test_inspect_companion_binding_readonly.py`. Execute only from reviewed `main` after merging code; account API token must have read capability. This audit does not alone authorize or perform production rollout. Next separate owner-approved guarded release must preserve existing bindings, 46 catalog adapters, 12 visible/34 hidden source UI, active/rollback version safety, deploy to 0%, validate version with 4 bindings and fake-token /api/companion/status returning 401 (not 502), then canary 5%, finally 100% with prior rollback. No changes to live traffic yet.

- Owner confirmed real Flud Companion Remote PWA reports Shield online and public GET health succeeds: Magnetra `/api/health` gives 46/46 and Flud Remote `/health` reports v0.25.2, `https-r2-mailbox`.
- Read-only command using intentionally fake Device ID/token on public `POST /api/companion/status` returned HTTP 502 `{"error":"Companion remote relay is unavailable."}`, whereas a direct fake-credential GET to the Flud Remote status route returned HTTP 401 `{"error":"Unauthorized"}`. These prove separate public endpoints respond, with Magnetra's relay subrequest throwing; they do NOT prove physical torrent delivery or identify the exact Cloudflare exception.
- This branch proposes adding Wrangler same-account service binding `FLUD_RELAY` targeting existing Worker `flud-remote-relay`, plus `env.FLUD_RELAY.fetch(new Request(fixedRelayUrl, ...))` for both status and magnet forwarding. Legacy outbound `fetch` remains a fallback only when binding absent, including in local development.
- Preserve the exact fixed allowlisted relay host, bearer token header, no credentials in URLs/logs, same-origin POST API, bounded 12s timeout, idempotency ID, queued vs Shield ACK distinction, auto-start guard and existing frontend UX. Do NOT touch Shield/Flud repo, DNS, Rock64, BTDigg or the original 46 provider adapters.
- **Activation gate:** confirm `alexlab-magnetra` and `flud-remote-relay` are deployed in the **same Cloudflare account**; GitHub ownership alone is insufficient. Ensure any immutable-version release process actually includes this new service binding and preserves every existing asset, secret and tunnel binding. Existing version-promotion scripts may assume a fixed binding count; audit/update them before a separate approved 0% → 5% → 100% rollout. No deploy, route modification, secret rotation or test magnet on this draft branch.
- Regression test `worker/test/companion-service-binding.test.mjs` uses fake credentials and an in-memory stub of the binding, covers status success, 401 passthrough, magnet request fidelity and sanitized transport failure. These are unit tests, not yet proof of real cross-Worker Cloudflare reachability.
- Owner acceptance after separately approved rollout: authenticate using existing browser pairing, click Verifică legătura Shield, confirm actual Online + auto-start readiness, then deliberately send a benign test magnet and verify physical Shield ACK, not merely relay queue acceptance. Keep rollback version available.


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

_Current operational checkpoint updated 2026-10-19, ~23:00 Europe/Rome; last verified pre-checkpoint `main`: `10818d487facbcf1ba66d7f92322926e9b76508a`. The historical 2026-10-12 baseline in older sections is not the live state. Full new-chat prompt: [`docs/MAGNETRA_MASTER_PROMPT_2026-10-19.md`](MAGNETRA_MASTER_PROMPT_2026-10-19.md)._

This file is the canonical human-readable technical checkpoint for AlexLab Magnetra. Repository state on the main branch takes precedence over old chat context. Material changes must reconcile this file, `config/project-invariants.json`, code, and CI guards.

## Product purpose

AlexLab Magnetra is a fork of `prajwalch/TorrentSearch` intended to preserve the upstream Android application while adding an installable web/PWA experience under the AlexLab Magnetra identity.

The product is a torrent metasearch client. It searches third-party providers and exposes metadata and actions such as magnet links, copy/share actions, and `.torrent` downloads when a provider supplies them. It does not host torrent payloads or copyrighted content.

## Current architecture

The repository retains the upstream Android application and now also runs a production PWA:

- Android application source: `app/`
- Language: Kotlin
- UI: Jetpack Compose + Material 3
- Networking: Ktor client with OkHttp engine
- HTML parsing: Jsoup
- Persistence: Room + DataStore
- Dependency injection: Koin
- Build system: Gradle / Android Gradle Plugin
- CI: GitHub Actions

The first PWA implementation is deployed and confirmed over HTTPS; real-device and provider-specific end-to-end testing remain pending. The separation is:

- `app/` — upstream-compatible Android implementation
- `web/` — installable, standalone mobile-first PWA (vanilla JavaScript, CSS, HTML, manifest, service worker) with browser-local `localStorage` for source preferences, bookmarks and Companion pairing, complete source catalog and magnet actions. IndexedDB is not implemented.
- `worker/` — Cloudflare Workers-compatible search/API and fixed-origin Flud Companion remote relay bridge

The PWA must not be implemented by destructively converting or replacing the Android codebase.

## Repository and upstream

- Canonical repository: `Zuzuitu/AlexLab-Magnetra`
- Upstream repository: `prajwalch/TorrentSearch`
- Default branch: `main`
- License: MIT
- Fork strategy: preserve upstream synchronization capability and minimize unnecessary edits to upstream Android files.

When upstream changes are imported, do not overwrite AlexLab-specific technical memory or silently change protected invariants. Reconcile conflicts explicitly.

## Product identity

- Product name: **AlexLab Magnetra**
- Repository name: **AlexLab-Magnetra**
- Current repository tagline: **Search. Magnet. Done.**

Branding of the future PWA is AlexLab Magnetra. Android package/application identity remains at the upstream baseline until an explicit, coordinated rebranding decision is made.

## Cost and service policy

- No paid service, paid API, subscription, higher-cost tier, or recurring paid infrastructure may be enabled without explicit owner approval.
- Unapproved recurring infrastructure cost is capped at **€0**.
- GitHub/GitHub Actions are currently used.
- No Lovable dependency is part of this project.
- Cloudflare Workers is the selected runtime. Canonical production domain: **`https://index.alexlab.media`**. Deployment must remain on the free/no-paid baseline unless the owner explicitly approves otherwise.

Cloudflare Worker source under `worker/` serves static web assets and same-origin `/api/*` endpoints. `worker/wrangler.jsonc` binds the Worker to **`index.alexlab.media`** as a Cloudflare Custom Domain. No subscription or paid tier is authorized.

## Definitive technical decisions

1. Repository truth is authoritative; chat history is not.
2. Material changes are made on branches and reviewed through pull requests; do not push implementation changes directly to `main`.
3. Keep the Android app in `app/` and add the PWA/backend as separate surfaces rather than replacing the upstream app.
4. Preserve the ability to sync upstream fixes.
5. The future PWA must expose magnet links and copy/share actions. Where the provider exposes a `.torrent` file, the PWA should expose that download as well.
6. The PWA is a search/control surface, not an in-browser BitTorrent engine. Actual torrent downloading remains the responsibility of an external torrent client or a future explicitly configured downloader integration.
7. Provider/browser limitations must be solved server-side where necessary; do not weaken browser security or put private credentials in public frontend code.
8. Critical invariants must be changed only with explicit owner approval and updated atomically in code, this checkpoint, machine-readable invariants, and tests/guards.
9. No automatic modernization of versions/configuration merely because a newer option exists.

## Protected Android baseline

The Android baseline was forked from upstream commit `100b3f21f98b93bb9b70869ba5f70eadc80fa14c`. Current fork `main` has intentionally diverged with AlexLab technical memory, PWA and CI changes; it no longer matches this upstream SHA.

Protected baseline values:

- Android application ID: `com.prajwalch.torrentsearch`
- minSdk: `25`
- targetSdk: `37`
- Java source/target compatibility: `17`
- CI Gradle daemon runtime: **JetBrains Runtime 21**, installed separately from Temurin 17 and required by `gradle/gradle-daemon-jvm.properties`.

These values are protected because they describe the known-good starting point. They may change later only as an intentional coordinated decision.

## First PWA implementation — historical first milestone (2026-10-07)

- Full canonical inventory: exactly **46 built-in upstream indexers**, derived from `BuiltinSearchProvidersModule.kt`. Guard checks matching upstream provider IDs, not merely count.
- Explicitly ported adapters in the first milestone (**21**): `AniLibria`, `Knaben`, `TorrentsCSV`, `ThePirateBay`, `YTS`, `Internet Archive`, `BangumiMoe`, `SubsPlease`, `Btsow`, `Nyaa` and `Sukebei`; plus `BTDigg`, `Dmhy`, `NekoBT`, `Mikan`, `TorrentKitty`, `Rutor`, `XXXTracker`, `AnimeTosho`, `LimeTorrents`, `TorrentDownload` (HTMLRewriter). These are implemented adapters, **not yet live-tested against every provider**; real-world availability remains an external dependency.
- **Historical only:** in this first milestone 25 providers were still **PORT PENDING**. All 25 subsequently received adapters in the second milestone. Full 46-source **live functional parity remains unverified**, so the historical PORT PENDING note is not the current state.
- Search worker accepts an allowlisted set of provider IDs, a bounded query and category, with provider-specific adapters, up to all 46 registered sources (once ported), with at most three simultaneous per-provider fetches to bound load.
- PWA displays source, size, seeders, peers, date, magnet, copy/share, torrent link when provided, bookmarks, and per-provider errors.
- Remote Flud Companion handoff uses a same-origin Worker endpoint which forwards only to `https://flud-remote.alexlab.media` and reuses the verified public Flud Companion `/api/v1/device/:deviceId/magnet` contract. It sends a stable request ID per command for duplicate protection.
- The Companion pairing credentials are stored only in the user's browser local storage; relay forwarding is via HTTPS and the Worker does not persist tokens. Never print or expose credentials in logs, URLs or public artifacts.
- Auto-start is optional and must respect Companion's already validated accessibility/helper state; do not alter Flud Companion's hardware-verified preflight/single-handoff rules.
- Hosted HTTPS PWA to plaintext LAN bridge can be blocked by mixed-content and private-network restrictions. Primary 1-tap integration is the HTTPS Remote relay; fallback is Copy magnet + open Companion PWA.
- The search backend must stay a fixed-provider metasearch service, not an arbitrary HTTP proxy.
- HTML ports are source-based, syntax/bundle-checked and contract-checked but external layouts and challenge pages still require integration validation. Production was deployed successfully on 2026-10-08; live HTTP/TLS, homepage, manifest, health and provider catalog passed the independent GitHub-hosted smoke check on first attempt. Actual searches and Shield Auto-start remain unverified end to end.

## Second PWA milestone — 46 adapter implementations (2026-10-08)

- All **46** registered Android source IDs now have concrete PWA adapter modules (21 pre-existing and 25 new). This is **implementation coverage**, not proof all third-party sources currently respond successfully.
- The 25 additional source contracts are defined in `worker/src/legacy-specs.mjs` and executed through `worker/src/legacy-adapters.mjs`, including original source-specific search URL patterns, provider-limited HTTP requests, and POST-specific implementations for EpubLibre (JSON/HTML) and NoNameClub (form search).
- For providers that only yield a magnet on their details page, search results remain visible with `magnet: null` and a provider-owned details URL. The PWA uses same-origin `POST /api/resolve` only when needed (Send, Copy, Share, Resolve). Resolution rejects non-HTTPS origins, private/unknown destinations, forged userinfo, oversize URLs and off-provider redirect responses. Some legacy providers may still require cookies or anti-bot sessions that cannot be reproduced in a Cloudflare Worker.
- All 35 HTML selector sets (25 new and 10 earlier) are validated syntactically in the **real Cloudflare workerd runtime** using a dedicated CI-only Worker entrypoint. This does **not** establish selector correctness against live third-party markup; a fixture/live audit is still required for individual indexers.
- PWA source buttons distinguish implemented adapters from audited availability; the existence of an adapter must never be presented as proof a third-party provider is online.
- After a deliberately approved production deployment, `scripts/audit-live-providers.py` performs a bounded-concurrency 46-provider innocuous `ubuntu` search health audit, without downloading torrents, sending magnets or accessing Shield credentials. It reports transport/provider errors versus empty results and does not fail builds merely because a third-party service is offline.
- Flud Companion `POST /api/v1/device/:deviceId/magnet` still uses the fixed HTTPS relay and `requestId`. The PWA now checks `lastResult.id` from the established remote `status` endpoint to distinguish relay queue acceptance from successful **Shield command acknowledgement** or a Bridge failure. Neither state proves torrent download completion.
- A **Test Shield connection** action queries existing authenticated Remote status but does not submit a magnet. True iPhone → relay → physical Shield → Flud operation remains **not end-to-end verified**, because no real user pairing credentials or device access are available. No magnet was sent to the user's Shield during automated tests.

### Missing swarm-stat metadata regression

During the full indexer port, `numeric(null)` was found to produce `0` because JavaScript coerces null to zero. This falsely represented missing provider seed/peer statistics as confirmed zero. Fixed by preserving `null` for unavailable/blank values and parsing valid comma-separated numeric counters explicitly; added a unit regression test.

### Important PWA CI regression fixed

While extending source testing, the HTML selector smoke check initially reported success because Wrangler picked up the production static-assets configuration and returned the PWA homepage (HTTP 200), **not** the test Worker response. Root cause: the CI command did not pin a dedicated test Wrangler config or validate response semantics. Fix: `worker/test/wrangler-selector.jsonc` specifies `selectors.worker.mjs`, and CI accepts only JSON with `ok === true`, `checked === 35` and zero invalid selectors. A new invariant prevents this test from silently reverting to an HTTP-only check.

## First live 46-provider production audit (2026-10-08)

The explicitly approved deployment `0b2eec1f2cec13fae05d3a7b4c15bca463afee7a` published 46/46 executable indexer adapters to `index.alexlab.media`. HTTPS, PWA manifest, health API and 46-source catalog passed.

The first bounded, non-destructive live `ubuntu` query audit returned:

- **8** sources with at least one search result: AudioBookBay, Dmhy, EpubLibre, Internet Archive, Knaben, NoNameClub, TorrentsCSV, 0Magnet.
- **14** empty or unverified (no results for this specific query, not automatically broken).
- **24** explicit provider-side errors: mainly HTTP 403; also one HTTP 429 (Nyaa), HTTP 530 (Torrentz), one redirect that the PWA initially refused (LinuxTracker), and an HTML source timeout (BTDigg). Details are in deployment run `37763214467` logs.

This is evidence of partial real-world availability, **not** 46/46 live functionality. A CI adapter test only proves local contracts/selector syntax. Source anti-bot pages, IP reputation, cookies and third-party layout changes remain external limitations.

### Provider fetch compatibility mitigation

The upstream Android `NetworkClient.USER_AGENT` is a fixed Android Chrome 141 UA and uses persistent WebView cookies when needed. The first Cloudflare Worker source fetchers did not consistently send that UA. The compatibility patch centralizes this exact baseline string for Workers in `worker/src/request-headers.mjs` and adds a strictly provider-local one-hop HTTPS redirect policy (instead of blindly following arbitrary redirects). This may improve some third-party compatibility; **no improvement is claimed until a second live audit confirms it**. This is not a Cloudflare challenge/CAPTCHA bypass.

## BTDigg and third-party provider recovery (2026-10-08)

Full 46-source outcomes and the 21 failing sources are tracked in **`docs/PROVIDER_AVAILABILITY.md`**. This is a dated observation, not a promise of live uptime.


Owner reported: `BTDigg: The operation was aborted due to timeout`, requesting remediation for all failing indexers.

### Verified source reachability facts

- The latest pre-recovery Cloudflare production audit (deploy run `37769029530`) found **12 sources returning results**, **13 without results for the benign test query** and **21 with provider errors**, including BTDigg and XXXTracker timeout.
- A temporary **GitHub-hosted** reachability probe tested `https://btdig.com/search?q=ubuntu`, `https://www.btdig.com/search?q=ubuntu` and the origin homepage. **All returned HTTP 429**, not search results. The Cloudflare Worker consistently timed out fetching BTDigg. This is a source/network rate-limiting problem; changing the selectors or increasing request timeouts does not establish connectivity.
- Separate probes of AniRena, BitSearch, LimeTorrents and TorrentDownload returned **403 with `cf-mitigated: challenge`** on GitHub hosts. A browser verification cannot be executed transparently by Cloudflare Workers; never treat these responses as valid search results, and never defeat the fixed-provider origin restrictions to chase redirect domains.

### Safe product behavior

- Source-specific errors now have machine-readable reason codes (`TIMEOUT`, `RATE_LIMIT`, `ACCESS_DENIED`, `CHALLENGE`, `REDIRECT_BLOCKED`, `UPSTREAM_ERROR`) and a user-friendly explanation while retaining the diagnostic raw error.
- Where the official query path is known, the PWA exposes **Open source search** using a hardcoded provider allowlist and HTTPS. This allows the user's browser to visit BTDigg itself without implying the Worker has bypassed an anti-bot challenge.
- **Paste magnet → Flud** is the manual-browser fallback when a source cannot be searched by the Worker. The browser clipboard is read only on user gesture; when unavailable, a manual paste dialog appears. The existing Companion pairing and queued/Shield acknowledgement checks still apply. No browser cross-origin scraping or hidden clipboard polling is permitted.
- The PWA also exposes **Search with available indexers**, explicitly selecting known responsive alternative sources; their results keep their real provider attribution and must never be relabeled as BTDigg or another failed source.
- BTDigg's Cloudflare Worker fetch timeout was shortened to 6.5 seconds to avoid a needless 11-second wait when rate-limited; this improves responsiveness **but does not make BTDigg automated searches work**. No automatic retry storms on 429 and no paid CAPTCHA/browser scraping service.
- Source links are restricted to catalog-defined fixed HTTPS origins. Do not reflect a third-party redirect target or user-supplied arbitrary URL.
- The temporary network diagnostic scripts/workflow steps were deleted after the findings were documented. Only enduring regression tests and the permanent provider audit are retained.

### PWA update/caching regression fixed

The existing service worker used a constant `alexlab-magnetra-v1` cache and served `/app.js` and `/styles.css` **cache-first**. Once installed, a phone could keep using older JavaScript even after a successful Cloudflare deploy, making newly fixed UI behavior appear absent. The service worker now uses `alexlab-magnetra-v2`, refreshes scripts/styles/manifest **network-first** with offline fallbacks, continues serving offline navigation from the cached shell, and refuses to cache `/api/` requests or authenticated Companion commands. The invariant guard and Node tests protect this contract.

### Outstanding

BTDigg and other inaccessible sources are still not reliably searchable automatically from Cloudflare's server network. This requires the provider to accept automated traffic, an officially supported provider API, or an owner-approved alternative architecture. The PWA's direct-browser fallback remains useful but does not silently feed browser-only results into Flud Companion.

## Production recovery deployment and follow-up audit (2026-10-08)

- PR **#6** was squashed to `main` as `060ce27a2ba36310e7e5bc814c025633aba10cff`, deployed by the explicit `[deploy-pwa]` marker.
- GitHub workflow **37816874771** confirmed Cloudflare publish, HTTPS, HTML, manifest, health and complete 46-entry provider catalog.
- Follow-up bounded production audit: **12 sources with query results**, **12 empty/unverified**, **22 provider-side errors**. Exact individual states and comparison with the previous 12/13/21 observation are recorded in `docs/PROVIDER_AVAILABILITY.md`.
- BTDigg still **times out** from Cloudflare, despite its hosted endpoints returning HTTP 429 independently from a GitHub runner. No programmatic recovery has been established. PWA now offers direct HTTPS BTDigg search and a manual magnet copy→Flud fallback.
- One `tokyotoshokan` response had `code: UNCLASSIFIED` in the audit despite an HTTP 403 diagnostic, while most other errors supplied typed codes. This might be edge rollout timing or an inconsistent API response; do not invent a cause, verify on any subsequent provider audit.
- The new source-recovery UI, clipboard handoff, typed error metadata, PWA cache refresh and invariant tests were deployed without paid infrastructure. Successful server deployment **does not imply every third-party search source is available**.

## Audit-aware provider selection (2026-10-08)

A review of the PWA revealed a real usability regression: the "Select working" button selected all 46 implemented adapters even though the verified post-deploy audit had only 12 sources returning results, 12 empty/unverified and 22 errors. This falsely implied that implementation coverage established provider uptime and needlessly prolonged searches.

Fix:
- Source-specific, timestamped audit snapshot in `worker/src/source-audit.mjs` from successful deployment run `37816874771` (benign query `ubuntu`, observed 2026-10-08T17:29:37Z). All 46 original IDs and three outcome categories are preserved.
- `/api/providers` now includes `audit.observedAt`, `query`, `workflowRunId`, and each provider's historical `lastAudit` result. **This is not live availability** and must not be presented as such.
- "Select last-audit results" selects only the 12 sources that returned results for the audit query, while "Select all 46" explicitly keeps the original complete search capability available. Users can still select any source individually, including BTDigg.
- Default sources for new installations are Knaben, TorrentsCSV, ThePirateBay and Internet Archive, excluding Nyaa after repeated HTTP 429 in the verified audit. Existing user selections in local storage are preserved.
- All statuses are visibly labelled **in test**, with dated explanations and tests protecting the identity/counts. An empty result for "ubuntu" is not evidence that a provider is offline or defective.
- This change only improves selection and status attribution; it does not bypass the external rate limits affecting BTDigg and others. Update the audit metadata only after a new complete, recorded production source audit.

## Audit-aware search deployment and comparative source audit (2026-10-08)

- PR **#8** merged at `bd09a0eb60b679e9e661f0dc1f34613605db2838`, explicitly deployed to `https://index.alexlab.media` via successful GitHub run **37827913584**. Public TLS, homepage, manifest, API health and full 46-source catalog passed the post-deploy smoke test. All PR PWA/invariant and Android Debug/Staging CI checks were green.
- The 46-source **live** `ubuntu` audit after deployment returned **12 with results**, **14 empty/unverified**, **20 with provider errors**, compared with the earlier 12/12/22 observation. This is evidence of changing provider availability, not a guaranteed reliability improvement caused by the selection UI.
- The **same 12 provider IDs** returned results in both the older audit and latest one; consequently the 12-source quick-select profile remains supported by an independent later observation. PWA uses a deliberately dated embedded snapshot from workflow **37816874771**, not a live status feed. The older snapshot's error/empty counts are not the latest audit counts, and must not be presented as such.
- `btdigg` remained `TIMEOUT` and `nyaasi` remained `RATE_LIMIT` (429). `tokyotoshokan` is now categorized `ACCESS_DENIED` (403) instead of `UNCLASSIFIED`. No change in upstream policies or verified programmatic BTDigg access is claimed.
- User-visible behavior now offers **Select last-audit results** versus **Select all 46**, and default API/PWA searches use four previously result-positive sources: Knaben, TorrentsCSV, The Pirate Bay, Internet Archive. Previously saved user selections persist.
- No additional Cloudflare deploy is required for this documentation update. Physical iPhone-to-Shield Flud Companion handoff still requires testing by the owner.

## Consolidated owner decisions and operational contract — current as of 2026-10-08

This section summarizes definitive decisions from the fork/bootstrap, indexer-parity, Cloudflare-deployment, Flud-Companion and provider-recovery sessions. Detailed history above stays preserved.

### Product identity and experience

- Product and repository are **AlexLab Magnetra**, public project at `https://github.com/Zuzuitu/AlexLab-Magnetra`; official PWA at **`https://index.alexlab.media`**, hosted through the owner's Cloudflare account. Keep the original Android TorrentSearch code and MIT/upstream attributions; fork updates do **not** sync automatically and must be explicitly merged/reconciled.
- The owner specifically rejected Lovable. Development and PRs must be done through the GitHub workflow with ChatGPT, without introducing app builders or paid services.
- The product should be a fast, intuitive, installable **mobile-first PWA** (not an Android UI inside a browser). Search and result inspection should be clear, lightweight and responsive on iPhone, Android and desktop. The PWA does not download torrents itself; it links magnets and provider-supplied `.torrent` files and serves as a controller for an external client.
- **All 46 upstream search sources must remain present and independently attributed.** 46/46 means all adapter source code exists, not that live providers are all healthy. Do not reduce the inventory, substitute sources, or silently return results from a different provider under a blocked provider's name. Do not claim the 46/46 **live** milestone is complete.

### Search, UI and source failure semantics

- Backend is a Cloudflare Worker with explicitly fixed provider adapters, not a generic proxy. API: `GET /api/providers`, `GET /api/search`, `POST /api/resolve`, `POST /api/companion/{status,magnet}`, `GET /api/health`. Provider-scoped detail resolution must remain HTTPS, origin-validated and bounded.
- Show real title/source, seeders, leechers, size, date and search result actions; missing seeders/peers must remain `null`, not falsely normalized to zero. Keep source/provider selections and bookmarks browser-local. Preserve progressive result rendering, bounded concurrency, UI sorting, Copy/Share/Open Magnet, Details, and `.torrent` action only when upstream supplies one. A result without immediate magnet may remain visible and lazily resolve the magnet from its allowed details URL.
- Default new-install source selection (same in PWA and API): **Knaben, TorrentsCSV, The Pirate Bay, Internet Archive**. Preserve existing users' locally stored selections. Provide distinct **Select last-audit results** (12 IDs from dated, tested `ubuntu` snapshot) and **Select all 46**. Any source can still be manually selected. Clearly state all audit badges are *historical*, **never 'online now'**.
- Audit statuses must distinguish `results`, `empty-or-unverified`, `provider-error` and `request-error`. A zero-result `ubuntu` query does not prove outage. Production search tests must be bounded (three concurrent), benign and non-destructive; never fetch torrents or submit live magnets in unattended audits.
- BTDigg is implemented but **does not work reliably via Cloudflare**: GitHub-hosted probes of `btdig.com` and `www.btdig.com` returned HTTP 429, while Worker searches timed out. Worker BTDigg timeout is 6.5s; increasing timeouts/retry storms, changing UA speculatively or pretending a source works are not acceptable fixes. Many other sources return 403/browser challenges, and some return 520/530 or 429. Provide typed errors and direct **Open source search** link on provider-owned HTTPS URLs, plus **Search with available indexers** that preserves correct attribution; these are UI workarounds, **not automatic provider recovery**.
- Last complete live audit **37827913584**: **12 results / 14 empty-or-unverified / 20 provider errors**, against the single `ubuntu` query; same 12 result-positive sources as previous audit. The UI's deliberately fixed `worker/src/source-audit.mjs` snapshot **37816874771** is older **12/12/22**. Keep both sources separately identified. The canonical longitudinal record is `docs/PROVIDER_AVAILABILITY.md`.

### Flud Companion workflow

- Preferred one-tap action is **Send to Flud**, via **same-origin Worker → fixed HTTPS relay `https://flud-remote.alexlab.media` → NVIDIA Shield/Flud Companion**. The existing external repository is `Zuzuitu/flud-companion`; do **not** modify it or replace its tested Auto-start / single-handoff semantics casually.
- Pairing uses a Remote Device ID and token saved locally in the owner's browser; the PWA can import them from the existing Remote QR URL fragment into local fields. Never commit/log/send pairing tokens to chat or URL query strings. Clipboard read is only on user action.
- Relay `202 queued` means the relay queued the command, **not** Shield acknowledgement and **not** torrent completion. Poll the existing Remote status for matching `lastResult.id` before showing a Shield acknowledgement; an acknowledgement still does not prove a finished download. Keep idempotent request IDs.
- Use read-only **Test Shield connection** before an actual magnet action. When a provider is browser-only, provide **Paste magnet → Flud** and a manual paste dialog on iOS where clipboard permission is unavailable. **No physical iPhone → Relay → Shield → Flud end-to-end verification has yet been supplied**; owner-assisted test still required. Never assert a download occurred based only on mocked CI.
- Preserve the PWA's `localStorage` pairing model as currently implemented and audit risks before any security/storage architecture change; no new account system or remote telemetry.

### Deployment, safety and regressions

- Cloudflare Worker hosts static `web/` via `assets`, custom domain route for `index.alexlab.media`; deployment via `.github/workflows/deploy-pwa.yml`. `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` are **already installed privately as GitHub Actions secrets**; never request them in chat or publish them.
- Only **manual workflow dispatch or an explicit `[deploy-pwa]` marker on a main-branch commit** deploys. Normal docs-only changes do not trigger a deployment. Before merging material code: branch → PR → `python3 scripts/check-project-invariants.py` → Node/provider tests → workerd selector validation → Cloudflare dry-run → Android Debug and Staging CI. After approved deploy: public HTTPS/PWA/API smoke and bounded 46-provider audit. `docs/PROJECT_STATE.md` and machine invariants must stay synchronized with architecture/rule changes in the same PR.
- Keep Android Kotlin app, minSdk 25/targetSdk 37, Java source 17, Gradle daemon **JBR 21**, GitHub workflow checks, MIT attribution and upstream merge ability. Never auto-modernize constraints. Release signing and Cloudflare secrets are never public.
- Known fixed regressions (history above): JBR 21 installation in Android CI; scope of JBR guard limited to Gradle jobs; Worker selector test previously falsely validated PWA HTML 200 rather than a dedicated workerd JSON response; JavaScript `Number(null)` falsifying unknown peers/seeders as zero; PWA v1 cache-first stale assets (now `alexlab-magnetra-v2`, network-first for scripts/styles/manifest, no caching `/api/`); 'Select working' erroneously selecting all 46 sources (now separate dated last-audit results and all-46 actions); API/PWA default selection drift.
- **No unapproved paid API, subscription, increased usage spend, proxy/SaaS, CAPTCHA-solving, telemetry or service tier.** Unapproved recurring spend limit **€0**.

### Next-chat working priorities (not claims of completed work)

1. **Verify current GitHub main and all CI runs**, then read this checkpoint, `config/project-invariants.json`, `AGENTS.md`, `docs/PROVIDER_AVAILABILITY.md` and `docs/NEXT_CHAT_HANDOFF.md`. Do not assume the SHA or provider status in this note is still current.
2. **Validate the live result pipeline, not only provider counts**: real benign-source fixtures/query relevance; complete results, working magnets and deferred detail resolution; fields, sort/duplicate handling and stable source identity. Prioritize the 12 confirmed result-positive sources and then assess the remaining 34 individually. Diagnose code defects separately from source-side 403/429/CAPTCHA.
3. Improve blocked provider diagnostics/recovery within safe fixed-origin security boundaries, focusing especially on **BTDigg**, Nyaa and any known domain moves. Do not promise 46 live sources without 46 verified source checks. Avoid excessive probing or automatic retries.
4. **Owner-assisted iPhone/Android ↔ Flud Companion ↔ Shield acceptance testing**: pair with existing Remote QR, read-only status, test a lawful magnet, observe queued → matching Shield acknowledgement → actual Flud appearance; offline, Auto-start, duplicate, invalid token and timeout paths. Never ask user to paste credentials into chat.
5. Complete mobile UX, accessibility, responsive layout, copy/open/share/`.torrent`, PWA update/cache behavior, and cross-device tests without regressing current installation. Add reproducible tests and source-specific fixtures.
6. Every material improvement: branch → implementation → tests → guarded PR → green CI → merge → explicit production deploy when approved → live smoke/audit → checkpoint/invariants/guards refreshed. **No payment or broader infrastructure changes without permission.**

## Data and security rules

- Never commit private keys, keystores, credentials, access tokens, real `.env` files, or service-account credentials.
- Release signing secrets belong in GitHub Actions secrets/environment configuration, not source files.
- Public frontend code must not contain provider credentials or private API tokens.
- Do not move signing material into `web/`, static assets, generated public bundles, or client-visible environment variables.
- The application may store local user preferences/history/bookmarks, but no new remote telemetry, account system, or user-data collection is approved by default.
- Torrent metadata comes from third-party providers; provider availability and correctness are external dependencies.

## Behaviors that must not change accidentally

- Existing Android build variants remain `debug`, `staging`, and `release`.
- Existing Android application/package identity remains unchanged until explicitly approved.
- Upstream Android functionality must not be removed merely to simplify PWA work.
- Release secrets must remain external to the repository.
- Invariant checks must run before build/deploy work in guarded CI workflows.
- PWA work must not make the repository dependent on a paid service by default.
- Upstream synchronization must remain possible.

## Known external limitations and workarounds

- Browser CORS rules prevent a PWA from directly calling every provider that the Android app can call.
- Some providers use Cloudflare challenges/cookies. Android has native handling that cannot simply be copied into a browser PWA.
- HTML-scraping providers may require server-side fetch/parsing.
- Provider APIs and page layouts are third-party dependencies and can change without notice.
- A provider proxy/backend must never become a generic open proxy; routes must be allowlisted to supported provider operations.

## Important regressions / causes

Several concrete PWA/UX and CI regressions were found and addressed in this session, including stale service-worker caches, misleading selection of all adapters as 'working', missing swarm-count coercion, workerd selector-test false positives, and inconsistencies between API and PWA default source IDs. Root causes and fixes are preserved above and in the provider documents.

The first repository-safety issue identified at project start was that existing build workflows had no project-invariant gate, and the release workflow could materialize signing material before any repository-policy validation. This memory-system change adds an invariant guard before build/release-sensitive steps.

Initial upstream CI regression (2026-10-07): both Debug and Staging failed before Android compilation with Foojay HTTP 400 while attempting to download JetBrains Runtime 21. Root cause: existing workflows only installed Temurin 17 although the committed Gradle daemon JVM criteria require vendor JETBRAINS/version 21. Fix: explicitly provision JBR 21 with `actions/setup-java` after JDK 17; keep Android Java 17 source/target compatibility unchanged. Guard: require correct Gradle daemon vendor/version and JBR setup in all Android workflows.

PWA CI invariant-guard regression (2026-10-07): adding the PWA job to `delivery.guarded_workflows` initially caused CI to fail because the JBR 21 prerequisite was checked for every guarded workflow, including Node-only tests. Root cause: guard scope was too broad. Fix: enforce JBR 21 only on workflows containing a Gradle build (`./gradlew`), while still requiring the general invariant gate for all guarded workflows.

Cloudflare production deployment initial failure (2026-10-08): deploy job failed at credential validation because newly created repository lacked `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` GitHub Actions secrets. Owner configured them privately; rerunning failed jobs deployed the Worker and its `index.alexlab.media` custom domain. Prevention: pre-deploy secret check; permanent independent post-deploy smoke workflow verifying HTTPS, homepage, manifest, health and provider catalog.

Future fixed regressions with durable lessons must be recorded here with:
- symptom;
- root cause;
- fix;
- guard/test that prevents recurrence.

## Current state

- Fork created successfully.
- Android baseline originates from upstream commit `100b3f21f98b93bb9b70869ba5f70eadc80fa14c`; fork `main` now diverges intentionally with PWA and technical memory.
- Technical-memory guard baseline is established in main and enforced in CI.
- PWA web shell and all **46 original provider adapter IDs** are merged and deployed. **Latest verified complete production audit (run `37827913584`): 12 source IDs returned results, 14 were empty/unverified for the single `ubuntu` query, and 20 reported upstream errors.** The older, deliberately dated UI snapshot (run `37816874771`) still describes 12/12/22; do not confuse these two datasets. Physical Shield handoff is unverified. Audit-aware source selection was merged in PR #8 and deployed.
- PWA backend/proxy is deployed to Cloudflare Workers with fixed allowlisted upstream endpoints.
- Full 46-provider **implementation coverage reached and deployed**, but functional/live parity remains unverified. Never infer source uptime from the catalogue.
- Production is live at **`https://index.alexlab.media`** via Cloudflare Workers Custom Domain. Initial deployment was verified by run `37596819448`; full 46-adapter deployment by run `37763214467`; source recovery by run `37816874771`; **most recent PWA deployment and HTTPS/provider smoke by successful run `37827913584`**. PR #9 was documentation-only and did not deploy. Deployment requires manual dispatch or an explicit `[deploy-pwa]` marker on `main`; ordinary pushes do not deploy.
- GitHub `main` checkpoint before this synchronization: `94d2b6b40e4a3ad465f0c39e64fc1df4301f9f87` (PR #9), with no open PRs as inspected on 2026-10-08. This SHA is an observation and must never be assumed latest in a future chat.
- Paid services: none approved.

## Next relevant steps

1. Maintain the canonical technical-memory baseline and keep its CI guard green.
2. Test real source searches and deferred magnet resolution, then verify Remote Companion handoff on iPhone/Shield without exposing pairing credentials.
3. Audit and repair all 25 newly ported indexers with live provider fixtures and targeted Cloudflare tests; document CAPTCHA/challenge providers honestly.
4. Verify real iPhone browser/PWA behavior and Shield integration, especially device offline/queue/Auto-start.
5. Verify the existing open/copy/share/magnet and `.torrent` result actions on real iOS and Android devices.
6. Add provider-specific tests and document every stable workaround/invariant discovered.
7. Keep the post-deploy smoke check and production invariants green after future explicitly approved releases.

## Maintenance rule

After any important milestone, update this checkpoint naturally when a definitive architecture decision, important bug root cause, external limitation, or new invariant appears.

When the owner says:

> “Actualizează checkpoint-ul proiectului cu toate deciziile din această sesiune.”

review current `main` plus the current session, update the technical memory without inventing decisions, and preserve still-relevant historical context.

## Mobile progressive search and Companion repeat-tap hardening (2026-10-08, proposed)

Following an inspection of live repository source and the separate `Zuzuitu/flud-companion` relay implementation:

- **Root cause — head-of-line search blocking:** `web/app.js` awaited three-source `Promise.all` batches. One 6.5–11-second blocked provider could prevent the fourth source from starting despite other slots being free. The UI now runs a maximum-three **sliding work pool**: successful or failed sources release their slot immediately, preserving streamed results and source attribution. Pressing Search again while searching cancels the current batch via `AbortController` and ignores subsequent stale completions; previous successful rows are retained. An alternate-source selection aborts the previous search before beginning the new selection.
- **Root cause — duplicate Companion commands:** result cards are recreated while search results arrive, which can replace a disabled Send button; previously each subsequent tap generated a new random `requestId`. The PWA now coordinates active sends by item and normalized BTIH identity, and reuses a request ID for repeat requests within **110 seconds**, inside the **120-second** recent-client-request window verified in `flud-companion/selfhost/relay/src/index.js`. The relay remains the authority for mailbox deduplication; no new persistent personal data or background automation was added.
- **Explicit status boundary:** the UI requires a non-empty relay receipt ID, labels a queued response as queued only, and reports Shield acknowledgement only after `status.lastResult.id` matches. No code can certify actual torrent download completion from this acknowledgement.
- **Regression coverage:** `worker/test/pwa-interactions.test.mjs` exercises sliding-pool scheduling against a blocked indexer, cancellation with a late transport response, and simultaneous/repeated magnet submissions using an isolated simulated browser and relay. Other invariant/Worker/workerd/Android checks remain required; fixture successes do not imply an external provider became available.
- **BTDigg comparison:** current fork's `BTDigg.kt` requests `https://btdig.com/search?q=` and uses `div.one_result > div`, `div.torrent_name > a`, `div.torrent_magnet > div.fa-magnet > a`, matching `worker/src/html-adapters.mjs`. This does not establish a successful upstream fetch; independent hosted HTTP 429 and Worker timeout remain authoritative. Preserve provider-owned browser fallback; do not claim a usable public official API without evidence.
- **Upstream feature-parity gap:** the original Android tree includes a user-configurable `TorznabSearchProvider` plus associated configuration and XML parsing. The PWA's **46 built-ins** do not constitute Torznab parity. No user-entered arbitrary Torznab endpoint was introduced, because that would require a separate threat model, allowlisting/SSRF policy, credential lifecycle and explicit architectural approval.

**Release status:** this change is on a feature branch for GitHub CI and pull-request review; the production Cloudflare version remains the previously approved deployed version until a separately authorized release. Provider availability counts remain at the last actual full production audit (**12 results / 14 empty-unverified / 20 errors**); no new live 46-provider audit is claimed by these changes.

## API and Nyaa outbound redirect security regression — proposed PR #12 (2026-10-08)

- **Verified root cause:** `worker/src/providers.mjs` used `redirect:"follow"` for its JSON API adapters, and default redirect following for Nyaa HTML. Unlike the legacy and HTMLRewriter provider adapters, these requests could follow an off-origin 30x response. This contradicted `AGENTS.md`, `config/project-invariants.json` and the protected one-hop same-origin HTTPS provider policy.
- **Scoped fix:** both `requestJson()` and `requestHtml()` now reuse existing `fetchProviderSameOrigin()`, preserving the existing provider URLs, request headers, timeouts, parsing and payloads while enforcing manual redirect inspection. No arbitrary proxy, no extra services and no new provider calls.
- **Regression tests:** `worker/test/outbound-redirects.test.mjs` covers off-origin rejection without following, one allowed same-origin HTTPS redirect, repeated redirects, POST request payload/method integrity, Nyaa HTML behavior and a single 429 with no retries. Production/provider behavior remains unverified until the next authorized deployment and audit; the snapshot counts remain 12/14/20.
- This is an independently reviewable security change, deliberately separate from the earlier PWA search/Flud flow PR #11; no automatic production release is authorized.

## Explicitly authorized production release — 2026-10-09

The owner explicitly instructed `Fa eploy si gata` after PR #14 (BTDigg browser import) and PR #15 (iOS installed-PWA clipboard handoff) were merged, so production publication of the **existing tested main code** is now approved on the existing Cloudflare free baseline. Release target: `https://index.alexlab.media`, approved source commit `3d2b02b6f895373f1284f13334701aafde53f855`. This release-only documentation PR is to be squash-merged with the exact protected `[deploy-pwa]` commit marker to invoke the existing guarded GitHub Actions workflow. The workflow must check project invariants, Node regression tests, Wrangler dry-run, Cloudflare credentials, deploy, production HTTPS smoke and actual 46-source audit. A merge or workflow trigger is **not** proof of successful production deployment; consult the workflow conclusion and live evidence before recording success.

The BTDigg import is **user-initiated**, reading visible BTDigg page results in Safari and importing via copy/paste into Magnetra PWA without changing Companion pairing. Automatic BTDigg server search is still blocked/unverified due to provider restrictions. No new services, payments, proxy/CAPTCHA bypasses, background crawlers or Shield downloads are authorized.


## BTDigg Rock64 residential gateway — implementation candidate (2026-10-09, NOT deployed)

The owner states that BTDigg is accessible via their home internet connection and explicitly approves proceeding with an automatic PWA search option through the existing Rock64; this is NOT evidence that Python on Rock64 has successfully fetched actual BTDigg result HTML. Existing direct Cloudflare BTDigg attempts have timed out or returned HTTP 429. The previously implemented manual iPhone browser bookmarklet fallback remains present in production but is not the user's desired final interaction.

A bounded, genuine-source-only **optional** path is now implemented on a feature branch:
- `rock64/btdigg_gateway.py` is a Python standard-library service bound **only to 127.0.0.1:8796**, requiring a strong bearer token. It fetches only `https://btdig.com/search?q=...`, never caller-selected origins, and returns real HTML through the original HTMLRewriter adapter, without inventing results. It refuses redirects and large/challenge/error responses, does not retry 429, caps concurrent and frequent requests, and never logs tokens, queries or magnets.
- `worker/src/btdigg-rock64.mjs` adds an optional authenticated, fixed `https://btdigg-rock64.alexlab.media/v1/search` subrequest. Only the **BTDigg** adapter is routed to it, and only if a valid secret `BTDIGG_GATEWAY_TOKEN` exists server-side. All other 45 indexers and the Flud Companion remote integration remain unchanged. If the secret is absent, original direct Cloudflare BTDigg search remains unchanged. If configured but unreachable/429, it fails closed and reports an error instead of relabeling another provider.
- The gateway expects `MAGNETRA_BTDIGG_TOKEN` in a root-owned Rock64 environment file, with precisely the same value. It uses neither paid providers nor arbitrary reverse proxies, DNS IP rotation, CAPTCHA bypass, new DHT crawling, or public torrent payload hosting.
- Dedicated, isolated systemd service examples for the Rock64 gateway and Cloudflare Tunnel have no overlap with CalciDatum's GitHub Actions runner, NexaPanel files/services, the router or any existing `cloudflared.service`. The tunnel is not installed until physical on-device preflight and a genuine-source one-time check pass; details, rollback and secret handling are in `rock64/README.md`.
- CI adds Python local HTTP/authorization/rate-boundary checks plus Node Worker transport/allowlist checks and preserves the existing Cloudflare workerd source selectors. The protected machine-readable `btdigg_residential_gateway` invariant and repository checker explicitly guard the new fixed-origin/secret architecture.

**Hard status boundary:** Code and tests in GitHub DO NOT mean the gateway is actually running on Rock64. A separate Cloudflare Tunnel route and matching secrets require local owner-controlled configuration; none may be assumed provisioned. No real BTDigg source HTML from Rock64, successful worker-to-tunnel connectivity or live PWA BTDigg search has yet been verified. Do not enable the production Worker secret, touch the production deploy, or claim full automatic BTDigg success until the protected local probe and end-to-end evidence are available. User-specified zero-cost rule and source attribution remain authoritative.

- A guarded, isolated one-command **staging installation** helper `sudo bash rock64/install-btdigg.sh` validates local tests and Python syntax, creates only Rock64 Magnetra-specific directories/service, generates a local secret without echoing it, and explicitly does not provision Tunnel/Cloudflare or alter pre-existing services. This does not remove the requirement to test real BTDigg HTML on Rock64 before activating remote search.

## BTDigg manual-import feature retired — 2026-10-12

Owner rejected the BTDigg Safari bookmarklet/manual clipboard workflow and explicitly ordered complete removal from application code and current instructions. The browser-import dialog, bookmarklet script, 3-step walkthrough, clipboard import, associated style, service-worker asset and obsolete tests are removed. Do not reintroduce the browser/clipboard BTDigg import mechanism without a fresh, explicit owner instruction. Flud Companion's *generic* magnet paste feature remains unchanged. BTDigg retains its canonical identity within all 46 upstream indexers.

The only permitted BTDigg-specific development path is **genuine automatic search**, ideally through the optional private Rock64 BTDigg gateway already in this repository; this integration is not considered functional in production until real Rock64 upstream HTML, the authenticated Cloudflare Tunnel and PWA search results are verified. No paid services, CAPTCHA bypass, third-party index substitution, or modifications to the 45 other providers are approved.

Upstream research: the galaris qBittorrent BTDigg plugin and SearXNG BTDigg backend both fetch the same BTDigg website HTML, not a proven public API. The qBittorrent plugin has open HTTP 429 reports; Jackett also has an upstream BTDigg no-results report. No alternative BTDigg client has been demonstrated to automatically provide actual results in the target hosting environment. Retain prior release/audit checkpoints as historical records.


## Consolidated owner-decision checkpoint — 2026-10-12 (authoritative current session)

This section supersedes *outdated present-tense status claims* in the historical notes above. Retain previous PR/release chronology for auditability. Re-fetch actual `main` and GitHub Actions at each future continuation.

### Verified GitHub code and production truth

- Canonical repository: `Zuzuitu/AlexLab-Magnetra` (fork of `prajwalch/TorrentSearch`). **Verified current main immediately before this docs PR:** `8969b9fe6758f859ac072bea984a5f9c9c59597f`. PR #18 merged into `main` as `2863b3b52ec54b2a882900316ad1c2615ce47c94` on 2026-10-09; PR #19 merged as `8969b9fe6758f859ac072bea984a5f9c9c59597f` on 2026-10-12. No open PRs at the verification moment. The protected CI for PR #19's resulting `main` passed: PWA/provider contracts, technical-memory invariants, Android Debug/Staging, and production smoke (which checks currently hosted production, not unshipped changes).
- **Latest successful protected production deployment verified:** `[deploy-pwa]` commit `239098ba3b1ff3b6a7a5a6021e2cdf3553d784d3`, GitHub Actions run **37980229044**, completed successfully on 2026-10-09. That deployed version still included the BTDigg Safari/clipboard guide. The deploy job for the newer `main` `8969b9fe...` was **SKIPPED** (run **38313083432**). Do not call PR #19's removal or PR #18's private gateway production-published until an explicitly authorized deployment succeeds. The old live UI can therefore differ from current `main`.
- **Last 46-source production audit from the actual latest successful deployment**, run 37980229044: **11 sources returned results; 12 empty/unverified; 23 provider errors; 0 request errors**. BTDigg specifically reported **TIMEOUT** with a browser-recovery URL in that historical deployed build. These numbers replace earlier historical snapshots (12/15/19; 12/14/20; 12/12/22) *for latest verified deployed audit only*. They do not describe present or future source availability. Catalog remains 46 built-in IDs / 46 coded adapters; coded does not mean 46 accessible providers.

### Explicit owner decisions, in chronological order

1. **Core experience:** user searches a query directly in Magnetra and sees genuine source-attributed results, with an optional one-tap send to Flud Companion. No extra manual website browsing, Safari bookmarklets or copying search results for BTDigg. Preserve Android upstream compatibility, all **46 original built-in indexers**, existing PWA and Flud Companion behavior.
2. **BTDigg source fidelity:** if the result says BTDigg, it **must actually originate from `btdig.com`**, not a Bitmagnet/DHT index, Knaben, proxy mirror, unrelated source, or a synthetic result. Changes must be scoped to BTDigg; leave **the other 45 providers intact**. Do not create an arbitrary, paid or unauthorized third-party proxy or try to defeat rate-limits/CAPTCHA.
3. **Original manual fallback:** PR #14 added browser-owned BTDigg import, PR #15 fixed iOS installed-PWA storage separation with a clipboard route, and PR #17 published a three-step Romanian Safari guide. These were experiments; the owner explicitly rejected the whole user workflow as pointless. **PR #19 deliberately REMOVED** `web/btdigg-bridge.js`, the BTDigg dialog, bookmarks, copy/import handlers, their special styles, related tests and service-worker asset; SW cache advanced to `alexlab-magnetra-v5`. The generic `Paste magnet → Flud` feature and privacy scrub for legacy `#btdigg=` fragments remain. Protected `provider_recovery.manual_btdigg_import_forbidden=true` forbids reintroduction without fresh permission. The older PR #17 deploy is historical, *not* a reason to restore the manual route.
4. **BTDigg automated source access:** direct Cloudflare Worker attempts have returned HTTP 429 or timeout. The owner's home browser reaches BTDigg, but that is **not proof** that a Python request on Rock64 can fetch searchable HTML/magnets. The user explicitly approved exploring a local residential Rock64 gateway instead of the bookmarklet. PR #18 implemented the optional code, not physical installation or production activation.
5. **Alternative clients investigated:** SearXNG BTDigg engine, a qBittorrent BTDigg plugin, and reports for Jackett appear to fetch/parse BTDigg's HTML and may hit identical upstream 429/challenges. `btdig/dhtcrawler2` creates its own DHT index; Bitmagnet similarly indexes separately. No alternative was *verified* as a true, automatic BTDigg backend on the required hosting. Evaluating candidates is allowed, but **do not replace BTDigg data and mislabel it** or alter unrelated indexers. Only a genuine-source, supported, tested mechanism qualifies.
6. **Zero new cost:** use existing Cloudflare free baseline and current Rock64 where feasible. Never add paid APIs, paid proxy services, cloud resource subscriptions, CAPTCHA solver payments, or expensive calls without explicit owner authorization. Never print or commit credentials. Never modify existing CalciDatum/NexaPanel services, their GitHub runner, the user's router, an existing `cloudflared.service`, or another project's files for this feature.
7. **Release approvals are scoped:** the earlier `Fa deploy si gata` approved the 2026-10-09 browser-import release, **not an indefinite authorization to publish subsequent revisions**. Production deployment and Worker secret activation require confirmation of the particular version, successful tests and owner approval. Do not claim a change is deployed solely because it merged to GitHub.

### Candidate Rock64 architecture already merged; NOT demonstrated live

- `rock64/btdigg_gateway.py`: Python-stdlib, BTDigg-only gateway bound to `127.0.0.1:8796`, requiring a strong bearer token in `/etc/magnetra-btdigg/gateway.env` as `MAGNETRA_BTDIGG_TOKEN`; fixed upstream `https://btdig.com/search?q=...`; no redirects, no proxy-environment fallback, no automatic retries on 429/challenge, 8-second upstream request timeout, 3MB maximum HTML, max one active search, minimum 5 seconds between new searches, 30-second in-memory same-query cache and no search/secret logging.
- `worker/src/btdigg-rock64.mjs` + `worker/src/index.mjs`: when and only when the Worker secret `BTDIGG_GATEWAY_TOKEN` is configured, BTDigg search uses fixed `https://btdigg-rock64.alexlab.media/v1/search` through a private authenticated Cloudflare Tunnel and then the **existing original BTDigg HTML adapter**. Without the secret, original direct Worker BTDigg fetch remains. The tunnel failure must fail closed, not substitute another index. All 45 non-BTDigg provider adapters and Flud Companion's fixed `https://flud-remote.alexlab.media` relay remain unchanged.
- `rock64/install-btdigg.sh` is the staged, guarded local service installer; `rock64/check-btdigg.py` is the one-time *real* Rock64 HTML+magnet proof; `rock64/magnetra-btdigg.service` and `rock64/magnetra-btdigg-tunnel.service` are isolated systemd unit examples; `rock64/README.md` is the canonical operating/rollback runbook. The Tunnel is **NOT** installed merely by merging these files. Do not assert that `btdigg-rock64.alexlab.media` is configured or available: there is no verified end-to-end result, no demonstrated live Rock64 HTTP 200 with real `div.one_result`/BTIH magnets, no verified Worker secret, and no completed tunnel connection.
- `config/project-invariants.json` key `btdigg_residential_gateway` and `scripts/check-project-invariants.py` protect the exact origins, token names, loopback listener and no-open-proxy/no-substitution/no-retry contracts. Python local HTTP tests, JavaScript Worker tests, dedicated Cloudflare workerd selector tests and Android CI passed, but **fixture/CI success is not physical-gateway success**.
- **Next technical gate** (do not skip): verify Rock64 environment and services *read-only*; validate installer paths, credentials and cloudflared compatibility; perform the one-shot local probe and require genuine HTML rows + valid magnet links. Only if proven and allowed by BTDigg's controls, configure a new isolated Cloudflare Tunnel, a fixed Worker secret (not frontend), and test genuine PWA results with explicit go-live approval. If blocked, diagnose honestly without unsafe CAPTCHA/rate-limit bypass. Avoid flooding searches or destabilizing Rock64/microSD.

### Unrelated but binding prior-session protections

- Progressive PWA searches use a maximum-three *sliding* provider pool with cancellation and stale-result rejection; do not reintroduce head-of-line batching.
- Flud Companion magnet dispatch is idempotent by canonical BTIH and request ID reuse for 110 seconds within the relay's verified 120-second dedupe; distinguish relay queued receipt from Shield acknowledgement and from actual download. No physical send test is authorized implicitly.
- Same-origin HTTPS fetch protection permits at most one redirect within the original provider origin for applicable adapters; maintain the upstream Android user-agent header and honest error/empty source classification.
- Keep service-worker offline shell, explicit browser gestures for generic magnet paste, no cached API/credentials, 46-source inventory and **no unapproved spend**.

### Required next-chat completion criteria

Check fresh `main`, merge/deploy status and actual Rock64 evidence first. Make real scoped improvements on a feature branch, run the repository guard, Node/Python/workerd regression suites and both Android CI variants, merge only with green CI, then deploy only if authorized. Report the precise GitHub commit/PR, real production SHA, last audit and the specific unverified external dependencies. The user also requested a complete new-chat Senior/Staff engineering master prompt; refer to the current handoff and this checkpoint, not the historical paragraphs as present-state instructions.

## 2026-10-13 Rock64 first positive real-source proof and owner-approved code publication

The owner ran the currently merged `rock64/btdigg_gateway.py` module directly on their **actual Rock64**, Armbian v26.11 Debian trixie ARM64, as an unprivileged `runner` user:
```
curl -fsSL https://raw.githubusercontent.com/Zuzuitu/AlexLab-Magnetra/main/rock64/btdigg_gateway.py -o /tmp/btdigg_gateway.py
python3 -c 'import sys; sys.path.insert(0,"/tmp"); from btdigg_gateway import SearchProvider; s,h=SearchProvider.fetch("ubuntu"); print("HTTP:",s,"Rezultate:",h.count(b"one_result"),"Magneturi:",h.count(b"magnet:?xt=urn:btih:"))'
HTTP: 200 Rezultate: 10 Magneturi: 20
```
This is **real positive residential HTTP 200 evidence with 10 HTML occurrences of `one_result` and 20 occurrences of the BTIH magnet prefix**. These are text counts, not yet a validated 10-result parsed API response nor unique torrents. It materially supersedes the old claim that no Python Rock64 source fetch had been tested. Owner approved: `Fa deploy dupa daca e necesar` for the already merged implementation and requested a complete new-chat Senior/Staff engineering prompt. Production code publication is approved; **public activation is a separate gate** involving an installed protected local service, a dedicated working Cloudflare Tunnel and a Worker secret.

Live install status still unknown: the user's command downloaded a module into `/tmp` and invoked its static `SearchProvider.fetch`, **not** `rock64/install-btdigg.sh`, `rock64/check-btdigg.py`, a persistent systemd unit or Cloudflare Tunnel. Never claim `btdigg-rock64.alexlab.media` reachable, the Worker secret provisioned, or end-to-end PWA search recovered until actually observed. The alternative `btdig/dhtcrawler2` and independent DHT indexes do not count as BTDigg data. The old Safari bookmarklet path was retired on owner request and remains forbidden by `provider_recovery.manual_btdigg_import_forbidden`; keep 45 other engines and Flud Companion unchanged.

Release mechanism: guarded GitHub Actions `Deploy Magnetra PWA` via an explicitly `[deploy-pwa]` marked squash release commit, after green PR CI, then production smoke and actual 46-source audit. It deploys the already merged *disabled-by-default* BTDigg gateway adapter to the current zero-new-paid-services Cloudflare Worker; without `BTDIGG_GATEWAY_TOKEN`, that adapter still uses the direct Cloudflare path and may time out. The release does not create or change Rock64 services, tunnel DNS, secrets, CalciDatum/NexaPanel, routers or Flud.

## 2026-10-13 release receipt — Cloudflare successfully deployed, Rock64 tunnel inactive

**Verified release:** PR #21 was squash-merged as commit `eb37a7ca5c605a125e4a858525991d82a7867db3` and deployed by GitHub Actions **Deploy Magnetra PWA run 38316637704**, conclusion **success**. Workflow results: 48/48 Node tests passed; the Cloudflare Worker deployed; HTTPS+TLS, HTML, manifest, `/api/health` and `/api/providers` all passed, reporting 46/46 implemented provider adapters. Its full post-deploy 46-provider audit reported **12 returned-results sources, 14 empty-or-unverified sources, 20 provider-errors, 0 transport request-errors**; BTDigg returned **TIMEOUT** through the still-unconfigured public path. These are measured results for that run only, not guarantees of later provider availability.

The user-provided direct Rock64 Python proof earlier in the session returned HTTP 200 and actual BTDigg HTML markers, so the upstream is reachable over the residential connection. The guarded permanent gateway service, isolated Cloudflare Tunnel and matching Worker secret were NOT installed/provisioned by the GitHub deploy; therefore **end-to-end automatic BTDigg search is not yet active or verified**. Keep the existing original 45 other providers, Companion integration, removed Safari bookmarklets, zero-new-paid-cost policy and token secrecy protected. Next operational step is `sudo bash rock64/install-btdigg.sh` from a verified main checkout, then `sudo python3 /opt/magnetra-btdigg/check-btdigg.py`, then Cloudflare tunnel + secret with owner-controlled privileged operations and end-to-end test. Avoid Cloudflare same-zone error 1042 by testing route; do not preemptively change global compatibility flags that may affect Flud Companion.

## 2026-10-13 Rock64 BTDigg infrastructure activation — end-to-end still failing

**This section supersedes the earlier uninstalled/staging statements above as operational history.** GitHub main inspected immediately before this documentation change: `4204c283da9a6622c006c58140f7a86c56dabe3b`. The last independently verified application-code Cloudflare release remains `eb37a7ca5c605a125e4a858525991d82a7867db3` (GitHub Actions run `38316637704`, success); main's later documentation-only deploy was skipped. Do not mistake a documentation merge for another production release.

**Physical Rock64 evidence supplied by owner:**
- Guarded `rock64/install-btdigg.sh` installation succeeded. `magnetra-btdigg.service` reported `ActiveState=active`, `SubState=running`, `Result=success`; `ss` showed Python bound exclusively to `127.0.0.1:8796`. `/opt/magnetra-btdigg/check-btdigg.py` returned **local HTTP 200, 10 parsed `one_result` rows, 10 validated BTIH magnet anchors, PASS** for benign query `ubuntu`. These are HTML-parser counts, not proof of ten unique indexed items or an API JSON capture.
- Installed Cloudflare `cloudflared` 2026.10.0 (Debian arm64) at `/usr/local/bin/cloudflared`, not the example unit's `/usr/bin/cloudflared`; the owner's *dedicated* `magnetra-btdigg-tunnel.service` was adapted to the verified absolute path and reported `active`. Gateway also remained `active`. Tunnel token is held in `/etc/magnetra-btdigg/tunnel-token`, gateway token in `/etc/magnetra-btdigg/gateway.env`; do not print, copy into GitHub or expose either credential.
- Cloudflare Tunnel hostname `btdigg-rock64.alexlab.media` is configured for local **HTTP** origin `http://127.0.0.1:8796`. An initial Cloudflare origin misconfiguration gave public HTTP 502; after correcting the origin scheme from HTTPS to HTTP, the owner observed **public `https://btdigg-rock64.alexlab.media/healthz` returning HTTP 401**, as expected for a reachable gateway without an Authorization bearer. Public HTTPS and private local HTTP are intentional.
- Owner configured the production Cloudflare Worker runtime **Secret** `BTDIGG_GATEWAY_TOKEN` to match the locally generated `MAGNETRA_BTDIGG_TOKEN`, initially reported success, **then reported that BTDigg returns no results and the PWA test shows an error**. End-to-end automatic BTDigg functionality is **NOT verified**. Diagnose the exact `/api/search?q=ubuntu&providers=btdigg` JSON `errors` before proposing Cloudflare compatibility changes; a previous ChatGPT link accidentally encoded `&` as `%26` and may have produced an incorrect query.
- **Verification provenance:** physical local HTTP 200/PASS, active services and public unauthenticated HTTP 401 were evidenced by terminal output posted by the owner; actual authenticated Worker JSON payload and its title/size/hash fields were not independently captured in this chat. A separate assistant-side HTTPS probe failed DNS resolution in the execution environment, not with an application-side error. **The owner's latest report contradicts their initial success report**: mark end-to-end as failing pending sanitized JSON diagnostics. No magnet was automatically sent to Nvidia Shield; Flud Companion's existing explicit-send and idempotency boundaries remain unchanged.

**Production boundaries preserved:** one authentic BTDigg adapter, other 45 sources untouched, no Safari bookmarklet flow, no paid infrastructure, no credential disclosure, no global Cloudflare compatibility change for error 1042, and no modifications to CalciDatum/NexaPanel/other tunnel services. `/healthz` returning 401 *without a bearer* is healthy and intentional; do not attempt to make it publicly unauthenticated.

**Future check (only if warranted):** with the user actively testing, inspect `/api/search?q=ubuntu&providers=btdigg` for genuine `provider:"btdigg"`, nonempty titles, sizes and valid magnet URIs, or investigate any reported errors. Do not auto-retry 429/CAPTCHA and do not submit a magnet to Flud without an explicit user action. Preserve existing installed services and secrets; do not rerun the installer just to observe state.

### 2026-10-13 post-activation API evidence and BTDigg magnet encoding repair (PR #23)

The owner uploaded a JSON result captured from `/api/search?q=ubuntu&providers=btdigg`: **HTTP application payload contains `total:10`, `stats:[{provider:"btdigg",count:10,ok:true}]`, `errors:[]` and ten records with genuine `btdig.com` detail URLs, visible nonempty names, size fields and BTIH magnet prefixes**. Thus the production Worker-to-Rock64-to-BTDigg-to-JSON path **does work for this specific query**; do not claim the API is broken based on a separate Python client receiving an HTML HTTP 403. PWA UI rendering and actual magnet delivery to Flud remain separate acceptance gates.

In the same session, a Python standard-library `urllib.request.urlopen` call from Rock64 to the public `index.alexlab.media` URL returned **HTTP 403 with non-JSON HTML**, while browser-captured JSON shows success. This strongly suggests differing Cloudflare client/IP treatment, but no WAF rule or response headers were captured; **do not assert WAF as proven, nor relax account-wide Cloudflare security**. The API itself cannot have produced this response from its normal `getSearch` path, which returns JSON even on provider errors. A test URL previously sent by the assistant had incorrectly escaped the query parameter separator as `%26`; use a literal `&` between `q` and `providers`.

**Real defect in otherwise successful JSON:** every BTDigg result magnet included literal HTML entity text `&amp;dn` and `&amp;tr`, rather than legal magnet query separators `&dn` and `&tr`. The BTIH part was present, but downstream clients could misinterpret display-name and tracker parameters. This PR adjusts **only BTDigg** HTML magnet output, decoding one remaining `&amp;` layer after HTMLRewriter's attribute read. A Node unit test verifies BTIH, name and tracker parameters; a real workerd selector fixture simulates HTML-escaped attributes based on observed BTDigg JSON. Other providers, Flud relay/idempotency logic and source identity stay unmodified. **This patch is not deployed until a separate authorized production release.**

## 2026-10-13 approved BTDigg release

The owner approved deployment of the merged BTDigg-only magnet parameter normalization from PR #23, based on GitHub main `a9d23b1206e867157ba4fb42ebd4b0a283503d74`. The release must use the existing gated GitHub Actions workflow; verification of the deployed version and API response is still required. No changes to other search providers or Rock64 services are included in this release marker.

## 2026-10-13 BTDigg magnet normalization — verified production deployment receipt

Production release PR #24 was squash-merged on `main` as `62a30d7b25da1ebcb6e6d35e27b840ba3dee8aac` with explicit `[deploy-pwa]` authorization marker. GitHub Actions deployment run **38361367716** completed with **success**. The workflow verified invariant guards, Node provider/Flud safety tests, Wrangler deployment, production HTTP/TLS/PWA smoke (`/api/health` and `/api/providers`, 46/46 adapters), and a full 46-provider live `ubuntu` audit.

- Cloudflare Worker name: `alexlab-magnetra`, custom domain `https://index.alexlab.media`.
- Actual Cloudflare Worker **Version ID** from deploy log: `b0375998-666b-4160-8390-987f62457f01`.
- Real production audit **13 providers returned results / 14 empty-or-unverified / 19 provider errors / 0 transport request errors**.
- Specifically `{"id":"btdigg","state":"results","count":10}` appeared in the production audit. This confirms that the deployed Worker can query the authenticated Rock64 BTDigg service and return BTDigg search results from the live path.
- The BTDigg-only `&amp;` query-separator normalization fix was included in the deployed code, with passing Node and actual Cloudflare workerd fixture tests. An independent live raw JSON magnet-field inspection **was not possible** from the assistant's environment (DNS/HTTP client limitation); do not claim a physical Flud send or a real-client magnet-delivery verification.
- Prior Python `urllib` HTTP 403 on Rock64 is a separate client-path observation; do not infer that the PWA/Worker search failed from that response.

No gateway/tunnel/repository changes to the other 45 indexers or Flud Companion were required for this release. No automatic Flud action was initiated. To complete human acceptance, the owner may search via BTDigg in the installed PWA, confirm results and optionally initiate an explicit lawful magnet send to Flud Companion; avoid unapproved background downloads, retries or paid infrastructure.

## 2026-10-13 BTDigg intermittent availability stabilization and audit display correction — awaiting rollout

User observed genuine BTDigg `ubuntu` results in Magnetra without iPhone VPN, followed by an intermittent "1 indexer unavailable / 0 results / This provider could not complete the search" for the same term, and later another successful search. This **does not** prove the user's mobile ISP or NordVPN caused Rock64-origin search failure. The dedicated Python gateway exits to BTDigg via the Rock64's own residential uplink, independently of the iPhone's exit IP. Earlier production GitHub audit run **38361367716** (2026-10-13 at ~07:14 UTC) confirmed BTDigg returned **10 actual results**. Intermittent upstream timeout, rate limiting, concurrency and tunnel errors remain distinct possible causes; no single root cause was directly evidenced from a failing `errors[]` JSON capture.

**Scoped stabilization changes on the PR branch**:
- Python gateway `rock64/btdigg_gateway.py`: success-only, small **20-minute** bounded in-memory LRU of up to **4** genuine BTDigg result pages and **6 MB** total. `one_result` HTML marker required before caching, no errors/CAPTCHA/zero-result pages cached. RAM only, no cache persistence on the Rock64 microSD and no query or credential logging.
- Coalesce concurrent identical BTDigg queries into **one** upstream attempt. A different uncached query remains subject to the original **one active request** + **5-second minimum upstream interval**, returning local 429 rather than queuing or retrying. Upstream time budget is 12s, Worker Rock64 fetch 16s; no paid proxy/CAPTCHA circumvention, no automatic retries or changing the other 45 adapters.
- Worker BTDigg-specific error classification differentiates HTTP 504/timeout, generic transport failures and potential Cloudflare 1042, without exposing raw private URLs or secrets.
- Real, complete GitHub production audit log (run 38361367716) replaces the UI's obsolete embedded 08-Oct snapshot: **13 with results, 14 empty-or-unverified, 19 provider errors, 0 request errors**, exactly **46** original indexers. BTDigg is one of the positive 13. `worker/src/source-audit.mjs`, `config/project-invariants.json` and `worker/test/source-audit.test.mjs` are synchronized. The UI differentiates this **dated historical observation** from current-browser-session outcomes and makes **no 46-provider background search requests**. The existing "Select last-audit results" choice uses the 13 last-audit positives; all 46 remain available to choose manually.
- One failed `ubuntu` audit cannot establish that an indexer is permanently nonfunctional. Do NOT delete, renumber, substitute or silently disable the 19 error-status adapters or the 14 unverified adapters; a later explicit multi-query/date/source-access audit and owner approval would be required. Rate-limited HTTP 429 is not an acceptable reason to hammer sources.

**Rollout and proof boundaries:** PR changes are not live merely because GitHub has code. The Python gateway is installed on the owner's Rock64 in an earlier version and requires an explicit, guarded **Magnetra-only code update and restart**, preserving `/etc/magnetra-btdigg/gateway.env`, systemd units and the separate tunnel. Worker/UI changes require a new owner-authorized Cloudflare release, with post-deploy proof of 46-provider catalog, BTDigg search result, secure tunnel, and no automatic Flud sends. The active 2026-10-13 Cloudflare Worker remains version `b0375998-666b-4160-8390-987f62457f01` until another release is evidenced; do not represent this stabilization as already deployed.

## 2026-10-13 physical Rock64 gateway update completed; temporary checkout cleanup defect

The owner ran the guarded Rock64 updater for main `dcdfdaa1d4ed53e6212701230c31c9a2b00178e8` and reported **7 Python unit tests passed**, **authenticated localhost health PASS**, **gateway upgrade PASS** and both `magnetra-btdigg.service` and `magnetra-btdigg-tunnel.service` **active**. This confirms the upgraded Python code was physically installed without changing credentials or the tunnel. The last command returned a nonfatal `rm: Permission denied` for `/tmp/magnetra-stable.4fzB6aEo/repo/rock64/__pycache__` during cleanup **after successful verification**. Root cause in repository: the guarded updater ran `python3 -m unittest` and `python3 -m py_compile` as sudo in a `runner`-owned checkout; Python therefore created root-owned bytecode and the outer non-root trap could not remove it.

Follow-up source-only fix: both `rock64/install-btdigg.sh` and `rock64/update-btdigg.sh` now execute unit tests with `python3 -B` and validate source syntax through Python `ast.parse`, which does not write bytecode. A regression test guards this contract. These script changes **do not need to be run on Rock64** for the already installed stable Python gateway to work. No one has modified Cloudflare Worker production in this step: new provider labels/dated audit and 16-second BTDigg Worker timeout from PR #26 remain **not deployed** pending an expressly authorized PWA/Worker release. The source updater remedy is historical cleanup hygiene, not evidence of a new gateway failure.

## 2026-10-13 owner-approved Cloudflare stabilization release — deployment pending

After PR #26 (`dcdfdaa1d4ed53e6212701230c31c9a2b00178e8`) and PR #27 (`aaf135acde784a86514045b388a19ba9aa0b4aef`), the owner supplied output proving the stabilized BTDigg Python gateway is installed on Rock64 (seven local tests PASS, authenticated health PASS, dedicated gateway + tunnel both active), then explicitly approved Cloudflare Worker/PWA deployment. The nonfatal temporary Git checkout cleanup issue was fixed in PR #27 and does not require a new Rock64 install.

**Approved release scope:** existing free-tier Cloudflare Worker `alexlab-magnetra` at `https://index.alexlab.media`, using the protected GitHub workflow and existing credentials/secret. This ships 16s BTDigg-only Worker gateway timeout, scoped timeout/transport categorization, dated 2026-10-13 46-provider audit (13 results including BTDigg count 10; 14 empty-unverified; 19 errors), and in-session-only provider status badges. All 46 original sources remain selectable and Flud dispatch remains explicit and unchanged. No paid service, unrelated Cloudflare setting or other Rock64 process is authorized.

**Release receipt still needed:** a successful GitHub Actions deployment run, a Cloudflare version ID, production smoke results and the actual live BTDigg outcome; the approval and this release marker alone are not proof of successful publication. No automated Flud magnet send is authorized. Any live audit failure may be intermittent and should not result in silently removing providers. Keep this as a pending release checkpoint until verified.

## 2026-10-13 VERIFIED production Cloudflare stability release receipt

Owner approved deployment after verified physical Rock64 upgrade (Python 7 tests PASS; authenticated gateway localhost health PASS; both gateway and dedicated tunnel active). Separate installer cleanup regression fixed in PR #27 (no root-owned checkout `__pycache__`). Owner-approved Cloudflare release PR #28 merged as commit `f7a37b555169c920ad1d2dfd35c31bb76fd3c0ac` with `[deploy-pwa]` marker. Protected deployment workflow **38373699387** completed with **success**. All Worker contract tests, bundle validation, existing Cloudflare credential checks, deployment, production HTTPS/PWA/API smoke checks and complete production 46-indexer audit passed.

**Cloudflare Worker `alexlab-magnetra` production Version ID:** `58df87fe-0ab8-48cc-9c86-8dd6922b8a3c`, custom domain `https://index.alexlab.media`.

**Latest separate production live audit at 2026-10-13 09:05 UTC (run 38373699387):** `results=13`, `empty-or-unverified=12`, `provider-error=21`, `request-error=0`. Specifically `{"id":"btdigg","state":"results","count":10}`, proving the released Worker-to-dedicated-Rock64-to-real-BTDigg search path works at that observation time. This latest audit differs from the deliberately embedded static UI historical snapshot from earlier the same date (run 38361367716: 13/14/19). **Do not misrepresent either single-query snapshot as current uptime or delete sources after an isolated 403/429/timeout.** The UI labels dated audit provenance and per-browser-session observations, not continuous health. All 46 original indexers remain selectable.

The gateway now runs the 20-minute success-only BTDigg RAM LRU (max four real HTML result pages, 6 MB), deduplicates simultaneous same-query upstream access, respects five-second unique-query throttling, preserves no retries on HTTP 429 or CAPTCHA and does not persist cache on microSD. Released Worker uses a 16-second Rock64 request timeout with safer categorized diagnostics. A successful audit proves current search operation but is not a guarantee against future upstream restrictions or tunnel disruptions. No physical Flud Companion dispatch was performed; that remains an explicit owner action. No token/tunnel/service changes, paid APIs, external DHT substitutions or modifications to the other 45 adapters.

## 2026-10-13 owner-requested BTDigg-first selector and rapid-search pacing (pending release)

Owner reports the previously stabilized Rock64/Cloudflare BTDigg search currently works, but also reports that after approximately **three rapid searches** the PWA may again display the generic BTDigg unavailable error. The exact failing provider API `errors[].code` was **not captured**, so rate limiting is a plausible but not proven root cause. Existing gateway has a hard 5-second minimum interval between new upstream queries and caches only real successful HTML results. Do **not** remove gateway guard, auto-retry HTTP 429, use IP rotation/paid bypass, claim source guaranteed uptime or auto-send magnets to Flud.

Owner explicitly requested the provider picker list be reordered by observed working/nonworking sources, with **BTDigg always first and selected by default**. Implementation in `web/app.js` sorts as: pinned BTDigg; sources with proven results in latest dated audit (or positive in this browser session); empty/unverified; then provider errors; within each group alphabetical. Session observations override stale historical badges, but the UI never calls sources in the background merely to order them. **All 46 indexers remain selectable**, even ones currently reporting errors. This list is audit-based, not a live health checker.

**Default selection now BTDigg plus the prior four positive sources** (`btdigg, knaben, torrentscsv, thepiratebay, internetarchive`), aligned between Worker fallback and PWA. New users receive this default. For current users whose saved selection is **exactly the old four default sources**, PWA safely migrates to include BTDigg; any genuinely customized selection remains untouched (no forced re-enable of BTDigg if deliberately deselected). Selector's `Select last-audit results` still only selects the 13 verified positive adapters.

The embedded audit snapshot is updated from the verified 2026-10-13 `GitHub Actions 38373699387` complete production log: 46 sources, `results=13`, `empty-unverified=12`, `provider errors=21`, BTDigg 10 results for `ubuntu`. This is **observed status only**, not guaranteed uptime. `config/project-invariants.json`, project guards and regression tests are updated in the same PR.

New browser-only safety pacing before a new BTDigg request uses a **minimum 5.5 seconds from the previous completed BTDigg request** when searching a distinct term / without a known successful cached same-term search. The PWA waits instead of sending repeated requests during the Rock64's 5-second upstream limit, and an AbortSignal cancels unsent waits. The existing positive Rock64 20-minute source cache still serves repeated successful same-query searches quickly. This is one delayed user-initiated attempt, **never an automatic retry**; it cannot fix an independent upstream BTDigg 429 or connectivity failure. A source-specific transient failure message replaces the misleading claim that the private Rock64 source is being accessed directly from Cloudflare.

**Deployment status:** code in PR is not live before successful CI, guarded squash merge and authorized Cloudflare Worker/PWA deploy. No need to change the already-installed Rock64 Python gateway or the dedicated Cloudflare tunnel/secret. No paid service, Android upstream change or Flud Companion change.

## 2026-10-13 BTDigg-first UI and 5.5-second request pacing — VERIFIED deployed receipt

Owner requested working/recently-successful sources to appear first, error-status sources last, with BTDigg pinned at #1 and selected by default, and additionally reported an error after approximately 3 quick searches. PR #30 was merged with `[deploy-pwa]` as main commit `6070b64bb626a65905c3b1604d0ff3df49b2483b` after all CI (invariants, Node/PWA/Cloudflare and Android Debug/Staging) passed.

**Guarded production deploy run `38387105924` completed SUCCESS.** Cloudflare Worker `alexlab-magnetra` custom-domain `https://index.alexlab.media` deployed Version ID **`0ea30e34-7b96-4ce6-a7e6-aaef210ed0d4`**. HTTPS/PWA/API smoke PASS. Full, actual 46-indexer benign `ubuntu` post-deploy audit **13 sources with results, 13 empty-or-unverified, 20 provider errors, zero transport request errors**, specifically `{"id":"btdigg","state":"results","count":10}`. This is a later live audit than the 13/12/21 historical snapshot deliberately shipped in the picker from run `38373699387`; differing one-time outcomes are expected and do not establish permanent online/offline status.

Deployed picker order: BTDigg pinned first, then positive observations (latest *embedded dated* audit or results observed in this browser session), then empty/unverified and error statuses; alphabetical within each group. Every one of the 46 original indexers remains available. Fresh-browser and Worker fallback default `[btdigg,knaben,torrentscsv,thepiratebay,internetarchive]`. A browser with exactly the previous four-item default migrates safely to include BTDigg. Any custom browser selection, including a deliberate removal of BTDigg, remains user-controlled.

New **client-only** 5.5s pacing of rapid *different* BTDigg queries respects the Rock64's protected 5s minimum new-upstream-query interval; waits are AbortSignal-cancellable and do not produce additional automatic attempts. Positive repeated identical queries can reuse the existing genuine 20m/4-entry/6MB success-only Rock64 cache. The released PWA distinguishes private Rock64 temporary errors from unrelated Cloudflare-provider messages. This targets preventable locally induced 429s but **does not prove all intermittent failures are fixed**. The exact failure code for owner's pre-patch burst issue was not recorded. No physical Shield/Flud dispatch attempted, no Rock64 update, no secrets/tunnel change, no external DHT replacement, no paid service, no changes to the 45 other provider adapters.

## 2026-10-13 repeated third BTDigg search timeout after 10+ second pause — scoped diagnostic change awaiting deployment

The owner observed the **third different BTDigg search failed even after approximately ten seconds between searches**, with the PWA's `"The provider did not respond in time."` message. Earlier searches (including `Supernatural` on subsequent manual attempt) had succeeded; Rock64 standalone BTDigg `debian` test returned 10 rows in 1.08 s, authenticated tunnel without token returned expected 401, gateway and tunnel services active. The owner uses Tailscale on the iPhone without an exit node. These facts disprove a simplistic *every failure is caused by less than five seconds between clicks* explanation; they do not identify the failing stage, prove a per-IP quota, or show that iPhone Tailscale changes Rock64 residential egress.

**No hard-coded 3-search cap exists** in Worker, browser or gateway. The gateway's 5-second limiter protects *distinct uncached upstream requests*, and the frontend's 5.5-second pacing is not a guarantee against a BTDigg upstream timeout or 16-second Cloudflare-to-Rock64 subrequest timeout. The released Worker currently classifies both a local Rock64 gateway HTTP 504 and an actual Cloudflare-to-Rock64 timeout as generic `TIMEOUT` with identical user-facing text, obscuring the evidence required for a targeted availability fix.

This diagnostic-only PR explicitly separates **`BTDIGG_SOURCE_TIMEOUT`** for a 504 reported by the authenticated Rock64 source gateway (about 12 seconds upstream/waiter) from **`BTDIGG_TUNNEL_TIMEOUT`** for an aborted/timed-out Worker subrequest (16-second external tunnel request). The safe error codes and distinct plain-language messages are visible in the PWA failure details on mobile; Node integration regression tests exercise both actual public API code paths and assert one request/no retry, with no exposed credential or private URL. Other provider error classifications and magnet/Flud logic are unaffected.

**No proven permanent availability fix or automatic retry is claimed**. If a future failed third search reports `BTDIGG_SOURCE_TIMEOUT`, investigate BTDigg upstream behavior from Rock64; if `BTDIGG_TUNNEL_TIMEOUT`, inspect Cloudflare tunnel ingress/subrequest behavior. Neither is conclusively caused by Tailscale. Do not increase timeouts blindly, restart router/gateway, enable proxies/exit nodes or relax global Cloudflare flags without evidence. This is branch-only until owner separately authorizes the protected Cloudflare deploy; installed Rock64 Python gateway remains unchanged.

## 2026-10-14 four legacy providers return HTTP 403 from Cloudflare; residential-only probe staged

Owner-supplied iPhone screenshot shows **1337x, BT4G, Ext, EZTV** labeled `Provider rejected requests from this server.` (`ACCESS_DENIED`) in Magnetra. Repository `worker/src/legacy-specs.mjs` confirms fixed hosts `1337x.to`, `bt4gprx.com`, `ext.to`, and `eztvx.to` plus HTML selector and deferred magnet details contracts. Cloudflare Worker outbound 403 is **not proof** of endpoint removal, source parser failure or global site outage. Changing NordVPN/Tailscale on an iPhone doesn't change the Worker's outbound IP. Physical Rock64 gateway currently serves **BTDigg only** by design: do not broaden its allowlist or disturb the stable tunnel to tackle these four.

Public source investigation confirmed EZTV's own keyless API at `https://eztvx.to/api/` advertises `limit/page` and `imdb_id`, **not arbitrary keyword searches**. It is a potential targeted integration, but using latest 100 torrents to pretend to fulfill a generic `Supernatural`/movie name search would violate provider result parity. Public Ext web search pages exist for `ubuntu`; this does not prove Cloudflare Worker or Rock64 origin can fetch them.

Staged a **fixed-origin, read-only, no-credential probe** under `rock64/probe-blocked-indexers.py` with unit tests. A single owner-run execution on the physical Rock64 checks HTTP/access/challenge/HTML-signature reachability of exactly the four established upstream domains and the official EZTV API, bounded to five GETs/9s each/256KB each, no redirects, torrent downloads, login, services, VPN or DNS changes. Output safe to paste without secrets. Only after results can a four-provider opt-in isolated residential gateway (plus detail magnet fetch and source-specific selectors/tests) be justified; if Rock64 also gets 403, assess per-process NordVPN using the owner's existing subscription as a separate approved and fully isolated possibility, never on the Rock64-wide interface. Until the owner supplies proof, **none of the four indexers is claimed repaired**, no new cloudflared route is installed and no paid service is started.
## 2026-10-14 EZTV API/TVmaze exact show lookup — staged implementation, NOT live

Rock64 one-time five-source test: 1337x 403 (0.10s), BT4G 403 (0.12s), Ext 403 (0.10s), EZTV website 403 (0.09s), but **the genuine EZTV keyless API returned HTTP 200 with a valid `torrents` marker (0.18s)**. This is a real new capability separate from the site's blocked HTML search. Italian regulator AGCOM's 2018 decision 110/18/CSP orders a DNS-level 1337x block in Italy; this is documented public context, **not proof** that each observed 403 is caused by that order or that a VPN will fix any site.

The official EZTV API's `/api/get-torrents` supports IMDb-ID queries but not arbitrary title search. TVmaze's free public `/search/shows?q=` returns `show.externals.imdb` and is CC BY-SA; attribution is required. **Staged exclusively for original `eztvx` provider ID**: `worker/src/eztv-official-api.mjs` resolves a unique normalized exact TV-series name to a verified IMDb ID using TVmaze's public API, or accepts explicit `ttNNNNN` query, then queries the actual EZTV official API with that ID and requires an exact `imdb_id` confirmation in the EZTV response. Only actual EZTV-supplied releases with valid magnet BTIH/valid hash are normalized; an ambiguous/fuzzy-only title, an unmatched IMDb ID or a non-series category yields an honest empty list. Source authenticity is preserved: TVmaze supplies only title-to-ID metadata and NEVER torrent listings. PWA provider picker credits TVmaze with a link. Both upstream origins are fixed, HTTPS, bounded, same-origin redirects only, no arbitrary host injection, no login/key/paid service, no retries or source replacement. We intentionally do not route foreign-origin EZTV episode links as trusted EZTV details and we do not claim generic movies/other categories are supported.

The independently existing BTDigg residential gateway is untouched, and no NordVPN service/proxy has been installed. Other 45 providers' search code paths and magnet/Flud dispatch stay unchanged. New tests cover exact title/IMDb lookups, mismatch and ambiguous name rejection, HTTP 403/429, category safety, magnet validation and attribution. This is **staged code only**, not evidence that Cloudflare Workers can reach TVmaze and the EZTV API from their real egress; it must pass CI plus targeted real Worker origin verification before any Cloudflare release. Whether the residential 1337x/BT4G/Ext 403s originate at ISP filtering or remote site is still not established; no proxy-bypass changes are authorized.

**Additional normalizer defect found by new CI test (same PR):** `worker/src/providers.mjs` historically passed a blank `details` field into `validateLegacyDetail`, where the base-URL resolver interpreted it as the source homepage (`https://eztvx.to/`). A magnet-only result was thus given a fabricated details link. The scoped fix ensures absent details and magnetSource fields remain `null` for **all** providers instead of inventing a result page; source identity/magnets are unaffected. The EZTV regression fixture catches off-origin details links and validates that missing details cannot become the homepage. This is a safety correction, not a provider availability workaround.

## 2026-10-14 — exact-title ambiguity evidence and safe UX patch

A read-only GitHub Actions diagnostic (PR #38, run 38584353452) returned 403
`text/html` for EZTV's API from the runner, and production
`/api/search?q=tt0460681&providers=eztvx` reported `ACCESS_DENIED`
(upstream HTTP 403). The owner's earlier `EZTV API shape unexpected`
observation is valid but remains an unverified *response body structure*:
different egress paths have produced different failures. Do **not** assert
that the EZTV API is functional; no authentic torrents were verified.

TVmaze's real exact-title search returned two distinct series titled
`Supernatural` (`tt0460681` and `tt0396375`); the adapter previously
returned `[]` silently because `exact.length !== 1`.
This patch preserves the fail-closed rule but surfaces the typed
`AMBIGUOUS_TITLE` error with instruction to search by IMDb ID.
No show is guessed, no torrents are substituted and all 46 provider IDs,
default preferences, BTDigg, Rock64, Flud and other projects are unchanged.
Breaking Bad returned a unique exact title (`tt0903747`) during diagnosis,
but its EZTV torrent response is not yet verified. A separate Rock64
read-only probe (`rock64/inspect-eztv-api.py` in PR #38) is awaiting
the physical host's response to distinguish real API schema errors from
egress blocking; do not deploy arbitrary schema guesses or broaden network
routing.

## 2026-10-14 — confirmed EZTV empty-response format (Rock64, owner terminal)

The physical Rock64 one-shot check of `https://eztvx.to/api/get-torrents`
received HTTP 200 JSON for IMDb `tt0460681` with exact root fields
`imdb_id`, `torrents_count`, `limit`, `page` and **no `torrents` key**.
The simultaneous unfiltered `limit=2&page=1` call received HTTP 200
JSON containing 2 genuine magnet-bearing row records, proving that EZTV
does expose source metadata from this residential egress. No result for
`tt0460681` has yet been proven. The original JSON-shape exception was
triggered by treating a missing torrent list as malformed. The PR's safe
adapter fix treats the absent array as empty **only if the exact IMDb echo
matches and `torrents_count` is explicitly zero**. Missing-array/
positive-count and API error envelopes still fail, and no unrelated recent
releases are substituted. Note that the original one-shot tool did not print
the numeric `torrents_count`, so this zero-count premise still requires
confirmation from the enhanced diagnostic.

For confidence that an actual known-positive IMDb search yields genuine
magnet-bearing rows, the upgraded Rock64 probe automatically selects an IMDb
ID from the unfiltered recent rows and performs a single fixed-origin
filtered lookup with only structural/magnet-count logging, never filenames,
hashes, magnets, credentials, downloads or external redirects. The Cloudflare
Worker remains independently 403-blocked in observed runs; this parser fix
does not prove the PWA can access EZTV or guarantee an EZTV result. Deploy
only following CI and explicit release confirmation; do not modify the global
network or any other provider.

## 2026-10-14 — EZTV residential gateway prepared, NOT activated

**Owner-verified real source evidence (twice) on physical Rock64 Armbian:**
- `imdb_id=460681` => HTTP 200 JSON, `torrents_count=0`, no `torrents` key, exact echoed IMDb; PR #40 parser handles it as an honest zero, and this is not an adapter error.
- Recent `limit=2` => HTTP 200 JSON, 2/2 valid source magnet links; `torrents_count=1092185` is the API-wide declared total, not results fetched.
- Filtered on a real IMDb ID extracted from one recent row => HTTP 200, exact echoed root and row IDs, `torrents_count=15`, **2 source rows with 2/2 valid magnets in the requested page**. No files or torrents downloaded.
- Independent GitHub Actions/Cloudflare egress previously received HTTP 403 from the API. The residential success establishes only the origin works from Rock64, not Cloudflare connectivity or a production result.

**Staged opt-in technical solution:** new `eztvx`-only `worker/src/eztv-rock64.mjs` authenticates with optional Worker Secret `EZTV_GATEWAY_TOKEN` to the **proposed and not yet created** host `https://eztv-rock64.alexlab.media`. The new independent Python gateway `rock64/eztv_gateway.py` is designed for `127.0.0.1:8797` (port availability not yet verified), with a distinct `MAGNETRA_EZTV_TOKEN`, official fixed EZTV HTTPS API, exact numeric IMDb only, no redirects, 1MB JSON bound, root/row matching IDs, protected status propagation, short read-only RAM cache and source rate limit. TVmaze continues by direct official API connection. No existing BTDigg listener/tunnel/process is modified, and 44 other provider adapters and Flud stay on prior paths. Without secret, normal direct Cloudflare path is unchanged.

**Repo state only:** templates `rock64/magnetra-eztv.service`, `rock64/magnetra-eztv-tunnel.service`, `rock64/install-eztv.sh`, safety tests/guards and `rock64/README_EZTV.md` are staged on a PR. There is **no physical EZTV service**, DNS record, new tunnel, Worker secret or new production deploy proven or claimed. Explicit owner authorization plus real Rock64 local health/result proof, tunnel proof (watch for same-zone 1042) and protected production deploy are required separately. No NordVPN, global routes, DNS, firewall, Tailscale, paid services or other project restart.

## 2026-10-14 — physical preflight passed; EZTV separate Cloudflare binary path correction

Owner supplied physical Rock64 output after PR #41 merged (`f175032e9334d06d751d6e20099e4cc9f82f6243`): 5/5 local EZTV tests PASS, `127.0.0.1:8797` port was unbound, `magnetra-btdigg.service` active, `cloudflared` executable resolved to **`/usr/local/bin/cloudflared`** (the old dedicated EZTV template incorrectly used `/usr/bin/cloudflared`). A follow-up PR adjusts **only the optional EZTV tunnel template** to the verified path and adds a token-safe, genuine-magnet local end-to-end acceptance script with offline regression tests. This does not verify the Cloudflare Tunnel or install any live EZTV gateway. **Activation still needs explicit owner action on Rock64, using only the isolated EZTV service, no BTDigg or other changes.** See `rock64/README_EZTV.md`.

## 2026-10-14 — EZTV gateway installed but local acceptance not yet validated

Owner installed `magnetra-eztv.service` using approved commit `a51585ef9e27c14da6b7183457491ba11178edca`: installer printed `PASS: dedicated EZTV API service on 127.0.0.1:8797`, `systemctl enable --now` completed, and five Python tests passed twice. The immediately following `check-eztv-gateway.py` printed a generic FAIL **without** first printing authenticated health PASS. No diagnostic stage or HTTP status was reported, so this is *not* evidence of a source EZTV failure, and no genuine filtered magnet reached the gateway through that acceptance check yet. No Cloudflare Tunnel, Worker Secret or production deploy was performed. A follow-up PR adds bounded listener-ready waiting and stage-specific, secret-safe diagnostics to the standalone smoke script only. Do not reinstall or restart unrelated services; inspect listener and safe HTTP 401 first, then rerun the updated local checker.


## 2026-10-15 — broader residential gateway question; evidence-first diagnostics staged

The owner confirmed the separate EZTV Rock64 local gateway authenticates
successfully (`EZTV local authenticated health: PASS`) but its
known-positive recent-IMDb filtered request returned **0 page rows / 0
valid magnet links** (`FAIL stage=local-filtered cause=local-data-or-response`).
This is not full EZTV recovery. A previous direct Rock64 API probe for an
IMDb from real latest results returned 2 genuine rows/2 magnets at
`limit=2`, while the installed gateway's upstream query uses `limit=100`.
**Different limit, temporal source variation and local gateway RAM cache are
competing hypotheses, not confirmed causes.** No Cloudflare Tunnel or Worker
Secret has yet been activated for EZTV.

The owner asked whether the successful EZTV/BTDigg architecture could also
serve Torrentz, UIndex, 1337x, BT4G, Ext and other failing source adapters.
The answer is conditional: the 2026-10-13 Cloudflare snapshot says
`torrentz=UPSTREAM_ERROR`, `uindex=ACCESS_DENIED`,
`1337x/bt4g/extdotto=ACCESS_DENIED`. Prior **physical Rock64**
GETs to 1337x, BT4G and Ext also returned HTTP 403; blindly adding a
Rock64 proxy cannot be claimed to repair those sites.

A read-only diagnostics PR stages `rock64/diagnose-eztv-filter.py`, a
same-IMDb **direct `limit=2` vs direct `limit=100` vs authenticated
EZTV loopback gateway** comparison without ID, magnet, title or secret
output. `rock64/probe-more-indexers.py` checks five original HTML sources
from fixed allowlisted URLs, or eleven with `--extended`, once each with
no redirects/proxy environment and short timeouts. An HTML marker is not
proof of parsed results; do not activate any additional gateway until source
rows and deferred magnet resolution are verified. No new tunnel/service,
secret, NordVPN, DNS, firewall, global route, paid service or production
deploy is authorized. See `rock64/README_MULTI_INDEXER_EGRESS.md`.

## 2026-10-15 — residential 11-provider and EZTV limit comparison (owner terminal)

The owner ran the pinned 2026-10-15 diagnostics against physical Rock64:
`torrentz` network/transport error in ~0.07 s; `uindex`, `1337x`,
`bt4g`, `extdotto`, `torrentdatabase`, `torrentdownloads`,
`tokyotoshokan` all returned real HTTP 403; `oxtorrent`,
`torrent9`, `bitsearch` returned HTTP 301 **with automatic
redirects deliberately disabled**. This is not proof any of the 301
redirect destinations contain genuine torrent rows; 403 sources cannot
be fixed by a gateway with the *same residential egress* without
additional source-side evidence.

EZTV source-to-gateway comparison for one genuine recent IMDb candidate:
the unfiltered recent source endpoint was HTTP 200 with a magnet
candidate, but direct filtered `limit=2`, direct filtered `limit=100`
and independently authenticated loopback `limit=100` all produced
**HTTP 200, correct IMDb echo, declared_torrents_count=0, missing
torrents array and 0 verified magnets**. This rules out the hypothesized
limit-100-only mismatch **for that candidate in this test**. An earlier
positive exact-IMDb lookup remains valid evidence for a different time/
sample; do not erase it or claim the API is permanently broken. The
EZTV private gateway at `127.0.0.1:8797` and BTDigg gateway remain
active. EZTV tunnel/Worker Secret and production are **NOT active**.

A narrowly scoped, additional *read-only* diagnostic PR stages
`rock64/probe-indexer-followup.py`: only the original Torrentz,
OxTorrent, Torrent9 and BitSearch fixed URLs are queried once, safely
reports DNS/TLS/connectivity *categories* and canonical redirect
**hostname only** without following the destination. The same script
samples at most four distinct genuine IMDb IDs from five official recent
EZTV releases and checks a fixed `limit=100` filtered search once
per ID; all output is only counts, no IDs, titles, hashes or magnets.
This differentiates API filter inconsistency from sampling a recent
release not indexed by the filter. Do not broaden proxies, change the
46-indexer catalog or historic audit, bypass 403 protections, run VPN,
change Rock64 network/services, pay for infrastructure or deploy.

## 2026-10-15 — real positive EZTV source sample and observed canonical redirects

Owner executed `probe-indexer-followup.py` on physical Rock64 with
read-only output:
- Torrentz `torrentz2.nz`: **TRANSPORT_FAILURE** before HTTP; specific
  cause not identified, no source replacement established.
- OxTorrent original HTTP 301 → `www.oxtorrent.co` (OFF_ORIGIN);
  Torrent9 → `www7.torrent9.to` (OFF_ORIGIN);
  BitSearch → `bitsearch.eu` (OFF_ORIGIN). No redirects followed,
  no destination HTML or true magnet availability verified.
- Official EZTV recent: HTTP 200, **four distinct recent authentic
  IMDb candidates**. Fixed `limit=100` filtered lookups for these
  showed 16/16, 31/31 and 100/100 valid IMDb-matching magnet rows
  respectively; fourth returned zero. The third advertised 2,026 total
  matching releases with 100 actually returned (page limit). No IDs
  or magnet content exposed. This establishes the API works for real
  filtered queries from Rock64; no mismatch attributable to limit=100.

**Next gated action** is to prove identical source-positive IMDb and
gateway-positive results on installed `127.0.0.1:8797`. A guarded
branch/PR updates only the standalone `check-eztv-gateway.py` test to
find a positive exact IMDb from up to four recent source candidates
before checking the loopback gateway once. Distinguishes source
UNVERIFIED (all sampled IDs zero) from gateway ERROR and prints
count-only proof. No service reinstall, no EZTV tunnel/Worker Secret
or PWA production deploy. Separate
`probe-redirect-candidates.py` tests exactly the three observed
canonical hostnames read-only, without redirect following or altering
any provider. **Do not automatically migrate hosts or relax exact
origin policy**. Preserve BTDigg, Flud and all 46 indexers.


## 2026-10-15 — EZTV REAL SAME-IMDb LOCAL GATEWAY SUCCESS; tunnel still not deployed

**Owner's physical Rock64 proof** from pinned commit `35d1b47e406eaf0e4e9deda5d313eae21ca8bdb3`:
`EZTV local authenticated health: PASS`, two genuine recent IMDb candidates, first direct source-positive sample; direct official EZTV filtered API yielded **100 page rows / 100 genuine IMDb-matching magnet links**; the **separate authenticated Rock64 loopback gateway 127.0.0.1:8797** returned **100 page rows / 100 IMDb-matching magnet links for the same hidden IMDb ID**; `PASS: genuine EZTV magnet metadata reached isolated local gateway`. The dedicated `magnetra-eztv.service` and existing `magnetra-btdigg.service` were both `active`. This conclusively validates the *local* EZTV source-to-loopback path; prior source-zero probes were caused by sampling a genuine recent IMDb without filtered results, not a demonstrated `limit=100` bug.

Additional safe, fixed-host canonical redirect probes, each without following redirects: `www.oxtorrent.co` HTTP 200 with 3 table rows / 0 observed magnet anchors (`LAYOUT_HINT_ONLY`); `www7.torrent9.to` HTTP 200 with 4 table rows / 0 observed magnet anchors (`LAYOUT_HINT_ONLY`); `bitsearch.eu` HTTP 520 (`HTTP_ERROR`). **HTML table rows are NOT validated torrent results**, and no deferred magnet on details pages is yet verified. No origin catalog change is authorized. `torrentz2.nz` previously yielded pre-HTTP TRANSPORT_FAILURE, and seven other sources still got 403 even on Rock64.

**Next action is an explicitly owner-approved independent Cloudflare Tunnel**, proposed fixed hostname `eztv-rock64.alexlab.media` routed to local `127.0.0.1:8797`, using only the isolated `magnetra-eztv-tunnel.service` (template currently not installed). Official Cloudflare Tunnel run docs say `TUNNEL_TOKEN_FILE` / `--token-file` is available in cloudflared **2025.4.0+** for remotely managed tunnels; installed Rock64 version/flag support must be read-only checked before enabling. The existing binary path observed on this machine is `/usr/local/bin/cloudflared`. Never run `cloudflared service install` (could replace global unit), never paste token in chat/repo, never expose the new origin without a bearer secret. Tunnel creation, route/DNS change, protected credential placement, Worker secret `EZTV_GATEWAY_TOKEN`, deploy and potential Worker-to-Tunnel same-zone 1042 testing each remain **NOT DONE / need explicit owner permission**, with independent rollback and no global compatibility flags changed. `index.alexlab.media` production has **not** been deployed from this PR, and no new indexer gateway was installed. Preserve BTDigg, Flud/Plex/NexaPanel/CalciDatum and the 46 providers.


## 2026-10-15 — owner approved dedicated EZTV Cloudflare Tunnel and DNS ONLY

The owner answered **“Da”** explicitly to the proposal to set up
a **new, independent** Cloudflare Tunnel with public hostname
`eztv-rock64.alexlab.media`, connected only to
`http://127.0.0.1:8797`, including its DNS route, **WITHOUT** yet
activating Magnetra production PWA. No payment, account upgrade,
shared/global cloudflared changes, Worker secret or production release
was approved.

The assistant has GitHub access but **no direct Cloudflare account
management connector or SSH execution into physical Rock64**.
Accordingly, a guarded optional dedicated
`rock64/install-eztv-tunnel.sh` is staged through a PR; the owner
must create the tunnel and Published application route in their
Cloudflare Dashboard, retain the sensitive tunnel token privately
and physically execute the installer with the new token typed into
a hidden terminal prompt. Use the existing independent
`rock64/magnetra-eztv-tunnel.service` template with
`LoadCredential` and `TUNNEL_TOKEN_FILE`, supported with cloudflared
2025.4.0+, and local `/usr/local/bin/cloudflared` version must be
verified before use. Stop on older binary, existing token or unit
collision. **Do not run `cloudflared service install`** because it may
replace a shared service. DNS CNAME is created as part of the
Cloudflare Published application route; check for hostname conflicts.
After activation demand independent service active, Cloudflare tunnel
Healthy and unauthenticated public `/healthz` HTTP 401,
while BTDigg remains active. Production Worker Secret,
same-zone 1042 workaround or global compatibility flag changes and
PWA deployment remain a **separate future approval gate**. No new
Cloudflare Tunnel/DNS/secret/real Rock64 service creation has been
proven from this chat yet.


## 2026-10-15 — correction from owner: NEVER create a Cloudflare Tunnel per indexer

Owner explicitly rejected continuing the dedicated EZTV Tunnel as an independent connector and specified **one shared solution for the remaining failing indexers**. This supersedes the previous owner GO for one EZTV-specific tunnel. **Do NOT execute the old PR #48 EZTV installer or create a new EZTV Tunnel/DNS record**. The GitHub-only installer and optional EZTV tunnel systemd template/test are removed in a new guarded PR; this change does NOT stop/delete/restart any physical Rock64 service or alter its existing tunnel. The proven authenticated EZTV local gateway at 127.0.0.1:8797 stays untouched (100/100 same-IMDb real magnet metadata); BTDigg 8796 stays untouched.

Architecture: reuse the **existing BTDigg Cloudflare Tunnel connector** and its current BTDigg published application unchanged; after verifying Dashboard management mode and physical service state, plan ONE additional published hostname magnetra-rock64.alexlab.media pointing to ONE future authenticated loopback dispatcher on 127.0.0.1:8798. Dispatcher can serve EZTV (via current 8797) and additional providers only after verification; no tunnel/DNS change per provider. No dispatcher is deployed yet. A new read-only rock64/check-shared-tunnel.sh preflight checks service states, listener counts and unauth protected health HTTP codes without leaking credentials. Cloudflare supports many hostnames to local services on one tunnel. Same-zone Worker fetch error 1042 needs isolated staging check; do not globally add compatibility flags that affect existing Flud/BTDigg. Sources with residential Rock64 HTTP 403 remain blocked regardless of a shared tunnel, requiring independent source validation, no misattributed fallback. Source-specific proxies/egress are not authorized or installed. Current legacy optional EZTV Worker host and invariant are inactive proposals that require migration in a future gated PR before any Worker secret/deploy.

See docs/SHARED_MAGNETRA_GATEWAY.md. No new Tunnel, route, DNS, Worker Secret, PWA deploy, VPN/global network configuration, or paid service is authorized by this correction without staged verification.


## 2026-10-15 — shared existing BTDigg tunnel confirmed as selected architecture; 8798 code staged

Owner explicitly affirmed: **reuse the EXISTING BTDigg Cloudflare
Tunnel without altering its existing BTDigg route; later add only one
new published application `magnetra-rock64.alexlab.media` to a new
central allowlisted gateway on local 127.0.0.1:8798**, which delegates
to EZTV's proven existing 8797 and future individually verified
providers. Before activating, verify tunnel mode/route in Cloudflare
Dashboard and actual Rock64 services, and isolate same-zone Worker 1042.

A dedicated PR now stages an **offline-only** central dispatcher
`rock64/magnetra_gateway.py`, loopback-only, authenticated with
a new `MAGNETRA_GATEWAY_TOKEN`, one exact
`/v1/eztvx/torrents?imdb_id=...` route, forwarding only to
`127.0.0.1:8797` with the *different existing private*
`MAGNETRA_EZTV_TOKEN`. All other provider IDs/paths and arbitrary
URLs are rejected; no URL proxy, no redirects, no provider swapping,
no fake magnet rows; authenticated health 200 and unauthenticated 401,
bounded 1MB response, 8 concurrent connections, sanitized errors,
no extra retry or cache. The existing 8796 BTDigg gateway and its
tunnel remain untouched. Optional new resource-limited
`rock64/magnetra-gateway.service` is **NOT installed or started**;
no secret file or port listener has been created on physical Rock64.

Worker optional EZTV-only fetcher is staged for the new *shared*
origin `https://magnetra-rock64.alexlab.media` and distinct
`MAGNETRA_GATEWAY_TOKEN`. Obsolete worker
`EZTV_GATEWAY_TOKEN` is ignored; this change is **NOT** published
to production. The original 46 provider IDs, original EZTV
matching/metadata tests, and Flud dispatch remain unchanged.
Service installer, Cloudflare Published application route, DNS,
Worker secret, staging same-zone 1042 test, paid infrastructure,
network/VPN changes, and PWA production deploy are **NOT performed**.
Run the merged read-only `rock64/check-shared-tunnel.sh` next and
verify Dashboard management mode before any physical installation.


## 2026-10-16 — OWNER ROCK64 + EXISTING CLOUDFLARE DASHBOARD PROOF (CURRENT CHECKPOINT)

The user provided **real read-only output** from
`rock64/check-shared-tunnel.sh` pinned to merged
`7129adfaa076c7cd2dcc2650913332a3de6f019e`:

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

**Interpretation:** the existing BTDigg backend, existing BTDigg
Cloudflare Tunnel connector and existing EZTV backend are active.
Local `8796` and `8797` are both listening and require auth.
The planned central dispatcher `8798` has **no listener** (not
installed/activated). The superseded `magnetra-eztv-tunnel.service`
was reported **inactive**, not proven absent: do not enable it or
claim it was removed from the physical host. No credentials, headers,
magnet URLs or private IMDb IDs were included. This is a read-only
preflight, not a public Worker-to-gateway acceptance test.

**Cloudflare Dashboard screenshots supplied by owner:** The existing
tunnel detail is `magnetra-btdigg-rock64`, connector Type
`cloudflared`, with exactly **1 active replica** (hostname shown as
`rock64`) and **1 Published application route**, namely
`btdigg-rock64.alexlab.media` →
`http://127.0.0.1:8796`. The tunnel's **Overview** route diagram
shows an `Add route` action leading to the same existing connector;
the `Routes` tab displays the one BTDigg route. A `Rotate token`
control is present. **Neither `Add route` nor `Rotate token`
has been clicked**; no second route or DNS change is documented.

This confirms the exact desired single-tunnel configuration and that
the Dashboard exposes management for additional Published application
routes. Screenshots **do not literally display the tunnel management
mode label** `Remotely managed` vs `Locally managed`, so do not
claim that setting was separately proven. `Type: cloudflared` is
the connector type, not the management-mode field. If a management-mode
specific check is needed before activation, obtain it read-only in
Dashboard. Preserve the existing BTDigg route without reordering,
editing, deleting or restarting anything.

**Definitive architecture, superseding all earlier per-provider
tunnel plans:** reuse this same existing connector and keep the
existing `btdigg-rock64.alexlab.media → 8796` route completely
unchanged. Install a single isolated/authenticated central dispatcher
`127.0.0.1:8798` later, then create only ONE additional Published
application route on the **same tunnel**:
`magnetra-rock64.alexlab.media → http://127.0.0.1:8798`.
This extra route is **not yet created** and must not precede local
positive functional acceptance. No extra tunnel, cloudflared
process, provider-specific DNS route, global network change or
paid service. New provider paths can subsequently be registered
within the allowlisted 8798 gateway without new Cloudflare routes.

**GitHub current main before this checkpoint:** PR #50 merged at
`7129adfaa076c7cd2dcc2650913332a3de6f019e`;
`rock64/magnetra_gateway.py` and
`rock64/magnetra-gateway.service` are staged, NOT installed
physically. The current code exposes only authenticated
`GET /v1/eztvx/torrents?imdb_id=<5–12 digits>`, forwards to the
already authenticated, proven localhost `8797` EZTV endpoint,
uses a distinct `MAGNETRA_GATEWAY_TOKEN` (not the existing
`MAGNETRA_EZTV_TOKEN`), rejects all arbitrary URLs/other provider
paths, imposes response/time/concurrency limits and preserves genuine
source/IMDb/magnet validation. Worker optional EZTV route has been
staged to fixed `https://magnetra-rock64.alexlab.media` with
server-side `MAGNETRA_GATEWAY_TOKEN` gating. The retired
`EZTV_GATEWAY_TOKEN` and EZTV-specific tunnel plan are **NOT
AUTHORIZED**. Tests for PR #50 passed: 76 Node, 55 Python, Android
Debug and Staging. No PWA deploy was made by merging.

**Previously verified EZTV physical source-to-8797 proof:** same
genuine IMDb sample had 100 matching magnetic metadata rows directly
from official EZTV API and 100 matching magnet-bearing rows through
authenticated 8797 gateway. **This does not yet prove 8798**. All
original 46 indexer identities remain. Other recoveries are separate:
OxTorrent observed off-origin redirect to `www.oxtorrent.co`
(HTTP 200 but only 3 generic rows, 0 magnets confirmed);
Torrent9 to `www7.torrent9.to` (HTTP 200, 4 generic rows,
0 magnets confirmed); BitSearch `bitsearch.eu` HTTP 520;
Torrentz pre-HTTP transport failure, exact cause unknown;
UIndex, 1337x, BT4G, Ext, TorrentDatabase, TorrentDownloads,
TokyoToshokan returned HTTP 403 **even from residential Rock64**.
Do not claim the shared gateway alone repairs blocked sources,
fabricate results, change source attribution, follow unapproved
off-origin redirects, or circumvent protections. Historical 46-provider
production audit on 2026-10-13 was **13 results, 12 empty/unverified,
21 errors**; it is not a live health statement.

**Next engineering / owner workflow, in exact order:**

1. Treat the Rock64 preflight and screenshots as sufficient for
   gateway design; optionally confirm the explicit Cloudflare management
   mode read-only, but do **not** touch any route yet.
2. Create an independently guarded, root-opt-in installer and an
   authenticated read-only local **8798 acceptance checker** in a new
   branch/PR. Installer may touch ONLY
   `/opt/magnetra-gateway`, `/etc/magnetra-gateway` and
   `magnetra-gateway.service`, must refuse overwrites, symlinks,
   port collisions or changing existing units; reuse existing EZTV
   credential privately, generate different 8798 token root-only,
   bound CPU/RAM/threads and no persistent disk cache. All tests and
   4 main PR CI workflows required. Ask separate explicit owner
   permission **before owner runs installer**, since that affects the
   physical Rock64; no remote SSH access from ChatGPT.
3. After owner-approved 8798 install, prove authenticated local
   `/healthz`, exact same source-positive IMDb/magnet metadata via
   `8797` and `8798`, invalid/missing authorization HTTP 401,
   and unchanged BTDigg 8796.
4. Only after local 8798 PASS and separate approval, in the same
   existing Cloudflare Tunnel use `Add route` once to create
   `magnetra-rock64.alexlab.media → http://127.0.0.1:8798`,
   with existing BTDigg hostname/route untouched. Check public
   unauthenticated `/healthz` gives 401 from gateway, inspect DNS
   conflict and tunnel health. **No secrets in chat/logs**.
5. Validate isolated **Worker → shared Tunnel** reachability in
   staging, explicitly checking for Cloudflare same-zone **1042**.
   Do not change global compatibility flags (notably
   `global_fetch_strictly_public`) or BTDigg/Flud behavior. If
   necessary design a narrowly scoped egress Worker/service binding,
   **not a second Cloudflare Tunnel**, subject to review.
6. Only after real end-to-end success and explicit owner approval,
   configure server-side Worker Secret `MAGNETRA_GATEWAY_TOKEN`,
   deploy using guarded `[deploy-pwa]`, test real EZTV results
   and zero/403/error semantics, recheck BTDigg and Flud, and
   maintain rollback confined to the NEW hostname route/8798.
7. Continue source-by-source evidence-led recovery for the other
   46-provider adapters: genuine original rows, deferred magnet
   resolution and source-specific outbound limitations. The shared
   dispatcher must NEVER become an open arbitrary URL proxy.

**Must preserve throughout:** NexaPanel, CalciDatum, Plex, Flud/Flood
Companion, Tailscale, NordVPN, Rock64 DNS/default route/firewall,
shared cloudflared units, the existing BTDigg tunnel + its hostname,
8796 and existing 8797 services. Never print/upload tokens, systemd
environment, private IMDb IDs, magnet URLs, hashes or downloaded
torrent data. GitHub changes via scoped PR and green CI, no implied
production release.


## 2026-10-16 — central 8798 installer and acceptance STAGED; physical activation pending

After verifying main at `05239e212f75638f93ce3987efbea445ef00f6f6`, the owner-requested next implementation is isolated to a new review branch/PR. New source files: `rock64/install-magnetra-gateway.sh` and `rock64/check-magnetra-gateway.py`, plus offline regression tests in `rock64/test_magnetra_install.py`. The established `rock64/magnetra_gateway.py` and `rock64/magnetra-gateway.service` remain the actual central dispatcher and template, without modification of the existing BTDigg, EZTV, tunnel or PWA.

The opt-in first-install script refuses pre-existing destination directories/unit, symlinks, a loaded service or occupied 8798 port. It verifies pre-existing BTDigg, BTDigg tunnel and EZTV units, pre-existing unauthenticated 401 on 8796 and 8797, validates the root-owned local EZTV credential WITHOUT displaying it, validates the isolated systemd unit, and runs offline unit tests before writes. Only after these checks does it create `/opt/magnetra-gateway`, `/etc/magnetra-gateway` and `magnetra-gateway.service`; it generates a separate central token with secure randomness, reuses the existing token file read-only, enables only the new unit, runs an authenticated/unauthenticated 8798 smoke test and performs dedicated-path rollback on failure. CPUQuota=20%, MemoryMax=128M and systemd sandboxing remain.

The separate read-only acceptance checker (after explicit physical install approval) checks existing service health, new 8798 authentication and genuine EZTV source metadata, then compares the **exact magnet multiset and counts for the same real IMDb** through original EZTV API, current authenticated 8797 and new authenticated 8798. It prints only PASS/FAIL, stages, and aggregate counts; no search ID, title, hash, magnet, response body or token. It does not download torrents or alter system state. It treats missing positive sources as UNVERIFIED, and does not invent successes. Installer runs `--smoke` only; real-source acceptance must be run explicitly afterward.

**Activation gates remain unchanged:** review + CI + PR integration, separate owner agreement to install on Rock64, successful physical read-only acceptance, separate agreement for ONE additional hostname on the existing `magnetra-btdigg-rock64` tunnel, isolated Worker-to-Tunnel/1042 verification, and finally explicitly approved Worker secret and protected `[deploy-pwa]` release. `gateway_deployed=false`, `worker_activated=false` and `new_dns_route_created=false` remain valid. The historical 13/12/21 source audit does not change.


## 2026-10-16 — real Rock64 8798 first installation failed at initial smoke; rollback

Owner executed the exact pinned main `73b916cdf811f777881a88ae17d9f6b5ae2280bb` installer on real Rock64. Evidence: project invariant PASS; previous 8796/8797 authentication and 8798 free-port preflight PASS; installer-scoped 18 offline Python tests PASS; `systemctl enable --now magnetra-gateway.service` returned success; immediate authenticated local smoke reported only `FAIL: local credentials, service integrity or authenticated health`. The installer then reported a rollback of the dedicated new central files and unit. No genuine 8798 EZTV acceptance was run; 8798 **must not** be represented as installed or healthy from this attempt. No Cloudflare or Worker/PWA deployment occurred.

Code inspection identified a genuine **readiness race in the installer/checker design**: a `Type=simple` unit can become `active` before its loopback listener is bound, but the old smoke made a single immediate request. This is a plausible cause of the observed failure, **not a proven physical root cause**, since the historical smoke collapsed all errors into one message and no post-failure service journal was supplied.

The recovery PR `fix/rock64-8798-readiness-diagnostics` adds bounded loopback-only readiness polling (connection-refused only; no retry on wrong HTTP, authentic source errors, or other transports), and safe stage-specific diagnostics for any subsequent failed health check, with regression tests. It does not change the 8798 dispatcher, systemd sandbox, existing units, tunnel, provider contracts or production routes. Await green CI and integration before retrying an owner-approved local install. No automatic root reinstall or new Cloudflare published hostname.


## 2026-10-16 — PHYSICAL ROCK64 ACCEPTANCE PASS: 8798 INSTALLED, AUTHENTIC EZTV MAGNET PARITY 53/53

**Latest operational checkpoint (supersedes the prior failed 8798 attempt for current state).** The owner ran the exact pinned `main` at `174d7e09c441f9430e14518b928f5efc4a0812e1` on the physical Rock64 and provided the terminal output. `scripts/check-project-invariants.py` PASSED. The isolated central installer preflight PASSED for existing authenticated 8796/8797 and free 8798 port; the installer-side 23 offline Python tests PASSED. The new `magnetra-gateway.service` was enabled and started, and its local smoke PASSED:

- `127.0.0.1:8798/healthz`: authenticated HTTP 200, unauthenticated HTTP 401.
- `127.0.0.1:8797/healthz`: authenticated HTTP 200, unauthenticated HTTP 401.
- `127.0.0.1:8796/healthz`: unauthenticated HTTP 401.
- `magnetra-btdigg.service`, `magnetra-btdigg-tunnel.service` and `magnetra-eztv.service` all remained active according to the checker.
- Installer reported `PASS: new gateway 127.0.0.1:8798 installed; 8796/8797 retained.`

**Real positive-source acceptance PASSED:** the read-only checker selected a recent genuine EZTV-supplied IMDb internally (not printed) and fetched filtered results through the same three stages. Original `eztvx.to` API: **53** matching genuine magnet rows; authenticated EZTV 8797: **53**; authenticated central 8798: **53**. The checker validated **exact magnet multiset identity**, not merely equal row counts: `PASS: exact genuine magnet multiset preserved through 8798 -> 8797`. No private IMDb, title, magnet, hash, token, or raw data was displayed.

`shared_magnetra_gateway.gateway_deployed=true` and `physical_8798_acceptance_passed=true` now describe **local loopback service installation and real Rock64 acceptance only**. They do **NOT** indicate that the new public Cloudflare hostname/route or the Cloudflare Worker integration is active. `new_tunnel_installed=false`, `new_dns_route_created=false`, and `worker_activated=false` remain accurate. There is no evidence of a new published application route, Worker Secret or PWA deploy; none were performed as part of the SSH block. Keep the historic 46 indexer catalog and 13/12/21 audit unchanged.

**NEXT EXPLICIT OWNER-APPROVAL GATE:** add exactly ONE additional Published application on the existing `magnetra-btdigg-rock64` Cloudflare Tunnel: `magnetra-rock64.alexlab.media` -> `http://127.0.0.1:8798`. Do not modify the pre-existing `btdigg-rock64.alexlab.media` -> `http://127.0.0.1:8796` mapping or rotate/restart its connector. After separate approval and execution, verify public HTTPS (unauthenticated `/healthz` => 401) and restricted authenticated access without disclosing the token. Only then stage the isolated Worker->Tunnel same-zone 1042 test. No global `global_fetch_strictly_public` change and no Worker Secret or `[deploy-pwa]` without later explicit approval.


## 2026-10-16 — Existing Cloudflare Tunnel now has TWO published routes; external HTTPS 401/TLS PASS, Rock64 local DNS A pending

**Later operational checkpoint, superseding the previous `new_dns_route_created=false` and "route requires approval" next-step assertions.** With separate user approval, the owner configured exactly ONE additional Published application under the **same existing** `magnetra-btdigg-rock64` Cloudflare Tunnel. Cloudflare Dashboard screenshots show both entries simultaneously, as distinct ordered routes:

1. Existing `btdigg-rock64.alexlab.media` -> `http://127.0.0.1:8796`, unchanged.
2. Newly added `magnetra-rock64.alexlab.media` -> `http://127.0.0.1:8798`.

Cloudflare DNS screenshots show both proxied CNAMEs directed to the **same existing `ff4f5913-4c08-4396-9e77-a307bfaeb67c.cfargotunnel.com` target** (abbreviated display; the visible UUID prefix and equality suffice; do not reconstruct other private data). Neither route requires a second tunnel. New tunnel installation remains FALSE.

Real owner-provided Rock64 observations: loopback `127.0.0.1:8798/healthz` no-auth returned HTTP **401**. Legacy public BTDigg HTTPS `/healthz` returned HTTP **401** over IPv4; BTDigg remained operational. Direct IPv4 DNS lookup `getent ahostsv4 magnetra-rock64.alexlab.media` returned **no IPv4 addresses** on that host, whereas its IPv6 lookup returned addresses, but IPv6 HTTPS failed equally for BOTH BTDigg and Magnetra. This implicates an unresolved Rock64 DNS/IPv6 client-side path, not evidence of a tunnel/backend outage. Root cause and worldwide DNS propagation have NOT yet been determined.

**Decisive external HTTPS route test**: owner called `curl --noproxy '*' -4 --resolve magnetra-rock64.alexlab.media:443:188.114.96.12 https://magnetra-rock64.alexlab.media/healthz` and repeated with `188.114.97.12` (known functioning BTDigg Cloudflare edge IPs). Both returned **HTTP 401, TLS verification result 0**, confirming valid HTTPS host handling and the expected unauthorized response for the new public hostname when local A-resolution is bypassed. This is a no-token edge-to-route smoke, **not a confirmed authenticated public end-to-end magnet fetch** and not a Worker->Tunnel compatibility proof. Do not print/submit owner tokens to check public auth.

Machine-readable `shared_magnetra_gateway.new_dns_route_created=true` and `public_unauth_https_401_verified=true` now reflect the owner-confirmed route and no-auth HTTPS/TLS test; `worker_activated=false` and `new_tunnel_installed=false` remain non-negotiable. No Worker Secret or production PWA deploy. **NEXT**: read-only public-vs-Rock64 DNS A diagnosis, then isolated Worker->Tunnel same-zone / 1042 feasibility test without global compatibility flags, without modifying production Worker, without extra tunnels or paid services. Obtain separate authorization before Worker Secret and protected production release. All 46 providers preserved.


## 2026-10-16 — Read-only public DNS-over-HTTPS confirms Magnetra IPv4 A records; local resolver anomaly isolated

**LATEST PHYSICAL DIAGNOSTIC.** Owner queried Cloudflare DNS-over-HTTPS directly from the Rock64 using `curl --noproxy '*' -4 --resolve cloudflare-dns.com:443:1.1.1.1`, requesting JSON for `magnetra-rock64.alexlab.media`. The public resolver returned `Status: 0` and exactly TWO IPv4 A addresses (`188.114.97.7`, `188.114.96.7`; TTL 300) and TWO IPv6 AAAA addresses (`2a06:98c1:3121::7`, `2a06:98c1:3120::7`; TTL 300). In the same terminal session `getent ahostsv4 magnetra-rock64.alexlab.media` on Rock64 still returned **no IPv4**.

**Interpretation:** a public IPv4 A record exists and resolves through Cloudflare DoH; the Rock64 OS default name-resolution path is returning no IPv4 answer. The exact local failure mechanism (configured resolver, local cache/negative cache, DNS filter, resolver/network settings, timing) has **not** been established. No reason to edit Cloudflare CNAME, add manual A records, create tunnels, restart services, or modify global DNS/VPN/Tailscale/network settings. Previously observed both Cloudflare edge IPs with `curl --resolve` produced HTTP 401 and TLS verification result 0, and local 8798 same-source acceptance passed 53/53. DoH alone is not proof that authenticated public traffic or Cloudflare Worker same-zone requests succeed.

**NEXT:** non-mutating inspection of `/etc/resolv.conf` nameserver entries, optional `resolvectl` DNS A query if installed, and a repeat local `getent ahostsv4` after DNS TTL; then isolated Worker-to-Tunnel HTTP request/1042 experiment independently from production (no Worker Secret, no `[deploy-pwa]`, no global `global_fetch_strictly_public` compatibility changes). Keep `worker_activated=false` and all protected services unchanged.


## 2026-10-16 — Rock64 DNS IPv4 self-recovered; real unmodified HTTPS 401; isolated 1042 probe code STAGED

**Latest owner-provided Rock64 terminal evidence, superseding the earlier temporary lack of A resolution:** `getent ahostsv4 magnetra-rock64.alexlab.media` now returned Cloudflare IPv4 addresses `188.114.96.12` and `188.114.97.12`, with STREAM/DGRAM/RAW entries. `/etc/resolv.conf` was a symlink to `/run/systemd/resolve/stub-resolv.conf`, with the systemd-resolved loopback stub `127.0.0.53`. `resolvectl query --type=A` returned both A addresses via link `end0` from cache in 9.4 ms. The user's **ordinary** `curl --noproxy '*' -4 https://magnetra-rock64.alexlab.media/healthz` returned **HTTP 401, IP=188.114.97.12**, WITHOUT `--resolve`. This is genuine normal Rock64 DNS+HTTPS success. The earlier negative lookup was temporary; whether it was cache timing/propagation/filtering is **unknown**. No DNS/VPN/router/systemd-network/cloudflared config needs alteration. Public Cloudflare DoH A/AAAA checks and exact local EZTV 53/53 acceptance remain valid.

**Next scope prepared but NOT activated:** standalone `worker/probes/tunnel-1042-probe.mjs`, `worker/test/tunnel-1042-probe.test.mjs` and `worker/probes/README.md`. The diagnostic issues only one unauthenticated no-redirect bounded GET to the fixed HTTPS `/healthz`, returns a redacted 401/1042/transport result, and exposes no proxy, magnet search, IMDb, token or source response body. It is not imported by production PWA and has **no Worker deployment config or remote test invocation**. GitHub stage/CI and physical Cloudflare Worker deployment are different gates.

Cloudflare documentation defines 1042 primarily as a same-zone Worker->Worker fetch limitation. A real diagnostic must execute from a Worker in the relevant `alexlab.media` zone; `workers.dev`/remote preview alone may not mirror that scenario. The temporary separate Worker plus a non-overlapping same-zone test domain requires explicit further owner consent and cost/tier checks, and should be removed afterward. Never edit `index.alexlab.media`, original tunnel routes, global `global_fetch_strictly_public`, Worker production secret, PWA release or the 46 provider registry to test 1042. A 401 from this probe proves unauthenticated Worker-to-host routing only, **not** authenticated magnet parity.


## 2026-10-16 — iOS Cloudflare Quick Edit clipboard blocked; single temporary Git Builds config staged (NOT deployed)

Owner has created the temporary Cloudflare Dashboard Worker `magnetra-1042-probe`, but the iPhone/Safari Cloudflare Quick Edit editor displays `Unable to read from the browser's clipboard`; the default Worker code still returns Hello World. No trustworthy 1042 test has been run, no same-zone temporary Custom Domain has been verified, and **no proof of successful probe deployment** exists.

A new **standalone `worker/probes/wrangler.jsonc`** is staged in GitHub specifically for Cloudflare's native Git Builds connection of the existing temporary Worker (avoids editing JavaScript on iOS). Its exact allowlisted contents bind Worker name `magnetra-1042-probe` to `tunnel-1042-probe.mjs` and exactly ONE temporary Custom Domain `magnetra-probe.alexlab.media`, with no assets, secrets, protected production hostname, cron or other routes; `workers_dev=false`. Existing tests and `scripts/check-project-invariants.py` assert the complete config. **The source checkout, PR and its CI do not deploy the temporary Worker.** A GitHub Actions workflow creation attempt was not available; do NOT tell the owner a one-click GitHub Actions deployment exists. Instead after reviewed green CI and merge, owner can use **Cloudflare Workers & Pages → magnetra-1042-probe → Settings → Builds → Connect**, choose GitHub `Zuzuitu/AlexLab-Magnetra`, branch `main`, root directory `worker/probes` exclusively (NOT repo root or `worker`), with deploy command `npx wrangler deploy` if prompted. Cloudflare may require a fresh Git push after connecting to build: wait for evidence and never assert deployment occurred by merely connecting.

Owner must explicitly authorize GitHub account access and halt if asked to enable paid service or if custom domain is already in use. Only after live deployment on same zone should one `GET https://magnetra-probe.alexlab.media/probe` return sanitized diagnostics; that response must not be fabricated or mistaken for real magnets. Afterwards disconnect Git Builds and remove only the temporary Worker/domain; do not modify production PWA, two existing tunnel routes, DNS resolver, secrets, or global Worker flags. `worker_1042_git_build_config_staged=true` describes CODE ONLY; `worker_1042_live_test_passed=false`, `worker_activated=false` remain.


## 2026-10-16 — Git Builds CONNECTED for temporary Worker; owner screenshot verified, first build not yet confirmed

Owner provided real Cloudflare screenshots of **`magnetra-1042-probe` Settings → Builds AFTER pressing Connect**. Git provider linked to `Zuzuitu/AlexLab-Magnetra`, production branch `main`, root directory **`worker/probes`**, deploy command `npx wrangler deploy`, optional build command unset, no build environment secrets, preview builds disabled. Dashboard displayed **"You can now push a commit to your Git repository to start your first build"**, so connection PASSED but deployed probe code, created Custom Domain, and live same-zone Worker→Tunnel result are **NOT YET VERIFIED**. Existing worker `alexlab-magnetra` and production PWA still untouched.

User screenshots showed selected build API token *display name* `calcidatum-build-token`, which may have unrelated project provenance. Do not assume it is overbroad, valid, or invalid; only if Cloudflare Build reports permission failure should owner inspect a dedicated least-privilege token. Do not print tokens, alter global account settings or rotate other projects' credentials.

The present protected PR changes only a checkpoint file in `worker/probes` plus canonical memory/invariant guard. Once tests green and merged into `main`, it provides the necessary first commit event for the **already-connected** temporary Git Build. Check Cloudflare Builds and log result before interpreting any success; failures require specific diagnosis. Do not manually publish the probe via iOS editor. After one successful live test, disconnect Git Builds and remove only temporary Worker/Custom Domain.


## 2026-10-16 — VERIFIED REAL same-zone Worker → Tunnel no-auth probe PASS; cleanup pending

**Owner-supplied physical Rock64 test is authoritative.** Git-connected temporary Cloudflare Worker `magnetra-1042-probe` had deployed version `081abe6f` with 100% traffic (Dashboard screenshot showed 0% errors). Safari initially downloaded an empty-looking `probe.txt`; user then tested from Rock64 using `curl --noproxy '*' -4 https://magnetra-probe.alexlab.media/probe`, saving headers/body. Result: DNS A `104.21.62.69` and `172.67.221.15`; HTTPS `HTTP=200`, edge IP `104.21.62.69`, `TLS=0`; `Content-Type: application/json; charset=utf-8`, `Content-Length: 50`; JSON parsed successfully: `result=PASS_UNAUTHENTICATED_401`, `status=401`. This is a **live Cloudflare Worker-to-existing shared Tunnel GET of protected /healthz returning expected unauthorized 401**, NOT a mocked CI test. It demonstrates no Cloudflare 1042 restriction on **this exact no-auth route**.

Limitations: no Worker bearer token was used, no original-same-IMDb source/magnet parity executed from a Worker, and original 53/53 parity proof remains a separate Rock64 local test. No production secret has been activated, no PWA deploy, and the 46 provider identities remain unchanged.

**Cleanup gate:** owner has not yet confirmed disconnection of Cloudflare Git Builds or deletion of **only** `magnetra-1042-probe` and its ephemeral custom domain `magnetra-probe.alexlab.media`. The terminal screenshot/report alone is NOT cleanup evidence. To avoid another unneeded temporary-worker redeployment, **hold merge of this checkpoint PR until owner confirms cleanup**, because current Git Builds is connected to `main` and may trigger on every new main commit. Owner should disconnect Git Builds on temporary Worker, then delete ONLY temporary Worker (Cloudflare may also remove its custom domain; verify DNS). Do not delete gateway hostname `magnetra-rock64.alexlab.media` or BTDigg hostname, and never touch `index.alexlab.media`.

Machine-readable `worker_1042_live_test_passed=true` means **no-auth fixed /healthz proof only**. The separate `worker_1042_live_authenticated_test_passed=false` explicitly prevents claiming validated Worker-to-8798 authenticated magnet flow. `worker_1042_temporary_worker_cleanup_confirmed=false` until owner evidence. Next step, after cleanup: separately authorize protected production Worker secret `MAGNETRA_GATEWAY_TOKEN` and controlled no-leak same-source integration test, then a gated PWA release. Do not disclose bearer token or change global `global_fetch_strictly_public` compatibility flag.


## 2026-10-16 — owner confirms temporary Worker teardown COMPLETE (latest)

Following the live 1042 no-auth PASS, owner replied **"Gata"** directly to the requested sequence: disconnect Git Builds, remove temporary `magnetra-probe.alexlab.media` custom domain, delete ONLY the temporary Worker `magnetra-1042-probe`. Record this as **owner-reported completion**, not independent Cloudflare API/dashboard verification. The disposable probe and its Git integration are therefore considered retired operationally, and future `main` commits no longer intentionally target that temporary Cloudflare deployment. No evidence or authority to modify the persistent Cloudflare Tunnel, `magnetra-rock64.alexlab.media`, BTDigg, Rock64 services, `index.alexlab.media`, or production secret.

The real no-auth Worker-to-Tunnel PASS remains valid historical evidence. The owner has **not yet authorized production `MAGNETRA_GATEWAY_TOKEN` activation, an authenticated Worker fetch or the protected production PWA deployment**. Keep `worker_activated=false`, `worker_1042_live_authenticated_test_passed=false`; require a distinct approval gate for next stage. State fields now distinguish historical `worker_1042_live_test_passed=true`, `worker_1042_git_connected=false` and `worker_1042_temporary_worker_cleanup_confirmed=true` (per user report).


## 2026-10-16 — UNIVERSAL 46-PROVIDER RECOVERY, Phase 1 STAGED; not an EZTV-only plan

Owner explicitly reaffirmed that the next Magnetra objective is to develop a general solution for **all broken/unverified original indexers**, not merely EZTV, and authorized starting implementation. This PR provides the first general layer while preserving source identity, all 46 adapter implementations, and the live application configuration.

New `worker/src/recovery-strategy.mjs` derives an exhaustive, ordered recovery plan from the historical complete 2026-10-13 production sample (13 with rows, 12 empty/unverified, 21 errors; run 38373699387) and independently recorded Rock64 evidence. Unlike naive bulk residential proxying, the classifier distinguishes: pre-existing BTDigg gateway (8796), EZTV proven 53-exact original→8797→8798 source parity (but Worker production secret/integration still OFF), observed 301 host candidates BitSearch/OxTorrent/Torrent9 (requires verification), 1337x/BT4G/Ext physical 403 from Rock64 as well as Cloudflare (residential routing not justified), Torrentz Rock64 transport failure, 429 stop, 52x/53x upstream outage, empty query non-evidence and unverified Cloudflare errors needing bounded egress comparison.

Code changes: `GET /api/providers` includes an additive per-provider `recovery` decision while keeping historical `lastAudit`; new read-only `GET /api/recovery-plan` returns summary + **all 46 provider plans** and does no outbound source calls. Operator `node scripts/recovery-plan.mjs` emits deterministic offline prioritized steps / machine-readable JSON, with neither source GETs nor tokens. Regression tests protect the original 46 IDs, historical audit provenance, known Rock64 observations, no automatic rerouting, no 429 retries, honest empty semantics and gateway eligibility **only** for existing BTDigg and tested EZTV. New invariant `provider_recovery_v1` and guard establish that the common plan is read-only, `worker_secret_activation=false` and `production_deployed=false`; existing protected `shared_magnetra_gateway.worker_activated=false` unchanged. `docs/PROVIDER_RECOVERY_PLAN.md` records steps and gates.

**CURRENT GATE:** This is staged GitHub code only, **not deployed**, does not make blocked providers work yet and does not call new private Rock64 endpoints. After CI and merge, get real owner-run results from the existing safe three-host `rock64/probe-redirect-candidates.py` before approving any origin/parser migration or a narrowly allowlisted 8798 endpoint. Do not alter 8796, 8797, 8798 unit files, existing cloudflared tunnel, DNS, other services, Cloudflare Worker secrets, production PWA or global compatibility flags as part of Phase 1.


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


## 2026-10-17 — MAGNETRA Cloudflare VERSION staging prepared, production 100% previous Worker

Owner's actual iPhone Cloudflare dashboard evidence: production Worker `alexlab-magnetra` active version **`a9df4429`**, serving **100%** traffic, error rate **0% as displayed** (not proof indexers return results). After adding `MAGNETRA_GATEWAY_TOKEN` through **Save version** rather than Deploy, Cloudflare displayed a **new undeployed secret-only version `ce808b27`**, with label `Add secret: MAGNETRA_GATE...`; active version remained `a9df4429` at 100%. Existing `BTDIGG_GATEWAY_TOKEN` must remain unchanged. There is NO evidence `ce808b27` contains PR #63 Worker code, so do NOT promote this draft version to production.

Owner has already physically confirmed the authenticated Rock64 8798 dispatcher accepting EZTV plus OxTorrent/Torrent9 real original source search/detail chains; physical 8798 2/2 source magnet proofs remain distinct from Worker's authenticated tunnel integration. Current `main` contains the opt-in Worker's EZTV/OxTorrent/Torrent9 8798 route mapping, but this is **not** deployed to production. All 46 existing indexers remain unchanged in production.

Manual-only new workflow `.github/workflows/stage-magnetra-worker.yml` must be **merged via protected PR and intentionally invoked from GitHub Actions**. The workflow does not run on pushes; it checks project invariants and all Worker contracts, builds an ephemeral Wrangler config derived from canonical `worker/wrangler.jsonc`, adds only `secrets.required` **NAMES** (`BTDIGG_GATEWAY_TOKEN`, `MAGNETRA_GATEWAY_TOKEN`) and uses `wrangler versions upload --keep-vars`. This creates a **code+assets VERSION with 0% active traffic** rather than calling `wrangler deploy`. If the required secret does not carry into the version, upload MUST stop instead of silently deploying without it. An upload alone is NOT a successful Worker-to-Tunnel test. No secret values or hashes may be shown in logs, copied to GitHub or chat; do not add `--secrets-file`.

**Next gates**: (1) CI 4/4 + merge staging workflow, (2) manually run the upload-only Action on main (user approval required), (3) verify the newly uploaded version contains Worker code plus **both** secret binding names in its version details, `a9df4429` still 100%, and explicit roll-back target, (4) perform safe version-URL/controlled canary backend search and deferred magnet tests before 100% promotion, (5) audit 46 original indexers. The new stage version ID is UNKNOWN until upload succeeds. Never press Deploy on draft `ce808b27`, use `workflow_dispatch` on `deploy-pwa.yml`, or deploy 100% without the intervening checks.


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

## 2026-10-19 — Cloudflare 100/0 audit correction and owner-authorized 5% canary preparation

**Observed in PWA:** BTDigg yielded genuine results, while OxTorrent and Torrent9 did not appear operational in normal traffic. Their earlier authenticated E2E successes targeted the 0%-traffic candidate Worker, not ordinary production.

**Read-only Cloudflare inspection #2:** candidate ID and binding names/types (BTDIGG_GATEWAY_TOKEN, MAGNETRA_GATEWAY_TOKEN, ASSETS) passed; job stopped at TRAFFIC_SHARES: UNVERIFIED. Root cause in scripts/inspect_cloudflare_version.py: rejected legitimate 0%-share entries and the expected two-version 100% old / 0% candidate deployment. This was an audit/parser failure, NOT evidence of modified deployment. Fix permits only old-only 100% or exact old 100% + approved candidate 0%; rejects duplicates, unexpected IDs, positive candidate traffic, invalid totals/types. Tests cover both accepted and fail-closed states.

**Owner decision (19 Oct):** explicitly authorized bounded candidate canary 5% / old 95%, with rollback to old 100%. This approval is not evidence of actual Cloudflare execution, successful PWA acceptance or permission to promote candidate to 100%.

**Prepared implementation:** scripts/deploy_magnetra_canary.py and manual-only .github/workflows/deploy-magnetra-canary-5.yml verify exact version and bindings, 100/0 preflight, deployment race protection, precise 95/5 operation, Cloudflare API postflight, guarded rollback refusing unknown concurrent deployments. Offline regression tests added. Default workflow input CANCEL. Only owner-triggered main-branch workflow can write deployment. No new Worker upload, Tunnel, DNS, Rock64, secret or frontend modifications.

**Deployment status at this checkpoint:** canary NOT EXECUTED; latest real split requires read-only Cloudflare confirmation. Do not mark worker_activated, production_worker_promotion_completed or canary_deployment_completed as true until actual live postflight evidence.

## 2026-10-19 12:00 Europe/Rome — Verified production 95/5 canary and scoped E2E follow-up

**LIVE confirmed deployment:** owner ran manual workflow [Activate Magnetra 5 Percent Canary #1](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39234183618), main SHA 1fb6980b97a3759b04baf801d97290a3a96f6f67. Job guarded-canary (117999163283) completed SUCCESS. The **actual non-mocked mutation step** logged `PREFLIGHT_PASS: exact candidate + bindings, old 100%, new 0%`, `APPLYING: old 95%, exact candidate 5%`, then `CANARY_POSTFLIGHT_PASS: old 95%, candidate 5% confirmed by API.` Early similar log lines in offline unittest output are synthetic and must not be misattributed to production. Previous rollback version a9df4429 remains 95%; candidate 249d6767-f4dc-4f4d-bbf7-f57bea2e5554 receives 5%. Historical BTDigg auth/source observations are unchanged. No evidence yet for user-facing OxTorrent/Torrent9 under ordinary stochastic routing.

**Canary is not full promotion:** `canary_deployment_completed=true` and `worker_code_version_activated=true` mean **partial 5% activation**, not `production_worker_promotion_completed`. 95% remains on prior Worker. No owner approval for 100% candidate; do not call normal 95%-old PWA search a candidate failure by mistake.

**New manual read-only E2E gate:** workflow `.github/workflows/verify-magnetra-canary-e2e.yml` plus `scripts/check-magnetra-canary-e2e.py`. Requires exact 95/5 Cloudflare GET proof and correct candidate bindings, forces **old and new versions independently** with Cloudflare-Workers-Version-Overrides and verifies differential candidate-only `/api/recovery-plan` 404 vs 200 with 46 entries. For each of original OxTorrent/Torrent9 runs one bounded `ubuntu` search and one original deferred BTIH magnet resolution via candidate Worker→Rock64 8798, with no download/retry/secret echo. Optional explicit EZTV positive check; **BTDigg never reprobed**. Requires deliberate `RUN_READONLY_HTML` or `RUN_READONLY_HTML_EZTV` dispatch, never an automatic run. Rechecks unchanged Cloudflare deployment after source probes. CI only proves fixtures and contracts; live result remains **NOT EXECUTED** until an actual manually started workflow.

**Next gate:** run owner-triggered read-only 95/5 test, inspect authentic source-positive results + actual Cloudflare split, then decide whether to prepare a *separately approved* 100% candidate promotion. Keep manual fallback to old-only 100% and avoid any Rock64 changes.

## 2026-10-19 — Actual 95/5 OxTorrent/Torrent9 E2E PASS; full release preparation WITHOUT approval

**Read-only source-positive result:** Owner dispatched [Verify Magnetra 5 Percent Canary E2E (READ ONLY) #1](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39241165033) on main 00c5150e4fdb8734e4654915c096a1adf6b65f21. Workflow job 118022042637 succeeded. Distinguish earlier mocked `unittest` lines from the actual `Authenticated E2E on exact 5% candidate version` step: `CANARY_DEPLOYMENT_GATE: PASS (old 95%, candidate 5%; 3 bindings PASS)`, `EXACT_VERSION_OVERRIDE_GATE: PASS (old 404, candidate 200 and 46 IDs)`, `CANDIDATE_PROVIDER_CATALOG: PASS 46/46`, `SEARCH_PASS_oxtorrent` 3 real original-source results and `DEFERRED_MAGNET_PASS_oxtorrent`, `SEARCH_PASS_torrent9` 3 real original-source results and `DEFERRED_MAGNET_PASS_torrent9`, `CANARY_POSTCHECK: PASS (unchanged 95/5)`, `CANARY_SOURCE_E2E_GATE: PASS`. No source magnet values, tokens or torrent downloads logged. EZTV live retest and BTDigg live retest were deliberately skipped, not falsely reported as revalidated in this run. Historical earlier BTDigg 10 old/new and EZTV 29 candidate source E2E proofs still stand as dated evidence, not a claim of current uptime.

**Decision:** full promotion to 100% candidate is NOT approved or executed at this checkpoint. The owner explicitly approved only the earlier 5% canary. The new manual release preparation must never be auto-dispatched or confused with an active deployment.

**Prepared but gated:** scripts/release_magnetra_candidate_100.py, `.github/workflows/release-magnetra-candidate-100.yml` and offline tests. Version-only promotion would require exact 95/5 canary preflight, the unchanged exact candidate UUID and all three bindings; deploy `old@0%` + `candidate@100%` to preserve a verifiable rollback slot. Manual rollback deploys `old@100%` + `candidate@0%`; double reads and API postflight reject unknown versions/overwrites and do not expose credentials. Workflow default `CANCEL`; exact typed operation is only possible after explicit separate owner approval and direct manual Run workflow on main. No changes to Rock64, DNS, tunnel, source parsers, secrets or PWA assets.

**Remaining steps:** after reviewed CI/PR merge, obtain owner's explicit approval for the risk of moving from 5% to 100%; execute manual workflow only then. Confirm Cloudflare postflight and iPhone UX, with bounded rollback ready. Keep history of E2E positive separated from production frontend acceptance.

## 2026-10-19 — Owner-approved full production promotion: exact candidate 100%, old 0%

**LIVE primary evidence:** owner started [Magnetra Candidate 100 Percent Release (MANUAL) #1](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39243522237) on branch main, reviewed commit `d026ef841f716f000dc8231ef68189a6b75107bc`, GitHub Actions job `guarded-release` / job ID `118029770204`, completed `SUCCESS` at approximately 2026-10-19 11:17 UTC. The separately identified REAL step **Execute exact owner-selected release operation** reported `MAGNETRA_RELEASE_ACTION: CONFIRM_PROMOTE_CANDIDATE_100`, `PROMOTION_PREFLIGHT_PASS: exact old 95% / candidate 5%; bindings present.`, `PROMOTING: old retained at 0%, exact candidate 100%.`, `PROMOTION_POSTFLIGHT_PASS: exact candidate 100%, old 0% available for rollback.` This is a Cloudflare deployment API postflight after Wrangler. Similar earlier output under **Offline immutable-version promotion and rollback tests** is SYNTHETIC and must NOT be mistaken for real live evidence.

**PRODUCTION TRAFFIC:** candidate UUID `249d6767-f4dc-4f4d-bbf7-f57bea2e5554` **100%**, former version with prefix `a9df4429` **0%, retained for rollback**. The authorized 5% canary and previous live E2E (#39241165033) established authentic OxTorrent 3 results + BTIH magnet, Torrent9 3 results + BTIH magnet, version fingerprint 404 old / 200 candidate, source attribution and catalog 46/46. BTDigg + EZTV had separate earlier candidate E2E evidence, including historic intermittent BTDigg 504; do not claim permanent BTDigg reliability.

**Evidence boundary:** 100% Worker *deployment* is confirmed, NOT independent real iPhone PWA search acceptance or real-time uptime of all indexers. No production smoke HTTP response was independently confirmed in this session; network from assistant runtime was not available. Remain explicit: `full_promotion_pwa_user_acceptance_confirmed=false`, `full_promotion_independent_http_smoke_confirmed=false`. User should perform first benign PWA search via https://index.alexlab.media selecting OxTorrent and Torrent9, observing actual source-specific results; then optionally EZTV/BTDigg respecting source rate limit. Do not automatically forward a magnet into Flud. The original old Worker stays rollback-ready through manual `CONFIRM_RESTORE_OLD_100` in `.github/workflows/release-magnetra-candidate-100.yml` with guarded 100% old / candidate 0% selection; do not roll back without an actual regression.

**Documentation consistency:** stage `full_promotion_owner_approved=true`, `full_promotion_executed=true`, `production_worker_promotion_completed=true`, `current_production_candidate_traffic_percent=100`, `current_rollback_version_traffic_percent=0`; keep all previous 95/5 canary snapshot fields as HISTORICAL measurements. Neither commit to main nor this documentation PR changes Worker code, version splits, DNS, tunnels, Rock64 services, secrets or PWA assets.

## 2026-10-19 — iPhone PWA post-100% verification: real source results; deferred Resolve blocked by canonical HTML route

**Owner screenshot 13:32 Italy:** normal production `https://index.alexlab.media` displays genuine provider-labeled results for **Torrent9** (`Hope.2026.Multi.Ca.WEBRIP-NOTAG`, 1.9 Go) and **OxTorrent** (`Toy.Story.5.2026.MULTi.CA.1080p.WEB.H264-SUPPLY`, ~6.6GB). At least one user-triggered **Resolve** produced `Provider could not resolve magnet: Noncanonical source HTML route refused.` Independently, the UI shows **BTDigg RATE_LIMIT** with `Wait a few seconds before another search.` Do not classify RATE_LIMIT as source timeout, permanent outage, or a 100% candidate regression without more evidence. Do not claim source listings prove deferred magnet resolved on mobile.

**Confirmed code origin:** `worker/src/html-rock64.mjs` `routeHtmlRequest()` throws exact message `Noncanonical source HTML route refused.` after it validates one static HTTPS origin and strictly formatted `/torrent/<digits>/<ASCII slug>` detail route, or strict fixed search template. `/api/resolve` in `worker/src/index.mjs` calls `resolveLegacy()` via this route for OxTorrent/Torrent9. The error is generated **in Cloudflare Worker before a physical Rock64 8798 upstream request** for that detail; it is NOT evidence that the provider lacks a magnet or that Rock64 service/tunnel failed. Existing E2E used only `ubuntu` links with simple ASCII slugs, so it did not cover the user's production details URL. Exact rejected URL/path shape has NOT been captured; don't widen allowlists or normalize unknown URLs on speculation.

**Read-only diagnostic staged:** `scripts/diagnose_magnetra_detail_routes.py` plus offline `scripts/test_magnetra_detail_routes.py` and manual-only `.github/workflows/diagnose-magnetra-detail-routes.yml`. Owner may dispatch `RUN_READONLY_2026_DETAIL_SHAPES` on main. Script verifies real candidate 100% / previous 0% deployment metadata, makes **one bounded production PWA /api/search GET for ONLY oxtorrent,torrent9 and benign query `2026`**, parses source-owned results to count *redacted URL shape classifications* and optionally classifies matching screenshot titles without logging title text, URL, torrent path IDs, magnets, tokens or HTML. No /api/resolve requests, no torrent downloads, Flud forwarding, retries, BTDigg or EZTV; exact deployment checked again at end. The result must inform a targeted fix (if needed in both Worker and Rock64) while preserving fixed-origin, anti-open-proxy rules. A workflow/PR merge alone performs NO live diagnostic and NO deploy.

**Release caution:** the exact production 100% Worker promotion remains confirmed from manual run `39243522237`; this diagnostic PR neither changes Cloudflare traffic nor PWA assets. Existing 0% old Worker retained for rollback. Mobile Resolve acceptance remains false until a new real result confirms it.

## 2026-10-19 — Exact owner-supplied OxTorrent detail URL: canonical, targeted resolve comparison pending

**Owner supplied exact Details link** after the iPhone PWA Resolve toast: `https://www.oxtorrent.co/torrent/133995/toy-story-5-2026-multi-ca-1080p-web-h264-supply`. It is canonical under current main `worker/src/html-rock64.mjs` `routeHtmlRequest()` fixed-origin/detail regex: HTTPS, verified allowlisted host, no query/fragment/credentials, numeric ID and ASCII slug. The source page itself is publicly accessible and displays the named record. **Do not blame this exact URL or weaken the allowlist** without checking the value actually passed to `/api/resolve`. iPhone `web/app.js` `ensureMagnet()` uses `item.magnetSource || item.details`; any difference must be determined, not guessed. Old live 100% result diagnostics for `2026` showed oxtorrent 50 canonical of 50, torrent9 20 canonical of 20; screenshot Toy Story item was absent from that particular sample.

**Focused test prepared without deployment:** Add direct Node regression for exact owner URL in `worker/test/html-rock64.test.mjs`; `scripts/diagnose_magnetra_exact_oxtorrent_resolve.py`, offline safety tests, and `.github/workflows/diagnose-magnetra-exact-oxtorrent-resolve.yml` (manual-only default CANCEL). Owner-selected `RUN_EXACT_OXTORRENT_READONLY` checks Cloudflare candidate 100%/old 0%, performs a single OxTorrent-only benign public PWA search for `toy story 5`, determines whether exact record is present and which URL PWA prefers (`magnetSource` vs `details`), then makes one non-mutating POST `/api/resolve` for owner URL and, only if different and allowlisted, one comparison POST for preferred source. Only sanitized outcome and route categories are printed (never names, URLs, IDs, magnets, hashes, bearer secrets, HTML), no torrent download, Flud call, service/DNS/tunnel/Worker/PWA mutation or retry; requires explicit separate manual run. The script reads responses but may make bounded original-source HTML requests through the existing Worker->Rock64 path. Live result remains **NOT EXECUTED** until GitHub manual workflow is run.

**Release remains unchanged:** Cloudflare candidate `249d6767-f4dc-4f4d-bbf7-f57bea2e5554` still expected at 100% from run 39243522237, old version 0% rollback; retain safety and avoid source-independent speculative fixes or changes to BTDigg rate limits. The screenshot's BTDigg rate-limit message is independent.

## 2026-10-19 — Owner confirms ALL 2026 result-card Resolve actions fail; BTDigg 429 again

**Screenshot 17:03 Italy:** browser production `index.alexlab.media`, 70 returned result cards (source attribution OxTorrent/Torrent9). Owner reports ALL 'Resolve' taps yield `Provider could not resolve magnet: Noncanonical source HTML route refused.` Screenshot foreground explicitly shows Torrent9-labelled Toy.Story.5 cards and same toast. BTDigg section explicitly says `BTDigg is limiting requests`, code `RATE_LIMIT` = 429, separate from historic 504. At 13:14 UTC exact-owner OxTorrent Details URL in run [39258418040](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39258418040) returned a **real VALID BTIH magnet** from `/api/resolve`; user screenshot failure is therefore NOT fully explained by the particular copied URL or upstream advertisement click-through. The older `2026` search-shape audit run [39248263290](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39248263290) measured 50 OxTorrent and 20 Torrent9 *details* links, all canonical by static path classification, but did NOT inspect `magnetSource` or perform Resolve on an item returned from that search.

**Critical code question:** the browser submits `item.magnetSource || item.details` from `web/app.js`; `worker/src/legacy-adapters.mjs` routes source URLs with fixed-origin `html-rock64.mjs`. The exact immutable candidate staging GitHub run #39015791760 had commit 2428f0120b213f706d9e6e0ae994c248d80c6c12, whose HTML gateway/legacy spec/content blobs match current main for relevant files; do **not** claim confirmed code-version drift merely from appearance. However the screenshot displays `.torrent` buttons for HTML source cards although current `LEGACY_SPECS.oxtorrent/torrent9` have no `torrentFile` selector, so runtime PWA/static assets/API payload consistency requires checking. Ads on the original source site might explain a click-through there but are **not yet demonstrated** to cause this specific route-refusal string; do not automatically follow ad links or weaken URL allowlists.

**New bounded manual read-only test:** `scripts/diagnose_magnetra_2026_card_resolve.py`, test `scripts/test_magnetra_2026_card_resolve.py`, and guarded `.github/workflows/diagnose-magnetra-2026-resolve.yml`. Explicit owner `RUN_BOUNDED_2026_CARD_RESOLVE` on main required (default CANCEL). Confirms production exact candidate 100%/old 0%, one original `/api/search` GET restricted to `q=2026&providers=oxtorrent,torrent9` (expected 70 but do not hardcode count), compares the **public `/app.js` SHA-256** against the checked-out reviewed `web/app.js` without printing its content, counts redacted `details`/`magnetSource` canonical URL shapes, `torrentFile` field presence, and flags frontend-preferred source overrides. Selects up to one canonical unresolved card per source, preferring user-observed 2026 title if found, performs one bounded non-mutating `/api/resolve` POST per source (plus at most one only when distinct preferred source is also canonical). Redacts all names, URLs, hash/magnet data and bearer auth. No torrent, auto Flud dispatch, BTDigg/EZTV traffic, retries, staging/deployment or Rock64 changes. Requires no CI output or evidence to be mistaken for real live execution until owner explicitly dispatches.

**Next:** if diagnosis finds bad preferred URL, fix selection of canonical original-source details without broadening gateway and add source-specific regression. If exact canonical search card resolves via script but still fails on iPhone, investigate PWA/client cache or route interception/version mismatch with server-generated safe fingerprint and avoid spurious Rock64 changes. Separate BTDigg 429 provenance (local 8796 five-second shared cooldown/inflight-vs-provider upstream 429); do not remove rate limits or add retry loops.

## 2026-10-19 — Definitive 70/70 card-to-Resolve root cause and two-provider PWA fix (NOT YET DEPLOYED)

**Authoritative REAL LIVE evidence:** Owner triggered [Diagnose Magnetra 2026 Resolve Fields (READ ONLY) #39286786842](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39286786842), exact immutable deployed candidate 100% / rollback old 0% verified. The ACTUAL live source-call step (not mocked unit tests) produced `PUBLIC_APP_JS_VS_GITHUB_MAIN: MATCH_REVIEWED_MAIN`; OxTorrent 50/50 canonical original `details` URLs and **50/50 noncanonical `magnetSource` OTHER_PATH_TEMPLATE**, with source overriding details on 50/50; Torrent9 20/20 canonical `details` URLs and **20/20 noncanonical `magnetSource` OTHER_PATH_TEMPLATE**, with override on 20/20. `torrentFile` is present in all 70 real cards despite prior selector-spec assumptions. For one original actual card from EACH provider, `CANONICAL_DETAIL_RESOLVE_<provider>: PASS_VALID_BTIH` was verified through production POST `/api/resolve`. Noncanonical preferred links were *not* queried; no ad clicks, .torrent/magnet outputs, BTDigg calls, Flud dispatch, deploy, secret logging or retries. Root cause is **frontend `ensureMagnet` choosing `item.magnetSource || item.details`**, which picks a noncanonical download/advertising path for both original HTML providers, not a Cloudflare Worker origin failure, bad physical Rock64 tunnel, or stale public PWA asset. Earlier owner screenshot at 17:03 had 70 result cards and universal `Noncanonical source HTML route refused.` toast; this run reconciles it.

**Minimal code fix in this branch, currently NOT LIVE:** `web/app.js` `ensureMagnet` uses only original source-owned `item.details` for `oxtorrent` and `torrent9`, instead of `magnetSource` when both are present. It fails closed if details absent; it does NOT attempt advertisement click-throughs. All other 44 providers retain prior `magnetSource || details` precedence, and direct genuine `item.magnet` remains unchanged. No changes to Worker route validator, legacy parser, gateway, DNS, Cloudflare traffic, BTDigg rate limits, other 44 provider IDs, or Flud Companion. Offline PWA behavioral regressions include 50+20 sample cards, actual `/api/resolve` body field value, caching of resolved magnet, legacy-provider compatibility, fail-closed missing details, and absence of ad/Flud calls.

**Publication gate:** GitHub PR/merge and passing CI do NOT deploy this JavaScript to the iPhone. The existing Cloudflare immutable 100% candidate version includes prior PWA assets. A dedicated, owner-approved controlled Worker/assets version release is required, with verification of both gateway tokens and ASSETS binding, a staged 0%-traffic candidate, real E2E, explicit rollout and rollback. Do **not** run `deploy-pwa.yml` automatically or silently upload/overwrite active versions; ordinary PR merge has no `[deploy-pwa]` marker. Until separate owner authorization and live smoke+iPhone acceptance, production Resolve bug remains OPEN and these corrective changes are NOT LIVE.

**Separate P0 BTDigg:** iPhone `BTDigg is limiting requests` means 429 / RATE_LIMIT and is not explained by this two-provider Resolve root cause. Rock64 gateway currently enforces 5s global minimum interval, singleflight, success-only 20min cache and upstream may itself return 429. Diagnose local-vs-upstream provenance from safe logs before any rate-limit tuning; no automatic retries after 429/timeout.

## 2026-10-19 — Staged Resolve fix Worker 540b (upload confirmed; bindings/traffic gate still unverified)

**Live GitHub Actions evidence:** owner ran manual [Stage Magnetra Worker (NO DEPLOY) #39298077357](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39298077357) from reviewed main commit `c6867647c10bba33db0361178f3380a7ffa48385` containing merged PR #89. Job #118215716306 completed SUCCESS after 46-provider/Worker contract tests, `wrangler@4.102.0` dry-run, existing credentials gate, and `wrangler versions upload --keep-vars` with ephemeral config requiring **names** of `BTDIGG_GATEWAY_TOKEN` and `MAGNETRA_GATEWAY_TOKEN`. Output: **`Worker Version ID: 540b3417-f845-47e8-96bd-856ccc9f1350`** and explicit `VERSION UPLOAD ONLY: No Deploy, no percentage shift.` Wrangler displayed `env.ASSETS Assets`, but the log does **NOT** independently attest secret bindings' presence in exact staged version metadata. **Do not treat 'upload success' as binding verification.**

**Production/rollback as last independently verified:** existing candidate `249d6767-f4dc-4f4d-bbf7-f57bea2e5554` at **100%**, older `a9df4429-...` at **0%**, per prior real deployment postflight (#39243522237). New 540b stage is uploaded **without traffic** and not yet attached as 0%-share in a Cloudflare deployment. No PWA update, Worker deploy, DNS, Cloudflare tunnel, Rock64 gateway or secret mutations were authorized/executed by the stage workflow. The source-code fix resolves only the card field selection: OxTorrent/Torrent9 use original canonical details rather than noncanonical magnetSource (50+20 proof in read-only run #39286786842); it remains **NOT LIVE** until a separate approved rollout and observed iPhone acceptance.

**Next strict gate:** manual read-only `.github/workflows/inspect-magnetra-resolve-fix-stage.yml` and parser `scripts/inspect_magnetra_fix_stage.py` GET Cloudflare version **540b** and live deployment metadata, verifying exactly `BTDIGG_GATEWAY_TOKEN`, `MAGNETRA_GATEWAY_TOKEN`, `ASSETS` binding *name/type* on the staged version and production still exactly 249d 100% (+ optional older a9df 0%). No full API bodies/credentials logged. Test fixtures reject wrong staged ID, absent secret binding, unexpected live version and nonzero traffic on 540b. Workflow merge itself does not run audit or mutate live state. If PASS, request explicit owner approval to attach a new **249d 100% / 540b 0%** deployment slot, preserving 249d as the immediate rollback. This would remove the historical a9df 0%-slot from the active split but does not delete the old version. Only then can version-selected staged E2E test real 2026 source cards and resolve before any 5% or 100% promotion. Preserve cost-zero rules and avoid unsanctioned PWA auto deploy.

## 2026-10-19 — Staged fix 540b bindings PASS; protected 0% slot and read-only E2E PREPARED ONLY

**Authenticated read-only audit PASS (REAL):** owner dispatched [Inspect Magnetra Resolve Fix Stage #39303873161](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39303873161) from `main` SHA `54d36cfa580b800df8dc9e289b8a7586ddf61a0e`. Its actual Cloudflare GET step (not synthetic fixtures) logged `STAGED_VERSION_MATCH: PASS`, `BTDIGG_GATEWAY_TOKEN: PASS`, `MAGNETRA_GATEWAY_TOKEN: PASS`, `ASSETS: PASS`, `CURRENT_PRODUCTION_249D_100_PERCENT: PASS`, `NEW_540B_VERSION_NOT_DEPLOYED: PASS`, `STAGE_GATE: PASS`. New exact uploaded version `540b3417-f845-47e8-96bd-856ccc9f1350` has both gateway secrets and ASSETS; current `249d6767-f4dc-4f4d-bbf7-f57bea2e5554` is 100% of ordinary traffic. Older `a9df4429` remains historical and may occupy previous 0% slot. No secrets/values printed or modified.

**New zero-percent procedure, NOT APPROVED/NOT EXECUTED:** reviewed Python `scripts/deploy_magnetra_fix_zero_slot.py` and manual-only `.github/workflows/magnetra-resolve-fix-zero-slot.yml`, owner choice `CONFIRM_CURRENT_100_FIX_0` (default `CANCEL`). Because Cloudflare active deployment supports at most 2 version slots, slot changes from current **249d@100 + a9df@0** (or 249d only) to **249d@100 + staged 540b@0**, preserving 249d as the immediate rollback; a9df is *not* deleted and can be recovered separately by administrator if needed. The 0%-slot operation mutates Cloudflare deployment metadata even though it does not redirect normal production traffic. Requires *separate explicit owner approval* and manual GitHub dispatch, never on PR merge. Exact staged binding preflight + current deployment ID race check, pinned Wrangler version-only deploy, bounded API postflight, guarded old-249d restoration and refusal of unknown concurrent deployments. No Worker upload, routes, DNS, Rock64, secrets, PWA assets, .torrent download, Flud action or automatic retry.

**New staged E2E procedure, NOT EXECUTED:** `scripts/verify_magnetra_fix_zero_e2e.py` and `.github/workflows/verify-magnetra-fix-zero-e2e.yml` with explicit `RUN_READONLY_540B_FIX_E2E`, default `CANCEL`. Only after the exact 249d@100/540b@0 slot, verify exact staged binding names/types and deployment identity; GET `/app.js` with immutable Worker version override for `540b` and compare cryptographic digest against the reviewed source-controlled frontend, require ordinary production static asset to be *different* (fail closed if override not honored), check 46 provider IDs, one bounded `2026` search for only OxTorrent/Torrent9 on 540b, then one original canonical-details `/api/resolve` per source validating real BTIH while withholding hashes. No BTDigg/EZTV requests, no ad clicks, Flud, torrent download, token disclosure, network retry or Cloudflare writes. If assets cannot be definitively tied to 540b, **STOP, do not claim candidate frontend fixed**. After E2E PASS, production rollout will still need separate approval + independent postflight + actual iPhone acceptance; not authorized here.

**Security/operational status:** BTDigg intermittent RATE_LIMIT 429 remains a separate P0 and is not changed by 540b fix. Other 44 provider identities and gateway limits unchanged. Commit #89 already fixed PWA field selection for OxTorrent/Torrent9 only; active production 249d still has old Resolve bug until a separately authorized later traffic promotion. CI green does not imply live deploy.

## 2026-10-19 — Exact staged 540b Resolve E2E PASS; bounded owner-gated 5% canary PREPARED ONLY

**Authenticated read-only E2E PASS:** owner ran [Verify Magnetra 0 Percent Resolve Fix #39311804881](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39311804881) from `main` SHA `4d66b19feb9dcd55bc9ca9d1a541bdd26cbd4a10`. The actual live E2E (not fixture output) verified `STAGED_0_PERCENT_GATE: PASS (249d 100%, 540b 0%, all three bindings)`, `STAGED_APP_JS_ATTRIBUTION: PASS (540b matches reviewed fix; 249d differs)`, `STAGED_PROVIDER_CATALOG: PASS 46/46`, `STAGED_SOURCE_SEARCH_PASS: OxTorrent 50, Torrent9 20 original results`, `STAGED_RESOLVE_PASS_oxtorrent: valid genuine BTIH`, `STAGED_RESOLVE_PASS_torrent9: valid genuine BTIH`, `STAGED_FIX_E2E_GATE: PASS`. Note: fixture unit tests also wrote smaller synthetic 1+1 result counts into the same job log; authoritative 50+20 counts come from the final authenticated source step. No BTDigg/EZTV, torrent downloads, magnet printed, ads, Flud or traffic mutations. Previous owner-run slot [#39310908577](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39310908577) established the exact Cloudflare **249d@100% / 540b@0%** slot. Thus fix is loaded, bound, source-tested, and selectable with version override, but normal iPhone PWA still gets 249d and remains broken for OxTorrent/Torrent9 Resolve.

**Manual 5% canary and read-only post-canary E2E PREPARED, NOT YET AUTHORIZED OR EXECUTED:** `.github/workflows/magnetra-resolve-fix-canary-5.yml` and `scripts/deploy_magnetra_fix_canary_5.py`. Owner must separately choose `CONFIRM_FIX_540B_CANARY_5` (default `CANCEL`). Exact version IDs `249d6767-f4dc-4f4d-bbf7-f57bea2e5554` 95% and `540b3417-f845-47e8-96bd-856ccc9f1350` 5%; requires exact prior 100/0 slot, both gateway secret bindings and ASSETS, stable Cloudflare deployment ID and bounded API postflight. Unknown/concurrent versions fail closed; unexpected known split guarded restore to `249d@100,540b@0`. Manual `CONFIRM_RESTORE_249D_100` action provides rollback only from known split. No code/asset uploads, D1/DB changes, DNS, tunnel, Rock64, BTDigg requests, automatic magnet sends or provider substitutions.

**Canary source test PREPARED, NOT EXECUTED:** `.github/workflows/verify-magnetra-fix-canary-5-e2e.yml` with explicit owner choice `RUN_READONLY_FIX_540B_CANARY` (default `CANCEL`) only after owner has run the separate canary rollout. Confirms 95/5 deployment + exact secret names/types; requests original `/app.js` under immutable **540b override** and old `/app.js` under immutable **249d override** (never rely on random 95/5 distribution) and validates the staged SHA-256 equals the reviewed fixed PWA while old differs. Checks 46/46 original IDs; one bounded `2026` search on staged version for **only** OxTorrent/Torrent9 and one real original canonical-details `/api/resolve` per provider for valid BTIH, redacted. Checks deployment identity unchanged after. This does NOT authorize production promotion. Only after PASS + owner approval should a separate guarded 100% promotion be prepared, and iPhone real-world acceptance must still be confirmed.

**Open separate P0:** BTDigg iPhone `RATE_LIMIT` / HTTP 429 has NOT been fixed; do not modify 8796 gateway five-second minimum, source retry, DNS, tunnel or shared Rock64 services as a side effect of this Resolve rollout.

## 2026-10-19 ~23:00 Europe/Rome — CANONICAL CURRENT CHECKPOINT: 249d@95 / 540b@5, Resolve E2E PASS (owner-approved 5% canary)

**Authority and next-chat reminder:** This section is the newest verified deployment/release snapshot and **supersedes** all earlier chronological sections that still discuss 249d@100/540b@0, 249d@100/a9df@0, or a9df@100/249d@0. The old entries are retained as historical evidence. Repository `main` and current authenticated Cloudflare deployment records supersede even this snapshot if future actions have occurred. Owner requested full session checkpoint and complete Senior/Staff continuation prompt: [docs/MAGNETRA_MASTER_PROMPT_2026-10-19.md](MAGNETRA_MASTER_PROMPT_2026-10-19.md). Practical new-chat handoff is updated in `docs/NEXT_CHAT_HANDOFF.md`.

### Latest **real Cloudflare deployment** (no extrapolation)

- **Current immutable previous production version:** `249d6767-f4dc-4f4d-bbf7-f57bea2e5554` at exactly **95% ordinary traffic**, currently the safe rollback target. It was the previously 100%-promoted version and **still includes the iPhone PWA OxTorrent/Torrent9 card Resolve bug**.
- **Current immutable fixed version:** `540b3417-f845-47e8-96bd-856ccc9f1350` at exactly **5% ordinary traffic**, Worker/assets uploaded from reviewed source commit `c6867647c10bba33db0361178f3380a7ffa48385` after PR #89. Binding names/types were authenticated for this exact ID: `BTDIGG_GATEWAY_TOKEN`, `MAGNETRA_GATEWAY_TOKEN`, and `ASSETS`.
- Real Cloudflare **owner-triggered canary workflow** [run 39323736403](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39323736403), job `118304107246`, passed the owner approval gate, checked exact 249d@100 / 540b@0 preflight, and its **actual Cloudflare operation** logged `CANARY_POSTFLIGHT_PASS: old 249d 95%, fix 540b 5%`. Do not confuse simulated rollback/unapproved-path outputs from preliminary offline unit tests in the same job with a real rollback operation. The real final step confirms 95/5. **No rollback was executed on live deployment.**
- Separate **owner-triggered immutable-version canary E2E** [run 39324007635](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39324007635), job `118305033434`, finished SUCCESS. The real authenticated step logged `CANARY_METADATA_GATE: PASS (249d 95%, 540b 5%, 3 bindings)`, `EXACT_TWO_VERSION_APP_JS: PASS (fix matches GitHub, old differs)`, `STAGED_PROVIDER_CATALOG: PASS 46/46`, `STAGED_SOURCE_SEARCH_PASS: OxTorrent 50, Torrent9 20 original results`, `STAGED_RESOLVE_PASS_oxtorrent` and `STAGED_RESOLVE_PASS_torrent9`, with valid **redacted original BTIH magnets**, then `FIX_540B_CANARY_E2E: PASS`. The synthetic unit tests in this job logged a separate 1+1 fixture, **not** the live sample.
- Verification selected **BOTH versions explicitly** using Cloudflare `Cloudflare-Workers-Version-Overrides` to avoid drawing random conclusions from 95/5 sampling, and checked deployed static `app.js` bytes against reviewed `web/app.js`. It did not change Cloudflare traffic, invoke BTDigg/EZTV, download torrents, click ads, print tokens/magnets, or send magnets to Flud.
- Historical `a9df4429` (formerly older rollback at 0%) is **not in the current two-version split**, but was **not deleted**. The earlier `ce808b27` secret-only version must not be promoted. Preserve the current 249d version as an immediate 100%-restore target.
- **540b promotion to 100% has NOT been prepared, approved, or executed.** Current iPhone PWA user acceptance for the fixed Resolve flow is **NOT confirmed**. One ordinary iPhone retry can still reach 249d (95%) and fail; do not misclassify it as a 540b regression. No normal PWA deploy/reinstall is needed for source preparation; do not accidentally trigger `[deploy-pwa]`.

### Proven Resolve root cause and fix (not a BTDigg change)

- Owner screenshot after searching `2026` showed **70 authentic results** and `Noncanonical source HTML route refused` for the Resolve button on OxTorrent **and** Torrent9; independent UI BTDigg section reported `RATE_LIMIT` (HTTP 429).
- Authenticated source field audit [run 39286786842](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39286786842) proved original `details` URLs were canonical on OxTorrent **50/50** and Torrent9 **20/20**, but each card also had `magnetSource` `OTHER_PATH_TEMPLATE`, which legacy PWA selected first in **70/70**. The fixed original details URLs independently returned real BTIH through `/api/resolve`, showing the problem was **field precedence in frontend**, not the gateway allowlist, physical Rock64 tunnel or a need for advertising click-throughs.
- **PR #89** changed **only** `web/app.js` `ensureMagnet` selection for `oxtorrent` and `torrent9`: use source-owned `details` rather than noncanonical `magnetSource`; if `details` is absent, fail closed instead of selecting ad/download path. Keep all other **44** provider preferences and true magnets unchanged, no auto-send to Flud, no relaxation of HTTPS origin/path or redirect guards. Regression simulates 50 OxTorrent + 20 Torrent9 result cards and proves each `/api/resolve` request uses canonical original details.
- Verified staged upload [run 39298077357](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39298077357) created exact 540b ID without deploy. Binding audit [run 39303873161](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39303873161) passed all 3 binding types; safe 100/0 slot created in [run 39310908577](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39310908577); real zero-slot E2E [run 39311804881](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39311804881) confirmed matching source assets, 46 catalog IDs, 50+20 source results, one authentic magnet for each. Both zero-slot and canary owner-approved workflows completed; **do not repeat them unless current deployment evidence demands it**.

### Separate BTDigg P0: intermittent 429 RATE_LIMIT and historical 504 TIMEOUT

- On iPhone BTDigg reported `RATE_LIMIT` / HTTP 429 in this session. A single 429 does **not** establish whether the Rock64 8796 locally enforced its **5-second interval** or original `btdig.com` returned 429. Earlier BTDigg returned `BTDIGG_SOURCE_TIMEOUT` / HTTP 504 (~12 s) and later real results after ~one minute without any gateway code change. Historical controlled differential [run 39134428856](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39134428856) verified 10 original results under old and staged Worker for one query, but did not prove stable uptime.
- `rock64/btdigg_gateway.py`: `TIMEOUT_SECONDS=12`, `MIN_SEARCH_INTERVAL=5`, `CACHE_SECONDS=1200`, success-only RAM cache max 4 entries / 6 MB, singleflight, **no retry on 429/timeout**; loopback `127.0.0.1:8796`, HTTPS `btdigg-rock64.alexlab.media`. Worker `AbortSignal.timeout(16000)`, PWA `BTDIGG_MIN_GAP_MS=5500`. Keep BTDigg source attribution truthful. `RATE_LIMIT` vs `BTDIGG_SOURCE_TIMEOUT` vs `BTDIGG_TUNNEL_TIMEOUT` are different outcomes.
- No BTDigg fix or Rock64/DNS/tunnel/service update is included in 540b. **Physical origin for BTDigg intermittent failures still UNKNOWN.** The next diagnostic, only with separate owner approval, is `READ_ONLY_ROCK64_DNS_TCP_TLS_TTFB_BODY_TIMING`, sanitizing timings and services and making at most one bounded real original-source request. Never defeat 429 or silently use Bitmagnet/other indexers as BTDigg.

### Decision boundaries / next authorized work

1. **First in new chat:** reread latest `main`, `AGENTS.md`, `docs/PROJECT_STATE.md`, `config/project-invariants.json`, `docs/MAGNETRA_MASTER_PROMPT_2026-10-19.md`, then latest Cloudflare deployment runs. Verify expected **249d@95 / 540b@5**; any more recent real deployment overrides this recorded observation.
2. **Prepare, do not execute, a new manual-only guarded 100% release and 249d rollback for the *NEW* version pair**: from exact 249d@95 / 540b@5 to **249d@0 / 540b@100** only after separate explicit owner approval. Add `CANCEL` default, immutable version+three-binding/asset gates, deployment ID race checks, bounded API postflight, safe restore to 249d 100 only for known pair; offline negative-path tests. **Older release workflow for a9df/249d has hardcoded IDs and must not be reused.** Branch → PR → all four required CI PASS → merge, but no traffic modification from a PR merge.
3. After approval and real promotion, verify log postflight, version-specific/current `app.js`, catalog 46 IDs, OxTorrent/Torrent9 source-owned magnet resolution and iPhone Resolve acceptance (without Flud auto-send). Separate rollback action if regression occurs; no PR should silently deploy PWA assets or change `web/sw.js` without evidence.
4. **BTDigg 429 after release:** read-only source-vs-local cooldown diagnostics, no aggressive re-queries. Preserve other Rock64 shared services, ports, DNS, tunnel, resource stability and €0 cost.
5. **Catalog caution:** 46 registered IDs/adapter implementations are not 46 live-healthy sources; last historical complete production audit 13 October [run 38373699387](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/38373699387) measured 13 results / 12 empty-or-unverified / 21 errors. Preserve all provider IDs and source attribution. EZTV historically verified 29 genuine results + magnets on original gateway; no new E2E for EZTV/BTDigg during 540b canary.

### Non-negotiable engineering restrictions

- €0 unapproved costs; no paid API, Cloudflare upgrade, generic proxy, CAPTCHA bypass, token/secret disclosure, or automatic requests after 429.
- Preserve the original 46 providers; do not attribute other source results to BTDigg/OxTorrent/Torrent9. No fake magnet, download, Flud/Shield auto-submit or leakage.
- Rock64 shared ARM64 with BTDigg 8796, EZTV 8797, dispatcher 8798; no unauthorized DNS/tunnel/router/systemd/reboot/update/fstrim/VPN/microSD/other-service modification.
- No direct `main` changes; branch/PR/CI/merge. Changes to protected invariants must update code/config, this document, `docs/NEXT_CHAT_HANDOFF.md`, tests/checker together. Do not use `[deploy-pwa]` in commit message for docs-only checkpoint; expected PWA deployment workflow `skipped`.
- Full manual prompt: [`docs/MAGNETRA_MASTER_PROMPT_2026-10-19.md`](MAGNETRA_MASTER_PROMPT_2026-10-19.md). Proven from authenticated runs **#39323736403** and **#39324007635**, not from chat recollection.


## 2026-10-19 — 540b full production release workflow PREPARED ONLY (NO DEPLOY)

**New reviewed-code candidate:** `.github/workflows/magnetra-resolve-fix-full-100.yml`, `scripts/deploy_magnetra_fix_full_100.py` and `scripts/test_magnetra_fix_full_100.py` were prepared through `feat/magnetra-540b-manual-100-promotion` for branch→PR→four CI checks→merge. This is **not** an authorization or actual Cloudflare change. Last verified live split remains **249d@95% / 540b@5%**, canary [#39323736403](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39323736403) and exact immutable source E2E [#39324007635](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39324007635) both PASS; no new live 100% claim.

A future *separately authorized* manual `workflow_dispatch` choice `CONFIRM_PROMOTE_FIX_540B_100` (default `CANCEL`) will first check both immutable Worker version IDs, all three binding names/types on **both**, exact 95/5 deployment ID, explicit JS SHA-256 comparison for both version-overridden assets, full catalog **46 IDs**, and a single real `2026` OxTorrent/Torrent9 search with one original canonical-details BTIH resolution per provider, plus deployment stability immediately before the write. Only after all gates pass is **one** Wrangler version-only deploy allowed to `249d@0% / 540b@100%`, preserving previous 249d as a 0% rollback slot. A bounded API postflight checks immutable IDs/shares/new deployment ID and production JS/catalog. Unknown or concurrent third version refuses action; no speculative retries or automatic rollback on ambiguous outcomes.

The separate explicit `CONFIRM_RESTORE_249D_FROM_FIX_540B_100` action permits guarded rollback only from exact `249d@0% / 540b@100%` to `249d@100% / 540b@0%`. The **existing** 5% workflow handles rollback from current 95/5. Both operations remain unapproved and unexecuted; they must never be run merely because this PR merges. No source auto-retries, BTDigg/EZTV requests, Flud activity, .torrent download, DNS/tunnel/Rock64 changes or additional cost.

**Owner approval for 100% remains FALSE.** UI acceptance on the actual iPhone remains unverified. BTDigg intermittent HTTP 429 remains an independent P0, with rate-limit origin not yet isolated.


## 2026-10-20 00:56 Europe/Rome — CANONICAL NEWEST LIVE CHECKPOINT: 540b@100%, 249d@0%; public Resolve PASS

**This supersedes every earlier chronological snapshot that said 540b was 0%, 5%, unapproved or unexecuted.** These older entries are retained only as history. Repository source and the latest authenticated Cloudflare deployment always take precedence over a recorded snapshot.

- **Owner explicitly approved full 100% release** on 2026-10-20 Europe/Rome. Reviewed manual workflow `.github/workflows/magnetra-resolve-fix-full-100.yml` on `main` was dispatched with `CONFIRM_PROMOTE_FIX_540B_100`: [run #39337836125](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39337836125). Production code had been merged in PR #94 at `d819a54704df139e6a1a500b957ce22f97e3b8d5`, all four required PR+main CI checks PASS, and unrelated automatic PWA deploy was SKIPPED.
- **Real release preflight** authenticated original immutable assets and three required bindings for BOTH versions, source-owned catalog 46/46, genuine original `2026` search OxTorrent **50** and Torrent9 **20**, one valid redacted canonical-details BTIH Resolve per provider, and exact stable `249d@95% / 540b@5%` deployment. The manual version-only write then resulted in exact **`249d6767-f4dc-4f4d-bbf7-f57bea2e5554@0%`** (rollback slot) and **`540b3417-f845-47e8-96bd-856ccc9f1350@100%`** (production).
- **The first release job concluded FAILURE** at `PROMOTION_POSTFLIGHT_PUBLIC_ASSET_UNVERIFIED` after Cloudflare metadata confirmed the new split and catalog / version-override assets passed. **Do not misrepresent that workflow as SUCCESS.** No automated rollback or second deployment occurred. Public `/app.js` at that first instant differed from the reviewed fixed version; exact underlying cause was NOT proven.
- **Independent later LIVE, read-only diagnostic** [run #39338307381](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39338307381), job `118353253206`, ended **SUCCESS** at **2026-10-19 22:56 UTC / 2026-10-20 00:56 Rome**. Confirmed Cloudflare metadata `249d=0%, 540b=100%` with exactly TWO versions. Local reviewed `web/app.js`, immutable **540b override**, normal **public /app.js**, and cache-busted normal **public /app.js** all had equal SHA-256 prefix `6fe7ac5e60ab9f72` and 28,097 bytes; old **249d override** correctly differed (`80fead40b472e563`, 27,644 bytes). All four asset GETs succeeded; `CF-Cache-Status: HIT` for the observed edge. This proves later public asset correctness from the GitHub runner, consistent with temporary propagation/cache delay, but does NOT prove its physical origin or every global edge.
- **Live PUBLIC (without version override) provider E2E also PASS:** 46 unique original provider IDs, OxTorrent **50 unresolved canonical results** + one valid redacted public BTIH Resolve, Torrent9 **20 unresolved canonical results** + one valid redacted public BTIH Resolve. **No BTDigg/EZTV test**, torrent downloads, Flud transmission, paid service, generic proxy, additional traffic deployment, DNS or Rock64 change.
- **Source hardening:** `scripts/deploy_magnetra_fix_full_100.py` now tolerates only up to three brief repeated successful HTTP-200 **static** `/app.js` mismatches after deployment metadata confirmation; requires stable deployment identity/split, never retries a provider/429/504 or makes another version write. Offline tests cover bounded propagation success, permanent mismatch and deployment changes. A separate **manual read-only** workflow `.github/workflows/magnetra-public-postflight-diagnostic.yml` and `scripts/diagnose_magnetra_public_postflight.py` preserve non-mutating health/audit capability.
- **Remaining acceptance:** actual owner's iPhone UI Resolve tap after the 100% change is **not yet confirmed by user**; remote genuine API Resolve works for both. **BTDigg intermittent 429 / source timeout remains a separate unsolved P0**; preserve 8796 original-only provenance/rate limits and Rock64 resource isolation. The prior `249d` remains as a guarded **0% rollback version**; no live rollback performed. Do not suggest a second release after this verified result unless a new issue requires it.

**Next work:** verify actual owner iPhone PWA Resolve (OxTorrent/Torrent9) using ordinary `https://index.alexlab.media` after reload if needed; separately investigate BTDigg local-vs-upstream 429/timeouts with strict rate limiting and no unapproved service changes. All 46 adapter IDs are present, NOT 46 verified healthy sources.


## 2026-10-20 — iPhone full-search relevance P0: root cause and staged fix (NOT DEPLOYED)

**Owner evidence:** ordinary iPhone Magnetra PWA query `the good dinosaur 2015`, all 46 indexers selected, UI reported **345 raw results** and **19–21 indexer errors** during observed searches. Screenshots show original relevant `The Good Dinosaur (2015)` rows mixed with unrelated `Knock Knock 2015`, `The Hateful Eight 2015`, and `Good Luck Have Fun Don't Die 2026`; source labels include TorrentsCSV, Knaben, YTS and Torrent9. The owner is dissatisfied with irrelevant results; do not treat a high raw-result count as high-quality search relevance. These are user-observed screenshots, not a fresh complete production health audit or proof that any single provider purposely ignored the query. User also saw `Flud Companion · Unavailable`; physical pairing/Shield availability was not diagnosed as part of the relevance change.

**Verified root cause in `main`:** Worker `getSearch` directly concatenated all returned normalized provider rows into `results`, `stats[].count` and `total` **without title-to-query relevance verification**. UI then sorted/displayed all raw rows, favoring high reported seeder counts even when titles had no match. External provider search semantics can differ or fail, so backend cannot trust every returned row as relevant.

**Source-only code fix, NOT current production:** `worker/src/query-relevance.mjs` applies a bounded, local, deterministic Unicode/diacritic-insensitive **all significant query-title token** match to the already normalized, source-owned row names. A requested year (e.g., 2015) is required as a discrete token **in the release title**, not inferred from a torrent upload date. English articles `the/a/an/of` are optional only when substantive terms exist. Handles periods, underscores, parentheses, case and normal filename suffixes (1080p/x265/codec/group); exact IMDb IDs (`ttNNNNN`) and BTIH hash lookups bypass title matching as their names are different from query identifiers. Each of the original 46 provider adapters, magnets, details, source IDs, gateway URLs, access/redirect/429 protections and Flud handoff remain **unchanged**. There is no new network request, retry, page navigation, paid service or ad-route relaxation. This conservative default may omit translated/alias titles not sharing query words; future explicit user-opted broad mode should be evaluated separately if needed, never fake source attribution.

**Truthful response accounting:** filtered `results`, `total`, `stats[].count` and per-source `rawCount`/`excludedOffTopic`; aggregate `excludedOffTopic` distinguishes unwanted rows from real errors and zero matching results. PWA reports “MATCHES” instead of raw “RESULTS” and shows a small count of unrelated rows excluded while separately retaining original error panels and provider selection. No indexer is silently removed (46 IDs remain individually selectable). Regression tests use **literal unrelated screenshot titles**; positive movie and release-year fixtures, IMDb lookup, Unicode, HTTP 403 separation and mock end-to-end original Knaben/TorrentsCSV rows with unchanged BTIH/provenance. The production PWA continues showing old search semantics until a separate guarded **Worker version upload, E2E validation and owner-authorized production release**. **Do not merge or deploy without four CI groups PASS.** After release, verify exact user query on iPhone and compare meaningful matches and excluded counts; do not assert 345 genuinely matched titles.

**Separate unresolved issues:** BTDigg intermittently returns HTTP 429/timeouts; 46 selected != 46 healthy providers; EZTV exact show/IMDb query is not generic year search. This fix does NOT address these or Shield/Flud pairing. Previous verified 540b@100,249d@0 remains current until newer authenticated Cloudflare deployment evidence.


## 2026-10-20 ~17:44 Europe/Rome — NEWEST RELEVANCE FIX STAGED 136c; SOURCE E2E NOT YET ROUTABLE

**Supersedes any prior section stating that the PR #96 relevance fix was not yet uploaded.** The previous production `540b3417-f845-47e8-96bd-856ccc9f1350` is still **100% live traffic**, and old `249d6767-f4dc-4f4d-bbf7-f57bea2e5554` remains **0%** in the current two-version deployment. No change to source result filtering has reached ordinary iPhones yet. The source patch for screenshot-based false positives was merged at main commit `83e1659538e037a12f4bf8044d2cb52f89e72d7f`, PR #96, four main/PR CI groups PASS.

Owner triggered [Stage Magnetra Worker NO DEPLOY #39450609144](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39450609144), concluded **SUCCESS**, authentic Wrangler log identifies uploaded immutable Cloudflare Worker version **`136c1425-0070-48db-b995-5708bd35bb75`**, containing the new title/year relevance filter and revised PWA from reviewed main commit. Uploaded three new/changed static files; staged version contains the mandatory secret NAME bindings. This operation only uploaded a version/assets and did NOT move deployment traffic.

Independent authenticated **READ ONLY** [stage audit #39451169718](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39451169718) succeeded. Cloudflare API verified exact immutable 136c ID and three required binding **names/types** (`BTDIGG_GATEWAY_TOKEN`, `MAGNETRA_GATEWAY_TOKEN`, `ASSETS`); current deployment remains **540b@100%,249d@0%**, staged 136c absent from active deployment. The new asset version-specific override returned **NOT_MATCHED_OR_NOT_ROUTABLE** while 136c was not in the deployed pair, therefore *do not claim* real staged JS hash match nor real title query verification. These are two different gates; override eligibility must be established by exact 0% slot first.

**Next prepared, manual-only action (not executed/approved by code alone):** `.github/workflows/magnetra-relevance-136c-zero-slot.yml`, guarded `scripts/deploy_magnetra_relevance_136c_slot.py` and `scripts/test_magnetra_relevance_136c_slot.py`. The manual `CONFIRM_540B100_136C0_SLOT_AND_READONLY_E2E` (default `CANCEL`) may replace **249d@0%** with **136c@0%**, leaving **540b@100%** ordinary traffic unchanged, only from exact previously observed deployment ID and binding versions. No third version or unknown percentages allowed; fail closed on races, single pinned `wrangler versions deploy` write, bounded Cloudflare postflight, no retries after source/rate failures or speculative rollback. 249d immutable version remains stored but is no longer in deployed pair. On confirmed 0% slot, same manual run executes version-overridden immutable JS hash comparison with reviewed `web/app.js`, 46 provider catalog count and one fixed `the good dinosaur 2015` query against only *original* Knaben/TorrentsCSV (no BTDigg, EZTV, Rock64 changes). Strict query-title/year matches and `stats.rawCount/excludedOffTopic` coherence are validated; real source failures or zero positive rows are marked INCONCLUSIVE and never declared successful positive E2E. The slot remains 0% even when source proof inconclusive; a separate user-approved 100% promotion with 540b as rollback is needed later. CI must pass four groups before merge; merging code does not deploy.

Owner's earlier iPhone screenshot had 345 raw source rows, including off-topic films and 19–21 errors, when searching `the good dinosaur 2015`. Do not assert 345 real relevant hits or 46 healthy sources. Personal Flud Companion observed unavailable is separate and not fixed. Previous iPhone Resolve fix on 540b remains running.


## 2026-10-20 20:37 Rome — LATEST 136c@0% confirmed; two independent LIVE source title E2E PASS; bounded canary CODE ONLY

**Production is still exactly 540b@100% and relevance candidate 136c@0%.** The user's manual `Magnetra relevance 136c 0 percent and E2E` [run #39475416019](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39475416019) passed immutable versions and three required bindings for each, performed **one version-only Cloudflare write** and confirmed **540b100/136c0** from Cloudflare API, but the job finished **FAILURE** on immediate 136c `app.js` hash mismatch (`NEW_IMMUTABLE_PWA_ASSETS_DONT_MATCH_REVIEWED_SOURCE`). No further deploy or rollback occurred. Do not falsely report this original workflow SUCCESS or rerun the 0% slot action (it must refuse because starting pair changed).

**Independent authenticated read-only source confirmation from GitHub runner, no new deployment:** [run #39475837891](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39475837891), SUCCESS. Cloudflare versions exact 540b100/136c0; 136c immutable required binding names/types PASS. Reviewed `web/app.js`, 136c version override and cache-busted 136c version override all hash **`ca9c44f311aa00f0`** (prefix), 28,637 bytes. Production 540b override and default public file both hash **`6fe7ac5e60ab9f72`**, 28,097 bytes. This authenticates new source, real routing and unchanged public site, with prior mismatch resolved. Transient cache/propagation is plausible, not proven.

**First genuine version-overridden original-title E2E:** run #39475837891, fixed `the good dinosaur 2015` from **Knaben and TorrentsCSV**: **89 correctly matched source-owned release titles**, **1** excluded off-topic, **0** source errors; API response has genuine `rawCount` and `excludedOffTopic` schema and rejected no matching results. No BTDigg or EZTV, no ad URL resolution, no downloads or Flud. **Second read-only screenshot-provider E2E:** [run #39476148621](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39476148621), SUCCESS, same immutable assets and 540b/136c shares, exact user query from original **Torrent9, OxTorrent and YTS**: **4** strictly title-matched genuine results, **70** off-topic excluded, **0** source errors. This directly validates the user-reported problem for these original providers; it is **not** a 46-provider positive uptime claim. No source retry / 429 bypass / brute force / proxy. Counts differ by provider/date and are not a synthetic live total for all 46.

**Next staged code step, NOT deployed at the time of this entry:** `feat/relevance-136c-5-percent-canary` introduces a fail-closed manual `.github/workflows/magnetra-relevance-136c-canary-5.yml`, default `CANCEL`; choice `CONFIRM_RELEVANCE_136C_CANARY_5` sets exactly `540b@95%/136c@5%` after immutable two-version binding checks, exact existing slot, reviewed `app.js` SHA and stable deployment identity, one single pinned Wrangler version-only write and bounded metadata postflight. Choice `CONFIRM_RESTORE_540B100_136C0` restores exact 540b100/136c0 **only from the known 95/5 canary**, no automatic rollback on unknown/race/ambiguous CLI outcome. The prior 249d version remains stored but is no longer in the current deployment pair. Canaries have NOT been activated by branch/PR/merge, which must skip PWA deployment. Offline negative-path tests and canonical guards accompany the PR, requiring 4/4 CI green. After an owner-selected manual canary run, verify the live percentage, code hashes and actual iPhone title result UX before any 100% promotion. **A 136c full-100% promotion workflow has NOT yet been prepared.** Keep 540b as 95% or 100% rollback base.

**Remaining separate issues:** 19–21 external errors in owner 46-source iPhone screenshot were historical user-observed, not resolved by relevance filtering. BTDigg intermittent 429/timeouts unresolved; EZTV generic year search does not guarantee results; Flud Companion observed unavailable on iPhone is separate. No claims of fixed 46/46 live indexers. Latest source commit for stage is `83e1659538e037a12f4bf8044d2cb52f89e72d7f`, immutable 136c.


## 2026-10-20 21:30 Europe/Rome — CANONICAL LIVE relevance 136c@5%, old 540b@95%; full 100% release CODE PREPARED ONLY

**Live, owner-triggered Cloudflare deployment:** `540b3417-f845-47e8-96bd-856ccc9f1350@95%` (safe last-good) plus `136c1425-0070-48db-b995-5708bd35bb75@5%` (relevance title/year filter). Manual [5%-canary run #39482838883](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39482838883) successfully verified exact immutable Cloudflare version metadata and 3 bindings, source `app.js` hash `ca9c44f311aa00f0`, performed ONE version-only traffic write and observed `CANARY_POSTFLIGHT_PASS: 540b 95% / 136c 5%`. **This supersedes all preceding 136c@0% checkpoint observations** (those are historical).

**Independent real live, read-only post-canary audit** [run #39484084015](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39484084015), job `118839851001`, succeeded after the change: still 540b95/136c5; 136c immutable `app.js` matches reviewed `web/app.js` SHA prefix `ca9c44f311aa00f0`, authentic 46 original adapter IDs. Actual override-selected `the good dinosaur 2015` results from Knaben+TorrentsCSV: **89 matching, 1 excluded**, 0 errors; Torrent9+OxTorrent+YTS: **4 matching, 70 excluded**, 0 errors. No title failing all core tokens made it through these two source groups. **Not** 46 proven healthy indexes, not 100% rollout, and owner's ordinary iPhone screenshot acceptance of the NEW relevance UI still pending. BTDigg intermittent 429, EZTV exact-TV-show query and Flud Companion iPhone unavailable are separate issues. No BTDigg/EZTV requests, magnet downloads, Flud sends or Rock64 changes were performed.

**New full release code prepared but NOT dispatched or deployed:** branch `feat/relevance-136c-full-100-manual`, `.github/workflows/magnetra-relevance-136c-full-100.yml` manual only, default `CANCEL`, explicit owner choice `CONFIRM_RELEVANCE_136C_FULL_100` promotes only exact `540b95/136c5` -> `540b0/136c100` after immutable version ID/binding and reviewed JS SHA checks, real unmodified original-title search for Knaben/TorrentsCSV and Torrent9/OxTorrent/YTS, and stable Cloudflare deployment ID. Exactly ONE Wrangler version-only write, four bounded metadata reads, no retries after provider errors/429/504, postflight validates both IDs, source override and public JS with bounded polling ONLY for HTTP-200 static hash mismatches (temporary edge cache propagation), no speculative automatic rollback. Old 540b kept in exact 0%-share rollback slot. Separate manually dispatched choice `CONFIRM_RESTORE_540B_FROM_136C_FULL_100` performs guarded full rollback ONLY from exact `540b0/136c100` to `540b100/136c0`, with its own stable deployment-ID gate. No changing 249d, URLs, bindings, ads, protections, tunnel, secrets or infrastructure. This is NOT a claim of live 100% until separate authenticated workflow dispatch and postflight.

**CI gate:** Offline `scripts/test_magnetra_relevance_136c_full.py` covers canceled action (no API), wrong split or third ID, two authentic provider groups, SHA mismatch, one-write semantics, eventual metadata/asset propagation, live edge HTTP errors (no retry), concurrency and restore. `scripts/check-project-invariants.py` and `config/project-invariants.json` pin workflow manual-only and immutable IDs. Every PR requires technical invariants + Worker/PWA contracts + debug Android + staging Android PASS, merge cannot auto-deploy. After full release, explicitly verify ordinary public title query on iPhone; inspect Cloudflare 100/0 and PWA `app.js` hash. Earlier original 0% slot workflow failure must not be mislabeled success; two independent 0% and current 5% audits supersede immediate SHA mismatch without second deploy.


## 2026-10-20 22:55 Rome — 136c full 100% ATTEMPT ABORTED BEFORE WRITE; live split remains 540b95/136c5

This **supersedes** any outdated prose calling the relevance 100% release not yet dispatched, and must not be interpreted as a 100% release. Owner dispatched reviewed `CONFIRM_RELEVANCE_136C_FULL_100` from `main`, [run #39495655870](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39495655870), conclusion **FAILURE**. Preflight verified exact immutable 136c JS hash prefix `ca9c44f311aa00f0` and authentic Knaben/TorrentsCSV `the good dinosaur 2015` (**89 matching, 1 excluded, zero errors**). The **subsequent screenshot-source check aborted** before `RELEVANCE_FULL_APPLY_ONCE`: therefore **NO Cloudflare traffic write occurred** in that full promotion workflow. Offline mocked test output printed earlier in the same job must NEVER be mistaken for live promotion.

Independent owner-credential GitHub **READ ONLY** diagnosis [run #39496009852](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39496009852) proved exact **540b@95%,136c@5%, two versions**, and reproduced underlying failure with one request: original **Torrent9 TIMEOUT (0 results), OxTorrent TIMEOUT (0 results), YTS OK (4 genuine titles)**, no unrelated titles in the 4 returned, exactly 3 provider stats and 2 classified source errors. The diagnostic intentionally concluded FAILURE because old release gate demanded zero provider errors; the Cloudflare application, JS identity, and release-title filter were not implicated. No retry, provider bypass, torrent, Flud, Worker write or Rock64 changes. This is **an indexer-availability problem, not a demonstrated relevance-regression**. Previously two independent 136c live runs had real positive matches from all 5 providers and 70 unrelated results excluded; source uptime is volatile.

**New source-only corrective PR:** `fix/relevance-full-timeout-isolation` changes only the *release safety preflight*, not Worker or search ranking. The production candidate `136c` is immutable and unchanged. One original `torrent9,oxtorrent,ytsmx` API GET remains required; always verify exact stats identities, every count and exclusion, genuine provider provenance, year/title terms and at least one positive match. Permit only distinctly and truthfully attributed `code=TIMEOUT` provider errors, flagged `stats.ok=false` with zero rows/counts for the timed-out sources; **never treat these sources as healthy** and always print `SOURCE_AVAILABILITY_DEGRADED`. Unexpected HTTP errors/codes/429, unknown IDs, all sources timed out, off-topic rows, contradictory counts, unknown deployments or asset mismatch still STOP with no Cloudflare write. No additional source request or retry is added. Offline tests reproduce exactly Torrent9+OxTorrent TIMEOUT/YTS positive plus negative forged timeout, off-topic, all-timeout, wrong counts. Full release retains all other strict immutable/three bindings/old 95-5/single-write/stable-ID/metadata/public JS hash gates and separate known-state manual rollback. Merge only after the four CI groups PASS, then user may manually dispatch **same** 136c full workflow (only if live split remains exact 95/5). Neither this code merge nor the failing first attempt changes actual traffic.


## 2026-10-20 21:30 UTC — CANONICAL LATEST: relevance 136c@100% LIVE, 540b@0% retained as rollback

**This entry supersedes all older current-state statements claiming 136c@0%, 136c@5%, or 540b@95/100%. Older notes are historical evidence only.** The owner explicitly dispatched `CONFIRM_RELEVANCE_136C_FULL_100` from the reviewed `main` commit `4f12f36e62831f6eb78fc234a7ecd4731fb433f5` in [full release run #39500459736](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39500459736). The full release job concluded **SUCCESS**, not just offline tests. In the real owner-authenticated release step, immutable 136c `app.js` and bindings were confirmed; original Knaben/TorrentsCSV search `the good dinosaur 2015` yielded **89 matching, 1 excluded, 0 errors**, and original Torrent9/OxTorrent/YTS yielded **4 matching, 70 excluded, no provider timeout** in that particular preflight. The stable 540b95/136c5 version-only Wrangler traffic write executed once, then Cloudflare postflight returned `RELEVANCE_FULL_POSTFLIGHT_PASS: 136c100/540b0`. Unoverridden public `app.js` matched reviewed GitHub source SHA256 prefix `ca9c44f311aa00f0` (28,637 bytes). There was no source retry, automatic rollback, Worker upload, manual Flud call or Rock64 modification. **540b stays as immutable 0%-share separately guarded rollback candidate.** The earlier full attempt [#39495655870](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39495655870) FAILED before traffic change due to original Torrent9/OxTorrent TIMEOUT; PR #100 fixed only the release gate to distinguish truthfully attributed TIMEOUTs from relevance correctness, and its CI passed 4/4. Do NOT re-run 95/5 promotion now (its exact starting-state gate should refuse).

**Independent REAL post-promotion public acceptance** [run #39500843622](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39500843622), job `118897641900`, conclusion **SUCCESS**; used ordinary **unoverridden** `https://index.alexlab.media` endpoints and authenticated Cloudflare metadata read-only. Confirmed exactly TWO deployed immutable versions: `136c1425-0070-48db-b995-5708bd35bb75@100%` and `540b3417-f845-47e8-96bd-856ccc9f1350@0%`; both expected secret/asset binding names/types present. Public `/app.js` SHA256 prefix `ca9c44f311aa00f0`, 28,637 bytes exactly matched reviewed `web/app.js`, and unoverridden `/api/providers` returned **46 distinct original adapter IDs** (NOT 46 verified healthy providers). One original public request for `the good dinosaur 2015` across **Knaben, TorrentsCSV, Torrent9, OxTorrent, YTS** returned **93 release titles all passing `good`+`dinosaur`+`2015` title token matching, 71 source rows excluded off-topic, and 0 provider error objects**. Grounded per-source accepted result counts: Knaben **77**, TorrentsCSV **12**, Torrent9 **0**, OxTorrent **0**, YTS **4**. Both Torrent9 and OxTorrent **responded without a classified error** in this observation but yielded no relevant title; this does NOT prove stable availability or absence of earlier timeout/rate limiting. The independent checker also confirmed accurate counts/provenance and no concurrent deployment change.

**Owner iPhone real UI acceptance of the new full-traffic search remains PENDING**: user should reload `https://index.alexlab.media` and search `the good dinosaur 2015` with original providers. Expected: only title- and year-matching rows and a separate count of excluded source rows; do not claim a fixed number of results on a later independent query. Provider error counts still reflect real HTTP timeouts/429/403, not unrelated titles, and Flud Companion availability is a separate issue. BTDigg intermittent 429, EZTV TV-title/IMDb semantics and 19–21 user-screenshot source failures remain to be investigated without generic proxies/retry loops, without altering 46 provider identities or Rock64 sensitive services. **Do NOT confuse accurate result relevance with all-source uptime.**

To preserve this independently reproducible release acceptance, source-only follow-up adds `scripts/verify_relevance_136c_full_public_readonly.py` and manually dispatched `.github/workflows/verify-relevance-136c-full-public-readonly.yml`. Both are GET/read-only and fail closed if the live split changes or an irrelevant title leaks; no automation/Cloudflare write, no retries of provider queries or torrent transmission. This is checked by canonical `config/project-invariants.json` and `scripts/check-project-invariants.py`. Follow branch→PR→all 4 CI→merge; **checkpoint merge never deploys Cloudflare traffic**. Latest code digest and live share must continue to be verified instead of relying solely on this historical observation.


## 2026-10-21 — P0 UX: OWNER RELEVANCE ACCEPTED, auto-pause failing indexers prepared (SOURCE ONLY)

**Owner accepted the live relevance fix on actual iPhone, not merely CI:** site `index.alexlab.media`, search `the good dinosaur 2015`, screenshot showed **182 MATCHES**, **163 unrelated source results excluded** and **18 indexers unavailable**. The owner explicitly prefers minimal manual intervention and said that if inaccessible sources cannot be repaired easily, only working sources should be kept. Note the screenshot is one time/one user query; 18 is not a universal immutable number, and zero matches for a given title does NOT establish source failure. Actual previous production remains immutable `136c1425-0070-48db-b995-5708bd35bb75@100%`, `540b3417-f845-47e8-96bd-856ccc9f1350@0%` until new authenticated Cloudflare evidence. The user's phone has already confirmed the source-filter UI `MATCHES` and correct top relevant titles, superseding older checkpoints that said acceptance pending.

**Root cause of repeated indexer errors in UI:** all 46 authentic adapters are intentionally selectable and previously saved `magnetra.providers.v1` browser selection persists; after an error, the previous `web/app.js` displayed a real warning but did not automatically exclude that failing provider from subsequent user searches. Blocking/redirected/upstream/rate-limited source sites cannot responsibly be repaired by generic proxying, changing origins, CAPTCHA or rate-limit bypass; further forced retries would worsen 429/timeout and cost latency. Existing `Select last-audit results` is based on a dated 2026-10-13 sample and is **not** reliable live status; previous 'Search with available indexers' had a hardcoded fallback that could reselect a failing source.

**Minimal reversible PWA solution, SOURCE ONLY until safely released:** `fix/magnetra-auto-pause-unavailable-indexers`. At the end of each **fully completed, non-cancelled** search, use ONLY `data.errors[]` and network exceptions already observed in this browser for the exact selected sources. Auto-uncheck sources with genuine failures for the **next** user search, persist the remaining source IDs in existing `magnetra.providers.v1`, and separately persist names of paused source IDs in `magnetra.paused-indexers.v1`. An accessible compact banner below the provider selector explains how many were paused. No fresh provider health requests, no auto retry, no background polling, no removal from original 46-source Worker catalog. An HTTP success with **zero matching titles remains selected**, because nonmatching title is not an outage; keyword-relevance exclusions are NOT counted as provider errors. If **all** searched sources failed, leave selection untouched rather than empty every source. Existing manual source checkbox, `Select all 46` and last-audit results selection can reactivate a paused source with one tap. "Search with available indexers" now prioritizes successful results or clean zero-result responses observed **in the current browser session**, falling back only to a short conservative stable-source list if no recent source evidence. No changes to BTIH magnets, Resolve, BTDigg 5.5s pacing, originals, Flud Companion, secrets, Cloudflare URLs or Rock64. Selection is a per-browser convenience, **not** a verified 46-provider health guarantee or a permanent deletion. Human may still select all and manually retry when desired; keep total original identities.

**Testing and minimum-intervention deployment:** Node/VM UI regression `worker/test/auto-pause-indexers.test.mjs` ensures one failed source gets paused while zero-result source stays active, metadata persists across reload, 46-source registry intact, no all-off when all unavailable, user reselect, no changes to bookmarks/pairing and cancelled searches aren't pruned. Protected config/checker pins explicit failure-only, no-extra-query and reversible behavior. A special manual-only, default-`CANCEL` release workflow `.github/workflows/magnetra-auto-pause-single-action.yml` allows **one owner GitHub dispatch** `CONFIRM_AUTO_PAUSE_SINGLE_ACTION_RELEASE`: preflight exact existing `136c100/540b0`, upload a new immutable Worker version with **existing required secret names and assets binding**, use one guarded Cloudflare versions deployment to `136c100/new0`, validate real immutable PWA `/app.js`, `/styles.css` and `/index.html` against reviewed source via version override (bounded cache propagation for successful HTTP 200 only), and only then perform guarded `136c0/new100`. Public three-asset SHA postflight and stable Cloudflare metadata are mandatory; old 136c remains at 0% as manual rollback. No provider-probing search in the release, no HTTP error retry, no automatic rollback on ambiguous states. Manual option `CONFIRM_AUTO_PAUSE_MANUAL_RESTORE` requires the exact new version ID and verified 136c0/new100 state to restore 136c100/new0, never blindly. Does not use unsafe older immediate Worker redeploy workflows. A source PR merge alone is **not** a Cloudflare deploy, and four CI groups must pass before merging. Latest live source state should be verified after any future release; this paragraph does NOT claim the auto-pause feature already live.

**Separate future work:** 18 unavailable in owner screenshot should not result in mass destructive deletion or unverifiable “fixed” statuses; if the user still wants a permanent strict whitelist, it can be derived only from multiple successful searches with authentic source evidence. BTDigg intermittent 429 remains rate-limited, EZTV year-only queries are semantically different, and Flud Companion status is a separate issue.


## 2026-10-20 23:05 UTC — Auto-pause immutable c86c at 0%; old relevance 136c at 100%; SAFE RESUME PREPARED, NOT EXECUTED

Owner launched reviewed one-action `Magnetra Auto-Pause One-Action Safe Release` [run #39510888059](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39510888059). Its offline code/invariants/Worker tests, origin/bindings, and Cloudflare candidate upload succeeded. **Actual newly uploaded immutable Worker version** `c86c9a32-31fd-4952-86ed-b35f1763b342` (shorthand c86c), with verified `BTDIGG_GATEWAY_TOKEN`, `MAGNETRA_GATEWAY_TOKEN`, and `ASSETS` binding names/types. Workflow executed ONE guarded version-only deployment `136c1425-0070-48db-b995-5708bd35bb75@100%` and `c86c9a32-31fd-4952-86ed-b35f1763b342@0%`. It verified exact new source `/app.js` SHA256 prefix `9998e0130b19ece9` and `/styles.css` prefix `1c7080d499b00207`, but **ended FAILURE** before attempting new@100% at HTML verification. **Cloudflare 136c remains 100% live, c86c 0%**; older 540b immutable remains stored but is no longer in the active two-version split. Do not rerun the original one-action upload workflow; its exact old 136c100/540b0 preflight should refuse after the slot changed, and fresh uploads would be unnecessary.

**Authenticated one-shot diagnostic of root cause, with no traffic writes:** [run #39511274282](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39511274282) confirmed 136c100/c86c0, 3 bindings each, and that Cloudflare responds to `/index.html` with **HTTP 307 redirect to `/`**. Fresh, version-overridden `/` served HTML from c86c (new `sourceHealthSummary` ID present), but source byte SHA differs due Cloudflare analytics injection near `</body>`. Previous release wrongly expected direct HTTP-200 `/index.html` and byte-for-byte `web/index.html`, and aborted harmlessly without enabling new traffic. Follow-up independent [strict HTML diagnostic #39511936377](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39511936377) **SUCCESS** verified exact reviewed HTML (9,264 source bytes; SHA256 prefix `6e6e2ca3388a5ce7`) modulo **ONLY** a bounded late HTML insertion containing specific Cloudflare Insights `static.cloudflareinsights.com/beacon.min.js`, `data-cf-beacon`, `/cdn-cgi/`, and script-only markup; it printed `STRICT_CLOUDFLARE_HTML_SOURCE_GATE: EXACT_PLUS_CLOUDFLARE_BEACON`. This is stronger than ignoring arbitrary HTML mismatches, and no CDN/source secrets or dynamic tokens were logged. The public root and old 136c root showed normal similar instrumentation. Do NOT claim the original failed job was success or that c86c is currently serving general user traffic.

**Minimal next step without re-upload:** source-only branch `fix/magnetra-auto-pause-resume-c86c` introduces strict safe HTML checker `scripts/cloudflare_html_asset_guard.py` and manual default-CANCEL `.github/workflows/magnetra-auto-pause-resume-c86c.yml` with explicit owner action `CONFIRM_RESUME_VERIFIED_C86C_100`. The script `scripts/resume_magnetra_auto_pause_c86c.py` requires unchanged exact slot `136c100/c86c0`, both immutable versions and 3 bindings each, original reviewed static JS/CSS SHA through **c86c version override**, and strict HTML source equivalence with the Cloudflare beacon on the correct **`/` path**. It then performs a **SINGLE** version-only write `136c0/c86c100`, keeps old relevance 136c@0 as immediate known rollback, and verifies same static files via normal public GETs with bounded polling **only after HTTP-200 old-hash responses**; never retries 429/504 or provider traffic. Separate `CONFIRM_RESTORE_136C_FROM_C86C_100` is owner-manual, exact known state only, restoring 136c100/c86c0 with one write. Neither action uploads another version; no worker/parser/source search/BTIH/Flud/Rock64 change. Offline negative-path Python suite `scripts/test_magnetra_auto_pause_resume.py` verifies unknown HTML injection rejected, exact one write, manual cancellation, wrong split and safe restore; four mandatory PR CI checks before merge. The source code that automatically pauses provider errors after completed iPhone searches is already embedded in immutable c86c; **owner acceptance after eventual full release still pending**.

**Production quality goal unchanged:** keep only sources that answered without real errors in the last completed browser search; don't treat a clean zero title match as outage; if all sources fail leave selection nonempty, preserve original 46 names and manual re-enable, no extra health probes, no paid tools or retries. Previously user confirmed 136c title relevance on iPhone, screenshot 182 MATCHES, 163 unrelated excluded, 18 external source errors. Source uptime and BTDigg 429 remain separate.


## LATEST CANONICAL — 2026-10-20 23:41 UTC / 2026-10-21 01:41 CEST — c86c AUTO-PAUSE LIVE 100%; 136c safe rollback 0%

**The newest real Cloudflare deployment, as confirmed by owner-dispatched authenticated [run #39516593949](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39516593949), is exactly `c86c9a32-31fd-4952-86ed-b35f1763b342@100%` and `136c1425-0070-48db-b995-5708bd35bb75@0%`.** Workflow `Magnetra Resume Verified Auto-Pause c86c 100% (MANUAL)` conclusion **SUCCESS**, real live run step (not mocked tests) logged `RESUME_PREFLIGHT`, `REVIEWED_ASSET_PASS:/app.js sha=9998e0130b19ece9`, `REVIEWED_ASSET_PASS:/styles.css sha=1c7080d499b00207`, `REVIEWED_HTML_PASS: EXACT_PLUS_CLOUDFLARE_BEACON source_sha=6e6e2ca3388a5ce7`, `RESUME_TRAFFIC_WRITE_ONCE: 136c0/c86c100`, and final public postflight `RESUME_FULL_POSTFLIGHT_PASS: c86c100/136c0`, including immutable three-binding checks for both versions and stable Cloudflare deployment metadata. No new upload after initial c86c@0% stage and no provider/Flud/Rock64 call. Keep original 136c immutable @0% for **manual known-state rollback** through `.github/workflows/magnetra-auto-pause-resume-c86c.yml` with `CONFIRM_RESTORE_136C_FROM_C86C_100`, only if real deployment still equals exact c86c100/136c0. Do NOT rerun obsolete `magnetra-auto-pause-single-action.yml` (it uploaded then failed on /index.html HTTP 307/Cloudflare beacon) or resume promotion workflow again now.

**User-facing c86c behavior verified in offline regressions and served public assets, but not yet accepted in ordinary iPhone browser:** after one fully completed, not-aborted query, PWA uses existing genuine provider error/transport list to deselect failing source IDs from *future* searches only. It persists remaining selected source IDs in `magnetra.providers.v1` and paused source IDs in `magnetra.paused-indexers.v1`, displays the paused count, preserves clean zero-title-result providers and refuses to clear every selected source if all fail. Users can reenable previously disabled sources manually or choose all 46. No 429/504 retry, new background probes, source deletion, router/tunnel/secret changes, torrent manipulation or Flud send. **This is a client/browser state change that takes effect only after the next completed search in that browser**; historical 18 unavailable screenshot was from older 136c app and may change. Indexer availability is independent from title relevance, BTDigg rate limits, EZTV matching and companion pairing.

**Owner's next minimal acceptance:** open `https://index.alexlab.media` on iPhone, perform one completed search with current selected providers, note current `Indexers N/46`, whether banner shows failed sources paused, then perform another search; count should reflect remaining working sources. There is no required count like 18 because responses change. Confirm accuracy of matching results and whether the zero-match providers remain enabled. New release is confirmed active; owner iPhone interaction is the sole remaining acceptance, not a prerequisite for claiming Cloudflare 100%.


## 2026-10-21 06:21+02 — BTDigg transport patch: original source IPv4 verified, Rock64 install PENDING

Owner explicitly requested a concrete fix for BTDigg without further repeated diagnostics. This session's prior owner screenshots showed `BTDIGG_SOURCE_TIMEOUT`, and their direct isolated Rock64 measurements were:
- `journalctl -u magnetra-btdigg.service`: two upstream transport errors `total_ms=12852`, `12753` with no HTTP headers received, and one genuine upstream success `total_ms=5734, open_ms=5654, read_ms=80`.
- Standalone original `btdig.com/search?q=ubuntu` curl request had HTTP 200, total **1.134972s**, DNS 0.547974, TCP 0.601254 cumulative, TLS 0.892791 cumulative, first response 1.055795. One Python DNS/TCP sample reported DNS 0.164s, IPv4 TCP 0.056s, IPv6 immediate error, order IPv4 then IPv6. **IPv6 failure does not prove the root cause:** TCP/SSL/HTTP/remote transient stall remains to distinguish; no claim of permanent repair yet.
- Earlier read-only one-shot public production GitHub workflow run `39529234338`: `c86c100/136c0` and genuine BTDigg public success 7 relevance matches, 10 source rows, 0 errors, 6465ms. No 429 retry attempted.

**Code patch SOURCE ONLY:** `fix/btdigg-rock64-bounded-ipv4-http-transport` changes only `rock64/btdigg_gateway.py`, offline tests and invariants/docs. Replaces generic Python urllib HTTPS fetch with a **single** IPv4 TCP connection to first DNS answer for `btdig.com:443`, `ssl.create_default_context()` verified CA/SNI, ALPN HTTP/1.1, `http.client.HTTPConnection` over pre-established TLS. All standard library, no IP hopping, no insecure TLS or challenge bypass, no extra requests or retry, no global IPv6/DNS setting or new Worker/Flud/API change. Keep existing overall 12s budget and explicit per-stage caps (TCP3, TLS3, HTTP6), preserve 429 and fail closed for non-200; bounded HTML size and source-owned `one_result` cache policy unchanged. Sanitized `dns_ms/tcp_ms/tls_ms/open_ms/read_ms/failure` gives actionable future evidence while avoiding query, URL, IP, magnet, auth and exception text.

The existing guarded update script `rock64/update-btdigg.sh` already backs up/reverts only this gateway and restarts/health-checks only `magnetra-btdigg.service`, not cloudflared/other services. CI tests run offline; **merging PR does NOT install any update on the physical Rock64**. Install only using a pinned, reviewed GitHub main checkout after 4/4 CI and PR merge. User will need one terminal action for single-service installation. If BTDigg was paused in their iPhone browser after a timeout, manually re-enable this one indexer in Indexers; this is client state, not a Worker bug. Real iPhone source uptime acceptance remains pending and intermittent source network policy cannot be guaranteed.


## LATEST 2026-10-21 13:13 CEST — PR #105 MERGED, CI green; BTDigg Rock64 physical install NOT YET VERIFIED

**AUTHORITATIVE:** Real repository main coding baseline **9c3930f406078ee744e0473b2093ded9b91cead7**, BTDigg source patch [PR #105](https://github.com/Zuzuitu/AlexLab-Magnetra/pull/105) MERGED. Four PR jobs succeeded (Technical memory invariants #39544804247, PWA and provider contracts #39544804225, Android debug #39544804277, Android staging #39544804248). Post-merge: technical invariants #39545284573 PASS; PWA/provider contracts #39545284466 PASS; Production PWA smoke #39545284514 PASS; Build debug APK #39545284517 PASS; Build staging APK #39545284411 PASS. Cloudflare Deploy Magnetra PWA #39545284540 **SKIPPED**, so no Worker traffic/asset change was made by this code-only PR. Later documentation-only merges may advance main while the tested BTDigg code commit remains immutable 9c3930.

**Production PWA authoritative last verified:** index.alexlab.media, Cloudflare Worker alexlab-magnetra: c86c9a32-31fd-4952-86ed-b35f1763b342@100% with manual rollback version 136c1425-0070-48db-b995-5708bd35bb75@0%. This deployment succeeded in real authenticated run #39516593949. Current c86c PWA filters off-topic rows, preserves 46 authentic source identities and automatically deselects genuine source errors *after a completed search* for future searches on that browser, while preserving successful-but-zero-result sources and manual reactivation. Previous error accordion can still show errors from the previous completed search; do not conflate that with the next search's current selection. No new Worker deploy needed for BTDigg Python patch. The user wants few interventions and only sources that actually work; don't permanently delete original 46 IDs.

**Original BTDigg failures and observations:** On physical Rock64, gateway journal recorded two ~12.8s transport failures before HTTP response headers (12852ms/12753ms, open/read null) and success 5734ms (open 5654ms, read 80ms). Direct original btdig.com curl yielded HTTP 200 total 1.135s, with IPv4 TCP fast, TLS fast. Python DNS output IPv4 then IPv6: IPv4 TCP 56ms success, IPv6 immediate OSError. An independent production search of original BTDigg [#39529234338](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39529234338) gave 10 real source rows / 7 relevant BTIH results in 6465ms, no errors. Thus upstream BTDigg is intermittent; IPv6 unreachable is a data point, not proven root cause. Rate limiting/challenge remains genuine, never circumvent.

**PR #105 CODE IMPLEMENTED, NOT PHYSICALLY INSTALLED/PROVEN:** Only rock64/btdigg_gateway.py upstream fetch was modified: one IPv4 socket to fixed original btdig.com:443 with ssl.create_default_context(), CA verification, correct SNI, ALPN http/1.1, one GET over verified TLS, no redirect or retries, remaining-budget checks on per-phase TCP 3s / TLS 3s / HTTP I/O 6s, original 12s target unchanged, no open proxy/IP hopping or source forgery, no changes to bearer, tunnel, 8797/8798, global router/DNS/IPv6, Flud, Plex, NexaPanel, YouTube or CalciDatum. Sanitized diagnostics include dns_ms, tcp_ms, tls_ms, open_ms, read_ms, failure category, family. Unit tests mock original socket/TLS/HTTP interface, source allowlist, 429/3xx challenge behavior, bounded response/caching and privacy. This improvement must still be validated against actual physical Rock64 failures; stage caps do not by themselves guarantee DNS getaddrinfo or repeated blocked socket ops will never exceed an absolute 12-second wall-clock total. Do not assert permanently fixed.

**Immediate handoff:** User was previously given a GitHub clone main+exact SHA install command, but after docs-only commits main can advance, making it fail before touching the host. Prefer the PINNED immutable SHA fetch command in docs/MAGNETRA_MASTER_PROMPT_2026-10-21.md section 3, then sudo bash rock64/update-btdigg.sh from that exact detached checkout. Updater is protected: one gateway file backup, Python test suite, only magnetra-btdigg.service restart, authenticated localhost /healthz, automatic previous-file rollback if failed, no token/Tunnel/other services edit. ***There has been NO user terminal confirmation from executing it.*** Physical installation and actual postinstall BTDigg query are pending, and the user requested a new-chat handoff at this point. In the next chat **first** determine whether this installation has already run before proposing another command. If source remains BTDigg auto-paused in iPhone browser, explicitly check BTDigg again in Indexers. Real successful user iPhone validation of new transport and automatic indexer retention still pending.

**Complete copyable handoff** is now in docs/MAGNETRA_MASTER_PROMPT_2026-10-21.md; top of docs/NEXT_CHAT_HANDOFF.md is authoritative. Older historical checkpoint lines (some implying the 2026-10-19 master prompt or 95/5 deployment is current) are preserved for audit, NOT current action.



## LATEST CANONICAL CHECKPOINT — 2026-10-21 ~13:13 CEST — Magnetra senior handoff; PR105 merged, physical BTDigg install UNKNOWN

**Canonical full replacement/new-chat instructions:** \`docs/MAGNETRA_MASTER_PROMPT_2026-10-21.md\`; read the NEW FIRST section of \`docs/NEXT_CHAT_HANDOFF.md\`. Historical states below/earlier are archived chronology, **not present deployment instructions**.

**Repository confirmed LIVE at audit:** \`Zuzuitu/AlexLab-Magnetra\` main \`9c3930f406078ee744e0473b2093ded9b91cead7\` (PR #105 MERGED). After-merge: invariants workflow #39545284573 PASS, PWA/provider #39545284466 PASS, public smoke #39545284514 PASS, Android debug #39545284517 PASS, Android staging #39545284411 PASS; automatic PWA deploy #39545284540 SKIPPED intentionally. A documentation-only merge of this checkpoint advances main commit without changing the tested BTDigg application baseline; install physical source from immutable \`9c3930f406078ee744e0473b2093ded9b91cead7\` rather than assuming HEAD/main equals it.

**Cloudflare PWA latest verified (real authenticated release, not inferred from GitHub):** \`c86c9a32-31fd-4952-86ed-b35f1763b342\` **100%**, \`136c1425-0070-48db-b995-5708bd35bb75\` **0%** fallback; run #39516593949 successful. Source-only PR #105 and this documentation-only checkpoint do NOT create any new production Worker deployment. PWA real-result search relevance live. Authentic 46 original provider IDs **retained**, but only responsive sources stay selected after a finished browser search with auto-pause. A clean source 0-match response is **not** failure. Auto-paused IDs persist per browser and can be manually rechecked; prior "18 indexers unavailable" reflects one particular finished query's failure report, not a permanent catalog pruning. Do not push old release workflows or mass-enable blocked 403/429 providers. Browser acceptance of two-search auto-pause behavior after c86c100 is only partially established; no user iPhone retest confirmed across consecutive searches.

**P0 BTDigg evidence:** original upstream \`btdig.com\` accessible sometimes, failing intermittently. Rock64 BTDigg old gateway systemd timing events: total=12852ms and 12753ms, \`failure=transport\`, \`open_ms=read_ms=null\`; successful old request total=5734ms, open=5654ms, read=80ms. Direct original Curl on Rock64 HTTP 200 total 1.134972s, cumulative DNS=.547974, TCP=.601254, TLS=.892791, TTFB=1.055795. Distinct Python socket check DNS=.164s, IPv4 connect=.056s, IPv6 immediate OSError, DNS order IPv4 then IPv6. Do NOT assert IPv6 caused old 12s stall. GitHub original BTDigg public one-shot #39529234338: HTTP 200 in 6465ms, 10 source raw rows, 7 relevant genuine BTIH magnets, zero errors. Thus source intermittently responds, no reason for permanent deletion.

**Source-only Rock64 patch #105 MERGED and 4/4 CI PASS:** updated \`rock64/btdigg_gateway.py\` uses a single IPv4 TCP socket first DNS A record to original \`btdig.com:443\`, CA verified TLS/SNI and ALPN HTTP/1.1, single fixed-origin HTTP GET with no redirect/retry and source 429 respected. Original 12s target, TCP3/TLS3/HTTP6 bounded stage ceilings, 3MB size, real-result bounded success-only RAM cache, 5s minimum source gap, bearer-authenticated loopback gateway and tunnel unchanged. Diagnostic logs now segment DNS/TCP/TLS/HTTP header/body latency and safe failure class. Unit tests/invariants pass. **CODE IN GITHUB != RUNNING CODE ON ROCK64.** As of this handoff, the owner has **not supplied the physical terminal installer output**. Record local installation as \`UNCONFIRMED\`, not successful. Per-stage socket timeout checks do not mathematically guarantee total absolute wall-clock when DNS itself stalls; classify from postinstall evidence if recurring.

**NEXT IMMEDIATE ONLY ONE OWNER ACTION:** First find out whether owner already ran \`rock64/update-btdigg.sh\` against the tested commit. If not, give pinned immutable checkout command, NOT \`git clone main; assert SHA\` because main may have advanced due these docs. Command details are embedded in \`docs/MAGNETRA_MASTER_PROMPT_2026-10-21.md\` and should download the known \`9c3930f...\` immutable commit, verify rev-parse and run \`sudo bash "$T/repo/rock64/update-btdigg.sh"\`. Installer runs local test suite, checks ONLY BTDigg ownership, stages backup and restarts ONLY \`magnetra-btdigg.service\`, performs authenticated loopback \`/healthz\`, tries restore on failure. No service alteration besides this gateway, no secret printing, no Cloudflare change, no Flud send. If owner did install, ask for sanitized actual stdout/stderr and verify; no duplicate blind installation.

**After validated install:** one normal source search or one \`check-btdigg.py\` test, never retry 429/504 automatically, verify a genuine BTDigg result and that stage fields \`dns_ms/tcp_ms/tls_ms/family\` appear in physical journal; if it still fails, read one phase classification before any change. Owner must manually re-check BTDigg on iPhone if auto-paused. Then minimal iPhone acceptance of stable source selection, error accordion and real resolve/Flud only where naturally needed. No app or router changes until a separate evidenced need.

**Safety/owner decision:** no costs, no open proxy, no CAPTCHA/429 bypass, no unsafe concurrent versions/deploys, no erasing original 46 adapter code, no invented torrents/magnets, no secret leakage, no changes to Plex/YouTube/NexaPanel/CalciDatum/Cloudflare Tunnel/firewall/NextDNS. Prefer one surgical code fix + offline tests + verified physical outcome + rollback, not endless diagnostics.

**Files:** \`docs/MAGNETRA_MASTER_PROMPT_2026-10-21.md\`, \`docs/NEXT_CHAT_HANDOFF.md\`, \`docs/PROJECT_STATE.md\`, \`config/project-invariants.json\`, \`scripts/check-project-invariants.py\`; current application implementation \`rock64/btdigg_gateway.py\`, \`rock64/update-btdigg.sh\`, \`worker/src/btdigg-rock64.mjs\`, \`web/app.js\`.



## LATEST RUNTIME UPDATE 21 OCTOMBRIE 2026 — CONFIRMAT PRIN SSH: BTDigg Rock64 PATCH INSTALAT

**Instalat pe Rock64: CONFIRMAT.** Proprietarul a executat updaterul `rock64/update-btdigg.sh` din checkout-ul imutabil `9c3930f406078ee744e0473b2093ded9b91cead7` și a furnizat outputul terminalului: `Ran 99 tests in 11.187s — OK`; `PASS: Magnetra gateway responded to authenticated localhost health check.`; `PASS: Magnetra gateway upgraded; existing tunnel and secrets untouched.` Instalarea fizică și pornirea/health local sunt astfel dovedite; NU repeta updaterul.

**Distincție critică:** Nu există încă o căutare reală post-instalare în BTDigg și nici loguri noi DNS/TCP/TLS din procesul actual. Nu declara disponibilitate stabilă sau timeout rezolvat permanent. Următorul pas P0: pe iPhone la https://index.alexlab.media, reactivează *numai BTDigg* în Indexers dacă a fost auto-paused; fă o singură căutare normală până la final și observă rezultatele/erorile BTDigg. Fără loop de retry 429/504. Dacă persistă eroarea, citește o singură intrare sanitizată `btdigg_upstream_timing` din jurnalul dedicat și clasifică faza. P1: confirmă apoi că după o căutare completă indexerele cu erori rămân deselectate la a doua căutare. Nu confunda bannerul de erori al primei căutări cu lista activă pentru a doua.

**Restul neschimbat:** Worker Cloudflare c86c@100% / 136c@0% (ultima confirmare reală run #39516593949), 46 de adaptere originale păstrate, Flud manual și neconfirmat E2E, fără alte redeploy-uri/proiecte/tuneluri/tokenuri modificate. PR #105 și #106 MERGED. Secțiunile istorice cu „instalare neconfirmată” de mai jos descriu starea ÎNAINTE de acest output SSH și sunt depășite.

---



## LATEST VERIFIED RUNTIME 21 OCTOMBRIE 2026 — BTDigg ORIGINAL: ROCK64 LOCAL HTTP 200 CU 10 MAGNETURI BTIH CONFIRMAT

**Local Rock64: HTTP 200 confirmat, cu 10 rezultate originale și 10 magneturi BTIH.** După instalarea fizică verificată în PR #107, utilizatorul a rulat o singură dată `sudo python3 /opt/magnetra-btdigg/check-btdigg.py` și a trimis dovada: `Local Rock64 HTTP: 200`, `Real BTDigg search page rows: 10`, `Magnet links found: 10`, `PASS: real BTDigg result HTML reached Rock64 gateway.` Logul **aceluiași proces gateway instalat**: `total_ms=1094`, `dns_ms=430`, `tcp_ms=483` (cumulativ; TCP ≈53 ms), `tls_ms=865` (cumulativ), `open_ms=1013`, `read_ms=80`, `failure=none`, `family=IPv4`. Nu expune tokenuri/IP-uri/magneturi.

**Incidente post-patch, încă reale:** două căutări iPhone au raportat `BTDIGG_SOURCE_TIMEOUT`; jurnalul noului gateway a înregistrat de două ori `failure=tcp_timeout`, `total_ms=3052/3007`, `dns_ms=48/3`, `tcp_ms=null`. Separat, `curl -4` a obținut HTTP 200 în 0.497 s, iar un test Python de conectare TCP prin contul shell a reușit în 50 ms cu un singur IPv4 DNS returnat la momentul respectiv. Acum inclusiv serviciul real, în context `systemd DynamicUser=yes`, a înregistrat HTTP 200 și 10 BTIH. Nu mai există motiv probat pentru schimbarea DNS/IP/IPv6, a limitelor `systemd` sau a transportului TLS; cauza intermitenței nu este încă demonstrată. **Acest PASS unic nu dovedește fiabilitate continuă ori dispariția timeouturilor.**

**Acțiunea următoare, numai pe iPhone:** în https://index.alexlab.media reactivează doar BTDigg în `Indexers` dacă a fost auto-suspendat și efectuează o căutare normală `ubuntu`, lăsând-o să termine, pentru verificare end-to-end browser → Worker → Tunnel → Rock64 → BTDigg. Nu lansa teste repetate agresiv, nu ocoli 429. Capturile precedente cu erorile 3→1 sunt compatibile cu auto-pause, dar validarea separată a listei active pe a doua căutare rămâne de confirmat. Textul UI `about 12 seconds` nu reflectă în mod necesar cele două timeouturi reale TCP de circa 3 s; orice corecție UX separat, fără rollout neaprobat.

**Alte servicii și producția neschimbate:** Cloudflare PWA c86c100 / 136c0 (ultima verificare workflow #39516593949), 46 indexere originale păstrate, Flud transfer manual, fără deploy/restart suplimentar. Istoricul anterior cu „postinstall source search pending” se referă la starea de DINAINTEA acestui test pozitiv.

---



## 2026-10-21 — OWNER-APPROVED PWA SOURCE CURATION (PR pending; not live until separately published)

Owner asked the iPhone PWA to **hide 17 specific consistently failing indexers so they cannot be seen or selected**, including bulk actions and stale browser saved preferences. UI-only exclusion; **all original 46 adapters and source IDs remain in Worker API and Android**; no provider data is deleted. Names and exact IDs: AniRena=anirena, BT4G=bt4g, BitSearch=bitsearch, Ext=extdotto, Eztv=eztvx, FileMood=filemood, LimeTorrents=limetorrents, Nyaa=nyaasi, 1337x=1337x, TokyoToshokan=tokyotoshokan, TorrentDatabase=torrentdatabase, TorrentDownload=torrentdownloadinfo, TorrentDownloads=torrentdownloads, TorrentKitty=torrentkitty, UIndex=uindex, XXXClub=xxxclub, Torrentz=torrentz. Torrentz remains retained in original code for possible later restoration if genuinely functional. These error observations are not a claim that the websites are permanently offline.

Display first: **BTDigg → Torrent9 → OxTorrent → Knaben → TorrentsCSV → ThePirateBay → Internet Archive**; thereafter other nonhidden original sources sorted by saved audit/session observations. BTDigg already defaults selected for new devices; retain four default backups and existing custom selected visible IDs. Saved hidden IDs are silently removed on load; missing all active IDs falls back to safe defaults. The bulk buttons and error recovery flow cannot resurrect hidden IDs. Picker total becomes **29 selectable of original 46 retained**. Historical 46-entry audit and public API remain unchanged. Never weaken Cloudflare provider redirects, anti-bot protections, source attribution, Flud pairing or BTDigg Rock64.

**Deployment boundary:** This UI feature remains only in branch/PR until 4/4 CI and an explicitly safe Cloudflare rollout with immutable version checks; do not trigger old historical promotion workflows or assume a merge is live. Latest validated previous production split c86c100/136c0; no production update yet proven for this UI change.

---



## 21 OCTOMBRIE 2026 — PUBLICARE CURATED PICKER AUTORIZATĂ; GATE 0% → 5% → 100% (ÎN PREGĂTIRE)

Utilizatorul a autorizat explicit publicarea pe `index.alexlab.media` a selectorului din PR #109 (17 ascunse, 29 vizibile, BTDigg implicit primul, Torrent9 și OxTorrent prioritare; 46 ID-uri originale păstrate în API). A fost pregătit un **workflow nou, unic, activat exclusiv prin commit-ul marker `[magnetra-curated-publish-20261021]` pe fișierul `docs/release-events/curated-picker-20261021.md`**; merge-ul PR-ului de infrastructură nu publică nimic.

Safety: preflight versiuni c86c@100/136c@0 (doar ultima stare confirmată istoric), hash SHA256 JS live verificat `9998e0130b19ece9`, trei bindinguri nume/tip pentru versiunile vechi/noi, protecție nume/route/assets, upload versiune numai cu `--keep-vars` și verificare exactă la 0% a JS/CSS/HTML Cloudflare beacon și catalog 46; canary 5%, apoi 100% numai dacă toate gates trec. Versiunea c86c rămâne rollback la 0%; rollback automat permis numai din procentaj cunoscut 95/5 sau 0/100, cu verificare. Nu se fac căutări torrent în release, nu se modifică Rock64, tunel, DNS, tokenuri sau Flud.

**Status: publicarea NU este încă dovedită.** Actualizează numai după workflow PASS și controlul live. Un rezultat STOP poate lăsa 0%-slot sau produce rollback; nu declara site-ul actualizat fără dovadă.

---



## 21 OCTOMBRIE 2026 — CURATED PICKER PUBLICAT: CLOUDflare 100% PASS

**Release efectiv executat:** [GitHub Actions #39605883294](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39605883294), `SUCCESS`, din `main` commit `6a832487dc75cc8694f324dfbb24a9764e503369`. Versiunea nouă Cloudflare `9bbb227f-7f2a-4a9b-acac-ce8cae620c51` la **100%**, versiunea anterioară stabilă `c86c9a32-31fd-4952-86ed-b35f1763b342` la **0% (rollback disponibil)**. Nu mai presupune că c86c@100% este live: aceea e stare istorică. Versiunea 136c a rămas disponibilă în istoricul Cloudflare, nu în actualul split.

**Verificare efectivă prin API și origin:** preflight live c86c100/136c0 și hash public `9998e0130b19ece9` PASS; new version uploaded cu `--keep-vars` și trei bindinguri autentificate nume/tip PASS; 0% stage, 5% canary, 100% full PASS; hash public/override `/app.js` `0945914b2f7bf266`, CSS `1c7080d499b00207`, HTML sursă `9658b96cf24f27f2` cu doar beacon Cloudflare permis PASS; original `/api/providers` încă **46 identități** PASS. Nu s-au făcut interogări torrent, schimbări secrete, Rock64, DNS, Tunnel, Flud sau costuri noi.

**Comportament PWA publicat:** 17 indexere expres numite de proprietar ascunse și ne-selectabile în interfață; 29 vizibile; BTDigg, Torrent9, OxTorrent primele, BTDigg selectat implicit alături de fallback-urile existente pentru instalările noi; selecțiile salvate pe iPhone care conțineau indexere ascunse se filtrează la load. Toate 46 adaptoare Worker/Android intacte. Torrentz este doar ascuns, nu șters. **Acceptarea vizuală pe iPhone a pickerului nou încă nu e confirmată**; solicită o captură cu `Indexers` și `29` vizibile, nu revendica asta ca test de iPhone realizat.

**În continuare:** test iPhone doar Indexers/default și funcționare căutare obișnuită; Flud Companion manual E2E separat, fără auto-download. BTDigg poate rămâne intermitent deși E2E pozitiv pe iPhone a fost raportat explicit de proprietar înainte de acest rollout.

---



## 21 OCTOMBRIE 2026 — EXTINDERE PWA CURATION: AnimeTosho și Mikan

Utilizatorul a cerut ascunderea suplimentară a indexerelor **AnimeTosho** (ID `animetosho`) și **Mikan** (ID `mikanproject`), după erori reale observate pe iPhone. Sunt ascunse împreună cu cele 17 surse de dinainte: **19 ascunse și 27 vizibile** în PWA. Nu se șterg adaptoarele: catalogul original de **46** indexere rămâne în Worker/Android. BTDigg, Torrent9 și OxTorrent rămân prioritare; BTDigg păstrează selecția implicită și fallback-urile existente.

Filtrare inclusiv a selecțiilor vechi și a pauzelor persistate, comenzilor bulk, fallback-ului și avertismentului `indexers unavailable`; dacă doar cele două surse ascunse ar fi eșuat, panoul de avertizare nu apare. Avertismentul rămâne legitim pentru eventuale *alte* surse vizibile cu erori; nu se ascund defecțiuni reale ale BTDigg. Nu există bypass de reclame/CAPTCHA, requesturi agresive, descărcări sau modificări Flud.

**Publicarea e separată de commit:** producția anterioară verificată era `9bbb227f-7f2a-4a9b-acac-ce8cae620c51@100%`, rollback `c86c9a32-31fd-4952-86ed-b35f1763b342@0%`, după run `39605883294`. O nouă lansare sigură trebuie să păstreze aceste versiuni exacte ca bază și să confirme din nou calea completă 0% → 5% → 100%, fără reutilizarea workflow-ului vechi legat de c86c.

---



## 2026-10-21 — PREPARED SAFE DEPLOY FOR 27-VISIBLE CURATED INDEXERS (pending)

The owner requested hiding AnimeTosho and Mikan as well as the earlier 17 problematic sources, bringing the PWA to 27 visible / 19 hidden, all original 46 Worker adapter IDs retained. The PWA errors banner filters hidden sources, but continues showing real failures from still-selectable providers.

Prepared a separate one-shot immutable Cloudflare release guard: `scripts/release_magnetra_hide_anime_mikan.py`, workflow `.github/workflows/magnetra-hide-anime-mikan-one-shot.yml` gated by a future **new activation-only** push to `docs/release-events/hide-anime-mikan-20261021.md` and exact marker `[magnetra-hide-anime-mikan-publish-20261021]`. Release must start from exact verified split `9bbb227f...@100%` / `c86c9a32...@0%`, verify live old JS SHA prefix `0945914b2f7bf266`, both existing binding name/types, original domain/ASSETS, then immutable upload with `--keep-vars`, 0% version-override JS/CSS/HTML SHA, catalog 46, canary 5%, full 100% only after checks. Previous 9bbb version retained at 0% as rollback. No Worker backend or Rock64/Flud changes. No torrent search during release.

**Unmerged deployment source or GitHub PR is not a live release.** Wait for 4/4 CI and activation workflow result and hash postflight. If an unexpected traffic split or SHA is found, STOP without blind retries.

---



## 2026-10-21 — 27-PICKER INITIAL FULL RELEASE STOPPED; VERIFIED ROLLBACK; BOUNDED RESUME READY

Initial launch [run #39610721257](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39610721257) FAILED on unversioned HTML postflight immediately after 100% promotion, **not** at source code build, JS, CSS or catalog. New immutable version **`6dadc612-9660-4195-aeed-cdb658b22cf8`** uploaded with all 3 correct bindings. At 0% and 5%, reviewed JS `85969467f08d21ee`, CSS `1c7080d499b00207`, HTML source `717d75204dafdc9e` (Cloudflare beacon allowed), provider catalog 46, all PASS. Immediately after 100% JS/CSS PASS then HTML NOT VERIFIED. Safe rollback output `ROLLBACK_POSTFLIGHT_PASS` verified **actual target `9bbb227f…@100% / 6dadc612…@0%`** in guard code; inherited print text `c86c100` was stale/wrong and has been corrected in source. Do NOT claim new 27-picker live while rollback remains.

Prepared **version-only resume** (no new upload) `scripts/resume_magnetra_hide_anime_mikan.py`; if owner-action workflow finds exactly `9bbb@100/6dad@0`, verify both 3 binding types and candidate JS/CSS/HTML+46 provider catalog via immutable override GET, move to 5% and then 100%. For final public `/index.html`-equivalent root HTML, allow bounded wait **only for valid HTTP 200 HTML SHA/beacon mismatch**, checking no concurrent Cloudflare deployment and sleeping 8s, up to 5 waits. Other failures, 429/504, network errors NEVER retried. A failed known-state canary/full resumes safe rollback to 9bbb@100/6dad@0; unknown split aborts without destructive writes. Guard workflow `.github/workflows/magnetra-resume-anime-mikan-one-shot.yml` triggers only after future explicit unique approval marker `[magnetra-resume-anime-mikan-20261021]` and file `docs/release-events/resume-anime-mikan-20261021.md` on main. No Rock64, Tunnel, Flud, DNS, providers or secret mutation.

**Status:** initial first release FAILED + rollback PASS; resume PR pending, not executed; iPhone visual acceptance pending. Never repeatedly rerun old upload job.

---



## 21 OCTOMBRIE 2026 — ANIMETOSHO / MIKAN ASCUNSE, 27 SELECTABILE: RELEASE FINAL CONFIRMAT

**Stare nouă, autoritativă:** [GitHub Actions #39619753243](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39619753243), `SUCCESS`, activat prin commit `f1a09311e76bb241fd8c8bb28d144d474549f5d7`. Versiunea imutabilă `6dadc612-9660-4195-aeed-cdb658b22cf8@100%` este noua producție; `9bbb227f-7f2a-4a9b-acac-ce8cae620c51@0%` rămâne rollback. **Nu considerați 9bbb@100 sau statusul primei tentative drept actual**. Prima lansare #39610721257 a eșuat pe HTML postflight și a revenit corect la 9bbb@100/6dad@0; reluarea reușită din #39619753243 este verdictul ulterior.

Dovezi log final live: `RESUME_PREFLIGHT_PASS: 9bbb100 / 6dad0`, `RESUME_STAGED_SOURCE_PASS`, `RESUME_CANARY_PASS`, `RESUME_FULL_100`, `REVIEWED_ASSET_PASS /app.js sha=85969467f08d21ee`, `/styles.css sha=1c7080d499b00207`, `REVIEWED_HTML_PASS EXACT_PLUS_CLOUDFLARE_BEACON source_sha=717d75204dafdc9e`, `ORIGINAL_PROVIDER_CATALOG_PASS:46`, `RESUME_CURATED_PUBLIC_PASS: 6dad100/9bbb0`. Testele CI 4/4 PASS, rollback disponibil, nu s-a făcut upload nou și nu s-a modificat Rock64, DNS, Tunnel, tokenuri, API provideri sau Flud.

**PWA acum publicat:** 19 indexere ascunse complet din picker, bulk, selecții persistente, paused și mesajul `indexers unavailable`: sunt incluse AnimeTosho (`animetosho`) și Mikan (`mikanproject`). Sunt 27 selectabile, BTDigg/Torrent9/OxTorrent primele, BTDigg implicit selectat cu surse backup; toate 46 adaptoare încă în cod/API și Android. Avertismentul rămâne vizibil pentru erorile surselor încă selectabile. **Acceptarea vizuală pe iPhone a noului selector încă așteaptă confirmarea proprietarului**, distinct de postflight Cloudflare confirmat.

---



## 2026-10-21 — 12 SOURCES VISIBLE, 34 USER-HIDDEN + ONLY ROMANIAN/ITALIAN

Owner specified **15 more original indexers to hide** (retaining original adapters/API IDs): BangumiMoe `bangumimoe`, Btsow `btsow`, Dmhy `dmhy`, LinuxTracker `linuxtracker`, MyPornClub `mypornclub`, NekoBT `nekobt`, Sukebei `sukebeinyaa`, YTS `ytsmx`, AniLibria `anilibria`, BlueRoms `blueroms`, EpubLibre `epublibre`, MegaPeer `megapeer`, Rutor `rutorinfo`, XXXTracker `xxxtracker`, FitGirl Repacks `fitgirlrepacks`. With 19 previously hidden, **34 hidden, 12 selectable**, BTDigg/Torrent9/OxTorrent prioritized; default selection BTDigg plus backup sources. Hidden IDs must not appear in PWA picker, legacy localStorage selections, select-all, alternatives or errors. Original 46 backend/Android adapters remain unchanged.

Owner requested PWA interface **only Romanian (default) and Italian**, select RO/IT from header, persist chosen language in browser storage, no external translation APIs. Static and dynamic text/notifications/Flud pairing/error categories localize. Historical source audit labels, user-visible `TEST`/developer-diagnostic text, old 46-provider debugging summaries and misleading EZTV help removed from public UI. Actual CI tests and safe error reporting remain; no API/Flud/Worker backend changes.

Code branch `ui/magnetra-ro-it-curated-12-20261021`, UI `web/app.js`, `web/index.html`, new offline `web/i18n.js`, `web/manifest.webmanifest`, `web/sw.js`, tests `worker/test/ro-it-localization.test.mjs`, `worker/test/indexer-curation.test.mjs`, invariants and checkpoint. **Do not confuse branch/PR with live Cloudflare publication**. Latest *proven* prior live split `6dadc612-9660-4195-aeed-cdb658b22cf8@100` with `9bbb227f-7f2a-4a9b-acac-ce8cae620c51@0`. Any new deployment needs own exact gated version upload / immutable override static integrity checks including `i18n.js` / 0%, 5%, 100% release and guarded rollback, with no secrets shown, no Rock64/Flud/Tunnel changes. No new costs.

---



## UPDATE 21 OCTOMBRIE 2026 — CURATED 12 SURSE + RO/IT: LANSARE SECURIZATĂ PREGĂTITĂ

**Ultima cerere explicită a proprietarului:** ascunde suplimentar BangumiMoe, Btsow, Dmhy, LinuxTracker, MyPornClub, NekoBT, Sukebei, YTS, AniLibria, BlueRoms, EpubLibre, MegaPeer, Rutor, XXXTracker și FitGirl Repacks; în total 34 ID-uri ascunse și 12 surse rămase în selector, BTDigg/Torrent9/OxTorrent primele. Întreaga interfață publică PWA este română implicită sau italiană la alegere (limba salvată în browser), fără badge-uri de audit/test. Sunt păstrate toate cele 46 adaptoare Worker și Android, fără modificări Flud, Rock64, secrete, DNS sau Tunnel. Cod UI este în PR #119; testele de regresie pentru traducere și selecții salvate iPhone.

**Lansare pregătită, NU executată de acest PR:** `scripts/release_magnetra_ro_it_12.py`, `.github/workflows/magnetra-ro-it-12-one-shot.yml`, `scripts/test_release_magnetra_ro_it_12.py`. Un viitor commit separat, unic, care modifică numai `docs/release-events/magnetra-ro-it-12-20261021.md` și conține marker `[magnetra-ro-it-12-publish-20261021]` declanșează workflow-ul numai după CI. Preflight fail-closed pe starea `6dadc612-9660-4195-aeed-cdb658b22cf8@100% / 9bbb227f-7f2a-4a9b-acac-ce8cae620c51@0%` și hash live app.js `85969467f08d21ee`. Urmează upload imutabil `--keep-vars`, verificare a JS/CSS/HTML **și i18n.js**, catalog 46 și 3 bindinguri, 0% staging → 5% canary → 100%, 6dad păstrat la 0% pentru rollback. Nu folosi workflow-urile de publicare vechi.

**IMPORTANT:** Faptul că pregătim workflow și că trece CI NU înseamnă publicare. Numai un run de release efectiv cu `PRODUCTION_100_PASS` și verificări de versiune justifică statusul LIVE.

---



## 21 OCTOMBRIE 2026 — RO/IT + 12 INDEXERE: PRODUCȚIE 100% CONFIRMATĂ

**Noua stare operațională autoritativă**: [GitHub Actions run #39637878742](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39637878742) = `SUCCESS`. Commit de activare `78a5f72895413b4edd3d7a7926cbae1e292d35bb`. Versiunea Cloudflare Worker+assets `60112a3d-b478-4071-b087-ab793fbdfd60@100%`, versiunea anterioară `6dadc612-9660-4195-aeed-cdb658b22cf8@0%` păstrată pentru rollback. **Nu mai considerați 6dad@100 / 9bbb@0 drept distribuție curentă**; este istoric.

**Dovezi postflight de pe site:** original 6dad100/9bbb0 cu 3 bindinguri verificate; noul upload imutabil cu `--keep-vars`; staging 0% PASS; canary 5% PASS; full100 PASS. Hashuri publice/override verificate `/app.js=44f1eac85e8550a7`, `/styles.css=71ea60a9eaf7c03e`, `/index.html source=37865e2eb60ee9f0` (doar beacon Cloudflare admis), noul `/i18n.js=3ca52c9b10d49502`; `ORIGINAL_PROVIDER_CATALOG_PASS:46`, bindinguri 3/3 PASS; log exact `RO_IT_12_PRODUCTION_100_PASS: 60112a3d-b478-4071-b087-ab793fbdfd60@100 / 6dad@0`.

**Comportament PWA publicat:** 12 indexere vizibile, 34 invizibile și ne-selectabile, păstrate ca originale în Worker/Android (46). Cele 15 ascunse în această sesiune: BangumiMoe, Btsow, Dmhy, LinuxTracker, MyPornClub, NekoBT, Sukebei, YTS, AniLibria, BlueRoms, EpubLibre, MegaPeer, Rutor, XXXTracker, FitGirl Repacks. BTDigg, Torrent9, OxTorrent rămân primele; BTDigg selectat implicit alături de fallback-urile consacrate. Interfața numai **română implicită / italiană opțională**, alegere salvată în browser; fără badge-uri publice `RESULTS THIS SESSION`, audit, `NOT AUDITED`, sau coduri diagnostic pe pagina normală. Avertismentele utile pentru surse încă vizibile rămân. Fără modificări Rock64, Tunnel, DNS, Flud, secrete ori costuri.

**Încă neconfirmat de proprietar:** test vizual direct pe iPhone al celor 12 surse și comutarea RO↔IT; dovada Cloudflare 100% este separată și deja confirmată. Următorul pas poate fi o verificare vizuală rapidă în `https://index.alexlab.media`, fără comenzi SSH.

---



## UPDATE 21 OCTOMBRIE 2026 — THE RARBG MAGNET 502: FIX PARSER PREGĂTIT, NU CONFUNDA CU BTDIGG

Utilizatorul a furnizat captură iPhone PWA română unde în cadrul rezultatului **TheRarBg** era butonul „Obține magnet” și toast „Cererea a eșuat (502)”. A clarificat expres că eroarea provine de la **TheRarBg** și este separată de eventualele timeouturi BTDigg. `/api/resolve` este endpointul Worker care întoarce HTTP 502 pentru orice excepție a resolverului, inclusiv parser/no-magnet, deci numai 502 nu dovedește HTTP 502 de la domeniul sursă.

Investigație: adaptorul `therarbag` din `worker/src/legacy-specs.mjs` extrage implicit doar `a[href^='magnet:']`. Pagina TheRarBg, în observare externă, prezintă și `Info Hash: <40 hex>` drept text propriu. Patch izolat în `worker/src/legacy-adapters.mjs`: după încărcarea reușită, validată prin same-origin allowlist/TLS/antibot/size, dacă nu apare ancoră magnet, transformă **numai** un unic infohash cu etichetă `Info Hash:` în `magnet:?xt=urn:btih:<hash>`; niciun retry, torrent download, bypass, redirect, combinație cu alte surse sau hash ghicit. HTTP 502/403 reale rămân erori. Teste noi `worker/test/therarbag-source-owned-hash-resolve.test.mjs`. Pentru un eșec real, interfața PWA afișează RO/IT mesaj specific și indică „Detalii” în locul unui toast 502 generic. All 46 adapters intacte; BTDigg/Rock64/Flud neatins.

Planul de release este separat de parser: workflow unic `.github/workflows/magnetra-therarbag-magnet-one-shot.yml` cu marker `[magnetra-therarbag-magnet-publish-20261021]`, preflight `60112a3d-b478-4071-b087-ab793fbdfd60@100% / 6dadc612-9660-4195-aeed-cdb658b22cf8@0%`, app.js hash vechi `44f1eac85e8550a7`; upload --keep-vars versiune imutabilă nouă, verificare 0%/5%/100% a app.js, i18n.js, CSS, HTML și 46 API IDs, rollback numai pe split cunoscut. **Publicarea și fixul E2E pe iPhone încă nu sunt probate**, până la un run succes și o acțiune efectivă pe iPhone.

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
