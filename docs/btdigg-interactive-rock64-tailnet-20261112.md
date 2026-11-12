# BTDigg interactive Chromium on Rock64 — owner-operated one-shot check

**Purpose:** Check the visible Google reCAPTCHA behavior in normal graphical
Chromium on the *same Rock64* on which the automated BTDigg pilot received a
59,180-character HTML verification page and zero torrent result rows. This
does **not** connect the browser to Magnetra's production PWA/API or solve
CAPTCHA automatically.

## Prerequisites

- Run unprivileged as `runner` on Rock64, not as root.
- Debian 13 ARM64 packages: `chromium xvfb xauth x11vnc novnc websockify`.
- Tailscale active on Rock64, providing its normal `100.64.0.0/10` IPv4.
- **Enable the Tailscale app on the iPhone**, logged into the same tailnet.
- The desktop is accessed only over Tailscale, not the public Internet, router
  port forwarding, or Cloudflare Tunnel.

After updating the Git checkout:

```bash
cd "$HOME/magnetra-cffi-live-20261028"
git pull --ff-only
python3 -B -m unittest rock64/test_btdigg_visual_session.py -v
bash rock64/run-btdigg-visual-session.sh
```

The script prompts for a fresh **temporary VNC password**. Choose at least
eight characters. Note that classic VNC authentication uses **only the first
eight characters**; Tailscale adds the encrypted and access-controlled
network transport. Never put the password in a shell command or URL.

Once it launches, it prints a link in this form:

```text
http://100.x.y.z:6088/vnc.html?autoconnect=1&resize=remote
```

Open that link in Safari while Tailscale is connected on the iPhone. Enter the
temporary VNC password. The graphical Chromium should already be at the exact
owner-verified BTDigg search URL, with `order=0`, searching
`The Dog Stars 2026`.

If a CAPTCHA appears, **the owner** may choose to interact with it manually
in the site as normal. Observe whether ordinary source result cards and
magnet links become visible *on the Rock64 browser*. A loaded CAPTCHA or
HTTP 200 is **not** search success.

## Network and cleanup boundaries

- Xvfb chooses an isolated display and disables X11 TCP connections;
  `xvfb-run` manages Xauthority.
- `x11vnc` listens on **loopback only**, port 5993, and requires the
  temporary password file with mode 0600.
- `websockify` binds explicitly to the **Rock64 Tailscale IPv4 only**,
  port 6088, serving Debian's local noVNC files.
- Chromium uses a temporary, private on-disk browser profile that is deleted
  when the session exits; no browser session is imported.
- Script runs in the foreground; closing Chromium or pressing Ctrl+C in the
  running SSH terminal terminates the temporary services and removes the
  session directory. No persistent systemd unit, cron, cloud tunnel,
  Cloudflare Worker route, web PWA, or existing cffi gateway is touched.
- No automatic verification, token capture, IP rotation, stealth tooling,
  source crawling, or background source polling. Only BTDigg's normal
  human-facing website is opened as one browser tab.

**If a browser shows the same challenge even after legitimate manual
interaction, stop:** the site may continue to restrict automated/server
requests. Do not interpret interactive access as authorization to build a
background scraper or reuse CAPTCHA session cookies.

### Diagnostic errors

- `Missing xauth`: the `xauth` package was not installed.
- `Tailscale has no IPv4`: verify `tailscale status` and the login.
- `websockify failed to bind`: port 6088 may already be occupied or the
  Tailscale interface is down.
- `x11vnc failed to start`: verify Debian package installation and that the
  Xvfb session is available.
- noVNC page unreachable: confirm the iPhone's Tailscale app is connected
  and tailnet ACLs allow the iPhone to reach port 6088 on Rock64.

**Expected feedback:** what the VNC screen actually shows (CAPTCHA checkbox,
challenge, BTDigg results, or a site error), and whether results appear after
any manual verification. Do not share VNC credentials, cookies, magnet URLs,
or internal token values.
