# NoNameClub owner card identity differential — 25 October 2026

Owner's exact non-logged-in 0Magnet-analog iPhone failure: Magnetra PWA
NoNameClub result Lupin (2026) errors "Sursă indisponibilă", but
original detail https://nnmclub.to/forum/viewtopic.php?t=1896364 has
public inline magnet and torrent icon.

Owner exact original-source diagnostic #40140578589 (after PR #175
merge to main) definitively passed: original URL GET HTTP200, valid
`a[href^='magnet:']` static HTML, existing production Cloudflare
`/api/resolve` metadata-only POST for `nonameclub`+exact URL HTTP200,
valid BTIH, same BTIH as source; no torrents or credentials, hash never
logged. This disproves a permanent parser defect for the exact link
AT AUDIT TIME, but does NOT prove the PWA card sent this same details URL
or that iPhone Safari ever received a valid response.

This new read-only gate checks exactly one normal PWA
`/api/search?q=Lupin&category=all&providers=nonameclub` GET (fallback:
`Lupin 2026` only if exact result absent). Enumerate only fixed-stage
classes for whether the exact owner `details` URL is present and
whether the search record contains an auxiliary `magnetSource`, already
resolved `magnet` or only canonical `details`. If present and not
already resolved, a single metadata-only `/api/resolve` POST for the
exact owner URL; no raw title, response body, magnet/hash/passkey/cookie
or URL exposed in logs. No source bypass, mutations, retries, .torrent
GET, Flud/Shield, DNS, Rock64, paid API or production rollout.

Conclusions must distinguish source/Worker success from iPhone success.
Only after evidence decide whether Safari cache/transport, card source,
or a truly defective resolver warrants an actual code release.
