# AlexLab Magnetra Stable — 27 October 2026

**Status: released to production and physically accepted by the owner for ThePirateBay search and Flud Companion handoff.** This is a documentary stable checkpoint, **not** a new GitHub Release, tag, deployment, binary build or additional Cloudflare change.

## Immutable release evidence

- Public PWA: https://index.alexlab.media
- Repository: `Zuzuitu/AlexLab-Magnetra`; reviewed implementation PR [#211](https://github.com/Zuzuitu/AlexLab-Magnetra/pull/211) merged at `2162ceceba42eeacec7762f4a0170c1f19031209`.
- Manual guarded release PR [#212](https://github.com/Zuzuitu/AlexLab-Magnetra/pull/212) merged at `aa3d31b6b6518ff707454c6e466bd244d1a3d869` (`main` at release).
- Owner-authorized [GitHub Actions run #40473100787](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/40473100787): `workflow_dispatch`, completed `SUCCESS` on 27 Oct 2026 at 08:23:44 UTC. The `guarded-production` job succeeded; its `offline-release-tests` job is intentionally skipped on a manual dispatch (the corresponding tests ran and passed in the PR CI).
- The production log documents a fresh read-only account/split/four-bindings check **before write**: `40bfd647-2b8a-4643-94f2-577e723aba97@100%` and `74754dac-1842-47b2-8e6f-92a10731f124@0%`.
- The immutable candidate was uploaded and independently checked: `fdffdc78-0bd3-4721-a5b1-11f515c52bd1`. Deployment transitions **0% → 5% → 100%** all logged `PASS`; latest release-log production split: **`fdffdc78-0bd3-4721-a5b1-11f515c52bd1@100%`**, former **`40bfd647-2b8a-4643-94f2-577e723aba97@0%`** preserved as rollback.
- The logs explicitly recorded `IMMUTABLE_FIVE_ASSETS_AND_ORIGINAL_46_API_PASS`, `IMMUTABLE_NONAMECLUB_EXACT_ORIGINAL_MAGNET: PASS` (redacted), `IMMUTABLE_NONAMECLUB_SEARCH_CARD_DETAILS_ONLY: PASS`, `PUBLIC_FIVE_ASSETS_HASHES_46_CATALOG_PASS` and `TPB_429_GUARDED_PRODUCTION_100_PASS`. This proves immutable/public asset checks and **46 original backend provider IDs**, not 46 currently responding source sites.
- The previous general-purpose PWA push deployment was skipped by design; no replay of older release workflows. No new paid infrastructure, DNS, WAF, Rock64, tunnel or Flud reconfiguration was performed by this release.

## Owner's real-device acceptance

After publication, the owner explicitly reported on 27 Oct 2026 that the **ThePirateBay search works correctly on iPhone** and sending the selected result to **Flud also works**. This closes the observed `RATE_LIMIT` P0 as a *presently functioning owner-tested workflow*.

This is **not** a claim that the original source will never rate-limit in the future, that every provider is healthy, or that every iPhone screen, language, pagination and bulk-selection edge case was manually retested during this acceptance. External-provider uptime remains outside Magnetra's control.

## Frozen stable behavior

- PWA: **11 visible and 35 excluded** indexers (SubsPlease excluded from PWA selector); **46 original Worker/Android provider IDs retained**.
- **50 client results per page**, all/none selector toggle with deliberately empty selection persisted, RO/IT localizations, iOS Home Screen safe area and service worker **v11**.
- BTDigg/TPB genuine-result exact-query cache, no fabricated results or alternate source origin; TPB respects origin HTTP 429 `Retry-After` with a bounded per-isolate cooldown and a clear localized error; failed TPB cannot immediately be reselected by the alternate-sources action. This is **not** global cross-isolate rate limiting.
- Optional owner-configured QR/token Flud Companion integration, Rock64/gateways, fixed-origin protections and 4 immutable Cloudflare binding types are kept unchanged.

## Post-stabilization PR triage (not blockers; no changes authorized here)

The following GitHub PRs were still open at checkpoint time. Do not merge, close, or deploy them just to make the dashboard look cleaner:

| PR | Topic | Suggested disposition |
| --- | --- | --- |
| [#199](https://github.com/Zuzuitu/AlexLab-Magnetra/pull/199) | Old 45-source deployment guard/read-only audit | Legacy baseline; inspect for documentation-only reusable tests, otherwise close later as superseded, **not** merge into stable branch |
| [#193](https://github.com/Zuzuitu/AlexLab-Magnetra/pull/193) | Worker API per-location rate limiting | Separate security/cost/bindings review and canary required; not part of current TPB cooldown |
| [#150](https://github.com/Zuzuitu/AlexLab-Magnetra/pull/150) | TheRarBg diagnostic stage visibility | Recheck current real defect and privacy before any decision |
| [#149](https://github.com/Zuzuitu/AlexLab-Magnetra/pull/149) | TheRarBg original detail-input hash extraction | Revalidate source ownership and current regression tests before any integration |
| [#36](https://github.com/Zuzuitu/AlexLab-Magnetra/pull/36) | Rock64 isolated NordVPN preflight | Deferred experiment; never change active routes, DNS, Flud or tunnels for cleanup |

## Operations / future work

1. **No new action needed** for the completed stable release. Avoid rerunning [workflow `magnetra-tpb-429-guarded-production-20261027.yml`](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/workflows/magnetra-tpb-429-guarded-production-20261027.yml) or any older one-shot release. The previous 40bfd6 version at 0% is the known rollback from the successful run, **not** necessarily a future live-split guarantee.
2. Any future code changes: dedicated branch and PR, relevant CI and security tests, new read-only live split/bindings verification, explicit owner approval, controlled immutable release/rollback. No generic `[deploy-pwa]` push or direct unreviewed Wrangler deploy.
3. For regressions: reproduce one provider/action at a time, preserve source provenance, no aggressive retries/rotating IPs or token leakage. For Flud, never expose QR token, private host, gateway credentials or local network details in public issues/logs.
4. This document is the **current authoritative checkpoint**. Older `docs/PROJECT_STATE.md` and `docs/NEXT_CHAT_HANDOFF.md` sections that say this same TPB fix is *only staged/not deployed* are chronological history and superseded by the stable checkpoint.

**No runtime code, production configuration, Cloudflare version, rollback percentage, repository release assets, tags or download counts were altered by documenting this checkpoint.**
