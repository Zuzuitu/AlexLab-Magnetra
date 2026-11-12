# BTDigg persistent owner-verified browser backend (12 Nov 2026)

## Physically established facts

The user opened a normal *visible Chromium* running on Rock64 through
Tailscale/noVNC. The BTDigg search showed "One more step" and a real
"I'm not a robot" Google reCAPTCHA. After the owner completed it,
genuine source results and magnet links appeared. A second search in
the **same** browser session required no further CAPTCHA.

We have not proven the duration of CAPTCHA acceptance, persistence after
browser restart, or the source operator's authorization for unattended
programmatic access.

## Architecture

The optional local candidate reuses the original `rock64/btdigg_gateway.py`
HTTP handler and `SearchProvider` (positive-only 20-minute cache, at most
one new query per five seconds). It changes the source of authentic HTML
from a stateless HTTP client to a **single persistent, visible Chromium
session** controlled through Playwright's private pipe.

A challenge page is **not** reported as zero matches. Without verified
source result rows, search returns HTTP 503 without retrying upstream.

## Isolated next-query tab and session shutdown (12 Nov owner test)

The owner physically verified the private browser gateway: the original
`--test-search` returned local 200 with genuine bounded HTML and both
source-result and magnet markers. One explicitly different query
`The Dog Stars 2026 720p` navigated the browser but displayed
"Too Many Requests"; local gateway returned 503. This is not a proven empty
search, nor evidence of unrestricted automatic browsing.

One new, explicitly requested query now opens a separate tab **in the same
browser context**. The original owner-verified result tab remains available.
Only a successful HTTP 200 with the correct BTDigg search query and paired
result/magnet HTML promotes the new page. Failed tabs are closed. The first
source refusal or browser navigation failure latches for the lifetime of
that foreground process, preventing repeat upstream requests; previously
verified results remain readable. On success, keep only the reference and
latest successful tab. A new tab neither rotates IPs nor clears cookies,
nor bypasses CAPTCHA or provider rate limits.

The Chromium "Restore pages?" banner shown by the owner is consistent with
a prior unclean shutdown. Closing the foreground terminal also stops the
browser process, though the private browser profile survives. The launcher
now tries a bounded graceful Playwright shutdown (up to 10 seconds) before
stopping VNC; a forced termination, power loss or SIGKILL still cannot be
guaranteed clean. To keep an interactive test running across SSH disconnects,
the owner can optionally start the foreground script from a tmux session
(if tmux is installed), detach with Ctrl+B then D, and later explicitly
stop it with Ctrl+C. This is not a systemd service or production deployment.
Once the human-verified browser has results, a case-only query difference
(e.g., manual `the dog stars 2026` vs. owner probe `The Dog Stars 2026`)
reuses the current verified page without triggering a second navigation.
A genuinely different search still requires its own explicit request.
A subsequent owner-triggered request can navigate within that same browser
and pass original HTML back
to the existing authenticated gateway. The Cloudflare Worker has its
existing HTMLRewriter parser and PSA, group, codec and resolution ranking;
those components are unchanged.

**Not live:** Default public BTDigg remains the existing cffi gateway.
The new gateway is opt-in only, listens on private loopback port 18896,
and requires a separate private bearer credential. The existing port
8796 is blocked by independent source-permission and production gates.

## Prepare the isolated Playwright environment (owner action)

The persistent launcher expects an isolated `~/.venvs/magnetra-browser/bin/python`.
It is **not** included in the default Debian Chromium installation. Run as the
unprivileged `runner` from the repository root:

```bash
bash rock64/setup-btdigg-browser-env.sh --check
```

If this prints `PLAYWRIGHT_ENV=NOT_READY`, opt in explicitly to prepare the
isolated venv (one package install from PyPI; no source search or browser launch):

```bash
bash rock64/setup-btdigg-browser-env.sh --install
bash rock64/setup-btdigg-browser-env.sh --check
python3 -B -m unittest rock64/test_btdigg_browser_setup.py -v
```

Existing, healthy Playwright 1.65.0 or 1.65.1 environments are accepted without
a new download. On an existing venv, ownership and group/world-writable
permissions of the venv root and `pyvenv.cfg` are checked read-only; insecure
permissions fail closed until the owner corrects them, without deleting files.

