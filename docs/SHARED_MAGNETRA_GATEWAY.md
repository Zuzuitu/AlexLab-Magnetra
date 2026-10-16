# Magnetra: ONE existing Cloudflare Tunnel for all recoverable providers

2026-10-15: owner explicitly rejects per-indexer tunnels. **CANCEL the
separate EZTV Cloudflare tunnel setup instructions and installer from PR #48.**
Keep existing EZTV gateway on Rock64. This plan supersedes previous EZTV
tunnel setup directions, but does not itself install or deploy anything.

## Existing physical evidence

- Existing BTDigg loopback port 8796, existing BTDigg tunnel/Cloudflare
  hostname, existing authenticated EZTV gateway on loopback port 8797.
- The owner verified exactly 100/100 authentic matching EZTV magnet records
  through the 8797 gateway for the same IMDb as the direct original source.
  BTDigg and EZTV gateway services were both active.
- PWA retains 46 original indexer identities. Existing OPTIONAL EZTV Worker
  points at the no-longer-approved hostname eztv-rock64.alexlab.media, but
  without its private Worker Secret it is disabled. DO NOT activate this old
  hostname or set this secret. Future central route requires new scoped PR.
- We have GitHub changes available but not direct Cloudflare account access
  or SSH to physical Rock64. The actual management mode/configuration of
  the existing BTDigg tunnel has not yet been confirmed in Dashboard.

## Central topology (staged proposal; NOT live)

    Magnetra PWA / Cloudflare Worker (46 source IDs)
       -> one authenticated https://magnetra-rock64.alexlab.media
          -> ONE EXISTING BTDigg Cloudflare tunnel connector
             -> new read-only 127.0.0.1:8798 dispatcher
                -> EZTV local 127.0.0.1:8797
                -> BTDigg local 127.0.0.1:8796 (optional later, approved)
                -> future verified OxTorrent/Torrent9 adapters
                -> future independently proven indexers

Retain the CURRENT published BTDigg hostname -> localhost:8796, unchanged.
Add only ONE new Cloudflare Published application on the SAME existing
tunnel: magnetra-rock64.alexlab.media -> http://127.0.0.1:8798.
Cloudflare supports multiple hostname-to-service mappings under one
connector. This is NOT a new Tunnel, cloudflared process, or DNS entry
per indexer. Once the dispatcher has approved new source-specific
handlers, they need no new public domains or tunnel settings.

The new loopback dispatcher must have a separate strong authentication
secret, fixed provider IDs and paths, fixed original/source-approved
upstream hosts, no arbitrary URLs, no source substitution, no origin
redirect escape, conservative timeouts/body size/thread limits,
per-provider rate limits, and no logging of tokens/magnet hashes/titles.
It must preserve original source attribution, authorized deferred
details/magnet behavior and current 46-provider PWA inventory.
No broad proxy can be exposed. Do not disrupt the current BTDigg/EZTV
services while developing the dispatcher.

## What the 2026-10-15 source evidence means

- EZTV: proven real, genuine 100/100 matching magnet metadata through
  the separate authenticated Rock64 gateway.
- OxTorrent: original HTTP 301 to www.oxtorrent.co. Candidate host
  returns HTTP 200, but only 3 generic table rows and 0 magnet anchors
  detected. Search results/deferred magnets NOT confirmed.
- Torrent9: original HTTP 301 to www7.torrent9.to. Candidate HTTP 200,
  4 generic table rows and no verified magnet data. NOT confirmed.
- BitSearch: original redirect to bitsearch.eu, HTTP 520 there.
- Torrentz: transport failure before HTTP from residential Rock64.
- UIndex, 1337x, BT4G, Ext, TorrentDatabase, TorrentDownloads and
  TokyoToshokan: all HTTP 403 even from Rock64. Routing through Rock64
  cannot fix those without a separately verified source-side solution.
- Other 46 providers: retain last historical audit, provider IDs and
  all existing working adapters. Do not replace rows with other sources.

