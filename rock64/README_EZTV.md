# SUPERSEDED: EZTV-only Cloudflare Tunnel plan cancelled

On 2026-10-15 the owner explicitly rejected one Cloudflare Tunnel per indexer. **Do not follow the old standalone EZTV tunnel creation, token, or service instructions below.** The separate EZTV local gateway at 127.0.0.1:8797 remains valid and proven. The new plan is ONE existing BTDigg Tunnel plus ONE central Magnetra dispatcher on localhost:8798; see docs/SHARED_MAGNETRA_GATEWAY.md. The previously staged EZTV tunnel installer/template have been removed by the superseding change. No new public route, gateway dispatcher, or production deployment has been installed by this change. Older notes below are historical only.

---

# EZTV official API via separate Rock64 gateway — staged, NOT activated

Evidence from the physical Rock64 on 2026-10-14 (two successful one-shot probes):
- imdb `tt0460681`: HTTP 200, exact echo, `torrents_count=0`, no `torrents` field.
- recent 2 entries: HTTP 200, 2/2 magnet URLs present.
- filtered by an IMDb ID occurring in recent entries: HTTP 200, exact root/row IMDb IDs, `torrents_count=15`, 2/2 magnet URLs. **Count 15 is upstream total, not 15 fetched rows.**
- GitHub Actions/cloud egress previously returned HTTP 403 for the EZTV origin.

These results verify the source API on this home's IP, NOT connectivity through a new Cloudflare Tunnel. No paid services, NordVPN, or other routes are needed for this prototype.

## Design and isolation

```text
Magnetra /api/search (eztvx ONLY, with private EZTV_GATEWAY_TOKEN)
 -> fixed proposed host https://eztv-rock64.alexlab.media/v1/torrents?imdb_id=NNN
 -> OPTIONAL separate Cloudflare Tunnel (not created yet)
 -> Rock64 127.0.0.1:8797 (new independent service)
 -> GET https://eztvx.to/api/get-torrents?imdb_id=NNN&limit=100&page=1
 -> only original JSON, validated exact IMDb -> existing EZTV parser.
```

TVmaze title-to-IMDb continues via `https://api.tvmaze.com/search/shows` and is never proxied by Rock64. Direct IMDb searches skip TVmaze. If `EZTV_GATEWAY_TOKEN` is absent from the Cloudflare Worker, no requests reach the EZTV gateway and the existing direct Cloudflare behavior is preserved.

**This gateway is single-source and not an open proxy.** The bearer token is checked first. Only GET `/v1/torrents?imdb_id=NNN` and authorized `/healthz` are allowed; no arbitrary hostname, path, redirect, port, file or query parameter. Only HTTPS official EZTV source is fetched. Upstream HTTP 429/403, malformed JSON, mismatched IMDb or errors cause explicit failure; never substitute recent results, never forward an unverified row. One upstream request at a time per IMDb, different queries limited to 3-second gaps, 60-second bounded RAM-only successful-response cache, no disk cache, no retry, maximum 1MB response and 10-second source timeout.

Rock64 preflight on 2026-10-14: 5/5 Python tests PASS, `ss` shows 8797 free, BTDigg reports active and `command -v cloudflared` returns `/usr/local/bin/cloudflared`. The dedicated tunnel template uses this observed path; **recheck the binary and token-file CLI support before configuring or starting the tunnel**. No service has been installed by this preflight.\n\nThe new service does not touch BTDigg's `127.0.0.1:8796`, existing `cloudflared` units, Tailscale, DNS, firewall, Plex, NexaPanel, CalciDatum, Flud or other 44 providers. The proposed separate loopback port **8797 and hostname are not verified to exist or be available yet**.

## Before activation — inspect only

Do not execute the installer or create a tunnel until the owner approves these exact changes.

On Rock64 from a current clean Magnetra checkout of an approved merged revision:
```bash
python3 -B -m unittest discover -s rock64 -p 'test_eztv_gateway.py' -v
python3 -B rock64/inspect-eztv-api.py
command -v cloudflared
ss -ltn '( sport = :8797 )'
systemctl is-active magnetra-btdigg.service || true
systemctl is-active nexapanel-preview.service || true
```
Do not output any credential, .env, tunnel token or other services' private data.

## First-time local service (requires separate approval)

