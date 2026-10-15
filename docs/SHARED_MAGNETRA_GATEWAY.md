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