## Gated implementation steps

1. Verify via owner read-only Rock64 check-shared-tunnel.sh that BTDigg
   tunnel and EZTV/BTDigg backend are active, loopback 8796/8797 listen,
   8798 is free, and unauth /healthz returns 401. Also confirm in
   Cloudflare Dashboard that the EXISTING BTDigg tunnel supports another
   Published application route. Never print tokens/service ExecStart.
2. Stage the new 8798 dispatcher with OFFLINE tests in a dedicated PR.
   Forward EZTV to the existing separate 8797 service using its
   private local token; do not change its unit. Additional providers
   only after real parser/source and magnet-resolution tests.
3. Validate the canonical redirected OxTorrent/Torrent9 sources with
   genuine HTML search rows and verified source-host details/magnet
   path. HTML 200 or a table alone is NOT a working indexer.
4. For HTTP 403/520/network failures, investigate actual source status,
   protected/authorized public endpoints, and independently scoped,
   owner-approved egress if practical. A new central tunnel does NOT
   change the outbound residential IP; optional isolated paid/owned
   VPN/SOCKS5 egress cannot be assumed to work and must not alter
   default routes, Tailscale, DNS, BTDigg, Plex, Flud, NexaPanel or
   CalciDatum. Never fake results, auto-retry rate limits or bypass
   challenges without explicit source authorization.
5. When the local dispatcher has passed real acceptance and has owner
   approval, add one new Published application hostname through the
   SAME existing BTDigg Cloudflare Tunnel to localhost:8798. Preserve
   existing hostname and route. Unauth public health should be 401.
6. Cloudflare Worker calling another hostname in the same zone may
   encounter error 1042. Verify a staging request first. DO NOT change
   the PWA Worker's global_fetch_strictly_public compatibility flag
   because it can affect existing Flud/BTDigg traffic. If needed,
   investigate a SECOND, narrowly scoped EGRESS WORKER with isolated
   compatibility settings and a service binding, not a second Tunnel.
7. Add Worker secret and guarded PWA production deployment only after
   real end-to-end success and separate owner approval. PR merge does
   NOT deploy Magnetra.

Rollback must affect only NEW dispatcher and NEW hostname route, not
the original BTDigg tunnel connector or local services.

Source Cloudflare docs:
https://developers.cloudflare.com/tunnel/concepts/routing/
https://developers.cloudflare.com/workers/observability/errors/


## 2026-10-15 — STAGED implementation; NOT installed or publicly routed

With the owner's explicit confirmation to **reuse the existing tunnel and
preserve its BTDigg route**, new isolated code is staged under:
`rock64/magnetra_gateway.py` (new optional 127.0.0.1:8798 dispatcher),
`rock64/magnetra-gateway.service` (optional standalone systemd template,
NOT installed), `rock64/test_magnetra_gateway.py` (offline/fake and
ephemeral-localhost-only unit tests). **No installer was executed**; no
root token, DNS record, tunnel route or new daemon exists as a result
of repository changes.

The new dispatcher initially supports **ONE exact provider-specific**
authenticated GET endpoint:
`GET /v1/eztvx/torrents?imdb_id=<5-12 digits>`. It checks its own
private `MAGNETRA_GATEWAY_TOKEN` first; on positive validation it
makes an authenticated direct *loopback-only* GET to the existing
`127.0.0.1:8797/v1/torrents?imdb_id=...` with the separate
`MAGNETRA_EZTV_TOKEN`. These two secrets must differ. All tokens stay
on server processes, never in Git, PWA client assets, query strings or
logs. Unlike a URL proxy, arbitrary URLs, extra parameters, other
paths or providers are rejected. The response is JSON with the
original IMDb echo, matching IMDb rows and genuine magnet syntax
verified, size-capped at 1MB and no retry/cache; source 403/429/504
are preserved without fabricated fallback. Upstream EZTV's existing
per-query rate limiting and RAM-only cache are left alone.
Port 8796/Btdigg is **not referenced by the dispatcher** and its
Cloudflare route is untouched.