After passing tests and checking port availability, run `sudo bash rock64/install-eztv.sh` from the verified checkout. This guarded installer creates only `/opt/magnetra-eztv`, `/etc/magnetra-eztv/gateway.env` (mode 0600, auto-generated secret) and `magnetra-eztv.service`. It refuses existing unit collisions and symlink paths and will not modify other service units. Local service starts only when the owner explicitly runs the installer.

Perform an **authenticated loopback** smoke without printing the token:
```bash
sudo python3 - <<'PY'
import urllib.request
from pathlib import Path
path=Path('/etc/magnetra-eztv/gateway.env')
token=path.read_text(encoding='ascii').strip().split('=',1)[1]
req=urllib.request.Request('http://127.0.0.1:8797/healthz',headers={'Authorization':'Bearer '+token})
with urllib.request.urlopen(req,timeout=3) as r:
 print('EZTV private health HTTP:',r.status)
PY
```
After the local health check, execute `sudo python3 -B rock64/check-eztv-gateway.py` from the approved Magnetra checkout. This read-only test accesses two fixed GET endpoints (EZTV recent and the authenticated local gateway for one genuine IMDb ID), and outputs only result and valid-magnet **counts**. It never prints the selected IMDb ID, token, title, hash or magnet; it never downloads a torrent or sends to Flud. A `PASS` is required before tunnel activation.

## Optional separate Cloudflare Tunnel — NOT installed by repository code

Use a **new** Cloudflare Tunnel for the proposed `eztv-rock64.alexlab.media` hostname to route to `http://127.0.0.1:8797`. Do NOT use `cloudflared service install`, which could overwrite existing global service ownership. The optional `rock64/magnetra-eztv-tunnel.service` template has separate credentials at `/etc/magnetra-eztv/tunnel-token`; verify actual `cloudflared` path and token-file support before installation. Never paste tokens into chat or GitHub.

Same-zone Worker-to-Tunnel requests may fail with Cloudflare error 1042. Test exact connectivity before altering any compatibility flags, because a global flag may affect existing Flud/BTDigg network behavior. If 1042 cannot be isolated safely, STOP and revisit architecture.

**Only after owner approval and physical end-to-end tests:** configure a Worker **Secret** `EZTV_GATEWAY_TOKEN` (matching the local `MAGNETRA_EZTV_TOKEN`) privately and release through the protected `[deploy-pwa]` workflow. DO NOT configure this in `web/` or as public variables. An ordinary PR merge without deployment leaves production unchanged.

Verify a *known-positive* IMDb (from recent official source) returns >0 authentic `provider:eztvx` results with valid magnet fields through `index.alexlab.media/api/search`. Re-verify the zero-result `tt0460681`, and unrelated BTDigg/default searches. Never send magnets automatically to Flud.

## Rollback
- Remove only Worker `EZTV_GATEWAY_TOKEN` to restore existing direct Cloudflare behavior.
- Separately disable only `magnetra-eztv-tunnel.service` and `magnetra-eztv.service` if installed.
- Do not restart BTDigg or mutate any existing tunnel/network configuration.

## 2026-10-14 — post-install local smoke failed before authenticated health

Owner ran the guarded installer from commit `a51585ef9e27c14da6b7183457491ba11178edca`: twice 5/5 EZTV Python gateway unit tests PASS; `magnetra-eztv.service` enabled and reported active on loopback `127.0.0.1:8797`; the immediately following `check-eztv-gateway.py` printed only its generic FAIL. The missing `EZTV local authenticated health: PASS` proves the failure occurred **before** the recent-source and filtered-source probes. Root cause is **not yet verified**; possibilities include startup readiness, invalid/unavailable local credential file, 401, or local listener failure. Do not reinstall or alter BTDigg.

This follow-up changes **only the read-only acceptance checker**, providing short, bounded retries solely for a refused local health connection after startup, never for provider HTTP 429/403 or searches. It prints the nonsecret failure stage (`credentials`, `local-health`, `recent-source` or `local-filtered`) and safe HTTP status, never tokens, IMDb IDs, magnet URLs or raw response bodies.

Immediate unprivileged health probe:
```bash
systemctl is-active magnetra-eztv.service
ss -ltn '( sport = :8797 )'
curl --noproxy '*' --max-time 3 -sS -o /dev/null -w 'HTTP %{http_code}\\n' http://127.0.0.1:8797/healthz
```
Without Authorization, HTTP **401** is expected when the gateway listener is healthy. If inactive or `000`, inspect only `magnetra-eztv.service`; avoid restarting other units. After merging the checker update, rerun the pinned script with `sudo python3 -B` to get the exact stage. **Do not install a Cloudflare Tunnel or Worker secret until positive local check passes.**

