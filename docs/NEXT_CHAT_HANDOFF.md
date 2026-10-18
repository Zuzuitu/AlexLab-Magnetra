# AlexLab Magnetra — New-chat engineering handoff

_Last synchronized: 2026-10-12, verified GitHub main immediately before this docs PR: `8969b9fe6758f859ac072bea984a5f9c9c59597f`. Always refetch GitHub main._

## READ FIRST — current operational state confirmed 2026-10-12

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