The Cloudflare Worker optional EZTV adapter
`worker/src/eztv-rock64.mjs` is *staged* to call
`https://magnetra-rock64.alexlab.media/v1/eztvx/torrents` only when
new server-side Worker Secret `MAGNETRA_GATEWAY_TOKEN` is configured
**after** a distinct activation approval. The retired
`EZTV_GATEWAY_TOKEN` does NOT enable the old EZTV-only hostname.
No actual PWA deployment accompanies a PR merge.

Next actual owner milestone is still **read-only**
`rock64/check-shared-tunnel.sh` on physical Rock64 and a private
Cloudflare Dashboard check that the existing BTDigg tunnel is
remotely managed and allows a new Published application, without
changing its existing hostname/route. The physical hub installation
requires **separate opt-in** after this preflight; then an isolated
same-IMDb 100/100 genuine-magnet loopback acceptance check; only then
add ONE additional hostname route to 8798 using the *existing*
tunnel connector, test unauthenticated health HTTP 401 and isolated
Worker-to-Tunnel connectivity/same-zone 1042. Only after all these
gates may owner authorize Worker secret and production deploy.


## 2026-10-16 — real physical preflight & Dashboard: NEXT STEP IS 8798 INSTALLER PR

Owner completed read-only physical preflight from main
`7129adfaa076c7cd2dcc2650913332a3de6f019e`:
`magnetra-btdigg.service=active`,
`magnetra-btdigg-tunnel.service=active`,
`magnetra-eztv.service=active`,
`magnetra-eztv-tunnel.service=inactive`;
one TCP listener each on `8796` and `8797`, both return
unauthenticated HTTP `401`. There is **no** listener on `8798`
(and no installed new hub has been demonstrated).
The physical check did not mutate host services and revealed no tokens.

Cloudflare screenshots of the existing
`magnetra-btdigg-rock64` tunnel show **1 active replica**,
**1 Published application**, the unchanged
`btdigg-rock64.alexlab.media` → `http://127.0.0.1:8796`,
and the `Add route` action on the SAME tunnel. The connector
type is `cloudflared`; `Remotely managed` is not explicitly
labeled in the screenshots. There is no new route or DNS record;
`Rotate token` must NOT be used. This confirms the necessary
current tunnel/route state; do not ask owner to recreate a tunnel.

The owner confirmed ONE new future hostname/route
`magnetra-rock64.alexlab.media` →
`http://127.0.0.1:8798` to be added *only after* local hub
acceptance is positive and after separate approval. **Do not click
Add route yet.** Existing BTDigg route, process, credentials and
cloudflared global services remain unchanged.

PR #50 code for `rock64/magnetra_gateway.py` and the isolated
`rock64/magnetra-gateway.service` template is in main, tested
offline (76 Node / 55 Python plus Android Debug/Staging).
The 8798 hub has NOT been installed physically; next coder step
is a separately reviewed guarded root-opt-in installation and
local authenticated same-IMDb EZTV acceptance checker.
Only `eztvx` is currently an accepted hub provider route.
Original localhost 8797 was previously proven to return 100/100
genuine matching magnet entries for same IMDb as official EZTV.
Do not claim that 8798 already passed a real-world test.

After owner-approved 8798 physical install, the acceptance sequence
is local authenticated health, same-source-positive 8797→8798 real
magnet-count equality and 401 on unauthorized health, BTDigg
regression, then one new Published application route, public
no-auth 401 and staged Worker→Tunnel 1042 check. Never modify
global `global_fetch_strictly_public`/network compatibility to
work around same-zone 1042. No Worker Secret or PWA production
deploy before isolated end-to-end proof and separate consent.


## 2026-10-16 — guarded install and genuine acceptance added to GitHub source