## 2026-10-15 — fixed positive-source validation before gateway acceptance

Physical source proof: the official EZTV API returned valid 16/16,
31/31 and 100/100 magnet-bearing rows (all matching their exact
respective IMDb IDs) from three of four distinct, genuine recent
IMDb samples on the Rock64. The fourth showed honest zero. The prior
local gateway smoke failed after choosing one zero-result IMDb, which
is **not** proof that the gateway cannot return valid magnet data.

Updated `rock64/check-eztv-gateway.py` does **NOT** change or restart
the installed EZTV service. It authenticates the loopback health
first, obtains up to five recent genuine source records, deduplicates up
to four IMDb IDs and performs one official fixed-origin `limit=100`
filtered GET for each until the first **positive** original result with
matching IMDb and valid magnet metadata. It then makes at most **one**
authenticated GET through the installed loopback gateway for the exact
same ID and checks the matching magnet count. Every request is one-shot;
no retries on HTTP 429/403, no fabricated success, no fallback to
other indexers, no credentials, titles, IMDb IDs, magnet URLs or hashes
printed. If none of the four is source-positive, it exits **UNVERIFIED**
without blaming the gateway. A successful result validates the
residential loopback path, **not** Cloudflare Tunnel or production.

After green CI and merged commit, run the updated pinned checker
with `sudo python3 -B` for private local token read; do not reinstall
`magnetra-eztv.service`. Configure no EZTV Cloudflare Tunnel or Worker
Secret without successful source-to-gateway verification and the
owner's separate approval.


## 2026-10-15 — local gateway positive acceptance complete

Owner physically verified `magnetra-eztv.service` running with authenticated
`127.0.0.1:8797`, official filtered EZTV API **100 / 100 genuine matching magnets**
and gateway **100 / 100 genuine matching magnets for the exact same IMDb**. The
up-to-four source-positive acceptance checker now prints `PASS: genuine EZTV
magnet metadata reached isolated local gateway`. BTDigg was independently
`active`. **Stop re-running acceptance/sampling unless later debugging is
needed.** The isolated EZTV API backend is ready for the separately gated tunnel
step; this is *not* public tunnel, DNS, Worker or PWA deployment verification.

The tunnel is NOT created by the scripts. An optional dedicated
`magnetra-eztv-tunnel.service` template exists but has not been installed
or started. Official cloudflared documentation confirms remotely managed
`cloudflared tunnel run --token-file <PATH>` / environment
`TUNNEL_TOKEN_FILE` support requires **cloudflared 2025.4.0 or newer**.
Before beginning an approved activation, inspect locally, without emitting
any sensitive token or existing service environment:
```bash
/usr/local/bin/cloudflared --version
/usr/local/bin/cloudflared tunnel run --help 2>&1 | grep -i -- 'token-file' || true
systemctl is-active magnetra-eztv.service
systemctl is-active magnetra-btdigg.service
systemctl show -p LoadState --value magnetra-eztv-tunnel.service
```
Only after **explicit owner consent**, create a **new** remotely managed Cloudflare
Tunnel in the correct account/zone, routing only `eztv-rock64.alexlab.media`
to `http://127.0.0.1:8797`. Keep its secret token private; do not paste
the `cloudflared service install` token command in chat or execute it.
Use only the independent dedicated service with `LoadCredential` and protected
token file; validate actual machine flag support before starting. Avoid
starting/updating/restarting existing cloudflared, BTDigg, Plex, Flud, NexaPanel
or other systemd services. Do not change global DNS/routes/Tailscale/VPN or
`global_fetch_strictly_public` merely to work around possible same-zone
Worker-to-Tunnel 1042. Stage end-to-end HTTPS authenticated checks before
entering Worker Secret `EZTV_GATEWAY_TOKEN` and owner-approved
`[deploy-pwa]` production deployment, and retain independent rollback.
Source reference for token-file requirements:
`https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/configure-tunnels/run-parameters/`.


## 2026-10-15 — approved scope: NEW tunnel and DNS only, not production PWA

Owner explicitly approved creating the **separate** Cloudflare Tunnel plus
`eztv-rock64.alexlab.media` DNS route, not a Cloudflare Worker production
release, paid services, existing gateway changes or any other Rock64
component. Local authenticated source-to-gateway proof is 100 original
matching magnets direct and 100 matching magnets via 127.0.0.1:8797
for the same real IMDb. No more repeated EZTV sampling is necessary.

