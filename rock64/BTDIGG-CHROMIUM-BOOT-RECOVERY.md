# BTDigg Chromium: guarded boot recovery (source-only)

## Problem confirmed by owner on 14–15 November 2026

In the working Rock64 installation, the private Chromium browser uses a
persistent profile, a human-accessible Tailscale-only noVNC session and an
authenticated loopback Playwright gateway on port 18896. The production
8796 Chromium bridge rejects any tab without genuine canonical BTDigg HTML
containing paired magnet/results. Owner verified a complete new PWA query
via Chromium, 10/10 pairs, and no 429; its browser-state was
\`selected_tab_verified=true\`.

When the browser starts on \`about:blank\` after a stop or reboot,
Magnetra cannot submit the first PWA query because 8796 rightly refuses
unverified browser contexts. Previously the owner had to open a search in
noVNC manually after every restart.

## Guarded opt-in boot behavior

Source changes on the **private Rock64 browser only**:

- A sanitized private file \`last-verified-query.txt\` contains only the
  most recent strictly canonical query, saved **after validated source HTML
  is observed**. No magnet, HTML, cookies, tokens, VNC password or browser
  storage is exported.
- Only when \`MAGNETRA_BTDIGG_RESTORE_ON_BOOT=1\`, and only if there is
  exactly **one blank tab** and a previously saved private query, launch a
  **single visible Chromium navigation** to the canonical BTDigg search URL.
  Reuse the same persistent session/profile. No new background tab, direct
  HTTP scraping, proxy rotation or verification bypass.
- Before that navigation, write the OS boot UUID to a private 0600 marker.
  Further browser/service restarts in the **same OS boot** cannot
  automatically repeat the source request, including after HTTP 429, 503,
  a challenge, a timeout or a failure to validate HTML.
- A restored existing tab, a different tab or a missing saved query
  triggers **zero** source requests. The 8796 fail-closed rules stay
  untouched. On an upstream challenge, owner verification remains manual.
- On the old tmux launch **without** the opt-in environment, the current
  backend behavior is unchanged.

## User-systemd setup

\`bash rock64/install-btdigg-browser-autostart.sh --check\` is read-only.
After pulling source and offline tests pass, the owner can explicitly run:

\`\`\`bash
bash rock64/install-btdigg-browser-autostart.sh --install --seed-query "The Dog Stars 2026 720p"
\`\`\`

This writes a private seed only if no verified query was saved previously,
then installs/enables a systemd **user** service for the **next boot**.
The installer NEVER starts/stops the current tmux Chromium, restarts 8796,
edits Cloudflare, downloads dependencies or makes BTDigg requests.

User services require an active login session or linger; the script reports
when \`sudo loginctl enable-linger runner\` must be explicitly performed.
Enable linger only after reviewing local host policy. The service depends on
the same reviewed project checkout, Tailscale and installed browser venv.

Do not run both the tmux session and the systemd browser service
simultaneously. The installer only enables next-boot operation and does not
start a second instance. A safe cutover and real OS reboot are **not yet
live-tested** by repository CI. Check \`systemctl --user status
magnetra-btdigg-browser\` and the authenticated browser-state after first
reboot. Success requires \`selected_tab_verified=true\`, \`validation=valid\`,
\`new_searches_paused=false\`, and a new PWA query, not a cached result.

## Security/rollback

Unit is opt-in and files are user-owned/private, not world-readable.
After a failed or undesired restart, \`systemctl --user disable --now
magnetra-btdigg-browser.service\` disables future autostart; it does NOT
erase the saved profile or token. Do not remove the existing CFFI /
Chromium 8796 service override or Cloudflare integration.

## Observed first live OS reboot — 15 November 2026

Owner rebooted the Rock64 and performed the new read-only postboot audit
from `main@67e7b71`. Linger enabled, user-systemd enabled/active,
Chromium 18896 and the 8796 production gateway on loopback, noVNC on
Tailnet 6088, and no duplicate tmux all passed. The user service reported
`NRestarts=2`; the precise cause was not established by the filtered logs.

The one-shot bootstrap returned `BTDigg cold boot: unverified_source`,
and its durable OS-boot marker matched. An authenticated, read-only
browser-state showed `visible_source_rate_limited=true`,
`selected_tab_verified=false`, `paired_rows=0`, and
`new_searches_paused=true`: a source-owned visible "Too Many Requests"
refusal, even though navigation may have succeeded at the HTTP layer.

Owner then ran one PWA query selecting only BTDigg. The PWA showed
"Provider unavailable" because the 8796 bridge mapped the known visible
source denial to generic HTTP 503. The reviewed source-only correction
maps **only an explicitly visible source refusal** to 429; other
unverified tabs still return 503. The existing source-429 cooldown and
local cache remain unchanged. This is a status/reporting correction and
**does not recover access, bypass the source refusal, or prove a fresh
successful production PWA query**. Applying new source code to an
installed running gateway requires a separately authorized deployment.

## Guarded production gateway update (separate owner action)

The new `rock64/update-btdigg-chromium-bridge.sh` supports `--check`
(read-only) and `--apply --owner-approved` (explicitly restarts only
`magnetra-btdigg.service`, never Chromium). It validates the installed
CFFI-then-Chromium override stack, the effective Python entrypoint, an
authenticated localhost health probe and **exact pinned Git blobs** for
old/new gateway source. Any divergence stops before mutation. The apply
path runs offline tests, preserves a protected private backup, replaces
only `/opt/magnetra-btdigg/btdigg_gateway.py`, and rolls back on a failed
service restart or health probe. No BTDigg search is sent by either mode.

Source merge or successful CI is not evidence that the installed 8796
gateway was updated. The owner must separately opt into the apply
command after the preflight says READY. Even after application, the
source may remain rate limited, so a real new PWA result is still not
proven.

## First guarded status upgrade: owner-observed health race

Following merge of PRs #279 and #280, the owner executed the guarded
Chromium-backed 8796 update. All **30 offline fixture tests passed**.
The script then printed `STOP: New 8796 gateway failed authenticated
loopback health.`, attempted a rollback, and printed
`ROLLBACK_GATEWAY_HEALTH=NOT_VERIFIED`. The independent user-Chromium
`/v1/browser-state` remained HTTP 200 but showed the same visible source
refusal. **It does not prove the production 8796 service's state**.

Source inspection found a flaw in the updater: after `systemctl restart`,
it made only one immediate authenticated `/healthz` request. Because the
service uses `Type=simple`, systemd can report active before the loopback
port is bound. The same flaw affects rollback health verification. This is
a plausible explanation, **not a proven root cause** until the production
systemd state, actual port listener, installed-code hash, and sanitized
journal are inspected.

The patched updater polls only the private `127.0.0.1:8796/healthz`
up to 30 attempts separated by 0.5 seconds *after* service restart.
It also safely reuses the private backup left by the failed attempt
**only if** its Git blob matches the exact reviewed old gateway; any
unexpected backup remains fail-closed. The original preflight is
one-shot read-only and tests remain offline. No automatic replay or
new BTDigg source query is performed. An owner invocation and a new
post-update health/status inspection remain required. If the service is
not already healthy, investigate before running the updater again.

## PWA-triggered new-tab recovery — owner-requested 30-second ceiling (candidate)

**Supersedes the earlier proposed 30-minute / 60-minute recovery delays.**
Owner explicitly chose **30 seconds** between an observed BTDigg refusal
and the next eligible *manual PWA search* that creates a new Chromium tab.
No service timer, automatic poller, periodic search or loop creates tabs.

- Rock64 18896: only one controlled tab, an explicitly visible
  "Too Many Requests" refusal or a previously claimed blank boot restore,
  and no visible CAPTCHA may enable a fresh tab. First read-only state
  observation starts 30 seconds; later user-requested queries can initiate
  at most one new-tab navigation. A repeated refusal waits another 30
  seconds and requires another PWA action. A human challenge stops recovery.
- If genuine BTDigg HTML with paired title/BTIH magnet anchors is validated
  on the new tab, the browser switches ownership and closes the old tab.
  On failure the newly created tab closes and the old tab is preserved.
- Rock64 8796: its self-imposed source-refusal lock is 30 seconds
  (instead of 300). The lock protects all uncached different terms and
  preserves the genuine 20-minute positive in-memory source cache.
- Cloudflare Worker: BTDigg's default 429 suppression is 30 seconds
  per isolate; a *real* longer numeric source `Retry-After` continues to
  be respected up to its existing bounded maximum. No provider substitution
  and no cross-isolate coordination claim.
- iPhone PWA: locally persisted BTDigg rate-refusal cooldown is 30 seconds
  regardless of consecutive user errors; no automatic re-query. The
  existing faster pacing for ordinary verified searches is unaffected.
- No source/IP identity rotation, CAPTCHA solving, automated challenges,
  direct HTTP fallback, hidden background retries, or new paid services.

The 30-second deadline is **local scheduling policy, NOT a promise that
BTDigg will lift a real server-side rate limit in 30 seconds**. If the
source continues refusing requests, the PWA must still report refusal
rather than fabricate matches. Explicit server Retry-After or a visible
human challenge remains authoritative.

**Implementation status:** repository source/CI candidate only, no
production Chromium 18896 restart, gateway 8796 install, Cloudflare
production deploy, PWA asset publication or live BTDigg search performed
in creating this change. Each requires a separate guarded operator
action and validation. Do not confuse a successful unit test with
production recovery.