The new `rock64/install-magnetra-gateway.sh` implements a FIRST-install-only, explicit-root-opt-in path for 8798. It guards root-owned EZTV token reuse, current healthy 8796/8797, 8798 port collision, destination collisions and loaded unit conflicts. It creates ONLY dedicated new central paths/unit, generates a separate token, and rolls back those newly created paths if startup/health validation fails. It does not manage Cloudflare, rotate any old token, restart any existing service or deploy the PWA.

The new `rock64/check-magnetra-gateway.py` has `--smoke` for local no-upstream 401/200 and service-state checks; its default run makes bounded requests to a source-owned EZTV recent/filtered endpoint and checks exact genuine-magnet identity from source through 8797 and 8798. Source failures or no positive sample are not successes. Offline fixtures validate identity/count mismatch handling without actual provider calls. No IDs/magnets/titles/tokens printed. Install is **NOT automatically executed by CI or merging**. Do not add the second Published application before explicit authorization and a positive real Rock64 acceptance.


## 2026-10-16 — first install attempt failed before authenticated smoke

Owner's real run of PR #52 installer: existing service preflight PASSED, 18 installer offline tests PASSED, new systemd enable returned, immediately-following local smoke FAILED, installer performed dedicated rollback. No physical 8798-to-8797 original-source magnet comparison occurred; there is still no demonstrated installed dispatcher. The previous smoke merged multiple distinct failures into a single message; cause remains unknown. The recovery branch adds only bounded no-auth loopback listener readiness and secret-free stage identifiers; systemd `active` is insufficient proof of HTTP readiness. No old units, credential, tunnel route or DNS were changed by this corrective code. Repeat local installation only after CI and new review/approval.


## 2026-10-16 — Rock64 central dispatcher 8798 installed and REAL source acceptance PASSED

Owner-authorized second installation used the precise SHA `174d7e09c441f9430e14518b928f5efc4a0812e1`. Physical installer preflight and 23 scoped offline tests passed; new central unit became operational with authenticated `/healthz` HTTP 200 and no-auth HTTP 401. Existing EZTV 8797 health was 200/401, BTDigg 8796 no-auth 401, and the pre-existing BTDigg tunnel/BTDigg/EZTV units remained active. Real read-only positive-source test reported `EZTV original matching magnets: 53`, `EZTV gateway 8797 matching magnets: 53`, `Central gateway 8798 matching magnets: 53`, and exact same-magnet-multiset PASS for original -> 8797 -> 8798. This positively proves functioning **local** EZTV dispatch; it does not establish that any other provider works via the central gateway.

The earlier first-install failure was rolled back; the later owner-authenticated successful output supersedes it for the present local service state. Update status as local gateway deployed/accepted, **not** Cloudflare-exposed or Worker-activated. The owner has not yet authorized the second Published application route. Next gated action: same existing `magnetra-btdigg-rock64` tunnel, add ONLY `magnetra-rock64.alexlab.media` -> `http://127.0.0.1:8798`, preserve 8796 hostname/service unchanged. Test public endpoint auth and isolated Worker same-zone 1042 before any Worker Secret/PWA production change.


## 2026-10-16 — Cloudflare published route created under SAME tunnel; unauthenticated HTTPS verified

Owner-provided current Dashboard screenshots show BOTH published applications beneath the single existing `magnetra-btdigg-rock64` tunnel: `btdigg-rock64.alexlab.media` -> `http://127.0.0.1:8796` (retained) and `magnetra-rock64.alexlab.media` -> `http://127.0.0.1:8798` (new). Both use proxied CNAME records pointing to the same already-installed Cloudflare tunnel. This **supersedes** earlier "do not add route yet" language as an historical gate: authorization was obtained and the owner added the one route; it is no longer pending.

Rock64 HTTPS public test for the new hostname via `curl --resolve` with two reachable Cloudflare IPv4 edge addresses succeeded twice: HTTP 401, TLS verify 0. Local 8798 no-auth remains 401; original BTDigg public IPv4 response remains 401. New hostname's ordinary IPv4 DNS resolution on Rock64 was empty, but both hostname IPv6 paths were failing; no source evidence yet distinguishes broken local caching/filtering from externally missing A answers. No changes to DNS server/global VPN/router/firewall/Tailscale/NordVPN settings until read-only DNS evidence exists.

