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
