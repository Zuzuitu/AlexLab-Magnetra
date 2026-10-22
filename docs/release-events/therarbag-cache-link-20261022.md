# Magnetra TheRarBg — source-linked torrent metadata release — 2026-10-22

This is the **unique owner-directed release event** for the reviewed source-owned
TheRarBg cache-link BTIH fallback (PR #135) and its immutable Cloudflare
release protections (PR #136).

## Mandatory immutable preflight
- Exactly `056d8394-79b0-459a-b93e-b5f5a8a7295d @ 100%` live and
  `8c4e0f6a-dc7a-4f72-9954-ba9cdd91392f @ 0%` rollback.
- Three bindings verified for existing and candidate version; no secrets exposed.
- Old SHA prefixes: app.js `adbd2f21c2803a1e`, i18n.js
  `2c0b099a3a840d78`, styles.css `71ea60a9eaf7c03e`.
- New source parser only reads a validated original TheRarBg detail page.
  Its source-linked `.torrent File` URL embeds the BTIH; NO cache or torrent
  file is fetched, and conflicting original hashes are always rejected.
- Strict 0%-traffic candidate assets and 46-original-provider catalog check,
  5% canary verification, full 100% postflight with prior 056d at 0%
  for rollback; unknown/concurrent Cloudflare split stops safely.
- No Rock64, Tunnel, DNS, BTDigg, Flud, other indexers, credentials or tracking
  changes. One iPhone same-card Genshin Impact 93.2 MB E2E retest follows
  only **after** successful release. Never claim an unverified functional pass.

Workflow: `.github/workflows/magnetra-therarbag-cache-link-one-shot.yml`
Release: `scripts/release_magnetra_therarbag_cache_link_20261022.py`
Unique activation commit marker: `[magnetra-therarbag-cachelink-publish-20261022]`
