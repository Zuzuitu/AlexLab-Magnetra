# TheRarBg iPhone wrong magnetSource FIX — exact owner-approved production release

Date: 24 October 2026 Europe/Rome. Only-current PWA user explicitly
approved controlled production testing on index.alexlab.media and preservation
of old immutable Cloudflare versions.

Owner actual PWA TheRarBg 352.7MB Cyberpunk soundtrack card failed with
URL fingerprint b12d9fd36aa0, HTML_NO_BTIH and JSON_URL_REJECTED.
Owner clicked Details, original same source had Magnet Download, Info Hash.
GET-only real run #40084154928 proved source's current exact original
details URL matches the user-copied link and is JSON eligible. Decisive
one-shot diagnostic run #40085002856 proved original source returns
a DIFFERENT magnetSource URL whose first 12 hex of SHA256 is exactly
the owner failing fingerprint b12d9fd36aa0. Exact same card original
details URL returned VALID_MAGNET with HTML_ANCHOR_VALID. Thus this is
the PWA source URL choice bug, not the provider's HTML hash parser.

Minimal code PR #161 fixes real client ensureMagnet: TheRarBg shares
details-first behavior of OxTorrent and Torrent9; all other 43 providers
keep pre-existing preference. Real function VM tests, 46 original source
IDs, 12 visible/34 owner-hidden, RO/IT PWA, Worker API and Android
regressions all passed four mandatory CI before code merge. Normal code
merge does not activate Cloudflare.

Owner authorizes guarded immutable 0-5-100 full live verification on
the sole-user main domain. PREWRITE EXACT baseline MUST match
139d97f7-4048-4bbb-8e90-80585f1f4b26@100% (diagnostic),
36019925-2308-4f99-8223-13854012d372@0% (older rollback).
This is an expected state, NOT assumption: re-query real Cloudflare
deployment id/shares, exact same account and custom origin, and all
FOUR binding types (ASSETS, 2 gateway secrets, FLUD_RELAY) both
versions before any upload. Upload new immutable candidate with pinned
Wrangler + --keep-vars; preserve bindings and percentages. Then slot
old100/new0, verify actual staged JS SHA matches reviewed web/app.js,
46/46 providers, one exact owner-supplied original detail magnet resolves
without logging hash or sending Flud; 5% canary; then old0/new100
and live static JS SHA/46 parity postflight. On a post-write fault,
guarded automatic rollback old100/new0 only if exact 5/full known,
never guess concurrent changes. No generic deploy; no DNS, Preview URLs,
Rock64, Shield, actual Flud send, other provider search, third party
torrent file request, secret reset or paid infrastructure change.

Do NOT say user iPhone E2E passed until they reproduce first 352.7MB
source card with Obtain Magnet, Copy, Share and (if desired) Send to Flud
after a verified workflow SUCCESS. Last user acceptance still pending.

Unique controlled release marker:
[magnetra-therarbag-details-first-fix-20261024]
