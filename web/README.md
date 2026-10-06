# AlexLab Magnetra PWA

This folder contains the first web port of the upstream Android search experience.

## Architecture

- `web/`: static PWA (vanilla JS, manifest, service worker, offline app shell).
- `worker/`: Cloudflare Worker for explicit provider adapters and an allowlisted Flud Companion Remote relay bridge.
- `worker/src/catalog.mjs`: all **46** upstream built-in sources, including transparent `ported: false` flags for unfinished adapters.
- `worker/src/providers.mjs`: first **11** individually implemented adapters; **35 remain to port and verify**.
- `worker/src/index.mjs`: `/api/providers`, `/api/search`, `/api/companion/status`, `/api/companion/magnet`.

## Development

From the repository root:

```sh
python3 scripts/check-project-invariants.py
node --test worker/test/*.test.mjs
node --check web/app.js
npx --yes wrangler@4.45.4 dev --config worker/wrangler.jsonc
```

The local preview is accessible via the URL printed by Wrangler. The Cloudflare Worker serves the static web files; opening `web/index.html` directly as `file://` is insufficient because searches require the same-origin backend.

## Deployment

Cloudflare deployment is **not automatic**. The owner controls a manual `workflow_dispatch` workflow:

`.github/workflows/deploy-pwa.yml`

Provide `CLOUDFLARE_API_TOKEN` (Workers deploy permission) and `CLOUDFLARE_ACCOUNT_ID` **as GitHub Actions secrets**, never in source code, chat, or URLs. Trigger the workflow manually after tests are green. No paid subscription is authorized; use the free tier only.

## Flud Companion

Pair once in the Settings sheet with your existing **Remote Device ID** and **Remote token**. The PWA calls a same-origin API that forwards commands only to:

`https://flud-remote.alexlab.media/api/v1/device/<deviceId>/magnet`

No dynamic target hosts or generic proxy paths are accepted. The browser retains pairing credentials locally. The Worker does not store credentials. The Remote relay only accepts commands while the Shield/Companion is online, and a `202 queued` response means **queued**, not downloaded or confirmed by Flud.

Auto-start uses the Companion's existing validated helper; the PWA does not implement an independent or duplicate magnet handoff. If an iPhone browser cannot open `magnet:` locally, use **Send to Flud** via the Remote relay or **Copy** and open the existing Companion PWA.

## Provider coverage policy

Catalog coverage is not functional parity. When an upstream provider changes:

1. Update the corresponding Worker adapter; do not silently fall back to unrelated search results.
2. Add source-specific fixtures/tests.
3. Mark `ported: true` only once the port exists and is tested.
4. Maintain all 46 upstream IDs (or deliberately reconcile additions/removals with the owner).
5. Document Cloudflare/CORS/provider limits in `docs/PROJECT_STATE.md`.

No production endpoint has been deployed or verified at the time this first scaffold is committed.
