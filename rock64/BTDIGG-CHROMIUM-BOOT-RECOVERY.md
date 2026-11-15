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
