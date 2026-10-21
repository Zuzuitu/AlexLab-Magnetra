# Magnetra — BTDigg via Rock64 (gateway/tunnel operational, PWA error under diagnosis)

**Purpose:** retain real `btdig.com` results in Magnetra without leaving the PWA.
Historical direct Cloudflare-to-BTDigg fetch attempts returned timeout/429 before the Rock64 activation. This optional
backend uses a dedicated Rock64-owned outgoing connection and the **existing**
BTDigg HTMLRewriter adapter: it does not create a new torrent/DHT index and
does not disguise other providers as BTDigg.

**Current evidence:** on 2026-10-13 the owner verified the installed Rock64 gateway with local HTTP 200, 10 result rows and 10 valid magnet anchors; the public tunnel returned unauthenticated HTTP 401. After the Worker secret was configured, a full real 46-source production audit on 2026-10-13 (run 38361367716) returned 10 BTDigg results; the owner later observed *intermittent* BTDigg search errors, not a permanent failure. See `docs/PROJECT_STATE.md` for evidence limits. BTDigg working in a browser alone never establishes gateway success. Enable production only after the one-shot
real-source check prints `PASS`. Respect 429/challenge responses: no rotating
IP addresses, CAPTCHAs, forced retry loop or web proxy service is implemented.

## Architecture and boundaries

```text
User searches BTDigg within index.alexlab.media
    |
Cloudflare Magnetra Worker (existing /api/search)
    | GET, fixed https://btdigg-rock64.alexlab.media/v1/search?q=...
    | Authorization: Bearer [Worker secret, never in browser]
    v
Cloudflare Tunnel (NEW dedicated tunnel, existing tunnels untouched)
    |
    v
Rock64 localhost:8796 (service only bound 127.0.0.1)
    | HTTP 200 genuine source HTML, bounded 3 MB
    v
https://btdig.com/search?q=... (fixed upstream; no redirects)
    |
    v
Existing BTDigg HTMLRewriter selectors, normal Magnetra results/Flud actions
```

**Fail-closed:** Without `BTDIGG_GATEWAY_TOKEN` in the Worker, the existing
direct Cloudflare adapter remains unchanged. When the Worker secret is present,
it only uses this dedicated gateway for BTDigg; if unavailable/rate-limited,
the source reports a genuine error, never silently falls back to an unrelated
index. All 45 other indexers and the Companion origin are unchanged.

**Resource controls (staged 2026-10-13 update):** fixed HTTPS source, bearer validation before search,
loopback-only bind, 5s minimum interval, one outstanding *upstream* search,
20-minute success-only bounded RAM cache (4 entries / 6 MB), same-query singleflight,
12s upstream timeout, strict 3MB HTML cap, disabled redirects,
no query/token logs and no public arbitrary proxy. Until you run the guarded updater,
the currently installed Rock64 gateway retains its prior 30-second/8-second limits. Service CPU and
memory limits are isolated from the existing NexaPanel/CalciDatum processes.

## Preflight (Rock64, read-only)

From a checkout of this repository's **merged, tested** revision:

```bash
uname -m
python3 --version
command -v cloudflared || true
systemctl is-active nexapanel-preview.service || true
systemctl list-units 'cloudflared*' --no-pager
python3 -m unittest discover -s rock64 -p 'test_*.py' -v
```

The gateway only uses the Python 3 standard library; it does not install pip
packages. If NexaPanel/CalciDatum are running, leave them untouched.

## 1. Install the *separate* gateway service

Use the repo's **guarded, idempotent installer**. It runs local tests,
creates only dedicated Magnetra paths and an isolated systemd unit, generates
a strong token privately on Rock64 and never alters existing CalciDatum,
NexaPanel or cloudflared units. It will NOT set up a Cloudflare tunnel.

From the Magnetra repository checkout on Rock64:

```bash
sudo bash rock64/install-btdigg.sh
```

No secret needs to be copied into the terminal command. The installer won't
replace an existing token, or overwrite a systemd unit owned by another app.

