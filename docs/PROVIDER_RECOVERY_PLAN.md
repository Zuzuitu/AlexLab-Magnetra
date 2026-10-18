# Magnetra — universal 46-indexer recovery plan, Phase 1

> **Actualizare verificată 18.10.2026 (supersede etapele istorice de mai jos):** Cloudflare candidate `249d6767-f4dc-4f4d-bbf7-f57bea2e5554` este în deployment la **0% trafic**, vechea `a9df4429` la **100%**. E2E reale pozitive numai pentru **BTDigg** (10 rânduri autentice pe fiecare versiune), **EZTV** (29 magneturi autentice), **OxTorrent** și **Torrent9** (3 rezultate + magnet deferred fiecare). Catalogul are 46 ID-uri, NU 46 surse pozitive. BTDigg a raportat ulterior pe iPhone `BTDIGG_SOURCE_TIMEOUT` (~12s), apoi rezultate după ~1 minut, fără intervenție; disponibilitate **intermitentă, rădăcină neidentificată**. Următorul pas este măsurarea read-only DNS/TCP/TLS/TTFB/total pentru 8796, nu bulk recovery și nu deploy. Detaliile curente: [master prompt 18.10](MAGNETRA_MASTER_PROMPT_2026-10-18.md), [checkpoint canonic](PROJECT_STATE.md). Restul acestui document păstrează dovezile istorice / strategia inițială, nu statusul actual de deployment.


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


## 2026-10-16 — OxTorrent + Torrent9 real search→details magnet proof, source-owned 8798 integration STAGED (NOT DEPLOYED)

Owner ran **real Rock64 read-only probe** at pinned GitHub commit `dd4666b04d76ee924df6a9aca0ba8445a9725ec4`. Results: `oxtorrent` alternate `www.oxtorrent.co`: HTTP 200 search, 3 real query-matching `ubuntu` rows, 3 same-source details candidates, first details HTTP 200 and a well-formed BTIH magnet anchor found. `torrent9` alternate `www7.torrent9.to`: exact same 3 query-matched rows/3 detail candidates/one HTTP 200 details magnet anchor. **No .torrent/magnet download or proof of actual swarm connectivity.** Earlier BitSearch alternate `bitsearch.eu` yielded HTTP 520 and remains excluded; other 44 indexers remain untouched. This evidence *does* justify a guarded new backend for these two sources only.

New staged code: `rock64/magnetra_html_egress.py` defines **two hardcoded HTTPS upstream hosts only**, search paths `/recherche/<encoded q>` and `/search_torrent/<encoded q>.html`, detail paths only `/torrent/<numeric-id>/<slug>`. Unprivileged source traffic has no proxy-env, redirects or retries, max 8 sec and 256 KiB/response, no token forwarding, no magnet/file download, no source HTML or URL logging. `rock64/magnetra_gateway.py` extends the existing **authenticated 8798 dispatcher** from the single EZTV path to exact `/v1/oxtorrent/html` and `/v1/torrent9/html` with `mode=search|detail` strict parameter allowlist. No generic proxy, no additional tunnel or route. Only HTTP 200 genuine HTML pages are relayed; upstream 403/429/504 remain errors. `rock64/upgrade-magnetra-gateway.sh` is **owner-triggered only** and designed for preflight/rollback of the *existing* 8798 script and new module, explicitly preserving 8796/8797 service configurations and credentials. Already installed 8798 must NOT be subjected to the original first-install script.

Worker stage: `worker/src/legacy-specs.mjs` pins the two *physically verified* canonical alternate hosts, leaves original selectors intact; `worker/src/html-rock64.mjs` creates an **optional** source-only fixed URL→8798 mapped fetcher using the existing server-side `MAGNETRA_GATEWAY_TOKEN`, never the frontend. `worker/src/index.mjs` uses it for search **and deferred details→magnet** only for OxTorrent/Torrent9 when secret exists; all other indexers use existing transport. Without a secret, no tunnel request. PWA behavior and 46 source IDs remain unchanged. No production Worker secret is activated, and no protected PWA deployment is tagged in this PR.

State of actual rollout **ON 2026-10-16**: `html_8798_implementation_staged=true`; `html_8798_physical_update_confirmed=false`, `html_authenticated_worker_e2e_passed=false`, `worker_activated=false`, `provider_recovery_v1.production_deployed=false`. Existing physical 8798 is unchanged, current production PWA remains unchanged, historical one-query 13/12/21 audit still the true recorded production snapshot. After 4/4 CI and merge: separately owner-run *pinned reviewed* source-only 8798 upgrade, verify service and source HTML parity, then explicitly approve safe Cloudflare production secret/deployment and test end-to-end before claiming either provider recovered in PWA. No paid upgrades or global Worker compatibility flag changes.


## 2026-10-16 — PHYSICAL 8798 upgrade successfully installed, 2/2 real source HTML→magnet acceptance PASS (LATEST)

Owner ran the pinned merged GitHub commit `60e2d250e318bf6eca65b5ad7acb55f62d378125` guarded central upgrade on physical Rock64 Armbian. Exact owner-provided terminal evidence:
- `Project invariant check PASSED`; **92 Python unit tests OK**.
- `PREFLIGHT_OK: existing 8796, 8797, 8798 authentication intact`.
- `POST_RESTART_READY: loopback 8798 responded HTTP 401`; this proves the bounded startup-readiness PR #64 patch fixed the practical install-blocking race during the successful attempt.
- `POST_INSTALL_OK: BTDigg 8796, EZTV 8797 and central 8798 each require authentication`; all four service components were protected in the upgrade preflight; no tunnel edits.
- Authenticated physical **8798** acceptor `check-magnetra-html.py` verified both real providers (not mocks): OxTorrent search HTTP 200, **3** query-matching Ubuntu results, selected details HTTP 200, valid BTIH magnet anchor; Torrent9 search HTTP 200, **3** query-matching results, selected details HTTP 200, valid BTIH magnet anchor; final `{"result":"PASS","checked_sources":2}`.
- Installer completed: `PASS: isolated 8798 code upgraded. EZTV/BTDigg/tunnel not changed.` No observed rollback required on this second attempt.
- Three printed `STOP: expected --post-restart or --rollback, read-only.` lines were produced intentionally by negative-argument offline unit test cases, **not** by live installer logic. This PR redirects that expected stderr into the test's capture buffer so future runs show no alarming false STOP text.

Updated machine-readable state: `html_8798_physical_update_confirmed=true`, `html_8798_real_source_acceptance_passed=true`, `html_8798_physical_acceptance_providers=["oxtorrent","torrent9"]`; existing `worker_activated=false`, `html_authenticated_worker_e2e_passed=false`, `provider_recovery_v1.production_deployed=false`, `new_tunnel_installed=false`. Do NOT misrepresent verified backend magnets as end-user PWA recovery yet, nor infer actual torrent download/connectivity.

**NEXT:** Use existing production Cloudflare `alexlab-magnetra` Worker/secret model, without disclosing the live private `MAGNETRA_GATEWAY_TOKEN` to GitHub/chat/commands logs. Production Worker has three optional shared-gateway source adapters (EZTV, OxTorrent, Torrent9) staged on main; secret is still NOT confirmed set, and no `[deploy-pwa]` or `workflow_dispatch` should run until source-specific authenticated Worker→8798 E2E rollout steps and rollback have been reviewed. Production domain `index.alexlab.media`, old BTDigg 8796 cloudflared route, EZTV 8797, other services and original 46 provider IDs must remain protected. Run real end-to-end single-query checks and full 46 provider audit after controlled release. Do not claim 3 providers recovered if checks are missing or stale.
