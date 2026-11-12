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
Once the human-verified browser has results, a subsequent owner-triggered
request can navigate within that same browser and pass original HTML back
to the existing authenticated gateway. The Cloudflare Worker has its
existing HTMLRewriter parser and PSA, group, codec and resolution ranking;
those components are unchanged.

**Not live:** Default public BTDigg remains the existing cffi gateway.
The new gateway is opt-in only, listens on private loopback port 18896,
and requires a separate private bearer credential. The existing port
8796 is blocked by independent source-permission and production gates.

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

The probe prints only bounded metadata and booleans. HTTP 200 with both
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
