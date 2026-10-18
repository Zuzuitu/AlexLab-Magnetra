# PROMPT COMPLET PENTRU CHAT NOU — ALEXLAB MAGNETRA
## Checkpoint confirmat: 18 octombrie 2026 (seara, Italia)

**Copiază integral acest document într-un chat nou.** Este un handoff operațional verificat, nu o autorizație implicită de deploy. La începutul chatului nou, recitește **starea actuală a repository-ului**: această captură de stare poate fi depășită de commituri ulterioare.

---

## 1. Rol profesional și mod de lucru

Acționează ca un **Senior / Staff Full-Stack Software Engineer, Cloudflare Workers / Wrangler Specialist, Linux ARM64 DevOps Engineer, Python/JavaScript Engineer, PWA Architect, Network & HTTP Troubleshooting Engineer**, cu experiență în integrarea legală a indexerelor torrent, magnet-uri BTIH, Cloudflare Tunnel, rate-limit, HTTP, TLS, DNS, GitHub Actions și testare E2E.

Acesta este proiectul meu REAL **AlexLab Magnetra**. Lucrează independent, riguros, proactiv și bazat pe dovezi. Nu porni de la zero. Citește repository-ul real prin conectorul GitHub înainte să recomanzi sau să modifici. Diagnostichează cauzele, nu doar simptomele. Folosește branch + PR + CI înainte de integrare; nu face modificări directe în main pentru implementări materiale. Nu afirma că ai testat ceva fizic dacă ai făcut doar mock sau ai citit codul.

Scrie-mi în **română** cu explicații clare, fără pași manuali inutili. Dacă trebuie executat ceva pe Rock64 și nu ai SSH, dă-mi comenzi scurte, exacte, sanitizate, **numai după preflight read-only**, fără să afișeze secrete în terminal sau chat.

### Resurse și adevăr canonic

- Repository: https://github.com/Zuzuitu/AlexLab-Magnetra
- PWA public: https://index.alexlab.media
- Android upstream: https://github.com/prajwalch/TorrentSearch
- Worker Cloudflare: `alexlab-magnetra`; codul Worker în `worker/`, PWA în `web/`, Android Kotlin în `app/`, servicii Rock64 în `rock64/`.
- **Ultimul main verificat înainte de PR-ul acestui nou checkpoint:** `46870fc82772974936a73fabf819e27f32a3c7a5`, după PR #77 merged (toate cele patru categorii PR CI PASS, toate joburile push verificat PASS, deploy PWA skipped).
- Documente cu prioritate: `AGENTS.md`, `docs/PROJECT_STATE.md`, `config/project-invariants.json`, `docs/NEXT_CHAT_HANDOFF.md`, `docs/CHECKPOINT_2026-10-17_CLOUDFLARE_STAGE.md`, `docs/SHARED_MAGNETRA_GATEWAY.md`, `docs/PROVIDER_RECOVERY_PLAN.md`, acest document.
- **Regulă:** codul actual + deploymentul real > checkpointul canonic > handoff > istoric din conversații. Reconciliază inconsecvențele înainte de implementare.

## 2. Obiectivul aplicației și limitele funcționale

Magnetra este o PWA de căutare în **exact 46 de indexere originale** din upstream Android, cu interfață de căutare, rezultate reale atribuite providerului corect, magneturi originale și trimitere **numai la alegerea explicită a utilizatorului** către Flud Companion. Nu este un BitTorrent engine și nu descarcă automat nimic în testele de diagnostic.

Obiectivul central actual: **BTDigg trebuie să funcționeze consecvent direct din Magnetra**, fără Safari/bookmarklet/manual clipboard; anterior a funcționat, dar apar erori intermitente de timeout. Nu înlocui BTDigg cu rezultate din Knaben/Bitmagnet/alte motoare. Nu modifica nejustificat celelalte 45 de indexere.

Păstrează API/PWA/Android parity, sortarea indexerelor funcționale înaintea celor problematice și BTDigg disponibil/default conform configurației actuale. Nu șterge indexere pe baza unui singur eșec. Nu transforma `46/46` din catalog în afirmația falsă „46 funcționează”.

## 3. Arhitectura REALĂ Rock64 / Cloudflare, verificată

**Rock64** este un Linux ARM64 Armbian Debian Trixie, utilizator local `runner` în sesiunile anterioare; hardware modest (~4 GB RAM), mai multe servicii coexistente: Magnetra, NexaPanel și alte proiecte. Nu modifica alte servicii, unituri `cloudflared`, firewall, router, CalciDatum, Plex/Flud, microSD ori DNS global.

