# 24 Oct 2026 — TheRarBg iPhone same-card URL shape diagnosis (READ ONLY)

The owner's real iPhone screenshot at 11:04 local on production opt-in
`https://index.alexlab.media/?magnetra_diag=1` shows:

- `THERARBAG_IPHONE_DIAG_V1`: **confirmed running on owner's iPhone**
- original failing first Cyberpunk Edgerunners 2 TheRarBg result, 352.7 MB
- `URL b12d9fd36aa0` (12hex fingerprint only)
- `HTML HTML_NO_BTIH` — original fetched document did not yield supported BTIH
- `JSON JSON_URL_REJECTED` — original JSON fallback URL validator rejected
  source details BEFORE performing a JSON request
- `55ms` reported diagnostic elapsed time

The previously owner-supplied known Cyberpunk direct detail URL fingerprints to
`3b00bf511347`, **different** from the actual iPhone card. This is a
strong link identity/shape mismatch signal, but the true candidate URL and
cause of the fallback validator refusal have NOT yet been established.

This one-shot does a maximum of two finite GET requests to the owner's own
`/api/search` endpoint for a direct, original TheRarBg search, matching only
SHA-256 first six bytes of the exact result-specific `details` field. Output
is the *category* of URL shape (query/host/path/slug), no raw URLs or hashes
or torrent filenames or magnets. No POST, resolve, torrent downloads, source
passwords, Cloudflare writes, traffic, secret, Rock64 or Flud changes.

Must never relax allowlist/SSRF protection or assume link shape absent the
actual same-card result match. A real root-cause fix requires matching fixture,
regression tests and separate staged owner-approved release.

One-shot read-only activation marker:
[magnetra-therarbag-iphone-linkshape-readonly-20261024]
