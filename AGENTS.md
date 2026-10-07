# AGENTS.md — AlexLab Magnetra contributor contract

This repository is the persistent technical memory for AlexLab Magnetra. Do not treat old chat context as the source of truth.

## Before any material change

1. Read `docs/PROJECT_STATE.md`.
2. Read `config/project-invariants.json`.
3. Inspect the current implementation on the main branch before assuming behavior from prior conversations.
4. Run `python3 scripts/check-project-invariants.py`.
5. If code, config, checkpoint, and implementation contradict each other, stop the feature change and reconcile the inconsistency first.

## Critical invariants

Do not change a critical invariant without explicit owner approval.

If the owner intentionally changes an invariant, update in the same pull request:

- implementation/configuration;
- `docs/PROJECT_STATE.md`;
- `config/project-invariants.json`;
- tests and/or invariant guards that protect it.

Never leave the checkpoint behind the code.

## Repository workflow

- Use a branch + pull request for material changes.
- Do not push material implementation changes directly to `main`.
- Keep changes scoped and reviewable.
- Preserve upstream syncability with `prajwalch/TorrentSearch`; avoid unnecessary churn in upstream Android files.
- Do not activate paid services, paid APIs, higher-cost tiers, or recurring paid infrastructure without explicit owner approval.
- Do not "modernize" versions/configuration solely because newer values exist. Existing values may represent provider, compatibility, cost, or stability constraints.

## Security

- Never commit secrets, tokens, private keys, signing keystores, service-account credentials, or real `.env` files.
- Release signing values must remain external to the repository.
- Never put private credentials in `web/`, public/static assets, client bundles, or public environment variables.
- Backend/provider proxy routes must be allowlisted; do not create a generic open proxy.

## PWA architecture

- Keep the existing Android source under `app/`.
- Add the PWA under `web/`.
- Add server-side provider/proxy logic under `worker/` when browser CORS or provider protections require it.
- Do not replace the Android app just to create the PWA.
- Preserve magnet/copy/share behavior and expose `.torrent` downloads when a provider supplies them.
- The PWA is not a BitTorrent engine unless the owner explicitly approves a future architecture change.

## Provider parity and Companion-specific protections

- Upstream source of truth is `app/src/main/kotlin/com/prajwalch/torrentsearch/di/BuiltinSearchProvidersModule.kt`: 46 registered providers today. Preserve all IDs in `worker/src/catalog.mjs` and update the manifest/guard if upstream changes.
- **Do not misrepresent inventory entries as functional adapters.** Only mark a provider `ported: true` after a real provider implementation exists and suitable tests pass. Full 46/46 functional coverage remains the target.
- Never use an arbitrary URL proxy. Companion remote relay calls are routed to one allowlisted HTTPS host. Keep tokens out of URLs, service worker caches and logs.
- Companion magnet commands must use idempotency request IDs; don't claim queued means downloaded. Never modify the proven Flood/Flud Auto-start boundary in another repository as part of a PWA convenience feature.

## Technical-memory maintenance

Update `docs/PROJECT_STATE.md` naturally after important milestones when any of these appear:

- definitive technical decisions;
- architecture changes;
- important bug root causes/fixes;
- new external limitations/workarounds;
- new critical invariants.

When explicitly asked to “Actualizează checkpoint-ul proiectului cu toate deciziile din această sesiune.”, verify current `main`, review only decisions actually made in the current session, and synchronize the repository memory without inventing decisions or deleting still-relevant history.
