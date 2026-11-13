# Magnetra: CFFI to Chromium migration (source-only / owner gated)

## Confirmed current state

On the owner's Rock64 (13 November 2026), magnetra-btdigg.service is active at 127.0.0.1:8796 with its effective ExecStart overridden by 50-magnetra-cffi.conf to run btdigg_cffi_gateway.py. Chromium is active on localhost port 18896, but reports verified_tabs=0, selected_tab_verified=false, one tab, and only legacy browser-state capability. The displayed BTDigg page says Too Many Requests. Thus source access is not verified.

The previous generic base-gateway updater failed its post-restart authenticated health probe, restored the previous source and left CFFI running. The exact cause of that transient health failure is still unknown. Cloudflare Worker/PWA #262 is active, but Chromium production routing is not.

## Separate CFFI-aware migration

Do not stack an earlier 20-owner-chromium-bridge.conf under the CFFI 50-magnetra-cffi.conf: the later CFFI ExecStart would still win. Do not delete or replace the existing CFFI override without a reviewed rollback.

The new migrate-btdigg-cffi-to-chromium.sh:
1. Validates exact effective CFFI entrypoint and exactly one existing CFFI drop-in, files and source syntax.
2. Reads only authenticated localhost Chromium 18896/v1/browser-state and production 8796/healthz. Browser must already have genuinely verified results and no active refusal. Legacy browser qualifies only with exactly one selected, validated result tab and no in-process navigation latch. Browser with verified_tabs=0 always fails before any writes.
3. --check performs only read-only checks. No restart, HTTP source search, or file modification.
4. --activate --owner-approved (separate owner action) passes offline regressions, retains a private root-owned copy of the old base gateway, stages the reviewed new base code and private browser credential, and creates a dedicated 60-magnetra-chromium.conf that resets ExecStart and selects Python stdlib btdigg_gateway.py with the separate Chromium bridge flag and systemd LoadCredential.
5. After daemon-reload verifies *effective* ExecStart, restarts only magnetra-btdigg.service, and validates authenticated localhost /healthz with bounded waits. On failure, attempts to restore original code and CFFI service; original 50-magnetra-cffi.conf is preserved.
6. rollback-btdigg-cffi-to-chromium.sh --rollback is a separate owner-invoked script that validates the exact known drop-ins and CFFI backup, restores original base gateway and removes only Chromium migration files.

Neither script starts/stops Chromium, touches tmux/noVNC, changes Cloudflare routes, credentials held by Flud, tunnel, DNS or other services, nor performs a BTDigg source search.

## Owner procedure

After source PR is merged and user does git pull:

    cd ~/magnetra-cffi-live-20261028
    sudo bash rock64/migrate-btdigg-cffi-to-chromium.sh --check

With current verified_tabs=0, expected result: BROWSER_READINESS=NOT_READY and STOP, with no mutation.

Only after the owner's browser independently displays authentic BTDigg result rows again and a separate owner approval:

    sudo bash rock64/migrate-btdigg-cffi-to-chromium.sh --check
    sudo bash rock64/migrate-btdigg-cffi-to-chromium.sh --activate --owner-approved

To revert a successfully migrated service:

    sudo bash rock64/rollback-btdigg-cffi-to-chromium.sh --rollback

Only after verified migration should the owner make one manual BTDigg query in the existing Magnetra iPhone PWA. A healthy localhost /healthz does NOT prove a new upstream search, an indexer result or a valid magnet. Do not repeat source 429 or invent a new search when access is denied.

## Evidence boundaries

These files are source-only; automated CI uses synthetic localhost fixtures and does not execute migration on the physical Rock64. Unrecognized service overrides, changed systemd paths, missing credentials, unverified browser tabs or rate limiting cause a deliberate STOP.
