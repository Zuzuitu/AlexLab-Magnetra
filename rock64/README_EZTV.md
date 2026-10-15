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