**Never post the token in GitHub, screenshots, logs, chat or a URL.** Read it
privately on the host when you configure the exact same value as a *Secret*
named `BTDIGG_GATEWAY_TOKEN` for the `alexlab-magnetra` Cloudflare Worker.
The name in Rock64's environment file is deliberately different:
`MAGNETRA_BTDIGG_TOKEN`. The token values must match.

## 2. Prove the *Rock64 process* can actually read the source

Run the one-time protected source check:

```bash
sudo python3 /opt/magnetra-btdigg/check-btdigg.py
```

Only a genuine HTTP 200 + real `div.one_result` and valid magnet links yields
`PASS`. If 429, blocked, or empty, **stop here** rather than connecting a
non-working public route. The one-time check never downloads torrent data.

## 3. Cloudflare Tunnel (free baseline, separate process)

From Cloudflare Dashboard → Networking → Tunnels, create a **dedicated**
remotely-managed tunnel named `magnetra-btdigg-rock64`. Publish the hostname

`btdigg-rock64.alexlab.media` → service `http://127.0.0.1:8796`.

The dashboard creates the DNS record. No router port forwarding required.
Do **not** use `cloudflared service install` when other tunnel services are
already present: that would risk overwriting `cloudflared.service`.
This repository provides an independent systemd unit
`rock64/magnetra-btdigg-tunnel.service` instead.

Requires `cloudflared` >= 2025.4.0 with `--token-file`. Check:
`command -v cloudflared` and verify the unit's `ExecStart` path (the sample
expects `/usr/bin/cloudflared`). In the Cloudflare dashboard, copy the token
for **this** tunnel only. Keep it in a root-owned mode-0600
`/etc/magnetra-btdigg/tunnel-token` file using a local editor; never put it
on the command line or send it into chat.

Then:

```bash
sudo install -m 0644 rock64/magnetra-btdigg-tunnel.service /etc/systemd/system/magnetra-btdigg-tunnel.service
sudo systemctl daemon-reload
sudo systemctl enable --now magnetra-btdigg-tunnel.service
sudo systemctl --no-pager --full status magnetra-btdigg-tunnel.service
```

The service uses systemd `LoadCredential` so the token stays private even when
the process runs under a dynamic unprivileged identity.

**Cloudflare Worker same-zone caveat:** Some Worker-to-Cloudflare-hostname
requests can fail with error 1042 without the
`global_fetch_strictly_public` compatibility flag. Do not alter that global
flag preemptively: it can also change network behavior for the existing fixed
Flud Companion relay. Verify the exact tunnel route in an isolated staging
request and authorize a tested targeted change only if 1042 is observed.
Cloudflare docs: https://developers.cloudflare.com/workers/platform/known-issues/

## 4. Activate ONLY after passing both tests

Use the Cloudflare Dashboard for Worker `alexlab-magnetra`:
Settings → Variables and Secrets → add a **Secret** named
`BTDIGG_GATEWAY_TOKEN` with the exact private gateway token. No secret is
committed to `web/`, GitHub or Worker source; do not set it as a public
variable. Ensure the tested code is deployed first; until then the secret must
remain unset. Activation of production is a **separate approval step**.

Test the actual normal `/api/search?q=ubuntu&providers=btdigg` response from
the running Magnetra UI. A successful result must have `provider:"btdigg"`,
a real magnet, and the title from the actual BTDigg page. Verify regular Flud
actions *only on an explicitly chosen lawful result*; the test does not
automatically send torrents to Nvidia Shield.

## Rollback / safety

- Deactivate immediately: delete only Cloudflare Worker
  `BTDIGG_GATEWAY_TOKEN`. Magnetra falls back to its unchanged direct adapter.
- On Rock64: `sudo systemctl disable --now magnetra-btdigg.service magnetra-btdigg-tunnel.service`.
- Do **not** change existing `cloudflared.service`, CalciDatum runners,
  NexaPanel directories, partitions, firewall ports or network routers.
- This is intentionally NOT a generic proxy, and not a proof of bypassing
  BTDigg anti-bot challenges or 429. Respect the site's policies.

Platform references:
- Cloudflare Tunnel routing: https://developers.cloudflare.com/tunnel/concepts/routing/
- Cloudflare Tunnel run parameters: https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/configure-tunnels/run-parameters/

