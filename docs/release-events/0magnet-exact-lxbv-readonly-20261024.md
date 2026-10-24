# 0Magnet exact owner 9mag.net URL diagnostic (24 Oct 2026)

Owner provided the exact original-source detail URL https://9mag.net/!lxbV
after reproducing the existing "Sursă indisponibilă" error in Magnetra
on iPhone. An older prefix-matched 0Magnet record resolved successfully,
but it was NOT proven identical to the screenshot card.

This event authorizes precisely one metadata-only **read-only** diagnostic:
one production original-provider search GET, one GET to the exact public
owner-provided 9mag.net path and, when the source was not blocked or
rate-limited, one POST to Magnetra /api/resolve with that exact source detail
URL. The POST never sends a magnet to any device. No PWA deploy, no
Cloudflare version percentage change, no Rock64, Flud, Shield, torrent
downloads, tokens or credentials; no automatic retry, off-origin redirect
following, challenge bypass or open proxy. Stop on 429. Log HTTP status and
fixed-stage enum only; never print the magnet, raw hash, source HTML, full
detail URLs, query records or upstream response bodies.

The incident is NOT declared fixed by this diagnostic. Distinguish
production API success/failure from iPhone Safari user-facing acceptance.
Retain TheRarBg owner-verified live 100% version and rollback as last
release-evidenced state.
