# Magnetra TheRarBg — production release activation — 2026-10-22

**Scope:** Immutable Cloudflare Worker/PWA release for source-owned TheRarBg
identical-infohash parsing and sanitized Romanian/Italian magnet-resolution
error stages already reviewed in PR #131 and release safety gates in PR #132.

## Activation constraints
- This activation is unique and may only be used with the squash merge commit
  subject containing the exact marker:
  `[magnetra-therarbag-stages-publish-20261022]`
- Fail before upload unless Cloudflare's current distribution is EXACTLY
  `8c4e0f6a-dc7a-4f72-9954-ba9cdd91392f @ 100%` and
  `60112a3d-b478-4071-b087-ab793fbdfd60 @ 0%`.
- Fail before upload unless live app.js / styles.css / i18n.js SHA prefixes and
  three required immutable bindings agree with reviewed source and metadata.
- Preserve existing tokens/secrets, worker name and custom-domain route.
- Stage immutable candidate at 0% and validate assets + 46 original adapters;
  canary 5%; full 100%; keep prior `8c4e...` at 0% for rollback.
- Safe rollback only after inspecting exact known traffic split; no blind retry.
- No DNS/Tunnel/Rock64/BTDigg/Flud changes; no remote source queries, magnet
  downloads, provider list modifications or anti-bot bypasses.
- After release validate real new candidate ID and final Cloudflare split.
  A repeated same-card iPhone test remains necessary to confirm functional
  resolution; release success is not user acceptance.

Workflow: `.github/workflows/magnetra-therarbag-error-stages-one-shot.yml`
Script: `scripts/release_magnetra_therarbag_error_stages_20261022.py`