This proves new hostname TLS and unauthenticated HTTPS response only; do not treat as public authenticated-gateway or Worker same-zone 1042 acceptance. Worker secret and PWA prod remain inactive and require separate consent. Next: public DoH/local DNS comparison; isolated Worker->Tunnel feasibility and eventual owner-approved activation.


## 2026-10-16 — Public DNS A is correct; Rock64 resolver A discrepancy remains to diagnose

Follow-up owner-run Cloudflare DNS-over-HTTPS test directly against `1.1.1.1` returned `Status:0` with Magnetra public proxied hostname A records `188.114.97.7` and `188.114.96.7` plus two AAAA records (all TTL 300). Same Rock64 default `getent ahostsv4` remained empty. This falsifies the hypothesis that the public Cloudflare A record is absent; the OS local name-resolution path is divergent for that hostname. Do not assume the reason (cache, resolver policy, propagation or filter) without local resolver evidence. No DNS/tunnel/gateway edits were required. Prior two-IP HTTPS bypass already proved no-auth 401/TLS=0; this does NOT yet establish Worker->Tunnel/1042 or public authenticated gateway access. Next non-mutating inspection: local resolver nameservers and optional `resolvectl`, followed by isolated Worker compatibility check after explicit owner approval.


## 2026-10-16 — Standard Rock64 resolver and HTTPS normal; same-zone Worker probe staged but NOT deployed

Owner rechecked the new hostname from Rock64: `getent ahostsv4` now returns two proxied Cloudflare IPv4 addresses, `resolvectl` obtains them from `systemd-resolved` cache (stub nameserver `127.0.0.53`, symlinked resolv.conf), and **normal HTTPS without --resolve** returns HTTP 401. This resolves the previously observed local IPv4 DNS A lookup anomaly operationally, with original transient cause still unproven. There is no justification to alter host DNS, interface `end0`, Tailscale, VPN, firewall, old tunnel route, or gateway unit.

A standalone, no-secret Worker-to-Tunnel 1042 probe has been staged under `worker/probes/` with regression tests, without any deployment, custom domain, temporary route, key, or modification to production Worker. It sends exactly one unauthenticated GET to the already-published `https://magnetra-rock64.alexlab.media/healthz`, and returns only a sanitized result. Cloudflare's 1042 is associated with same-zone Worker-to-Worker fetches; neither Rock64 curl nor `workers.dev` preview fully demonstrates same-zone Worker compatibility. Owner's *separate* approval is required before deploying a temporary same-zone test Worker, and it must not share hostnames with the existing PWA or tunnel routes. No new paid tier and no `global_fetch_strictly_public` changes.


## 2026-10-16 — iOS clipboard workaround: temporary Worker Git Builds configured but NOT deployed

Owner created `magnetra-1042-probe` Cloudflare Worker, but iOS Safari's editor could not read its clipboard; the deployed test Worker has not been proven to contain diagnostic code. The safe alternative is Cloudflare native Git Builds connected to the **existing temporary Worker only**, with Git repository root `worker/probes`, branch main. Strict `worker/probes/wrangler.jsonc` specifies ONLY `magnetra-1042-probe`, its fixed-target no-secret source, and temporary Custom Domain `magnetra-probe.alexlab.media`. CI tests and invariant guard verify the exact name/domain configuration. This source staging is distinct from Cloudflare deployment; the actual no-secret live 1042 probe remains PENDING until owner connects Builds, successful Cloudflare build is independently shown, and endpoint `/probe` is queried. Disconnect Builds and remove temporary worker/domain immediately after test; do not affect original tunnel 8796/8798, secrets, or PWA.


## 2026-10-16 — Cloudflare temporary Worker Git Builds connected, first live probe still PENDING

