# AlexLab Magnetra — checkpoint operațional verificat 17.10.2026

**Status:** aplicația publică este protejată; gateway-ul Rock64 8798 are două surse HTML validate fizic; noul cod Worker a trecut prin workflow-ul **manual, upload-only**, dar **nu există încă dovadă a execuției autentificate Worker→Tunnel→8798**, a versiunii candidate în Cloudflare sau a promovării la producție.

## Sursa canonică / GitHub

- Repository `Zuzuitu/AlexLab-Magnetra`; PWA `https://index.alexlab.media`; 46 de provideri originali, identități păstrate.
- PR #58: Worker `magnetra-1042-probe` pentru dovada conexiunii; PR #59 Git Builds; PR #60 dovadă live Worker→Tunnel 401 și ștergerea probe-ului temporar confirmată de proprietar.
- PR #61: motor general de triere/dovadă pentru toate cele 46 de surse, **nu doar EZTV**, + raport offline + API `/api/recovery-plan` staged în cod.
- PR #62: diagnostic OxTorrent/Torrent9, originale căutare→detalii→magnet.
- PR #63: rute HTML fixate OxTorrent/Torrent9 pe gateway-ul comun și suport Worker pentru căutare și rezolvare magnet.
- PR #64: remedierea race-ului Type=simple la pornirea 8798: așteaptă maxim 12 secunde pentru HTTP 401; rollback verificat.
- PR #65: dovezi fizice 8798 2/2 PASS și eliminarea mesajelor false `STOP` de la testele negative.
- PR #66: workflow manual `.github/workflows/stage-magnetra-worker.yml`, cu `wrangler@4.102.0 versions upload --keep-vars` și cerința numelor `BTDIGG_GATEWAY_TOKEN`, `MAGNETRA_GATEWAY_TOKEN`. **PR #66 verificat merged** la `2428f0120b213f706d9e6e0ae994c248d80c6c12`.
- Acest checkpoint va fi înregistrat ulterior pe `main` prin PR dedicat; înaintea oricărei acțiuni noi verificați SHA-ul real de pe main.

## Dovezi de la Rock64, separate de producția Cloudflare

- Rock64 Armbian Debian Trixie, IP LAN `192.168.0.216`; servicii preexistente, care NU trebuie repornite/modificate fără motiv: BTDigg `127.0.0.1:8796`, EZTV `127.0.0.1:8797`, gateway central Magnetra `127.0.0.1:8798`; tunnel `magnetra-btdigg-rock64` existent.
- Rute externe publicate în același tunnel: `btdigg-rock64.alexlab.media→8796`, `magnetra-rock64.alexlab.media→8798`; NU creați alt tunnel/rută, NU modificați BTDigg.
- Protecție: `/healthz` fără bearer pe 8796/8797/8798 = HTTP 401; Worker de probă real a returnat `PASS_UNAUTHENTICATED_401`, `status=401`, fără error 1042 pentru această cale. Worker temporar și domeniu de probă șterse după confirmarea proprietarului.
- EZTV: teste independente reale original→8797→8798, **53 magneturi identice**. Autentificare Worker→8798 nu este demonstrată.
- OxTorrent `https://www.oxtorrent.co`: original search `/recherche/ubuntu`, 3 rezultate pertinente, primul link detalii HTTP 200 și ancoră magnet BTIH bine formată.
- Torrent9 `https://www7.torrent9.to`: original search `/search_torrent/ubuntu.html`, 3 rezultate pertinente, primul detaliu HTTP 200 și magnet BTIH bine format.
- Primul upgrade 8798 a eșuat la `ConnectionRefusedError` imediat după `systemctl restart`, iar rollback-ul a restaurat serviciul. PR #64 a introdus bounded startup wait. Al doilea upgrade `60e2d250e318bf6eca65b5ad7acb55f62d378125` a trecut **92 teste Python**, `POST_RESTART_READY`, `POST_INSTALL_OK`, `PASS checked_sources=2`, ambele HTTP 200 + magnet via 8798. Instalare fizică confirmată de utilizator.
- Aceste rezultate nu demonstrează downloadul torrentului sau rezultate în PWA.

