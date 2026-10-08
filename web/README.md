# AlexLab Magnetra PWA

This folder contains the first web port of the upstream Android search experience.

## Architecture

- `web/`: static PWA (vanilla JS, manifest, service worker, offline app shell).
- `worker/`: Cloudflare Worker for explicit provider adapters and an allowlisted Flud Companion Remote relay bridge.
- `worker/src/catalog.mjs`: all **46** upstream built-in sources, including transparent `ported: false` flags for unfinished adapters.
- `worker/src/providers.mjs`: dispatches all **46** executable source adapters (21 pre-existing and 25 additional source-specific implementations).
- `worker/src/legacy-specs.mjs` + `legacy-adapters.mjs`: 25 additional legacy-source contracts, including detail-page magnet resolution.
- `worker/src/index.mjs`: `/api/providers`, `/api/search`, `/api/resolve`, `/api/companion/status`, `/api/companion/magnet`.

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

Canonical production URL: **`https://index.alexlab.media`**. Cloudflare deployment is guarded: normal `main` pushes do not deploy. It runs by manual `workflow_dispatch` or by a `main` commit explicitly containing `[deploy-pwa]`:

`.github/workflows/deploy-pwa.yml`

Provide `CLOUDFLARE_API_TOKEN` (Workers deploy permission) and `CLOUDFLARE_ACCOUNT_ID` **as GitHub Actions secrets**, never in source code, chat, or URLs. No paid subscription is authorized; use the free tier only. The custom domain is declared in `worker/wrangler.jsonc` with `custom_domain: true`.

## Flud Companion

Pair once in the Settings sheet with your existing **Remote Device ID** and **Remote token**. The PWA calls a same-origin API that forwards commands only to:

`https://flud-remote.alexlab.media/api/v1/device/<deviceId>/magnet`

No dynamic target hosts or generic proxy paths are accepted. The browser retains pairing credentials locally. The Worker does not store credentials. The PWA Settings sheet includes a read-only **Test Shield connection** action. The Remote relay only accepts commands while the Shield/Companion is online, and a `202 queued` response means **queued**, not downloaded or confirmed by Flud.

Auto-start uses the Companion's existing validated helper; the PWA does not implement an independent or duplicate magnet handoff. If an iPhone browser cannot open `magnet:` locally, use **Send to Flud** via the Remote relay or **Copy** and open the existing Companion PWA.

## Provider coverage policy

**All 46 source adapters are coded**, but implementation does not prove they currently work against every upstream site. Full live validation remains mandatory. Catalog coverage is not verified uptime. When an upstream provider changes:

1. Update the corresponding Worker adapter; do not silently fall back to unrelated search results.
2. Add source-specific fixtures/tests.
3. Mark `ported: true` only once the adapter exists and passes test contracts. **This flag is not provider-live-verified**.
4. Maintain all 46 upstream IDs (or deliberately reconcile additions/removals with the owner).
5. Document Cloudflare/CORS/provider limits in `docs/PROJECT_STATE.md`.

Production is deployed at **https://index.alexlab.media** (2026-10-08). GitHub-hosted smoke checks passed HTTP+TLS, homepage, manifest, health and 46-entry provider catalog. Provider-level live search reliability, mobile PWA installation and Shield handoff still require independent end-to-end validation.

`python3 scripts/check-production-smoke.py` verifies the public site and is run automatically after canonical Cloudflare deploys. The standalone workflow `.github/workflows/production-smoke.yml` also checks the public endpoint.

### Production provider audit

After each explicitly marked `[deploy-pwa]` deployment, `scripts/audit-live-providers.py` checks all 46 indexers with a benign `ubuntu` search, capped at three concurrent searches, without fetching torrent files or opening magnets. Outcomes distinguish results, empty/unverified, provider errors and request errors. Upstream blocking does not falsely mark repository CI as broken; review job logs for follow-up fixes.

### Live provider audit findings (2026-10-08)

After the 46-adapter deployment, a benign `ubuntu` search returned results from 8 sources, 14 empty/unverified sources and 24 explicit upstream errors, mostly 403. Use job `37763214467` for provider-level evidence. Search results are not guaranteed simply because a source adapter is installed. Cloudflare challenge cookies and upstream server restrictions require independent compatibility work.

The follow-up outbound compatibility layer mirrors the pinned Android `NetworkClient.USER_AGENT` and permits **one same-origin HTTPS redirect**, never arbitrary redirects. Do not silently introduce a generic fetch proxy or third-party paid CAPTCHA service.

## Indexer availability and recovery

The source inventory and implemented adapters do not guarantee live access to each site. On 2026-10-08, BTDigg returned HTTP 429 from GitHub-hosted tests while the production Worker timed out; some other sites required browser verification.

Magnetra now reports distinct error statuses, offers a direct HTTPS source-search link when supported, and a separate search using working alternative indexers. Alternative results always carry the correct indexer name. Browser-restricted results cannot be read back automatically into the PWA.

No paid dependencies are used. See docs/PROJECT_STATE.md for the verified diagnostics.

### Copy from browser → Flud Companion

If you open BTDigg (or another source) directly in Safari, copy a magnet link. Return to Magnetra and press **Paste magnet → Flud**. The clipboard is read only after that explicit tap; if iOS denies clipboard access, a manual paste field opens. The existing paired Remote relay handles the dispatch, and the UI still distinguishes relay queue acceptance from Shield acknowledgement. This is a manual browser-origin fallback, not direct cross-origin scraping.

### Automatic PWA updates

The service worker uses network-first refresh for scripts, styles and the manifest, while retaining an offline shell. API calls, including Flud Companion commands, are never cached. This corrects an older cache-first strategy that could keep iPhone users on stale JavaScript after a successful deployment. After the first update, reopening the PWA normally should pick up fresh assets; a one-time close/reopen may be needed when replacing a previously installed worker.
