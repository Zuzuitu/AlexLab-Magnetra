# Multi-indexer Rock64 residential egress diagnosis (read-only)

**Purpose:** decide which original Magnetra providers are actually reachable
from the Rock64 IP before writing or activating any additional residential
gateway. Never infer that every HTTP 403 can be fixed by rerouting.

## Evidence / baseline

- 2026-10-13 production historical `ubuntu` audit: `torrentz`
  `UPSTREAM_ERROR`, `uindex` `ACCESS_DENIED`, and 1337x, BT4G and Ext
  `ACCESS_DENIED`. This is **Cloudflare egress**, not a Rock64 reachability result.
- Physical Rock64 earlier observed HTTP 403 for 1337x, BT4G and Ext,
  so rerouting those identical sites via the same residential exit is **not
  currently justified**. Their sites may use challenges or ISP/domain filtering.
- Genuine EZTV API from Rock64 returned JSON HTTP 200 and a known-positive
  IMDb query with two original magnet URLs when requested with `limit=2`.
  After the independent EZTV gateway was installed and authenticated, a
  gateway query (hardcoded `limit=100`) returned zero rows. No tunnel has
  been configured, and the cause is not yet known. Do not change the
  installed EZTV gateway's limit or invent torrent data without measurements.

## Safe one-shot Rock64 tests

From a merged, CI-tested repository revision, or download the exact files
from its pinned GitHub revision into a directory in `/tmp`:

```bash
python3 -B rock64/probe-more-indexers.py
python3 -B rock64/probe-more-indexers.py --extended
sudo python3 -B rock64/diagnose-eztv-filter.py
```

The default indexer scan performs **five** source-owned benign `ubuntu`
searches (Torrentz, UIndex, 1337x, BT4G and Ext); `--extended` performs
**eleven total** fixed GET requests covering six more HTML legacy sources.
Each checks at most 128 KiB with 8s timeout, disabled redirects, no
proxy environment, one request per source and no downloads. Output is only
provider ID, HTTP status, high-level HTML marker classification and elapsed
time. A marker is not proof of a real listing or functioning deferred magnet.
No API token, secret, title, magnet, hash, torrent file, raw HTML or response
body is printed.

The EZTV comparator performs **four bounded GET requests**:
1. Official EZTV last 2 entries, select a real IMDb ID with valid magnet
   (the ID stays in memory and is never printed).
2. Official EZTV filtered by the identical IMDb ID, `limit=2`.
3. Official EZTV filtered by the identical IMDb ID, `limit=100`.
4. Authenticated loopback gateway `127.0.0.1:8797`, same IMDb ID, which
   currently uses `limit=100` upstream.

The comparator needs `sudo` solely to read the separate private
`/etc/magnetra-eztv/gateway.env` secret in memory; no token is printed.
It never logs or sends any magnet to Flud, changes files, restarts services,
installs packages or modifies network configuration. It prints only source
HTTP status, verified match counts, array length and declared upstream
counts. Compare `direct-limit-2` with `direct-limit-100` before
changing the API adapter. A `local-gateway-limit-100` difference can
also stem from source response variance, rate limiting or RAM cache;
the diagnostic alone does not guarantee a fix.

## Safe staged integration policy

Use a **single narrowly allowlisted design per verified provider**, rather
than broadening BTDigg or sharing their credentials. For each original source,
prove, in order:

1. Rock64 gets real, source-owned result rows, not HTTP 200 challenge HTML.
2. Source search URL, method and parsing selectors match the upstream
   Magnetra adapter.
3. If magnets are deferred, source-owned HTTPS details URLs can be fetched
   and resolved safely. No open proxy and no unrelated external redirects.
4. Tests cover exact provider identity, origin allowlist, 403/429 behavior,
   no retries, cache caps, no secrets, loopback-only listener.
5. Only after that: isolated gateway/tunnel opt-in, end-to-end proof from
   Cloudflare Worker and a separately authorized protected production deploy.

**Do not install/restart/change** BTDigg 8796, EZTV 8797, NexaPanel,
CalciDatum, Plex, Tailscale, NordVPN, the router or any existing Cloudflare
Tunnel while running these diagnostics. Avoid enabling paid services.
Never replace source error statuses in the permanent 46-indexer audit from
one narrow test. Preserve source names, Flud behavior and all 46 adapters.

