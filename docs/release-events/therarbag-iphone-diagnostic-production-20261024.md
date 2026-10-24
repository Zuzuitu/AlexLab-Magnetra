# AlexLab Magnetra — TheRarBg iPhone Diagnostic: owner-approved production release

Date: **24 October 2026 (Europe/Rome)**.

The owner explicitly authorized testing on the canonical production URL,
explaining that **they are the sole user** of the PWA. Preview URLs are currently
disabled. The existing immutable owner-opt-in iPhone diagnostic was merged by
PR #154. Cloudflare uploaded immutable version
`139d97f7-4048-4bbb-8e90-80585f1f4b26` through successful
version-only run #40058004336.

**Controlled deployment authorization**: after all four mandatory GitHub CI
checks pass, and ONLY via this unique one-shot event on reviewed main, permit
Cloudflare version-only deployment **0% -> 5% -> 100%** of exact candidate
`139d97f7-4048-4bbb-8e90-80585f1f4b26`, preserving original active
`36019925-2308-4f99-8223-13854012d372` at 0% for rollback. The
precondition is exact existing Cloudflare split:
`36019925-2308-4f99-8223-13854012d372@100%`,
`c201cbf9-2080-4a5b-9e40-723a8714d94c@0%`.
These identifiers are hard STOP guards, **not** presumed current values.

The release verifies both Cloudflare Worker identities in the same account,
the unchanged custom domain/asset origin, all four immutable binding name/type
pairs (ASSETS, BTDIGG_GATEWAY_TOKEN, MAGNETRA_GATEWAY_TOKEN, FLUD_RELAY),
reviewed PWA JS SHA, 46/46 public provider identities, Worker runtime health
and an owner-supplied original TheRarBg detail through opt-in diagnostic only.
The original source may still fail intermittently; testing diagnostic stage
presence is NOT asserting magnet resolution as fixed. A single bounded
original-source read from Cloudflare is permitted; no .torrent download or
magnet delivery to Flud, no real device credential reads.

If a stage fails after a recognizable 5% or 100% write, attempt reversible
rollback to old 100% / new 0%; never guess if concurrent modifications occur.
No new Worker upload, no DNS/preview settings/Tunnel/Rock64/Shield/Flud
mutation, no paid infrastructure and NO generic [deploy-pwa] marker.

Only after the production endpoint and public assets are verified may the owner
test the PWA at **https://index.alexlab.media/?magnetra_diag=1** on iPhone.
The owner must reproduce the exact same failing TheRarBg card and provide the
finite trace screenshot; success from GitHub runner is not iPhone acceptance.

Unique release event marker for the review/merge commit:
[magnetra-iphone-diagnostic-release-20261024]
