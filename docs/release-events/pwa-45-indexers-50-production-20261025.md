# Owner-approved Magnetra PWA activation — 25 October 2026

This is an **explicit, one-time production activation event**, separate from PR #196 (the
app/UI) and PR #197 (the fail-closed 0→5→100 release mechanism). The owner
instructed the assistant to continue the approved publication after CI passed.

## Exact source and intended changes

- Reviewed PWA application source: `main` commit `c962da6d7a2e44df8846012c2001cefcade7c41c`,
  verified Git blob `web/app.js:eb98cfe79e1a9edb48b6e3d650d7eed81ed7c3a4`.
- SubsPlease excluded from PWA selection, search, result and failure displays.
- All 45 other original source IDs selectable; only one "Selectează toate" action.
- Client-side result pages of 50 (no first-400 truncation), Romanian and Italian labels.
- Keep all original 46 Android/API source adapters. Preserve tested Flud/Shield,
  NoNameClub, 0Magnet, TheRarBg, iOS safe-area and provider protections.

## Safety conditions that must pass before any traffic shift

- Release script/workflow under PR #197 must be present on a reviewed protected main;
  five required CI gates must pass on this activation PR.
- Verify the exact current Cloudflare deployment before any write. Last verified split
  from successful iOS production run #40173857614: version
  `76a15eae-5c8c-41a2-bace-adb9b2460933` at 100% and
  `24642346-9db0-4cea-a56e-12e30f35569f` at 0%.
  If this has changed, **STOP**. Do not guess a new baseline.
- Confirm existing Cloudflare account, worker identity, exact single custom domain,
  original 4 bindings, unchanged two secret names, existing service binding.
- Validate source blob and all expected PWA changes before a Cloudflare request.
  Upload one immutable version with `--keep-vars`. Test candidate with zero
  traffic and version override, five exact asset SHA-256 hashes, health/catalog
  46, original nonameclub no-false-auxiliary, and read-only owner source magnet
  resolution (never display or send the magnet).
- Move to a 5% canary only after the zero-slot gates pass; repeat checks, then
  promote to 100% and verify public assets + 46 API catalog. Keep prior working
  version at 0% for immediate rollback on a known candidate failure.
- **Never** use normal `wrangler deploy`, DNS edits, token changes,
  external paid services, Rock64 changes, or Flud automated submissions.
  Do not reuse another release's activation marker.

## Execution and acceptance

Only the exact main merge commit message
`[magnetra-pwa-45-indexers-50-owner-approve-20261025]`
may trigger the guarded release workflow via this unique event path.
A PR build or an ordinary merge must not change production.
Owner iPhone PWA acceptance is pending until the successful Cloudflare release
log, public postflight, and later physical owner verification.
