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
