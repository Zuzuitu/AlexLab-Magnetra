# Magnetra 0Magnet original details-first iPhone fix — owner-approved release

Date: 24 October 2026 (Europe/Rome)
Approval: owner explicitly confirmed the guarded Cloudflare 0% -> 5% -> 100%
release with rollback immediately after PR #168 was merged.

Exact original user-supplied result: https://9mag.net/!lxbV
Root cause supported: same-card original details resolves to source-owned
valid BTIH via /api/resolve HTTP 200; 0Magnet result additionally includes
magnetSource that the old PWA erroneously prioritizes. PR #168 changes
only the 0magnet frontend selection precedence. The different auxiliary
URL's specific HTTP failure code was NOT separately confirmed, and
physical Safari success remains an independent post-release gate.

Safeguards: one-shot release from reviewed main only, exact live active
916d0671-b9c5-432d-8724-aed27bc22c4f @ 100% and prior 139d97f7-
4048-4bbb-8e90-80585f1f4b26 @ 0% expected at preflight; abort on any
mismatch or concurrent deployment. Verify the four bindings ASSETS,
BTDIGG_GATEWAY_TOKEN, MAGNETRA_GATEWAY_TOKEN and FLUD_RELAY, Worker account
and config, backend and 46 providers. New version immutable, 0%-5%-100%
with state gates, candidate asset SHA + exact original owner resolver.
On recognized 5%/100% failure rollback previous active to 100%.
On unknown state, stop fail closed and request manual inspection.
No other worker changes, no paid service, no torrent transfer or Flud
command, no Rock64, tunnel, DNS, secret logs or credentials changes.

Do not rerun the historical TheRarBg workflows or this one-shot.
