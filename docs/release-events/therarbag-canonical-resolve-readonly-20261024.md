# Real iPhone TheRarBg exact-card canonical resolver audit, 24 October 2026

Owner source screenshot and Safari copied address confirm a 352.7 MB
Cyberpunk Edgerunners 2 Original Series Soundtrack item has source-owned
Magnet Download, Copy Magnet and Info Hash. iPhone failure URL SHA256-12
was b12d9fd36aa0 with HTML_NO_BTIH and JSON_URL_REJECTED.

Crucial new evidence: real production GET-only run #40084154928 matched
one same 352.7 MB result, and its current API details URL was IDENTICAL
to owner copied source URL, fingerprint 3b00bf511347; valid JSON URL
structure and no query, fragment or host mismatch. The old iPhone resolver
input fingerprint differs. Exact cause of that divergence remains OPEN.

This one-shot audits whether source's current magnetSource property is
absent, same or different, then sends the sole-owner-provided canonical
details URL to our existing read-only /api/resolve with owner-opt-in diagnostic.
The resolver reads at most original HTML and original per-detail JSON. It
prints only validated enums/status; never magnet, torrent hash, source URL,
title, HTML or credentials, and never sends anything to Flud. Zero
Cloudflare/DNS/Rock64 mutation or traffic change.

Activation marker: [magnetra-iphone-canonical-resolve-readonly-20261024]