## Operational troubleshooting — 2026-10-13

The physical Rock64 gateway and isolated tunnel are active. Local gateway authenticated HTML probe passed (10 rows / 10 magnets); public tunnel `/healthz` without bearer correctly returned 401. Owner-supplied `/api/search?q=ubuntu&providers=btdigg` JSON captured from a browser reported `total:10`, `ok:true`, `errors:[]`. A separate public HTTP request using Python urllib from Rock64 returned HTML 403; do not treat it as proof that Worker-origin search is broken, nor change account-wide Cloudflare security without examining response headers and browser/network discrepancies.

A BTDigg-specific magnet HTML entity issue in the API JSON was identified: literal `&amp;dn` / `&amp;tr` instead of `&dn` / `&tr`. PR #23 adds a one-layer BTDigg-only correction with both Node and real workerd fixture tests. Until that patch is deliberately deployed, public API responses can still contain these encoded separators. This does not require reinstalling the gateway or tunnel.

## BTDigg stability patch (2026-10-13; staged code, not automatically installed)

The bounded Python gateway stabilization is delivered by PR #26: 20-minute RAM-only success LRU (4 result pages, <=6MB), coalescing duplicate in-flight searches, original 5-second different-query limit, 12-second upstream timeout, no paid services/retries/challenge bypass. Only genuine BTDigg `one_result` HTML pages are cached. Existing Cloudflare Worker 16-second tunnel request timeout is coordinated with this implementation. New code copied to GitHub does not replace the running `/opt/magnetra-btdigg/btdigg_gateway.py`; an explicit guarded staging and `systemctl restart magnetra-btdigg.service` on the physical Rock64 are still required, followed by authenticated `check-btdigg.py` proof. Never run `cloudflared service install`, modify the isolated tunnel, show gateway.env, or touch other systemd units. User must confirm any interrupted or failing post-restart gateway, not assume success merely from CI.


### Guarded upgrade command after the PR has passed CI and merged

In a checkout pinned to the approved merged commit, run:

```bash
sudo bash rock64/update-btdigg.sh
```

This updater validates the source and dedicated systemd unit, runs local Python tests,
stages only the Magnetra gateway source file with a temporary rollback copy,
restarts **only** magnetra-btdigg.service, and verifies its authenticated
`http://127.0.0.1:8796/healthz` endpoint without printing any secrets.
If validation fails, it restores the previous source and attempts to restart
the previous gateway. It does not touch /etc/magnetra-btdigg/gateway.env,
tunnel-token, cloudflared, router, CalciDatum, NexaPanel or Flud Companion.

The updater makes **no direct BTDigg search request**; one human-controlled
`sudo python3 /opt/magnetra-btdigg/check-btdigg.py` can confirm real source
results after the cache starts. No scheduled polling or retries are added.

## Four original Magnetra providers rejected from Cloudflare — read-only diagnosis (2026-10-14)

On the iPhone the owner observed **HTTP 403 / ACCESS_DENIED** for 1337x, BT4G, Ext and EZTV. The exact original hosts from `worker/src/legacy-specs.mjs` are `1337x.to`, `bt4gprx.com`, `ext.to`, and `eztvx.to`. All four have implemented adapters, but source-side 403 means they cannot currently be claimed as fully working. iPhone NordVPN/Tailscale alone will NOT change the Cloudflare Worker's upstream egress. The owner already has a NordVPN subscription but no VPN changes are authorized or necessary before measuring the real source response from Rock64.

Use `python3 -B rock64/probe-blocked-indexers.py` on the physical Rock64 as unprivileged `runner`. It makes **five** fixed HTTPS GET requests: one benign `ubuntu` query for each original source plus an official EZTV API probe (`/api/get-torrents?limit=2&page=1`). Only status, safe classification and elapsed time are printed. Each is at most 9s, inspects at most 256KB, never downloads torrent files/magnets, follows no redirect, reads no secrets, starts no services, changes no DNS/firewall/VPN routes and never affects the existing BTDigg tunnel. Run only once and provide output, not screenshots containing credentials.