## 2026-10-15 follow-up after real Rock64 output

The user-provided 11-indexer run observed seven HTTP 403, three HTTP 301
and one fast network failure (Torrentz). The EZTV direct `limit=2`,
direct `limit=100` and authenticated local `limit=100` test
all returned 0 rows for the SAME recent-magnet IMDb candidate.
Thus the limit discrepancy is **not sufficient** to explain this sample;
the earlier 2-magnet result may reflect different real candidate data or
temporally variable source indexing.

Next one-time, read-only:
```bash
python3 -B rock64/probe-indexer-followup.py
```
It performs exactly four source HTTPS GETs (Torrentz, OxTorrent,
Torrent9 and BitSearch) **without following redirects**, and up to
five EZTV API GETs (one last-five and at most four distinct verified
recent IMDb filters). Output for redirects includes **only host**, not
full Location URL/path or credentials; output for Torrentz is only a
transport cause category. The EZTV output is only a sample ordinal,
declared upstream result count, page row count and count of valid magnets
matching the sampled IMDb; never the ID/name/magnet/hash. No sudo or
local gateway token is needed. No torrent data is downloaded.
A redirect that changes host is **not** automatically authorized:
separate source legitimacy, origin allowlist and parser tests are needed.

## 2026-10-15 — redirects observed, hosts still unverified

The exact owner-supplied redirects (with **no destination followed**)
were OxTorrent `oxtorrent.co` → `www.oxtorrent.co`,
Torrent9 `www6.torrent9.to` → `www7.torrent9.to`, and
BitSearch `bitsearch.to` → `bitsearch.eu`. Torrentz
`torrentz2.nz` failed with `TRANSPORT_FAILURE` before an HTTP
status, despite the prior low-latency error. This categorization does
not identify why the connection failed or prove a replacement domain.

New independent read-only `rock64/probe-redirect-candidates.py`
performs exactly **three** fixed HTTPS search GETs at those recorded
redirect hostnames, with redirects disabled, at most 256KB of each
HTML page, 8-second timeout and no proxy environment. The output
contains only status, coarse layout hints/counts, challenge indicators,
and if redirected, only a destination hostname. This is not proof of
authentic torrent search results and is **not** permission to migrate
the original provider origin, follow another redirect or dispatch
magnets. A later owner-approved origin migration would require source
verification and updated exact-origin guards, parsers, deferred details
handling, tests and project invariants.


## 2026-10-16 — Physical redirect-candidate results, original selector → magnet detail proof next (NOT activated)

Owner ran merged `main` revision `7685641735669ec57e463cf0447f9cac223b4fbb` from physical Rock64. `scripts/check-project-invariants.py` passed. Exact fixed-host, no-redirect `rock64/probe-redirect-candidates.py` output: **OxTorrent `www.oxtorrent.co` HTTP 200 with `LAYOUT_HINT_ONLY`, 3 `<tr>` table rows and 0 direct magnet anchors; Torrent9 `www7.torrent9.to` HTTP 200 with `LAYOUT_HINT_ONLY`, 4 table rows and 0 direct magnet anchors; BitSearch `bitsearch.eu` HTTP 520 `HTTP_ERROR`**. These were real Rock64 results, not a Worker or CI fixture. **Neither OxTorrent nor Torrent9 is yet verified to return source-owned result rows or valid magnets**, and HTTP 520 must not be auto-retried. The original Android implementations for both sites use original `table > tbody > tr`, `td:nth-child(1)>a` search→details and a magnet selector on the **details page** (OxTorrent `div.btn-magnet > a`, Torrent9 `a[href^="magnet:"]`).

This PR stages strictly bounded, read-only `rock64/probe-result-details.py` for **exactly two pinned alternative hostname URLs** (OxTorrent/Torrent9) with benign query `ubuntu`: original-structure first-column result rows; fixed origin and same tested hostname detail URL allowlist; 1 search GET and at most 1 selected details GET per source; no URL/host input, no redirect following, no proxy environment, max 8 seconds and 256 KiB each; a well-formed BTIH magnet anchor is checked in memory without logging names, URLs, hashes, magnets, bodies, or retrieving .torrent files. No source-host origin migration is automatically authorized; a valid magnet-shaped anchor is NOT proof of downloadability. Dedicated offline Python regression tests and existing GitHub gates must pass before owner may execute the one-time physical diagnostic.