## Catalogul de 46: audit istoric, nu disponibilitate live

- Audit vechi (13.10.2026) `38373699387`: **13 cu rezultate, 12 gol/neconfirmat, 21 erori** pentru o singură interogare; statusurile NU se aplică automat zilei curente.
- Triere generală în `worker/src/recovery-strategy.mjs`, `scripts/recovery-plan.mjs`, API în cod `/api/recovery-plan`. Nevoia utilizatorului: providerii funcționali sus, defecți jos, fără a șterge niciunul și fără rezultate substituite între provideri. Această ordonare în producție nu este confirmată implementată.
- BitSearch candidat `bitsearch.eu`: HTTP 520, nu se activează automat.
- 1337x, BT4G, Ext: 403 și de pe Rock64, deci gateway rezidențial nu este soluție demonstrată.
- Torrentz: problemă de transport local. HTTP 429: respectare limită, fără bypass/retry automat. Redirecționări/zero rezultate trebuie investigate cu dovezi reale.
- Pentru fiecare nou provider: origine allowlist fixă, test sursă reală, parser, căutare, pagină detalii/magnet dacă necesară, rate limit, test E2E Worker și protecția surselor deja valide.

## Cloudflare: starea exactă la checkpoint

- Worker de producție: `alexlab-magnetra`, domeniu `index.alexlab.media`.
- Din captura iPhone de dinainte de upload: versiune activă **`a9df4429` la 100% trafic**, dashboard arăta 0% errors. Acesta este **rollback target identificat**; procentul 100% trebuie **reverificat după noul workflow**.
- `BTDIGG_GATEWAY_TOKEN` era singurul secret. Utilizatorul a adăugat `MAGNETRA_GATEWAY_TOKEN` din dashboard prin **Save version**, NU Deploy, creând draft neactivat **`ce808b27`**. Nu se cunoaște dacă `ce808b27` conține codul de pe main, deci **NU deploy pe ce808b27**. Nu rotiți tokenul BTDigg.
- În 17.10.2026 utilizatorul a trimis captură GitHub Actions verde: **`Stage Magnetra Worker (NO DEPLOY)` execuția #1**, *via manual request*, branch **`main`**, durata afișată **23s**, `just now`. Workflow-ul din main execută manual `wrangler versions upload --keep-vars`; **nu face deploy/traffic promotion**. E rezonabil să consemnăm succesul workflow-ului/uploadului conform capturii, însă **ID-ul exact Cloudflare al versiunii cu cod nou NU a fost observat; nici bindingurile din acea versiune nu au fost inspectate**. Nu susțineți că producția funcționează cu noul cod.
- Statusuri păstrate distinct: `worker_code_version_uploaded=true` conform Action verde; `new_code_version_cloudflare_id_verified=false`; `new_code_version_required_bindings_verified=false`; `active_100_percent_after_stage_reverified=false`; `worker_code_version_activated=false`; `staged_worker_authenticated_test_passed=false`; `worker_to_tunnel_authenticated_e2e_confirmed=false`; `shared_magnetra_gateway.worker_activated=false`; `provider_recovery_v1.production_deployed=false`.
- Secretele au fost setate pe Cloudflare, fără a fi lipite în chat/GitHub/fișiere frontend. Nu cereți valorile lor.

## URMĂTORII PAȘI (fără presupuneri)

