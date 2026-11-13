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

## Opt-in offline Chromium-to-gateway fixture test (13 Nov)

The physical owner confirmed `19/19 PASS` for the Rock64 gateway
and a still-running legacy browser with `verified_tabs:0`. The current
BTDigg source must NOT be probed just to test this architecture.

A standalone smoke harness is now available in
`rock64/check-btdigg-offline-chromium-path.py`. Unlike the live GUI, it
creates a separate **temporary headless Chromium profile**. Every page
request is intercepted locally; one fake BTDigg-shaped PSA result and one
fake HTTP 429 are served in memory and all other requests are aborted.
It verifies real Chromium selectors, original HTML and magnet pairing,
the authenticated loopback gateway, caching the exact query, and source
429 pause without following new searches. It does not prove that BTDigg
has this release or that access to the actual site has recovered.

```bash
cd "$HOME/magnetra-cffi-live-20261028"
git pull --ff-only
python3 -B -m unittest rock64/test_btdigg_offline_chromium_path.py -v
"$HOME/.venvs/magnetra-browser/bin/python" rock64/check-btdigg-offline-chromium-path.py
```

The first two commands are source/test-only. The final command launches
one isolated temporary Chromium for the test but **does not reuse,
restart or send messages to** the live tmux browser or ports 18896, 8796
and 6088. Its output should contain `"result":"PASS"`,
`"requests_to_btdigg_origin":0` and
`"proof":"synthetic_fixture_not_source_availability"`.
A failure returns `"result":"FAIL"` with a generic exception class,
without raw queries, source HTML, tokens, IP addresses or magnets.
The CI suite checks static and localhost-only contracts without
launching Chromium. It does not replace a real Cloudflare HTMLRewriter
runtime validation; a separate guarded stage is still required.

## Private BTDigg rate-limit scope header (Worker ↔ Rock64 source only)

When the Rock64 gateway responds with HTTP 429, it now labels its *own*
authenticated response with `x-magnetra-btdigg-429-scope: source` if the
real fetcher previously received source 429, or `local-pacing` if the
five-second minimum search gap was enforced locally without source traffic.
The `Retry-After` header remains numeric seconds, with a local-pacing
minimum of five seconds; a source refusal reports its remaining five-minute
deadline. The header does not expose queries, cookies, tokens, IPs or magnets.

The private Worker BTDigg adapter treats `local-pacing` as a safe
`RATE_LIMIT` error but does **not** start the Worker five-minute upstream
refusal timer. For source refusal it passes a strictly parsed numeric
`Retry-After` into the existing BTDigg Worker-isolate cache, capped at
30 minutes, with no automated retry. Missing scope on older gateways
continues to be treated conservatively as source 429. This is protocol
parity and offline test coverage, not a live switch to browser port 18896.

The owner physically confirmed 18/18 offline tests on Rock64 at main
`8da0b7d` before this source-only change. No restart is needed to
run new offline tests after pulling the source. The already-running
Chromium backend, gateway on port 18896 and active production port
8796 do not hot-reload from a Git pull. Don't restart them to test 429
metadata while BTDigg is refusing searches.

## Source HTTP 429 pause in gateway (not the live browser)

The new gateway-source candidate adds one source-only five-minute refusal
deadline shared by all searches handled by a given Rock64 gateway process.
Only a real `fetcher() -> 429` establishes it; a local 5-second pacing 429
does not. Original positive cache hits remain eligible for the same query.
A response during the pause includes a bounded `Retry-After` reflecting
the remaining deadline. There is no timer, automatic retry or provider
network probe. Other indexers and other Rock64 services are unchanged.

Tests: `python3 -B -m unittest rock64/test_btdigg_gateway.py -v`
run locally without BTDigg source calls. Code merge alone does not restart
the running tmux Chromium process or change production gateway port 8796;
do not restart a live process solely to observe this new deadline.

## Read-only Xvfb/noVNC process inventory (no Chromium restart)

The owner's `pgrep` showed four Xvfb displays (`:99`–`:102`) with
one active `x11vnc -display :102`, backend and websockify process. This
snapshot cannot establish whether the earlier displays belong to other
applications or were abandoned; nor does it establish the cause of the
Chromium "Restore pages" banner or the provider's rate limit.

After updating GitHub source, from an ordinary SSH shell:

```bash
cd "$HOME/magnetra-cffi-live-20261028"
python3 rock64/check-btdigg-visual-processes.py
```

The script reads only the local process list and tmux session names. It
outputs sanitized PIDs, display IDs and booleans, without URLs, VNC auth
paths, tokens, queries or cookies. It never contacts BTDigg, opens
Chromium, restarts the gateway, or kills any processes. An Xvfb display
in `displays_without_observed_vnc` is **not proven orphaned** and must
not be killed based on this report alone. Preserve the current tmux
session and request an explicit review before considering a cleanup.

