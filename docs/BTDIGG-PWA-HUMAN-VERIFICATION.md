# Magnetra PWA — verificare BTDigg în Chromium privat

Status: source + CI candidate; production is NOT activated just because a PR merges.

## Confirmed evidence (15 Nov 2026)

The owner solved BTDigg reCAPTCHA MANUALLY in their existing Chromium/noVNC session.
Magnetra then displayed real BTDigg PSA magnets, followed by 3 relevant
Toy Story results. Chromium reported exactly 1 verified tab, 10 paired
title/magnet rows, and no visible rate limit. Magnetra never solved a CAPTCHA.

## Human-only PWA workflow

1. Authenticated Rock64 8796 preflight reads 18896 browser-state locally.
   A visible human-verification requirement returns private HTTP 428 without
   source requests or browser navigation. A visible Too Many Requests refusal
   remains distinct from a verified HTTP 429.
2. Cloudflare maps the 428 to fixed code BTDIGG_CAPTCHA_REQUIRED.
   Only source errors requiring manual inspection show the button
   'Verify BTDigg inside Magnetra'. No background retry or page polling.
3. The dialog accepts one private HTTPS Tailscale noVNC URL on port 8444.
   It stores only the verified HTTPS origin in iPhone localStorage.
   A user click loads the noVNC iframe. Password and CAPTCHA remain within
   the private VNC connection, never in Cloudflare/Worker or Magnetra APIs.
4. Owner completes the challenge manually if requested. Clicking
   'Verified · Search again' issues exactly one NEW user-requested search;
   closing the dialog tears down the iframe connection.
5. iOS Safari may refuse cross-origin framing; an explicit HTTPS link to
   the same private tailnet viewer is offered as a fallback.

## HTTPS access without touching the verified Chromium

The existing noVNC websockify binds the Rock64 Tailscale IPv4 on port 6088,
not localhost. Tailscale Serve proxies localhost backends. The new Python
TCP adapter binds ONLY to 127.0.0.1:6089 and transparently forwards bytes
to the same host's 100.64/10 Tailscale IPv4:6088. It does not parse URLs,
VNC data, challenge HTML, passwords, cookies, magnets or traffic content.

An owner opt-in Tailscale Serve port 8444 makes the existing noVNC available
inside the tailnet over HTTPS, without modifying Tailscale Serve :443 used
by NexaCore and without enabling public Funnel. Tailscale must be running
on the iPhone to access the private viewer.

Owner private URL after configuration:
https://rock64.example.ts.net:8444/vnc.html

## Owner activation (separate from Cloudflare deployment)

Run as the unprivileged runner user on Rock64:

    cd ~/magnetra-cffi-live-20261028
    git pull --ff-only origin main
    bash rock64/activate-btdigg-captcha-gateway.sh --check
    # only if READY:
    bash rock64/activate-btdigg-captcha-gateway.sh --apply --owner-approved
    bash rock64/install-btdigg-private-novnc-https.sh --check
    # only if READY:
    bash rock64/install-btdigg-private-novnc-https.sh --apply --owner-approved
    python3 -B rock64/check-btdigg-browser-backend.py --browser-status

The first script changes/restarts ONLY 8796 with exact-version backup and
rollback. The second starts a separate 6089 loopback user service and
adds ONLY the unused private Tailscale HTTPS 8444 port. Neither restarts
Chromium 18896, Rock64, Plex or NexaCore. No BTDigg source query is sent.
Stop if CHECK says STOP; do not override existing Serve/Funnel configuration.

Cloudflare Worker/PWA release is a separate reviewed operation. Public
CSP adds only frame-src https://*.ts.net:8444. No general proxy exists.

## Limits

No automatic reCAPTCHA solver, challenge bypass, token sharing, proxy
identity rotation, CAPTCHA farming, background source retry, or new paid
service. Explicit source Retry-After remains authoritative. HTTPS iframe
support must be verified on iPhone; Safari private-link fallback is provided.

## 15 Nov 2026 — first owner HTTPS adapter activation stopped at startup

The owner successfully activated the private CAPTCHA signal on 8796:
BTDIGG_8796=HUMAN_VERIFICATION_428_READY; Chromium 18896 untouched.
The 6089 adapter's offline 3 synthetic tests passed and systemd created
its user-service symlink, but the installer immediately curled port 6089
after systemctl --user enable --now and received ConnectionRefused.
The script exited BEFORE running any Tailscale Serve :8444 command.
This alone is consistent with a Type=simple readiness race, but does not
prove the Python process remained running. First do read-only:

    systemctl --user show magnetra-btdigg-novnc-private.service -p ActiveState -p SubState -p Result -p ExecMainStatus -p MainPID -p NRestarts
    ss -H -ltnp '( sport = :6088 or sport = :6089 )'
    curl --noproxy '*' -sS -o /dev/null -w 'HTTP_6089=%{http_code}\n' --max-time 8 http://127.0.0.1:6089/vnc.html
    journalctl --user -u magnetra-btdigg-novnc-private.service -b -n 25 --no-pager -o cat

The safe follow-up fix makes --check and --apply resumable if an exact
reviewed user-systemd unit controls the local 6089 listener, as shown by
its MainPID. Unknown listeners still STOP. Fresh/recovering Python processes
receive bounded socket + HTTP 200 readiness checks before private Serve
:8444 is configured, with sanitized systemd diagnostics upon failure.
A failed health check NEVER restarts Chromium, gateway, Tailscale :443 or
other services. If the adapter is inactive, inspect journal first; do not
force a second browser or reset Tailscale Serve.