1. Proprietarul deschide Cloudflare `Workers & Pages → alexlab-magnetra → Deployments` și furnizează captura după workflow cu **Active deployment** plus versiunea nouă apărută, mesaj `Magnetra 46-provider stage: EZTV/OxTorrent/Torrent9 8798, no traffic`, versiunea ei exactă, și dacă `a9df4429` rămâne 100%. Nu apăsați Deploy/Rollback/Rotate.
2. Inspectați **detaliile noii versiuni** (nu `ce808b27`) și verificați că include codul nou Worker, assets, bindinguri **ambele secrete ca NUME**, domeniul corect. Evitați orice extragere sau publicare de valori secrete.
3. Planificați canary/test pe o cale sigură. Nu confundați pagina Cloudflare Worker Versions cu un endpoint de preview testabil fără configurare; validați posibilitatea reală înainte de instrucțiuni. Dacă testarea unei versiuni fără trafic nu este posibilă, cereți aprobare explicită pentru o **promovare graduală, cu rollback imediat** și test limitat. Rețineți restricțiile de Worker→same-zone Tunnel dovedite numai pentru no-auth GET.
4. Testați autentic **EZTV** cu IMDb corect, **OxTorrent + Torrent9** cu un termen relevant și POST de rezolvare magnet; verificați răspunsuri, source identity, erorile și BTDigg nemodificat. Nu descărcați torrente și nu expuneți magneturi în loguri.
5. Numai după confirmare E2E și acord explicit, creșteți procentul producție la versiunea nouă, păstrând rollback `a9df4429`; efectuați `scripts/check-production-smoke.py` și `scripts/audit-live-providers.py` pe 46 indexere. Nu executați vechiul GitHub `deploy-pwa.yml` `workflow_dispatch`/commit cu `[deploy-pwa]` până nu este pregătită promovarea; ar face deploy direct.
6. Continuați programul de recuperare pentru celelalte surse cu dovezi, fără noi tunneluri și fără planuri plătite.

## Reguli de protecție

- Nu modificați `index.alexlab.media`, BTDigg 8796, EZTV 8797, alte servicii Rock64 sau proiectele Plex/NexaPanel, tunnelul existent ori `global_fetch_strictly_public`.
- Schimbările materiale în repo: PR + 4/4 CI (PWA contracte, invariante, Android debug, Android staging) înainte de merge, fără direct-main.
- Nu inventați disponibilitate live, numere de versiune Cloudflare, succes E2E sau valori secrete; cereți doar captura Cloudflare fără valori și păstrați backup/rollback.


## 2026-10-17 — Live Cloudflare screenshot + verified staged Version ID (post-PR #67)

GitHub Actions run #1 logs on `main` at SHA `2428f0120b213f706d9e6e0ae994c248d80c6c12` show **Worker Version ID `249d6767-f4dc-4f4d-bbf7-f57bea2e5554`**, with Wrangler 4.102.0 `versions upload --keep-vars`, **96/96 Worker tests PASS** and asset binding `ASSETS` visible at upload. PR #67 documenting earlier staging was merged at `e31f1fac0e30e0a7abbd2f2bc1a01bba9a457aaa`.

User Cloudflare screenshot at ~16:37 local time: deployment `a9df4429` **remains at 100% production traffic**; staged version `249d6767` listed but **not active**; secret-only `ce808b27` still inactive. Second screenshot at ~16:42 local time: **Production Settings lists two secret names** (BTDIGG and MAGNETRA gateway); **this does not verify that both are bound in the specific staged version**. Production `workers.dev` and Preview `workers.dev` are both OFF; the canonical custom production domain `index.alexlab.media` remains. "No connected bindings" in Settings must not be interpreted as proof that `ASSETS` is missing; Worker upload output independently showed `env.ASSETS`.

The new **manual-only, read-only** workflow `.github/workflows/inspect-magnetra-cloudflare-version.yml` uses existing GitHub-held API credentials and two Cloudflare **GET** endpoints to inspect specific version binding *names/types* and current deployment shares. It does not expose raw responses, secrets or magnet URLs, and does not upload/deploy Worker code. **As of this documentation, workflow has NOT yet been executed and version-specific binding verification is NOT PASS.** Its results must be reviewed before a safe isolated E2E plan.

There is no new Rock64 installation, tunnel or DNS change, no change to BTDigg and no production activation. Version URLs remain OFF because public previews would expose another entry point unless secured; do not enable automatically. Retain `a9df4429` as rollback while verified to be live, and never deploy secret-only `ce808b27`.

