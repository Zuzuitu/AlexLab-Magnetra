# AlexLab Magnetra curated picker — owner-authorized activation

Owner approval: 2026-10-21 (requested publication of merged PR #109).

## Scope

Publish exactly the reviewed curated PWA indexer picker (29 selectable, 17 hidden, BTDigg/Torrent9/OxTorrent pinned at top), preserving the original 46 Worker catalog IDs, Rock64 gateways, Flud Companion pairing and existing Cloudflare secret bindings.

## Activation gate

The unique squashed commit title **must include** `[magnetra-curated-publish-20261021]`. This file exists solely to match the dedicated `on: push paths` of `.github/workflows/magnetra-curated-picker-one-shot-release.yml`. PR review and CI alone do not upload or deploy anything. Without both the exact changed path and exact marker, no release job runs.

The guarded workflow first checks the current immutable Cloudflare split and the old JS hash, then uploads an immutable version with preserved secret bindings, verifies zero-percent assets and full 46-entry API catalog, runs 5% canary, and only then promotes to 100%. A known-state rollback to previously verified c86c is available. No source search, torrent transfer, DNS, tunnel, Rock64 or Flud changes.

This document is an **intent record**, not proof of publication. Only a completed release run with confirmed 100% version and asset/API postflight establishes production success; if it stops, inspect real traffic rather than retry blindly.