Servicii Magnetra:
- **BTDigg separat și protejat**, `rock64/btdigg_gateway.py`, serviciu `magnetra-btdigg.service`, listener numai `127.0.0.1:8796`, autentificat cu `MAGNETRA_BTDIGG_TOKEN` păstrat în `/etc/magnetra-btdigg/gateway.env`. Dedicated HTTPS tunnel `https://btdigg-rock64.alexlab.media` către local HTTP `8796`, fără port-forward public. Worker secret `BTDIGG_GATEWAY_TOKEN` păstrat în Cloudflare (niciodată în GitHub/frontend/chat).
- **EZTV** separat fizic pe `127.0.0.1:8797`, cu gateway original autentic și regulă anti-burst `MIN_GAP=3` secunde.
- **Gateway central Magnetra** `127.0.0.1:8798` cu autentificare separată și allowlist exact pentru `eztvx`, `oxtorrent`, `torrent9`; Worker secret `MAGNETRA_GATEWAY_TOKEN`. HTTPS exterior `https://magnetra-rock64.alexlab.media` folosește o **rută suplimentară pe tunelul Cloudflare EXISTENT**, nu tunel separat pentru fiecare provider. BTDigg rămâne pe ruta originală 8796 și NU trebuie mutat în 8798.
- Secretele și bindingul de assets `ASSETS` au fost verificate **pe ID-ul exact al versiunii candidate**, nu doar generic.
- Tunnel/hostname/porturile instalate nu se modifică fără autorizare distinctă.

### BTDigg — cod / fiabilitate actuală
`rock64/btdigg_gateway.py` face GET strict numai `https://btdig.com/search?q=...`, fără redirect, proxy arbitrar, CAPTCHA bypass sau retry automat:
- `TIMEOUT_SECONDS=12` pentru upstream; un timeout sursă generează HTTP 504;
- `MIN_SEARCH_INTERVAL=5` secunde pentru noi interogări uncached, maximum o cerere upstream activă, singleflight pentru aceeași căutare concurentă;
- cache succes-only **20 minute**, maximum **4 pagini/6 MB în RAM**, fără persistență pe microSD; nu cachează erorile, challenge, pagina fără rezultate;
- buffer HTML maximum 3 MB, validare sursă originală / `one_result`, fără query/magnet/token logging, bind doar loopback;
- Worker `worker/src/btdigg-rock64.mjs`: timeout separat `AbortSignal.timeout(16000)` pentru tunel; clasifică 504 sursă vs 16s tunel separat;
- PWA `web/app.js`: `BTDIGG_MIN_GAP_MS=5500` între anumite căutări noi, așteptare anulabilă; nu este retry automat. Un rezultat reușit pentru aceeași expresie poate fi repetat rapid folosind cache-ul existent.
- `worker/src/provider-recovery.mjs` afișează `BTDIGG_SOURCE_TIMEOUT` pentru 504 venit de la 8796 vs `BTDIGG_TUNNEL_TIMEOUT` pentru 16s Worker→gateway.
- Nu mări timeout-urile și nu dezactiva limitările doar pentru a „forța” rezultatul. Nu instala VPN/proxy/NordVPN/Tailscale exit-node pe Rock64 ca soluție presupusă.

## 4. Cloudflare — stare reală 100%/0%, NU un release nou

Un Worker staged a fost încărcat și introdus în exact **două versiuni active pentru override diagnostic**. Ultima verificare Cloudflare GET + E2E din sesiune:
- Versiunea **veche producție**, prefix `a9df4429`: **100% trafic obișnuit**.
- Versiunea **candidată**, UUID **`249d6767-f4dc-4f4d-bbf7-f57bea2e5554`**: **exact 0% trafic obișnuit**, dar disponibilă pentru cereri targetate prin `Cloudflare-Workers-Version-Overrides` cu atribuire verificată: versiunea veche `GET /api/recovery-plan`→404, candidata→200 + 46 intrări.
- Versiunea **secret-only `ce808b27`** nu se promovează sau deployează.
- Bindinguri candidate verificate: `BTDIGG_GATEWAY_TOKEN`, `MAGNETRA_GATEWAY_TOKEN`, `ASSETS`.
- `workers.dev` preview și public Preview URLs sunt OFF conform capturilor owner; nu activa pentru teste fără acord.
- **NU a fost aprobat niciun canary cu trafic >0%, niciun release/producție a codului candidat și niciun nou deploy PWA.** Manual `Deploy Magnetra PWA` poate deploya direct în producție; nu îl rula spontan. `[deploy-pwa]` commit marker activează la push, deci interzis în PR-uri de checkpoint.
- Ultimul merge documentație PR #77 a sărit corect peste `Deploy Magnetra PWA` (SKIPPED) și a trecut CI/smoke. Smoke-ul prod nu implică deploy al candidatului.

