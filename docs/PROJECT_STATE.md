# AlexLab Magnetra — Project State

_Last updated: 2026-10-12; verified repository `main` before this documentation PR: `8969b9fe6758f859ac072bea984a5f9c9c59597f`._

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