## Chromium startup and local profile exit markers

The persistent backend no longer has a default `page.goto()` search
on startup: if Chromium starts on a blank page, it remains blank until
the owner navigates manually in the visible noVNC session. This avoids
adding an explicit source request when the source currently refuses
new searches. **Chromium may still itself restore/reload a persisted
tab**, so this change cannot guarantee zero upstream requests after a
process restart; never restart just to exercise the diagnostic.

Before ending the current tmux session, a read-only local marker check
may be run from another SSH shell (no Playwright API and no internet):

```bash
cd "$HOME/magnetra-cffi-live-20261028"
python3 rock64/check-btdigg-browser-backend.py --profile-exit-state
```

This reports only `profile_marker_available`, `exit_type`,
`exited_cleanly` and a runtime caveat. Chromium sometimes marks its
profile `Crashed` / `exited_cleanly=false` **while it is still running**,
so such live values do NOT prove a bad prior shutdown. Do not modify
the profile or click Restore based solely on these marker values.
To determine whether the next intentional shutdown is clean, compare
markers when the Chromium process is fully stopped, after normal
Playwright `context.close()`. No background observer or source request
is introduced.

## Source refusal visibly present after restart

The owner provided an actual noVNC screenshot showing `Too Many Requests`
inside the existing Chromium BTDigg page and Chromium's "Restore pages"
banner. The local browser-status route had reported 1 tab, 0 verified result
tabs, no tracked navigation refusal, and `new_searches_paused=false`.
This last field only represented the in-process navigation latch, **not**
source availability. The restart-related banner is consistent with an
unclean browser exit at some point, but does not prove when or whether the
source refused because of that exit.

The new source-only behavior recognizes the exact `Too Many Requests`
text of an already open canonical BTDigg page. Its authenticated status
reports `visible_source_rate_limited=true` and
`new_searches_paused=true`, while keeping
`last_navigation_status=null` unless a real browser navigation response
was observed by this process. This DOM-only observation never visits the
source. A distinct uncached owner-requested query is locally rejected
without an upstream attempt while the refusal remains visible. Previously
verified tabs may still be reused for their exact queries. The
implementation does not dismiss Chromium's restore banner, reset cookies,
try different IPs, or suppress provider refusals.

The current owner-controlled tmux browser process does not hot-reload
GitHub changes. Avoid restarting a live session simply for this diagnostic:
a restart could reload/reopen a source page even when the browser does not
deliberately run a new query.

## Older running Chromium process and source-status uncertainty

A Rock64 code update does not reload the process already launched in tmux.
The older `/v1/browser-state` route may omit
`visible_source_rate_limited`, even while the visible GUI still shows a
BTDigg refusal. The local read-only checker now reports that generation as
`diagnostic_capability: legacy_navigation_latch_only`,
`visible_source_rate_limited: null`, and
`new_searches_paused: null`, while retaining
`in_process_navigation_latch` as a historical process-only field.
Null is UNKNOWN, not a signal to send a new query. The newer process
reports `diagnostic_capability: visible_source_rate_limit_detection`
with the actual boolean fields.

Use `python3 rock64/check-btdigg-browser-backend.py --browser-status`
without restarting Chromium or visiting the source. This only queries the
already-running authenticated loopback gateway.

## Read-only browser state after owner-controlled tmux detach

The owner physically confirmed persistent Chromium/noVNC remains available
after detaching from tmux and reconnecting Safari, and the local gateway
still returns HTTP 200. This verifies process and GUI continuity, not
that BTDigg is accepting new queries.

A new authenticated test-only route `/v1/browser-state` reports only
`browser_connected`, `open_tabs`, `verified_tabs`,
`selected_tab_verified`, `new_searches_paused`, and
`last_navigation_status`. It reads the **existing browser DOM** without
visiting BTDigg or triggering a query; it never exposes titles, query URLs,
magnet links, cookies or access tokens.

After the owner updates source and explicitly restarts the experimental
backend, invoke from another SSH shell:

```bash
cd "$HOME/magnetra-cffi-live-20261028"
python3 rock64/check-btdigg-browser-backend.py --browser-status
```

The script never requests BTDigg. A 200 from the ordinary `/healthz`
only proves that the gateway is alive, not that a browser tab is verified.
A 200 from `--browser-status` with `verified_tabs >= 1` proves the
gateway observed a previously loaded result page with paired magnets.
It does not mean that BTDigg currently accepts new requests.
The browser can reuse a *manually opened, already verified* tab for the
same requested query; refusal remains latched for any **new automated**
navigation. No retry or challenge bypass is introduced.

If an owner-run tmux session is currently healthy, do not interrupt it
just to exercise the new endpoint. These source changes only take effect
after an intentional restart with `git pull --ff-only` and the original
safe launcher; the persistent profile survives, but server verification
can still expire. No automatic systemd process or production route is set.

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
