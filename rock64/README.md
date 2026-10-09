# Magnetra — BTDigg via Rock64 (STAGING, not installed)

**Purpose:** retain real `btdig.com` results in Magnetra without leaving the PWA.
The current Cloudflare-hosted BTDigg search returns timeout/429. This optional
backend uses a dedicated Rock64-owned outgoing connection and the **existing**
BTDigg HTMLRewriter adapter: it does not create a new torrent/DHT index and
does not disguise other providers as BTDigg.

**Important:** BTDigg working in an iPhone browser does not prove its HTML will
be available to Python on Rock64. Enable production only after the one-shot
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

**Resource controls:** fixed HTTPS source, bearer validation before search,
loopback-only bind, 5s minimum interval, one outstanding search, 30s in-memory
repeat-query cache, 8s upstream timeout, strict 3MB HTML cap, disabled redirect
following, no query/token logs and no public arbitrary proxy. Service CPU and
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