The owner successfully connected **only** existing `magnetra-1042-probe` to GitHub `Zuzuitu/AlexLab-Magnetra`, `main`, root `worker/probes` with deploy command `npx wrangler deploy`, no custom build command or secrets, preview builds disabled. The Cloudflare Settings page states a **new Git push is needed to start the first Build**. Its Build API token's display name is `calcidatum-build-token`, whose permissions are unverified. Do not change existing tokens without a specific failure and least-privilege review. A probe-directory checkpoint change through green CI/squash PR is intended to supply that first push. This does not imply the Build succeeded, that `magnetra-probe.alexlab.media` is already active, or that Worker→Tunnel no-auth connectivity/1042 has been tested. Separate protected 8796/8798 routes, original tunnel, production PWA, Worker secret, and the 46 indexers remain unchanged. Check actual temporary build logs, run one no-secret `/probe` only after successful deployment, disconnect Git Builds and delete the test Worker/domain afterward.


## 2026-10-16 — LIVE same-zone Cloudflare Worker → existing tunnel no-auth acceptance PASS

Owner's actual Rock64 curl of `https://magnetra-probe.alexlab.media/probe` returned HTTP 200/TLS=0, JSON 50 bytes: `result=PASS_UNAUTHENTICATED_401`, `status=401`. The temporarily Git-deployed `magnetra-1042-probe` Worker made its hardcoded no-auth GET to `https://magnetra-rock64.alexlab.media/healthz` and received 401: no 1042 restriction on this **specific tested path**. Original direct Rock64 53=53=53 magnet parity is separate. No authenticated bearer from Worker, source magnets, production Worker config, or PWA activation was tested/changed. Await owner's confirmation that Git Builds was disconnected and ONLY the temporary probe Worker/custom-domain deleted; do not merge the new checkpoint while the temporary Worker remains Git-connected to main, as a new push can retrigger deployment. After cleanup, separately authorize production authenticated E2E EZTV validation with secret stored safely, not pasted in chat, and avoid global Worker compatibility changes.


## 2026-10-16 — owner-reported end of temporary Worker/Custom Domain

After live no-auth probe success, the owner confirmed completion of the directed Git Builds disconnection, temporary `magnetra-probe.alexlab.media` removal and `magnetra-1042-probe` deletion. This is **user confirmation only**, not independently verified from Cloudflare API. No reason to issue more temporary Worker deploys. Local true-source 53=53=53 magnet multiset parity and live same-zone Worker GET health 401 remain independently evidenced tests; authenticated same-IMDb exact magnet parity via the **production Worker** is still pending. A new explicit approval is necessary before activating `MAGNETRA_GATEWAY_TOKEN` in the protected Worker and its gated production deployment. Avoid touching existing BTDigg and Magnetra Tunnel hostnames, Rock64 services, 46 original indexers or global compatibility flags.


## 2026-10-16 — General recovery is all 46, but central 8798 remains EZTV-only until independently proven

User authorized generalized provider recovery instead of stopping at EZTV. New `worker/src/recovery-strategy.mjs` records a deterministic plan for **all 46**, with explicit provider classifications and gateway evidence; `docs/PROVIDER_RECOVERY_PLAN.md` is the phase-by-phase implementation contract. BTDigg stays separately protected on 8796; central 8798 still has only `/v1/eztvx/torrents` and Rock64 authentic source→8797→8798 53/53/53 proof. No generic route or open proxy has been added. The same-zone temporary Worker's 401 / no 1042 success remains an unauthenticated transport proof, not authenticated production magnet parity.

Previously observed physical 403 from Rock64 for 1337x/BT4G/Ext means same residential exit is not proven useful; known 301s for BitSearch/OxTorrent/Torrent9 require real candidate-host listing verification and exact-origin parser tests before any changes. No operational gateway installation or Worker token activation is part of the staged recovery classifier. Future new provider routes must be hardcoded, authenticated, bounded, tested and individually approved; never create per-provider Cloudflare Tunnels. Phase 1 has NO PWA deployment and preserves all 46.
