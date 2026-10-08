# AlexLab Magnetra — New-chat engineering handoff

_Last synchronized: 2026-10-08, based on GitHub `main` commit `94d2b6b40e4a3ad465f0c39e64fc1df4301f9f87` (PR #9). This SHA is historical; always refetch GitHub main._

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
