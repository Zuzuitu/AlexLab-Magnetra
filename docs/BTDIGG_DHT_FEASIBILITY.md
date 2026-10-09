# BTDigg integration feasibility — evidence checkpoint (2026-10-09)

**Scope:** This is a technical investigation, not a statement that BTDigg search works. Do not change BTDigg attribution or the 46-source audit snapshot because of this document.

## Verified current baseline

- Magnetra's `btdigg` HTML adapter mirrors upstream `app/src/main/kotlin/com/prajwalch/torrentsearch/providers/BTDigg.kt` search URL and CSS selectors. The fork's Kotlin file matched upstream byte for byte in the 2026-10-08 comparison.
- The last authorized production source audit (workflow 37827913584) classified BTDigg as `TIMEOUT`; independent GitHub-hosted checks returned HTTP 429. On 2026-10-09, an independent web fetch of `https://btdig.com/contacts` also returned HTTP 429. These observations do not establish that every client IP is blocked.
- Blind retries, modified User-Agent strings, paid CAPTCHA solvers and unauthorized proxy rotation are **not** valid corrective actions. Existing browser-open and manually supplied magnet fallbacks must remain available.

## Analysis of https://github.com/btdig/dhtcrawler2

Verified repository on `master` commit `433efb028be3020841e227924fc4b53c5d35af4a`; source code resides on separate `src` branch (observed commit `82f14c458c808bc4ef2f1f90486cfcc88830dce6`).

- The project is an Erlang DHT crawler with a local MongoDB database. It does **not** document access to the existing `btdig.com` production index.
- It includes a **separately self-hosted** search service: `src/http_front/api.erl` implements an `api:search` handler which returns JSON including `hash`, `name`, `created_at`, `total`, and `files`; magnets are constructed from valid infohashes.
- `src/http_front/crawler_http.erl` starts Erlang `inets` HTTP with default port 8000 and `bind_address, {0,0,0,0}`. The demonstrated HTTP interface has no suitable documented Internet-facing authentication/TLS boundary. **Do not expose this service publicly or attach it directly to Cloudflare.**
- README documents Erlang R16B-era startup, MongoDB and optional Sphinx/Coreseek. Most crawler code originated around 2013; the `master` README change was in 2023. Running it today would require compatibility/security work and a growing database, and produces a **new independent index**, never the historical BTDigg dataset.
- The Cloudflare Workers supported protocols documentation lists HTTPS, outbound TCP, WebSockets, etc., but not general-purpose UDP sockets required for normal BitTorrent DHT crawling. Therefore a continuous DHT crawler cannot be hosted directly inside the existing Worker.

## Feasible paths, strictly separated

### A. Actual BTDigg coverage: permissioned source integration

Obtain a documented and **authorized** API/allowlisted access contract from BTDigg operators. SearXNG's third-party `btdigg` engine documents `official_api_documentation: https://btdig.com/contacts` with comment `on demand`, while `use_official_api: False` and HTML parsing remain its implementation. This is a lead to verify with the operator, **not** evidence that a free or accessible API exists. The organization controls `btdig.com` (GitHub verified) and displays a public contact address. No external email or API purchase has been authorized. A public-documentation-only search does not identify a reliable official endpoint.

**Engineering gate:** Only implement after the operator supplies a permitted endpoint, response format, authentication rules, quotas and explicitly confirmed cost. Use fixed HTTPS origin allowlisting and CI fixtures; do not put secrets in frontend assets. Real provider results may then retain ID `btdigg` after verification.

### B. Additional independent DHT source: Bitmagnet, NOT BTDigg

A maintainable alternative to the legacy Erlang project is https://github.com/bitmagnet-io/bitmagnet (source-owned documentation https://bitmagnet.io). It provides a DHT crawler, PostgreSQL-backed search, GraphQL and Torznab endpoints (`/torznab`) and ARM64 builds. Estimated project requirements: about 300 MB application RAM plus at least 1 GB PostgreSQL RAM; the source documentation estimates ~80 GB of disk per 10 million indexed torrents, with unbounded growth. Actual performance will vary.

A proposed **optional** private pilot on existing owner hardware would:
1. First inspect real free disk, CPU, Docker availability, processes, runner services and ports on Rock64; do not assume capacity from historical measurements.
2. Require explicit owner approval to start new 24/7 services or introduce external networking.
3. Store crawler data on a dedicated bounded volume (ideally spare external storage), with resource limits and independently monitored storage pressure. Do not interfere with existing CalciDatum/NexaPanel/other services.
4. Keep Torznab/GraphQL administration private. Bitmagnet itself warns against public exposure due to unauthenticated/destructive API surfaces. Use a separate read-only, authenticated, rate-limited adapter with exact known target origin if remote access is later approved. No arbitrary proxy URLs, credentials in client bundles or unsafe redirects.
5. Add a distinct source identity (e.g. `localdht`), **never label these results BTDigg**, and revise canonical catalog/count invariants intentionally in the same PR only after approval. Keep 46 built-in provider parity.
6. Verify source metadata, magnet/infohash, quota and end-to-end queries on the actual device. Empty initial corpus means this is **not** an immediate BTDigg replacement.

This pilot can potentially reuse existing hardware without new subscriptions, but hardware wear, energy, storage consumption and network workload are not zero; cost / resource impact must be approved. Nothing has been provisioned or installed during the research.

## Decision / release boundary

BTDigg automatic search cannot be claimed repaired by using `dhtcrawler2`, Bitmagnet, a generic SearXNG instance, or an unrelated torrent indexer. Two feasible next actions require new evidence or authorization: a permitted BTDigg API agreement (for genuine BTDigg search), or approval for a distinctly attributed local DHT index (for broader independent DHT search). No deployment is authorized by this research. No change to runtime code, provider catalog, historical provider audit, CI invariants or Flud credentials has been made.

External references:
- https://github.com/btdig/dhtcrawler2/tree/src
- https://github.com/btdig/dhtcrawler2
- https://github.com/btdig
- https://github.com/searxng/searxng/blob/master/searx/engines/btdigg.py
- https://developers.cloudflare.com/workers/reference/protocols/
- https://bitmagnet.io/guides/endpoints.html
- https://bitmagnet.io/faq.html
- https://bitmagnet.io/setup/installation.html

## Owner scope clarification — 2026-10-09

**Binding scope:** The owner wants **genuine BTDigg search result listings displayed within Magnetra**, not an independent DHT indexer or a Bitmagnet/dhtcrawler2 installation. Path B above is REJECTED as a proposed delivery milestone, retained only as background comparative research. Do not build, provision, or label an independent crawler as `btdigg`. Existing browser fallback does not meet the requested automatic integrated search acceptance criterion.

Acceptance criterion: a benign `ubuntu` search to the canonical BTDigg source must return result rows with verifiable BTDigg origin, title, magnet/infohash and other fields where available; the established tests should exercise real provider response and fixtures. If the provider continues to block automated requests or offers no permitted API, report the dependency rather than faking results. Contact/permission for an official endpoint is a prerequisite for a reliable server integration. Historical public `api.btdigg.org` paths appearing in unrelated old third-party scripts are **not** verified/current API contracts and must not be used without operator confirmation.