**NEXT GATE:** After protected branch CI and merge, owner runs one read-only `python3 -B rock64/probe-result-details.py` on pinned Rock64 GitHub checkout and returns sanitized JSON. Based on real results, implement exact-original provider parsing/origin changes on a separate PR only if source owned valid rows + details magnet are demonstrated; do not make generic 8798 proxy, change either Cloudflare tunnel application or production Worker, activate secret, reroute BitSearch or claim new indexers are healthy. Current worker_activated remains false, production provider-audit historical 13/12/21 unchanged.


## 2026-10-16 — OxTorrent + Torrent9 real search→details magnet proof, source-owned 8798 integration STAGED (NOT DEPLOYED)

Owner ran **real Rock64 read-only probe** at pinned GitHub commit `dd4666b04d76ee924df6a9aca0ba8445a9725ec4`. Results: `oxtorrent` alternate `www.oxtorrent.co`: HTTP 200 search, 3 real query-matching `ubuntu` rows, 3 same-source details candidates, first details HTTP 200 and a well-formed BTIH magnet anchor found. `torrent9` alternate `www7.torrent9.to`: exact same 3 query-matched rows/3 detail candidates/one HTTP 200 details magnet anchor. **No .torrent/magnet download or proof of actual swarm connectivity.** Earlier BitSearch alternate `bitsearch.eu` yielded HTTP 520 and remains excluded; other 44 indexers remain untouched. This evidence *does* justify a guarded new backend for these two sources only.

New staged code: `rock64/magnetra_html_egress.py` defines **two hardcoded HTTPS upstream hosts only**, search paths `/recherche/<encoded q>` and `/search_torrent/<encoded q>.html`, detail paths only `/torrent/<numeric-id>/<slug>`. Unprivileged source traffic has no proxy-env, redirects or retries, max 8 sec and 256 KiB/response, no token forwarding, no magnet/file download, no source HTML or URL logging. `rock64/magnetra_gateway.py` extends the existing **authenticated 8798 dispatcher** from the single EZTV path to exact `/v1/oxtorrent/html` and `/v1/torrent9/html` with `mode=search|detail` strict parameter allowlist. No generic proxy, no additional tunnel or route. Only HTTP 200 genuine HTML pages are relayed; upstream 403/429/504 remain errors. `rock64/upgrade-magnetra-gateway.sh` is **owner-triggered only** and designed for preflight/rollback of the *existing* 8798 script and new module, explicitly preserving 8796/8797 service configurations and credentials. Already installed 8798 must NOT be subjected to the original first-install script.

Worker stage: `worker/src/legacy-specs.mjs` pins the two *physically verified* canonical alternate hosts, leaves original selectors intact; `worker/src/html-rock64.mjs` creates an **optional** source-only fixed URL→8798 mapped fetcher using the existing server-side `MAGNETRA_GATEWAY_TOKEN`, never the frontend. `worker/src/index.mjs` uses it for search **and deferred details→magnet** only for OxTorrent/Torrent9 when secret exists; all other indexers use existing transport. Without a secret, no tunnel request. PWA behavior and 46 source IDs remain unchanged. No production Worker secret is activated, and no protected PWA deployment is tagged in this PR.

State of actual rollout **ON 2026-10-16**: `html_8798_implementation_staged=true`; `html_8798_physical_update_confirmed=false`, `html_authenticated_worker_e2e_passed=false`, `worker_activated=false`, `provider_recovery_v1.production_deployed=false`. Existing physical 8798 is unchanged, current production PWA remains unchanged, historical one-query 13/12/21 audit still the true recorded production snapshot. After 4/4 CI and merge: separately owner-run *pinned reviewed* source-only 8798 upgrade, verify service and source HTML parity, then explicitly approve safe Cloudflare production secret/deployment and test end-to-end before claiming either provider recovered in PWA. No paid upgrades or global Worker compatibility flag changes.
