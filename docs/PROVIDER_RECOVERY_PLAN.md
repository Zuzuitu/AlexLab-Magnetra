# Magnetra — universal 46-indexer recovery plan, Phase 1

This is **not** the EZTV-only roadmap. All 46 original Android/PWA
indexers have a canonical, deterministic recovery decision even if the
historical result is "empty". The same evidence classifier feeds the
non-mutating Worker endpoints `GET /api/providers` (additive `recovery`
metadata), `GET /api/recovery-plan` (prioritized complete report), and
the offline operator command `node scripts/recovery-plan.mjs`.

## Non-negotiable boundaries

- **46/46 preserved** with original provider identity and attribution.
- `ported: true` or a historical row is not proof of current uptime.
- No automatic retries after HTTP 429, no CAPTCHA evasion, no arbitrary
  URL proxy, no automatic redirect following or hostname migration.
- No auto-enabling new providers through Rock64 based on a generic 403.
- One existing tunnel, two existing published routes, and original
  BTDigg/EZTV/8798 systemd installations are untouched. Per-provider
  new tunnels forbidden.
- No private tokens, magnet URLs, hashes, titles or source response bodies
  in plans/logs. No `[deploy-pwa]` or production Worker secrets in this PR.

## Evidence classes (historical snapshot from 2026-10-13)

The historical **one-query** production audit (run 38373699387) yielded
13 with result rows, 12 empty/unverified and 21 errors. The recovery
planner uses that snapshot without rewriting it. Distinct investigation
strategies:

- **GATEWAY_READY_FOR_AUTH_TEST**: EZTV, real positive original → 8797 →
  8798 identical 53 magnet rows on physical Rock64; isolated no-auth
  Worker → Tunnel GET succeeded without 1042. **Production Worker bearer
  and authenticated E2E remain NOT tested**.
- **EXISTING_GATEWAY**: BTDigg has its own operational 8796 route and
  behavior; never redirect it to the 8798 dispatcher.
- **CHECK_REDIRECT_CANDIDATE**: BitSearch, OxTorrent, Torrent9 returned
  observed HTTP 301 from the Rock64. New hostname candidates are
  historical leads only, not verified site migrations.
- **BLOCKED_BOTH_PATHS**: 1337x, BT4G, Ext yielded HTTP 403 from Rock64
  as well as historical Cloudflare failures. Residential rerouting
  would not yet solve this and must not be activated.
- **LOCAL_TRANSPORT_FAILURE**: Torrentz failed from Rock64 before HTTP;
  investigate DNS/TLS/transport only.
- **RATE_LIMITED**: HTTP 429 is a stop signal, not a retry target.
- **UPSTREAM_FAILURE**: upstream HTTP 52x/53x requires source
  availability verification rather than misattributing unrelated results.
- **VERIFY_EMPTY_SAMPLE**: query-dependent zero results do not imply a
  nonfunctional provider.
- **COMPARE_EGRESS**: historical Worker errors without physical
  Rock64 evidence are candidates for one bounded diagnostic, not
  automatically gateway eligible.
- **KEEP_OBSERVED_RESULTS**: results existed in a dated audit; repeat a
  representative search before making a current uptime claim.

The exact strategy/nextAction is generated from
`worker/src/recovery-strategy.mjs`, not a hardcoded separate
spreadsheet. The *only* initially gateway-eligible IDs are BTDigg
(existing separate service) and EZTV (new central path). This state
is `gatewayEligible`, **not** permission to enable a Worker secret.

## Operator report (OFFLINE, no network)

```sh
node scripts/recovery-plan.mjs --summary
node scripts/recovery-plan.mjs
node scripts/recovery-plan.mjs --json
```

The first shows totals and strategy counts, the second produces an
ordered 46-provider queue, and the third emits structured JSON for
future audits. All use the same live code and canonical 46-provider
catalog. No external GETs, secrets or physical changes.

## Physical source-probe phase, only after CI + merge

Use the already-existing bounded read-only Rock64 tests for the FIRST
three host-redirect candidates:

```sh
python3 -B rock64/probe-redirect-candidates.py
```

It sends exactly three fixed HTTPS GETs, disables redirects, limits
response previews to 256KB per source and prints only sanitized
layout counts/hostnames, not magnets, raw HTML or user queries. No
package install, `sudo`, token, filesystem edit, service restart,
proxy environment, or tunnel modification. Do not interpret
`LAYOUT_HINT_ONLY` as a working torrent parser.

After owner provides source-owned real result evidence, prepare a
**separate tested PR per approved provider-origin/adapter pair**.
For each real candidate: confirm original indexing semantics, genuine
source results/magnets and required deferred detail flow, align
fixed origin and parser, unit tests + error guards, isolated Worker
verification, explicit deployment approval. Only when Rock64 genuinely
succeeds where Cloudflare fails do we add a narrowly allowlisted,
authenticated 8798 provider route — *not* a generic open proxy.

## Safe phase gates

1. Phase 1 (this PR): static evidence-wide classifier + report, code
   tests and CI, no production deployment.
2. Phase 2: bounded source probes and evidence-driven parser/origin
   repair for all applicable providers.
3. Phase 3: extend central gateway only for positive verified
   Rock64-only sources using code-defined origin/method/path,
   fixed backend and separate resource caps.
4. Phase 4: protected Worker secret + authenticated EZTV E2E
   under explicit owner approval; existing source errors and rate
   limits remain truthful.
5. Phase 5: gated production PWA deploy, 46-provider live audit,
   preserve sorted working-first UI and historical provenance.

Do not declare 46/46 functional from a CI run or automatically
substitute another provider's results.