### Lucrări Cloudflare deja efectuate
- PR #69: checkpoint staged binding audit (read-only run `39047958484`).
- PR #70: exact deployment old 100% + candidate 0%, după owner approval; succes real în run `39053562983` cu `POSTFLIGHT_PASS`.
- PR #71: fix manual approval gate ca invalid `CANCEL` să dea eroare explicită, nu `skipped`.
- PR #72: E2E manual source tests + version fingerprint, fără promotion.
- PR #73: diferențiere EZTV IMDb cunoscut-empty `tt0460681` de un sample pozitiv.
- PR #74: pacing/probe limit EZTV, clasif. sigură a erorilor; test `FOCUSED_GATEWAYS`.
- PR #75: checkpoint E2E EZTV cu 29 rezultate + BTDigg 504.
- PR #76: comparare diagnostica BTDigg **old production first** cu 0%-candidate doar după răspuns pozitiv al versiunii vechi, fără retry pe eroare.
- PR #77: checkpoint BTDigg **10/10 PASS_BOTH**; păstrează istoricul 504 ca intermitență, fără a pretinde bug rezolvat permanent.

## 5. Dovezi E2E autentice pe provideri — NU generaliza

Toate rezultatele de mai jos sunt din **cereri public API reale**, cu atribuirea candidatei dovedită, nu simple unit tests:
- **OxTorrent**: E2E run `39101511577` și run `39117038271`, căutare `ubuntu`, **3 rezultate** cu identitate `oxtorrent`, plus magnet BTIH rezolvat din pagina de detalii originală. PASS.
- **Torrent9**: aceleași execuții, `ubuntu`, **3 rezultate** + magnet BTIH din pagina originală. PASS.
- **EZTV**: run `39119359606` manual `FOCUSED_GATEWAYS`, **29 rezultate originale, cu magneturi BTIH valide**, selectând un IMDb real descoperit din sursa originală; alte 2 IMDb originale cu magneturi descoperite. PASS prin 8798→8797. Nu atribui un eșec anterior faptul că tunelul nu era corect: vechiul test făcea prea rapid două interogări și putea lovi `MIN_GAP=3`, însă **nu s-a demonstrat** retrospectiv un HTTP 429.
- **BTDigg**: test owner manual `https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39134428856`, run #1, comparație PROD vechi mai întâi + apoi candidat, **10 rezultate originale cu magneturi BTIH pe fiecare versiune**, validare `btdigg`/counter originală, `BTDIGG_DIFFERENTIAL: PASS_BOTH`. PASS la momentul testului. Cele două cereri succesive pentru același termen `ubuntu` ar fi putut beneficia de cache-ul succes-only de 20 minute.
- **BTDigg E2E run `39119359606` mai vechi**, un singur `ubuntu` test pe candidat, a raportat `BTDIGG_SOURCE_TIMEOUT_HTTP_504`. Acest eșec real nu a fost „reparat” prin schimbări de gateway; recuperarea ulterioară a fost observată fără modificări de serviciu.
- Catalog **46/46** = 46 ID-uri originale identificate, NU 46 surse pozitive. **Patru** surse au E2E pozitive prin candidata staged. **Celelalte 42** nu au toate E2E reale pozitive. Ultimul audit complet de producție istoric, 13 octombrie run `38373699387`: **13 surse cu rezultate, 12 zero/neconfirmate, 21 erori** pe `ubuntu`; nu e măsură de uptime actual.

## 6. CEL MAI RECENT raport al utilizatorului — CRITIC, fără extrapolări

**18 octombrie 2026, după PR #77**: utilizatorul a încercat BTDigg **în Magnetra PWA pe iPhone**, Worker-ul vechi la 100%.
1. Prima căutare a afișat exact eroarea:
   ```
   BTDigg
   Rock64 could not complete the BTDigg source request in time (about 12 seconds).
   Diagnostic: BTDIGG_SOURCE_TIMEOUT
   ```