## 2026-10-17 18:06 Europe/Rome — Worker version binding audit PASS (LATEST)

**GitHub Actions run:** [Inspect Magnetra Cloudflare Version (READ ONLY) #1](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39047958484), manual workflow_dispatch on reviewed `main` commit `8ce9c9b2458dac8a0caa642997467fea48bc6e14`, complete SUCCESS. Job `117440400755` executes the **exact version** Cloudflare GET audit with 6/6 no-leak parser tests passing and no writes. Result lines: `VERSION_ID_MATCH: PASS`, `BTDIGG_GATEWAY_TOKEN: PASS`, `MAGNETRA_GATEWAY_TOKEN: PASS`, `ASSETS: PASS`, `ROLLBACK_ACTIVE_100_PERCENT: PASS`, `CANDIDATE_NO_TRAFFIC: PASS`, `STAGE_METADATA_GATE: PASS`. Candidate exact ID: **`249d6767-f4dc-4f4d-bbf7-f57bea2e5554`**. Thus **specific-version binding names/types verified**, and production deployment still targets historical `a9df4429` 100%. Log `CANDIDATE_HAS_PREVIEW: UNVERIFIED`; owner's previous Cloudflare Domains screenshot shows Preview URL toggle OFF.

**No end-to-end authenticated provider search yet.** `staged_worker_authenticated_test_passed=false`, `worker_to_tunnel_authenticated_e2e_confirmed=false`, `worker_code_version_activated=false`, `production_worker_promotion_completed=false`, `canary_rollout_approved=false`; no provider may be marked production-recovered based on this audit.

**Next gated approach (NOT EXECUTED):** Because Version URLs are OFF, Cloudflare [Version Overrides](https://developers.cloudflare.com/workers/versions-and-deployments/version-overrides/) can select the candidate only when it is included in the currently active deployment. Cloudflare supports a controlled deployment containing `a9df4429` at **100%** and candidate `249d6767` at **0%**, followed by an explicitly targeted `Cloudflare-Workers-Version-Overrides` request. This is a deployment configuration mutation despite 0% normal traffic and **requires explicit owner approval** and exact rollback preflight before use. Version override may not be applied; must verify invoked version, not mistake old Worker results for new candidate. No Preview URL exposure, no new tunnel, no secret output, no auto torrent downloading. If header override cannot be independently verified, STOP. Prepare a scoped E2E plan for authentic EZTV IMDb, OxTorrent/Torrent9 Ubuntu search plus deferred magnet resolution, BTDigg baseline and post-check audit of all 46 providers. If another safer supported isolated test path becomes available, assess first.

**Do not run:** `wrangler deploy`, promote/split, `[deploy-pwa]`, any traffic mutation, router/tunnel/Rock64 modification until separately approved. Preserve rollback `a9df4429` and don't activate secret-only `ce808b27`.


## 2026-10-17 — Explicit authorization for 100% old + 0% candidate E2E slot (NOT YET EXECUTED)

Owner explicitly confirmed the narrowly-scoped Cloudflare operation to create a **two-version deployment** with previous `a9df4429` at **100% normal traffic** and candidate **`249d6767-f4dc-4f4d-bbf7-f57bea2e5554` at exactly 0%**, only for targeted `Cloudflare-Workers-Version-Overrides` E2E testing. This approval does **not** authorize 0.01%, 1%, or any ordinary traffic to the new version, secret changes, other code deployments or general production promotion.

Official Cloudflare documentation at https://developers.cloudflare.com/workers/versions-and-deployments/version-overrides/ explicitly demonstrates a 0% candidate included in current deployment; Wrangler version deploy noninteractive accepts `<old-id>@100%` and `<new-id>@0%`. Cloudflare public API specification displays 0.01 as minimum; **if Cloudflare rejects exactly 0%, STOP safely, do not round up**.

The dedicated GitHub Actions workflow `.github/workflows/configure-magnetra-zero-percent.yml` is strictly **manual-only** on main and requires typed input `CONFIRM_OLD_100_NEW_0`. It revalidates exact Worker version, candidate binding names/types, current 100%-old deployment, full previous UUID retrieved from Cloudflare, then invokes pinned Wrangler 4.102.0 to request 100% old + 0% candidate. Postflight checks both exact percentages; if they deviate, it attempts bounded rollback to old 100%. On any missing proof, token/API error or concurrent deployment it stops rather than mutating/overwriting unrelated versions. Raw API outputs, Wrangler stderr, tokens and magnets are withheld from logs. Tests assert exactly 0% (never 0.01%). **The workflow has not been run yet, and the two-version slot is NOT verified configured.**

Previously [manual exact-version GET audit #1](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39047958484) passed for BTDIGG, MAGNETRA and ASSETS bindings and previous 100%-old only state. The candidate is not yet proven Worker→Tunnel→8798 authenticated, no EZTV/OxTorrent/Torrent9 PWA E2E success, and no production provider recovery can be claimed. Preview workers.dev remains off. Any later activation above 0% requires **new explicit owner approval** and live rollback verification.


## 2026-10-17 19:24 Europe/Rome — authorized exact Cloudflare 100/0 deployment PASS, candidate E2E pending

Owner triggered [GitHub Actions Configure Magnetra 0 Percent E2E Slot #3](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39053562983), workflow_dispatch on main `9bdca3e1753e50d49c46a8e9fb5df5eae3de492c`. Run SUCCESS; real deployment phase (not mock tests) printed `PRECHECK_PASS`, `ZERO_PERCENT_ONLY`, `APPLYING`, `POSTFLIGHT_PASS: exact old 100% and candidate 0% verified by API`, and `OVERRIDE_SLOT_READY`. GitHub step and overall job both succeeded. Previous `a9df4429` remains 100% ordinary traffic; candidate exact `249d6767-f4dc-4f4d-bbf7-f57bea2e5554` is **present at 0% in current deployment**. No public-preview workers.dev, tunnel, secret or Rock64 changes. Invariants now record this actual postflight.

Cloudflare [Version Overrides](https://developers.cloudflare.com/workers/versions-and-deployments/version-overrides/) supports `Cloudflare-Workers-Version-Overrides: alexlab-magnetra="249d6767-f4dc-4f4d-bbf7-f57bea2e5554"` for a version included at 0%. **Override may silently not be applied**: successful HTTP 200 does NOT prove routing to candidate. Its documented safeguards require either per-invocation version observability or a differentiating code behavior. Existing candidate has no version-metadata response binding. Next test will require the legacy 100%-active API to return 404 for `GET /api/recovery-plan`, and override candidate to return 200 with all 46 recovery metadata records. If both return identical responses, STOP and mark `OVERRIDE_ATTRIBUTION_UNVERIFIED`; do not infer which version ran.

A newly staged **manual only, read-only** workflow `.github/workflows/test-magnetra-candidate-e2e.yml` first verifies through Cloudflare GET that the two-version deployment is still precisely 100%/0% and that candidate has `ASSETS` and both gateway secret bindings. Then it requires the candidate-only fingerprint, verifies 46 provider IDs, searches `ubuntu` from `oxtorrent` and `torrent9` (one query each), resolves one genuine same-origin details magnet per provider via `POST /api/resolve`, and checks `eztvx` by canonical IMDb `tt0460681` through the existing 8798 authenticated dispatch. It also makes at most one observational BTDigg query, never retries or downloads torrent payloads, never logs magnet strings, tokens, source HTML, raw upstream error responses or secret values. An absent/blocked upstream response remains **UNVERIFIED**, not fictional PASS; no updates to production source-health snapshot on an incomplete audit.

**The E2E workflow is not yet integrated or executed at this checkpoint.** New CI tests cover the version fingerprint, provider attribution, input approval, no-leak magnet handling, and exact 100/0 gate. No provider E2E is marked PASS yet. Promotion of the candidate above 0% still requires a separate explicit owner approval and guarded rollback.