### Cloudflare Dashboard (account-owner action)

No ChatGPT Cloudflare management integration/SSH credentials are present;
do not claim remote creation or service activation. With the account
that owns the `alexlab.media` zone, open
[Cloudflare Dashboard](https://dash.cloudflare.com/) >
**Networking > Tunnels > Create Tunnel**. Choose a **new remotely
managed** tunnel named `Magnetra-EZTV-Rock64`, not an existing BTDigg
or Flud tunnel. Add a **Published application** route under Routes:

- Hostname: `eztv-rock64.alexlab.media` (subdomain `eztv-rock64`
  under the existing `alexlab.media` zone).
- Service URL: `http://127.0.0.1:8797`, protocol HTTP.
- No Access policies for this trial; the origin itself authenticates
  all requests including health, and rejects unauthenticated requests.
- Check for **existing conflicting DNS records** before adding the
  route; do not replace an unrelated DNS record.

Cloudflare creates the tunneled DNS CNAME when you add a Published
application route through the Dashboard. **If Cloudflare requires the
connector to become Healthy before the Routes step, first install/start
the dedicated tunnel on Rock64 using its new token (below), click
Continue in Dashboard, and only then add this Published application route.**
Do not execute the Dashboard's suggested global service installer. Do not manually create a
second DNS record unless the Dashboard shows an actionable error.

**Do not run** the Dashboard's `cloudflared service install <TOKEN>`
command; it can conflict with other globally managed cloudflared
services on Rock64. The remotely managed token is a sensitive secret;
never paste it into ChatGPT, GitHub or shell history.

### Dedicated Rock64 install (user physically runs after above)

After creating the new tunnel and obtaining its private token (the
Published application route can follow after the connector is Healthy),
obtain `rock64/install-eztv-tunnel.sh` and
`rock64/magnetra-eztv-tunnel.service` from **the same merged, pinned
GitHub commit**, in the same temporary folder. Execute
`sudo bash install-eztv-tunnel.sh` from that folder, interactively.
The optional installer:

- checks root privilege, installed `/usr/local/bin/cloudflared`
  `>=2025.4.0`, explicit `--token-file` help support, original
  EZTV and BTDigg service activity, local 8797 protected 401;
- refuses replacing any existing token or unit and checks the
  exact dedicated systemd template;
- prompts for the new tunnel token **without terminal echo** using
  Python's getpass, stores it only in root-only
  `/etc/magnetra-eztv/tunnel-token` (mode 0600);
- installs/enables/starts **only** the optional
  `magnetra-eztv-tunnel.service` with `LoadCredential` isolated from
  other cloudflared instances, without editing DNS, gateways,
  global VPN/Tailscale/routes/firewall or other projects.

If token-file or version checks fail, **stop**; do not update the
shared global cloudflared binary automatically. Unit startup only
indicates the local process runs; verify that the newly created
tunnel is **Healthy** in the Cloudflare Dashboard.

### Public boundary verification before any Worker config

From the Rock64 or another network, without credentials:
```bash
curl --max-time 10 -sS -o /dev/null -w 'HTTP %{http_code}\n' \
  https://eztv-rock64.alexlab.media/healthz
```
Expected HTTP **401** from the *origin*, proving the protected
health route is reachable through HTTPS Tunnel. A public 200 without
Authorization is **not** the intended security posture; investigate
before progressing. 502/530/1033/other errors are *not* success.
Never include the gateway token in public chat or command history.

The optional Worker EZTV gateway code already exists but is
disabled without a separate Worker Secret `EZTV_GATEWAY_TOKEN`.
**Do not configure that secret or deploy** the PWA under this
approval. Later isolated Worker-to-Tunnel proof may encounter
same-zone Worker error 1042. Do NOT modify
`global_fetch_strictly_public` or compatibility flags globally, since
other projects rely on the existing fetch/network behavior.
Protect the rollback scope: disable only `magnetra-eztv-tunnel.service`
if required; do not touch BTDigg/Flud or existing tunnels.

Docs: https://developers.cloudflare.com/tunnel/get-started/ ;
https://developers.cloudflare.com/tunnel/reference/tunnel-tokens/ ;
https://developers.cloudflare.com/tunnel/configuration/ .
