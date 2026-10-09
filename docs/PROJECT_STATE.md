# AlexLab Magnetra — Project State

_Last updated: 2026-10-08_

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

## Browser-owned BTDigg result import (candidate, 2026-10-09; not yet deployed)

The BTDigg Worker adapter continues to return TIMEOUT or HTTP 429 at the server boundary. The source is NOT recovered for automatic search. As an explicitly opt-in compatibility route, the PWA has a new browser-origin BTDigg result import under `web/btdigg-bridge.js`, with a dedicated UI/dialog in `web/index.html` and `web/app.js`. The script runs only when the user invokes its Safari/desktop bookmarklet on the **actual** HTTPS BTDigg search page; it extracts currently visible `div.one_result` rows, their real magnet URIs, titles and details, and navigates to Magnetra with URL-fragment data. Import occurs entirely in the local browser, and the fragment is scrubbed via `history.replaceState` before other PWA initialization. No BTDigg credential, Companion token, worker proxy, paid service, background scraping or arbitrary-domain read is introduced.

The PWA validates infohashes and fixed BTDigg HTTPS details origins, de-duplicates hashes, and shows imported rows with explicit `BTDigg · browser import` attribution through existing search results and Flud Companion actions. Rows are user-provided, NOT independently server-verified, and must never update the historical 46-provider live audit. The flow needs a user-maintained Safari bookmarklet and real iPhone testing; bookmarklets can be restricted by browser policies. It is a **manual fallback**, not full automatic BTDigg integration; authoritative permitted BTDigg API access remains the only demonstrated plausible route to stable fully automatic retrieval. Work remains within current free hosting; no release authorized. Unit/behavioral tests cover extraction and malicious import validation.

## iOS installed-PWA BTDigg import correction (2026-10-09)

**Verified external platform constraint:** An iOS Home Screen Web App has storage separate from Safari; Apple WebKit documents that `localStorage` is not shared with Safari even when Home Screen creation copies login cookies. The first BTDigg bookmarklet in PR #14 launched `https://index.alexlab.media/#btdigg=...` in the browser, which does not ensure access to an already paired Flud Companion in the *installed* Magnetra PWA. Source: https://webkit.org/blog/14787/webkit-features-in-safari-17-2/ and https://developer.apple.com/videos/play/wwdc2023/10120/.

**Scoped fix:** The importer now provides two explicit Safari bookmarklet modes, both manually invoked on the genuine HTTPS BTDigg search page: `open` navigates to the normal browser import, while `copy` exports visible BTDigg result metadata and magnets as `BTDIGG_IMPORT:`-prefixed text to the system clipboard. Inside the separately installed Magnetra PWA, an explicit user gesture imports that text through `navigator.clipboard.readText()`; a manual paste field supports browsers that deny clipboard read. The PWA validates and de-duplicates this payload with the same source-origin and infohash rules as the fragment path, without disrupting local Companion pairing; the browser fragment path is preserved. Clipboard writing may require permission; Safari can fall back to a manual copy prompt. Export retains the previous 25-row / length limits and copies neither credentials nor API tokens. Mark results as `BTDigg · browser import` and do not imply server-origin verification.

No BTDigg API has been obtained, no independent DHT crawler has been deployed, no result was generated from another provider, no paid service introduced, and **automatic server-side BTDigg search remains blocked or unverified**. Bookmarklet behavior on the owner's real iPhone must still be confirmed after an **explicitly approved Cloudflare release**. GitHub merge alone is not production deployment.
