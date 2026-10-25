# AlexLab Magnetra — owner-directed guarded release activation

Date: 2026-10-25. Scope: restore curated **11 visible, 35 hidden indexers** on the PWA (including SubsPlease excluded), select/deselect-all toggle with explicit empty selection persistence, and preserve existing client pagination at **50 results/page**. Original 46 Worker/Android adapter identities retained.

Independent production preflight: GitHub Actions [#40213908118](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/40213908118) showed immutable `8d9c19f4-ca38-428b-888e-757ef578c829` at **100%** and **no 0% version**. Public app.js known 45-indexer SHA-256 prefix `1160fa81597ce6ca` and all four live binding types verified. Do not extrapolate the mock unit-test 0% version from output.

Release implementation is separately reviewed/merged from PR #204 and MUST enforce exact active baseline, source pinned blob, GET-only audit preflight, backend 46 parity, Cloudflare binding guard, fixed-origin HTTPS, no secret exposure, immutable version upload with `--keep-vars`, candidate at 0%, 5% canary, 100% after validated assets and known source-owned NoNameClub magnet/card test. Preserve the previous active 8d9c version as **0% rollback** if promotion reaches 100%, or restore it to 100% after known release failure. Refuse unknown/concurrent traffic splits; no blind retry.

This file is a one-time release event, not a request to use the unsafe generic direct deploy. Never change Rock64, Flud, DNS, WAF, Android signing, paid tier, API secrets or unrelated providers. Physical iPhone acceptance is separate from Cloudflare postflight.