The **EZTV official API** requires no key and documents latest torrents and IMDb-ID queries; it does **not** advertise generic full-text `q` search, so do not silently substitute its two recent entries for the source's normal keyword search. A working residential 200 also does not yet prove selectors or detail-page magnet resolution on that path. If residential source HTTP 200/expected structure is verified, consider a separately allowlisted and authenticated **four-source** local gateway + separate Cloudflare Tunnel (not the already stable BTDigg-only gateway), including search **and** deferred details/magnet resolution, with targeted tests and owner-approved rollout. If the home IP itself gets 403, only then evaluate a per-service NordVPN route after explicit owner permission; never send NordVPN password to GitHub/chat or change the OS-wide default route, because Rock64 hosts other critical services.


## BTDigg transport hardening (2026-10-21, source patch — NOT YET INSTALLED ON ROCK64)

Real owner logs from `magnetra-btdigg.service`:
- failures: total **12.852 s** and **12.753 s**, `open_ms=null`, `read_ms=null`, `failure=transport`;
- success: **5.734 s**, open 5.654 s, read 80 ms;
- one independent original public `/api/search?q=ubuntu&providers=btdigg` succeeded in 6.465 s, 7 relevant valid BTIH from 10 raw results; intermittent, not permanent 429/504.
- Owner's `curl --http1.1 --noproxy '*'` from Rock64 received genuine BTDigg HTTP 200 in **1.135 s**: DNS 0.548 s, TCP 0.601 s cumulative, TLS 0.893 s cumulative, TTFB 1.056 s cumulative. A distinct Python IPv4/IPv6 TCP probe had DNS 0.164 s, IPv4 connect 0.056 s, IPv6 immediate error. **This does not prove IPv6 was the root cause**, especially as DNS listed IPv4 first; it proves the generic error classification was insufficient.

**Source-only targeted change:** replace only this Python stdlib gateway's `urllib.request` upstream fetch with a single explicit IPv4 socket to the original **`btdig.com:443`**, `ssl.create_default_context()` with host-correct SNI and CA validation, ALPN `http/1.1`, and one `http.client.HTTPConnection` request over that already verified TLS socket. First IPv4 DNS result only, no per-IP fallback or subsequent request, no redirects, no open proxy, no DNS/network-wide changes. Keep original **12s overall budget** with TCP stage 3s, TLS stage 3s and header/body I/O stage 6s individually, bounded to remaining overall deadline when entering each phase; no timeout increase or bypass. Errors still return authentic 429/503/504 and never cache failures. Gateway remains localhost 8796, current bearer/tunnel untouched. Sanitized timings now include `dns_ms`, `tcp_ms`, `tls_ms`, `open_ms` (TTFB to headers), `read_ms`, `failure` (e.g. `tcp_timeout`, `tls_timeout`, `headers_timeout`), and constant family IPv4. These are source diagnostics, **not a claim that transient upstream outages will disappear**. Offline tests mock the entire socket/TLS/HTTP path and enforce fixed origin, one fetch, TLS SNI and ALPN, rate limit preservation, no challenge acceptance and no query/IP/token in logs.

**Operational deployment after source PR 4/4 CI green and merge:** the existing guarded `rock64/update-btdigg.sh` verifies only this unit, tests the sources and the update, preserves the existing config file and token, temporarily backs up the previous Python gateway, restarts only `magnetra-btdigg.service`, checks authenticated loopback `/healthz`, and automatically restores the backup on failed startup. No Cloudflare traffic/version rollout needed for Rock64-only change. Source presence in GitHub does not imply anything is installed on the physical Rock64. After installing, explicitly **re-enable BTDigg in the iPhone Indexers selector** if previous errors auto-paused it; the previous pause is stored per browser and a Rock64 repair does not silently change it. Confirm real BTDigg query through the normal PWA if needed, without retrying source errors or probing other services.

**Note:** Since a one-off success and error logs cannot isolate the exact remote TCP/TLS/HTTP cause, if this single-connection transport patch still times out, inspect the new *phase-specific* log evidence before any further change. Do not blindly tune global IPv6, OpenWrt DNS, network firewall, Worker secrets, timeout limits, source IP, TLS verification or user agent.