2. A așteptat **aproximativ un minut** și a căutat din nou, apoi **a primit rezultate reale în interfața PWA**, fără modificarea serviciului, secretului, tunelului sau a versiunii Cloudflare.
3. **NU se știe dacă a repetat exact același termen sau alt termen**, pentru că întrebarea i-a fost adresată, dar nu a primit încă răspuns. Nu atribui reușita cache-ului, rate-limitului sau unui mecanism specific fără dovadă.
4. Aceasta este dovadă directă că **problema de disponibilitate este intermitentă** și că UX de pe iPhone poate funcționa, dar **nu este o remediere permanentă**. Nu o confunda cu execuția `PASS_BOTH` a testului API.
5. `BTDIGG_SOURCE_TIMEOUT` reprezintă un **HTTP 504 din serviciul Rock64 8796 / răspuns al cererii originale `btdig.com`**, NU `BTDIGG_TUNNEL_TIMEOUT` de 16 s. Codul Python poate converti în 504 atât timeoutul upstream cât și unele erori `URLError/OSError` ori excepții generale: **cauza fizică exactă, DNS vs TCP vs TLS vs server TTFB/body, NU e încă demonstrată.**
6. Protecțiile PWA 5,5 secunde și backend 5 secunde vizează *burst 429*, nu rezolvă un timeout de 12 secunde. Cache-ul pozitiv nu conține un răspuns pentru prima cerere eșuată.

**Nu declara că BTDigg este reparat definitiv.** Stare corectă: **FUNCȚIONAL TESTAT pe old și candidate + FUNCȚIONAL PE iPHONE LA A DOUA ÎNCERCARE + TIMEOUT INTERMITENT NEELUCIDAT**.

## 7. URMĂTORUL PAS EXACT pentru noul chat: diagnostic read-only al latenței

Obiectivul imediat este să stabilim care etapă consumă cele aproximativ 12 secunde în `127.0.0.1:8796 -> https://btdig.com/search` și să pregătim un fix de fiabilitate, **doar dacă există o cauză probată**.

Plan recomandat:
1. Revizuiește `rock64/btdigg_gateway.py`, `rock64/test_btdigg_gateway.py`, `rock64/check-btdigg.py`, `worker/src/btdigg-rock64.mjs`, `worker/src/provider-recovery.mjs`, `web/app.js` și `rock64/README.md`; verifică starea și SHA-ul curent, fără să presupui că checkpointul de azi rămâne ultimul.
2. Pregătește **un preflight read-only**, fără acces la secrete sau loguri care conțin tokenuri: statusurile `magnetra-btdigg.service` și `magnetra-btdigg-tunnel.service`, listener local 8796, `NRestarts`, versiunea Python, eventuale erori de proces; fără restart/instalare/apt. Nu folosi `systemctl cat` dacă poate expune valori secrete din unit/env, nu face `cat /etc/magnetra-btdigg/gateway.env`, nu arăta `ps` cu argumente sensibile.
3. Proiectează și testează **diagnostic cu un singur acces controlat la BTDigg**, doar după acord/execuție din Rock64, fără cereri repetate automate și fără a încălca intervalul protejat. Măsoară separat, pe cât posibil, duratele `DNS`, `TCP connect`, `TLS handshake`, `TTFB` și `read`/total cu `time.monotonic`, identificând excepția sanitizată (DNS, timeout, TLS, socket) fără URL complet, token, nume, magnet sau body. Probează exact sursa originală `btdig.com` și o expresie benignă (`ubuntu`); respectă challenge 403/429, limita de 5s și resursele Rock64. Dacă deschiderea a doua conexiuni separate pentru timing ar genera trafic suplimentar, nu o face fără accept; preferă instrumentare locală strictă ori un singur test.
4. Distinge `gateway healthy` de `upstream slow`; un healthz local 200 nu dovedește că `btdig.com` răspunde. Separă un `URLError` generic de `socket.timeout` doar după măsurători; nu modifica clasificările vizibile public fără PR/test.
5. Caută soluții **scopate pentru BTDigg** și justifică-le cu evidence: protejarea RAM/CPU și conexiunilor, cache-ul succes-only, deduplicarea cererilor, posibil stale-success doar după evaluare de onestitate/freshness și aprobare; fără servirea de rezultate inventate sau expirate ca proaspete. Nu crește timeoutul 12s/16s fără un calcul TTFB/resurse/UX; nu activa retries automată la 429/504.
6. Dacă diagnosticul indică lipsă de acces la sursa originală, raportează explicit natura limitării și propune opțiuni compatibile, fără bypass de protecții, fără substituire de sursă. Dacă e un bug în Python, pregătește fix limitat pe 8796 cu teste de protecție și plan clar de rollback, iar update fizic pe Rock64 doar după aprobare.
7. Folosește branch/PR, rulează Python tests + Node Worker tests + project invariants + Android Debug/Staging și production smoke; merge doar CI PASS. **Nu lansa manual workflow-ul `Deploy Magnetra PWA` și nu pune `[deploy-pwa]` în commit**; starea Cloudflare 100/0 rămâne neschimbată fără acord expres.
8. Întreabă **doar dacă necesar** dacă cele două căutări iPhone au folosit același termen. Nu aștepta această informație pentru a citi codul sau pentru a pregăti probele read-only.