The installer pins Playwright 1.65.1 for fresh environments, restricts installation to an unprivileged
Linux ARM64 user, requires 512 MiB free space, refuses symlinked paths and
existing non-matching environments, and does not install Playwright's browser
bundle, change system Python, Cloudflare, systemd or port 8796. It reuses
`/usr/bin/chromium`. Package installation needs normal PyPI connectivity
and the Debian `python3-venv` package. On failure it stops without attempting
to repair or delete an existing venv automatically.

## Test procedure (post-merge)

The old visual session uses a **temporary** browser profile. Stopping
it deletes that original profile; transferring a live browser profile
with an active SQLite store is unsafe. Expect to complete CAPTCHA once
in the new persistent profile before benefiting from session reuse.

1. Press Ctrl+C in the terminal running the old noVNC session, freeing
   its Tailnet-only web port.
2. From a fresh Rock64 SSH terminal, as unprivileged `runner`:

```bash
cd "$HOME/magnetra-cffi-live-20261028"
git pull --ff-only
python3 -B -m unittest rock64/test_btdigg_browser_backend.py rock64/test_btdigg_visual_session.py -v
bash rock64/run-btdigg-visual-session.sh --persistent-backend
```

3. First run: choose a VNC password, stored locally for later sessions.
   The script generates a separate random private gateway credential
   automatically; neither credential is printed.
4. On the iPhone, enable Tailscale, open the URL printed by the script
   in Safari, and perform any website CAPTCHA **manually**. Confirm
   BTDigg result cards and magnet links in the browser.
5. From a **second** SSH terminal, while the original session runs:

```bash
cd "$HOME/magnetra-cffi-live-20261028"
python3 rock64/check-btdigg-browser-backend.py
```

The above checks only the local authenticated `/healthz` endpoint; it
does NOT search BTDigg.

6. After the graphical browser has genuine results, optionally do one
   owner-triggered, fixed-query test:

```bash
python3 rock64/check-btdigg-browser-backend.py --test-search
```

The original probe prints only bounded metadata and booleans. For a
stronger functional test of browser-driven source searches, the owner
can explicitly run **one distinct follow-up query** using the same
verified Chromium session:

```bash
python3 rock64/check-btdigg-browser-backend.py --test-next-search
```

This intentionally searches `The Dog Stars 2026 720p`, different
from the bootstrap `The Dog Stars 2026` and grounded in genuine
720p results shown by the source screenshot. Run **only once** after
successful original-query verification; do not auto-repeat if the
source challenges the browser again.

HTTP 200 with both
`source_result_marker=true` and `source_magnet_marker=true` establishes
authentic HTML passing the local browser backend. HTTP 503 means that
verification or genuine source rows are missing, **not** zero matches.
Do not auto-retry HTTP 403/429.

7. Ctrl+C in the foreground terminal ends the browser, noVNC and
   private test gateway. The Chromium profile and its verification
   state remain in the owner-only state directory for future launches.

## Security and deployment boundaries

- No auto CAPTCHA solver, challenge bypass, stealth, IP rotation, proxy
  or imported cookies. Verification expiration is visible and fail-closed.
- No DevTools remote debugging port. The Playwright browser control pipe
  remains private and single-owner; graphical interaction uses only
  Tailscale and password-protected VNC.
- Persistent profile, VNC password and gateway token are private to the
  owner Unix account, not public GitHub files or Cloudflare credentials.
- No background auto-service, new public port, new Cloudflare route,
  systemd mutation, or change to other indexers.
- The browser backend is single-threaded for Playwright thread safety.
  Source search still uses original cache, pacing, validation and limits.
- The profile may expire and require owner intervention. There is no
  supported promise of permanently CAPTCHA-free browsing.
- Before actual production activation, obtain any necessary provider
  permission, verify physical source HTML and user consent, and prepare
  a rollback of the currently functioning BTDigg systemd/tunnel setup.
  The source owner's website may restrict programmatic access even
  after one human verification. A documented, authorized API remains
  the preferred path for reliable unattended operation.
