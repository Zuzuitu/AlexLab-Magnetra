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
- `web/` — installable, standalone mobile-first PWA with IndexedDB-like local bookmark persistence (currently localStorage), full indexer inventory and magnet actions
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

The fork currently matches upstream at commit `100b3f21f98b93bb9b70869ba5f70eadc80fa14c`.

Protected baseline values:

- Android application ID: `com.prajwalch.torrentsearch`
- minSdk: `25`
- targetSdk: `37`
- Java source/target compatibility: `17`
- CI Gradle daemon runtime: **JetBrains Runtime 21**, installed separately from Temurin 17 and required by `gradle/gradle-daemon-jvm.properties`.

These values are protected because they describe the known-good starting point. They may change later only as an intentional coordinated decision.

## First PWA implementation (2026-10-07)

- Full canonical inventory: exactly **46 built-in upstream indexers**, derived from `BuiltinSearchProvidersModule.kt`. Guard checks matching upstream provider IDs, not merely count.
- Explicitly ported adapters in the first milestone (**21**): `AniLibria`, `Knaben`, `TorrentsCSV`, `ThePirateBay`, `YTS`, `Internet Archive`, `BangumiMoe`, `SubsPlease`, `Btsow`, `Nyaa` and `Sukebei`; plus `BTDigg`, `Dmhy`, `NekoBT`, `Mikan`, `TorrentKitty`, `Rutor`, `XXXTracker`, `AnimeTosho`, `LimeTorrents`, `TorrentDownload` (HTMLRewriter). These are implemented adapters, **not yet live-tested against every provider**; real-world availability remains an external dependency.
- The remaining **25** providers are inventoried and visible as **PORT PENDING**, not represented as working. Full functional parity remains an outstanding explicit product requirement; never count catalog coverage as adapter parity.
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

### Important PWA CI regression fixed

While extending source testing, the HTML selector smoke check initially reported success because Wrangler picked up the production static-assets configuration and returned the PWA homepage (HTTP 200), **not** the test Worker response. Root cause: the CI command did not pin a dedicated test Wrangler config or validate response semantics. Fix: `worker/test/wrangler-selector.jsonc` specifies `selectors.worker.mjs`, and CI accepts only JSON with `ok === true`, `checked === 35` and zero invalid selectors. A new invariant prevents this test from silently reverting to an HTTP-only check.

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

No end-user PWA regression has been confirmed and fixed yet. The project has addressed the repository/CI regressions below.

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
- PWA web shell and all **46 provider adapters implemented in this feature milestone**; provider-specific live search reliability and physical Shield integration are not yet established, and code is pending PR/CI promotion.
- PWA backend/proxy is deployed to Cloudflare Workers with fixed allowlisted upstream endpoints.
- Full 46-provider **implementation coverage reached**, but functional/live parity remains unverified. Never infer source uptime from the catalogue.
- Production is live at **`https://index.alexlab.media`** via Cloudflare Workers Custom Domain, deployed in successful GitHub Actions run 37596819448 (retry attempt 2). Independent public smoke run 37755554228 confirmed HTTP+TLS, HTML, PWA manifest, `/api/health` and `/api/providers` (21 ported flags/46 total). Deploy requires manual dispatch or an explicit `[deploy-pwa]` commit marker on `main`.
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