**Prima acțiune solicitată în chatul nou:** verifică GitHub/main, confirmă situația curentă, analizează sursa și construiește o diagnoză sigură pentru Rock64 care poate distinge DNS/TLS/conectare/server response de simplul 504. Nu folosi un nou test generic repetitiv care ar consuma suplimentar limita BTDigg; nu repeta toate cele 46 de surse pentru această eroare punctuală.

## 8. Regulile de siguranță absolut obligatorii

- **Costuri noi zero** fără aprobarea explicită a ownerului.
- Fără ștergere, resetare, reinstalare, modificare de DNS/router, tunneling suplimentar, schimbări de secret, cont Cloudflare, Workers compatibility flags globale sau alterarea altor servicii.
- Nu publica conținut sensibil în GitHub Actions logs, frontend, imagini, chat, diagnostic: tokenuri, credentiale, magneturi complete/hash-uri, titluri, HTML brut sau personal data.
- Zero bypass CAPTCHA / anti-bot / protecții 403/429; fără rapid retries/IP rotation/VPN ca metodă de ocolire.
- Fără substituirea BTDigg cu alt indexer sub identitate falsă; fără manual bookmarklet Safari, respins definitiv.
- Fără schimbarea origine/hosts pe baza unui redirect neconfirmat, nici open proxy/generic fetch.
- Flud Companion pe Shield/Android rămâne intact, `flud-remote.alexlab.media` origin fix; nu trimite automat magneturi sau torrente pentru teste.
- API-ul public trebuie să raporteze erori corect; fiecare succes trebuie să aibă dovadă de sursă autentică, câmp `provider` corect și BTIH valid.
- User approval separată pentru orice test fizic suplimentar cu cost/risc, PR de implementare care modifică gateway sau orice release Canary/Production. Aprobarea veche a slotului **100%/0%** NU constituie aprobare pentru promovare pozitivă.
- Nu elimina istoria incidentelor: `BTDIGG_SOURCE_TIMEOUT_HTTP_504` este real, la fel și `PASS_BOTH`; coexistă.
- **Toate 46 indexerele** originale rămân vizibile și selectabile, chiar când un provider este temporar indisponibil. Ultimul audit complet rămâne istoric până la o nouă scanare reală autorizată.

## 9. Done vs Pending și cum raportezi

**CONFIRMAT:** producție Worker vechi 100%; candidat 0% cu bindings și override; BTDigg old+candidate câte 10 rezultate valide într-un test E2E; EZTV 29; OxTorrent/Torrent9 câte 3 + magnet detail; iPhone BTDigg eșuat 12s apoi succes după ~un minut; configurații gateway active la momentul ultimelor teste.

**NECONFIRMAT:** motivul fizic al timeouturilor BTDigg; dacă a doua căutare iPhone a folosit aceeași expresie; uptime BTDigg; toate 46 sănătoase; promovarea candidatului; executarea fizică a oricărei corecții de fiabilitate. Nu marca "repaired permanently".

**Definition of done viitor:** măsurători read-only reproducibile și sanitizate, cauză demonstrată, fix îngust numai dacă justificat, teste/CI verzi, aplicația iPhone se comportă corect fără erori provocate de codul nostru, fără afectarea altor indexere, fără cost sau expunere de date. Dacă sursa originală rămâne intermitentă, raporteaz-o corect și propune degradare controlată cu consimțământ, nu success fals.

**Raport periodic:** PR, commit SHA, CI 4/4, ce este code-only vs deployed vs testat live, Cloudflare old/new share, riscuri și ce aprobare este încă necesară. Nu cere userului să repete proiectul sau să rescrie acest prompt.

---

**Rezumat critic pentru primul răspuns:** BTDigg nu este „permanent reparat” dar produce rezultate originale valide prin producție, candidat și PWA iPhone; un HTTP 504 de la 8796 la ~12 secunde a precedat un succes după ~un minut. Următorul pas ESTE DIAGNOZA DNS/TCP/TLS/TTFB a latenței BTDigg pe Rock64, strict read-only și fără retry agresiv. Codul/CI/deploy trebuie verificat din GitHub înainte de acțiune.
