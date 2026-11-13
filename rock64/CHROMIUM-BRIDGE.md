# Magnetra — opt-in browser bridge (BTDigg, 13 Nov 2026)

## What this adds

An **opt-in, fail-closed** route from the existing Cloudflare Worker `index.alexlab.media` → existing private Tunnel → Rock64 gateway `127.0.0.1:8796` → human-verified Chromium gateway `127.0.0.1:18896`.

The browser's separate bearer token stays local. The existing Worker secret and Cloudflare Tunnel are unchanged. The gateway defaults to its original direct fixed-origin BTDigg transport unless `MAGNETRA_BTDIGG_CHROMIUM_BRIDGE=1` is supplied together with a secure systemd `LoadCredential=browser_token:...`. There is no fallback to direct BTDigg when browser mode is enabled and the browser fails.

The browser process itself is never restarted, navigated, refreshed, or modified by this bridge installation. The browser backend already enforces fixed BTDigg origin, visible manual verification before new navigation, no CAPTCHA automation, and refusal after source HTTP 429. The bridge requires a **confirmed, already-verified selected tab**. Modern Chromium backends must report `visible_source_rate_limited:false` and `new_searches_paused:false`. A pre-upgrade legacy browser may instead qualify **only** with exactly one tab, that one tab verified as authentic results, `new_searches_paused:false`, and `last_navigation_status:null`. Legacy unverified/multi-tab or missing fields fail closed. A stale visible `Too Many Requests` page is **not permission to probe again**.

## Owner's observed state at development time

Rock64 `tmux magnetra-browser`, Xvfb `:102`, noVNC and `18896` were up, but the GUI displayed `Too Many Requests`; read-only API gave `verified_tabs:0` and the **legacy** browser diagnostics (rate-limit state unknown). The bridge must not be activated in this state. No actual BTDigg 200 was proven by offline tests. There is no provision to bypass the site's refusal or automatic retries.

## Installation sequence (only after the owner confirms normal legitimate source access)

1. Merge this reviewed source PR and `git pull --ff-only origin main` on Rock64. Do not restart the current tmux Chromium just because source code was updated.
2. Run `python3 -B rock64/check-btdigg-browser-backend.py --browser-status`. With the current legacy backend, activation requires exactly one browser tab, `verified_tabs:1`, `selected_tab_verified:true`, `in_process_navigation_latch:false` (the underlying backend's `new_searches_paused:false`), and `last_navigation_status:null`. Modern backends instead require `visible_source_rate_limited:false` and `new_searches_paused:false`. A git pull does not hot-reload Chromium; no restart is necessary just to gain modern diagnostics if the existing single tab becomes verified. If the source page is still old/429 or there are multiple legacy tabs, stop. Never automatically reload to test whether a rate limit expired.
3. When the browser is verified and current source access is confirmed, run `sudo bash rock64/update-btdigg.sh` to install the reviewed production gateway implementation (still **direct upstream** and bridge flag OFF). This script restarts **only** `magnetra-btdigg.service` and checks authenticated `/healthz`.
4. After inspecting preflight output, deliberately opt in with `sudo bash rock64/activate-btdigg-chromium-bridge.sh --enable`. It performs a new **read-only** browser-state preflight and production health check before any change, refuses unverified pages, copies the browser token into a root-owned credential file, creates only a dedicated systemd drop-in, restarts **only** the production BTDigg gateway and verifies `/healthz`. The existing Cloudflare tunnel and Flud remain untouched.
5. Only then make **one manual user-triggered** PWA BTDigg query. Verify actual source-owned name, magnet hash, provider attribution and upstream status. Never infer live availability from `/healthz` or synthetic fixtures.

## Disable / rollback

If the dedicated drop-in was created by this process, deactivate the bridge by removing only `/etc/systemd/system/magnetra-btdigg.service.d/20-owner-chromium-bridge.conf` and `/etc/magnetra-btdigg/browser-token`, then `sudo systemctl daemon-reload` and `sudo systemctl restart magnetra-btdigg.service`. Verify authenticated `/healthz` again. Do not remove the browser profile or stop the tmux session as part of a bridge rollback. The Cloudflare immutable candidate should separately retain its prior version for rollback.

## Security and evidence boundaries

No web browser API or debug port is exposed to LAN or internet. Local bridge uses separate credentials, strict fixed loopback port, bounded JSON/HTML reads and per-request timeouts (3s state + 11s search), no redirects, no retry loops and no release name/token/URL logging. A local 5s pacing 429 is not promoted to source-wide 429. A source 429 still pauses uncached terms. Existing Worker results remain attributed to BTDigg only if they pass its real HTMLRewriter parser. TPB remains independent; ranking unchanged. This code alone does **not** deploy to Cloudflare or change a running Rock64 process.


## Important: existing CFFI `50-magnetra-cffi.conf` override

On the owner's Rock64 the effective systemd unit currently uses `/opt/magnetra-btdigg/.venv-cffi-0.17.0/bin/python -I /opt/magnetra-btdigg/btdigg_cffi_gateway.py` via `/etc/systemd/system/magnetra-btdigg.service.d/50-magnetra-cffi.conf`. The CFFI entrypoint dynamically imports `btdigg_gateway.py` but has its **own** search transport. Changing only the base library is not the same as switching to Chromium. The old `update-btdigg.sh` did not check effective overrides, attempted the base-library replacement, restarted the CFFI service, then failed its short localhost health probe and restored the prior base file. The live process recovered, but the exact cause of that transient health failure is not established by the filtered journal.

The updated source-only updater refuses ANY pre-existing systemd override before changing files, and the owner Chromium activation script also refuses to stack its `20-...` drop-in beneath the existing `50-...` CFFI ExecStart. **Do not remove the CFFI override, restart the browser, or run the original updater in a loop.** Use `python3 -B rock64/check-btdigg-service-entrypoint.py` for a read-only effective-entrypoint inventory (no service requests). A future verified CFFI-to-Chromium migration requires separate owner approval, backups, exact active-unit validation, user-verified BTDigg results, and rollback. While Chromium displays `Too Many Requests` and `verified_tabs=0`, no such activation is permitted.
