# AlexLab Magnetra — read-only Cloudflare Version URL audit, 24 Oct 2026

The owner approved continuing the staged TheRarBg iPhone diagnostic without
exposing the existing user population to an unverified change.

Current verified immutable candidate version:
`139d97f7-4048-4bbb-8e90-80585f1f4b26` (uploaded by run #40058004336).
Cloudflare reported production `36019925-2308-4f99-8223-13854012d372@100%`
and previous candidate `c201cbf9-2080-4a5b-9e40-723a8714d94c@0%`
unchanged after upload; this is a historic checkpoint, NOT assumed fresh state.

This UNIQUE read-only event allows one GitHub Actions invocation to check
official Cloudflare account and Worker script subdomain metadata using
authenticated GETs. It will NOT enable preview URLs or workers.dev, upload
a Worker, change percentages, deploy, modify secrets, DNS, tunnels, Rock64,
Flud or Shield, or send a torrent or magnet. The checked candidate must retain
all four immutable bindings and the exact historic split must still hold.

If and only if preview URLs already are enabled, the audit constructs the
version-specific workers.dev URL from a verified account subdomain, checks
real version-specific /api/health 46/46, verifies /app.js matches reviewed GitHub
source SHA256, then prints a REAL owner-testable URL. If previews are disabled,
it reports disabled without altering Cloudflare. Any unverified response fails
closed.

Activation marker for the dedicated main-branch one-shot workflow only:
[magnetra-iphone-version-url-readonly-20261024]

No general PWA deploy marker and no default production rollout.
