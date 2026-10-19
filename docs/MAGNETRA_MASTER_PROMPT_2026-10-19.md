# CONTINUARE PROIECT ALEXLAB MAGNETRA — PROMPT MASTER SENIOR/STAFF
## Checkpoint verificat: 19 octombrie 2026, ~23:00 Europa/Roma — FIX RESOLVE CANARY 95% / 5%

> **Copiază integral în chat nou.** Acest text este un handoff, nu o aprobare de deploy. Regula absolută: **repository \`main\`, codul efectiv, GitHub Actions și starea Cloudflare reală au prioritate față de orice checkpoint/chat**. Cele mai vechi secțiuni din documente sunt cronologie istorică, nu starea curentă.

### 1. ROLUL ȘI MODUL DE EXECUȚIE
Acționează ca Senior/Staff Software Engineer, Full-Stack Developer, Cloudflare Workers/Wrangler specialist, SRE/Linux ARM64 DevOps, Network Engineer și Security Engineer, cu ownership integral pe proiectul **REAL** AlexLab Magnetra. Lucrează autonom: citește codul și dovezile, identifică root cause, propune modificări minime, scrie teste negative și pozitive, deschide branch/PR, urmărește toate verificările CI, corectează probleme și integrează PR după PASS, respectând interdicția de a modifica producția fără aprobarea separată a proprietarului. Comunică **în română**, precis, fără presupuneri, fără blocaje repetate sau întrebări deja rezolvate. Dacă o operațiune cere acțiune GitHub \`workflow_dispatch\` pe care connectorul nu o poate executa, dă direct linkul și opțiunea exactă, apoi verifică **logurile reale** după ce proprietarul spune „Gata”.

### 2. REPOSITORY TRUTH — CITEȘTE ÎNAINTE
- GitHub: https://github.com/Zuzuitu/AlexLab-Magnetra (branch \`main\`); upstream Android: https://github.com/prajwalch/TorrentSearch (MIT).
- PWA public: https://index.alexlab.media; Worker Cloudflare **\`alexlab-magnetra\`**, Custom Domain.
- **Ultimul SHA \`main\` verificat ÎNAINTE de PR-ul acestui handoff:** \`10818d487facbcf1ba66d7f92322926e9b76508a\` (PR #92 deja integrat). După documentarea checkpointului acesta, \`main\` va avea alt SHA: refetch, NU presupune SHA istoric ca HEAD.
- Citește în ordinea: \`AGENTS.md\`, \`docs/PROJECT_STATE.md\`, \`config/project-invariants.json\`, implementarea reală, \`docs/NEXT_CHAT_HANDOFF.md\`, apoi \`docs/MAGNETRA_MASTER_PROMPT_2026-10-19.md\`. Rulează \`python3 scripts/check-project-invariants.py\` și teste relevante.
- Nu confunda **PR merged**, **versiune Cloudflare uploaded**, **deployment record**, **trafic activ**, **test live E2E** și **acceptanță iPhone**. Sunt dovezi diferite.

### 3. STAREA LIVE LA FINALUL SESIUNII — CONCLUZIA CAPITALĂ
**Confirmat din loguri reale la 19 octombrie 2026: Cloudflare are exact două versiuni în deploymentul actual:**
- **\`249d6767-f4dc-4f4d-bbf7-f57bea2e5554\` = 95% trafic obișnuit**. Este versiunea anterioară, pe care PWA „Resolve” pentru OxTorrent/Torrent9 încă poate eșua.
- **\`540b3417-f845-47e8-96bd-856ccc9f1350\` = 5% trafic obișnuit**. Este noua versiune cu fixul \`web/app.js\`, încărcată cu sursa din commit \`c6867647c10bba33db0361178f3380a7ffa48385\`.
- Versiunea istorică \`a9df4429\` a fost scoasă din perechea actuală 100/0 la reconfigurarea slotului pentru 540b, **NU ștearsă**. Versiunea \`ce808b27\` „secret-only” nu se promovează.
- **NU există încă promovare 540b la 100%**, nici aprobare pentru ea, nici acceptanță utilizator iPhone confirmată. **Nu reexecuta stage, 0%-slot, 5%-canary sau E2E fără un motiv verificat.**
- Cele 3 bindinguri din 540b au fost verificate pe versiunea *exactă*: \`BTDIGG_GATEWAY_TOKEN\`, \`MAGNETRA_GATEWAY_TOKEN\`, \`ASSETS\`.
- Rollback sigur din canary cunoscut: **\`249d@100% / 540b@0%\`**, prin workflow-ul deja existent. Acțiunea de rollback a fost **testată offline**, dar nu afirmăm o restaurare live executată în sesiunea actuală.
- \`Deploy Magnetra PWA\` a rămas \`skipped\` la PR-urile de cod și checkpoint; **nu face \`wrangler deploy\` direct**, nu folosi accidental markerul \`[deploy-pwa]\`.

### 4. DOVEZI REALE / RUNS (nu înlocui cu mock-uri)
1. **Versiunea veche \`249d\` a fost promovată anterior la 100%**: https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39243522237 ; două versiuni 249d 100%, a9df 0%.
2. **Producție iPhone:** căutarea \`2026\` pe OxTorrent/Torrent9 afișa 70 rezultate, dar butonul **Resolve** eșua pentru cardurile ambelor surse cu \`Provider could not resolve magnet: Noncanonical source HTML route refused.\`. Separat BTDigg afișa \`BTDigg is limiting requests\` / \`RATE_LIMIT\` 429.
3. **Cauza dovedită prin live search**: https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39286786842 : \`PUBLIC_APP_JS_VS_GITHUB_MAIN: MATCH_REVIEWED_MAIN\`; OxTorrent **50/50** și Torrent9 **20/20** aveau \`details\` canonical, dar \`magnetSource\` era \`OTHER_PATH_TEMPLATE\` și câmpul era preferat de vechiul PWA în **70/70**. Ambele surse au returnat magneturi BTIH valide din \`details\` când \`/api/resolve\` a fost testat pe pagina originală. Nu a fost un bug Rock64/tunel sau necesitate de CAPTCHA/ads-click.
4. **Fix corect în PR #89 (merged)**: \`web/app.js\` \`ensureMagnet(item)\` folosește \`item.details\` **exclusiv pentru \`oxtorrent\` și \`torrent9\`**, cu fail-closed dacă lipsește; restul **44 de provideri** păstrează precedența anterioară \`item.magnetSource || item.details\`. Nu se apasă prima reclamă și nu se slăbește \`routeHtmlRequest\`. Testul simulează 50+20 carduri.
5. **Upload-only 540b**: https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39298077357 — versiunea exactă 540b, fără trafic la upload. **Audit bindings**: https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39303873161 — toate cele 3 PASS și vechea 249d 100%.
6. **0%-slot 249d100/540b0**: https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39310908577 — postflight PASS.
7. **E2E autentificat 540b la 0%**: https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39311804881 — \`STAGED_APP_JS_ATTRIBUTION: PASS\`, 46/46 ID-uri, \`2026\` OxTorrent **50** + Torrent9 **20** rezultate, câte un original magnet BTIH PASS, exact 100/0 păstrat. În loguri există și probe de unit test 1+1; **50+20 din pasul live** sunt cele relevante.
8. **Canary owner-approved 5%, deja EXECUTAT**: https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39323736403 — \`CANARY_PREFLIGHT_PASS\`; în pasul de execuție reală \`CANARY_POSTFLIGHT_PASS: old 249d 95%, fix 540b 5%\`.
9. **Canary E2E la 95/5, owner-run, deja EXECUTAT**: https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39324007635 — \`CANARY_METADATA_GATE: PASS\`, bindingurile 3/3, \`EXACT_TWO_VERSION_APP_JS: PASS\` (selectare explicită 249d/540b prin \`Cloudflare-Workers-Version-Overrides\`; 540b JS coincide cu fixul și 249d diferă), catalog 46/46, \`STAGED_SOURCE_SEARCH_PASS: OxTorrent 50, Torrent9 20\`, ambele \`STAGED_RESOLVE_PASS\` pentru BTIH autentic, \`FIX_540B_CANARY_E2E: PASS\`. NU a trimis magneturi către Flud și NU a modificat traficul.
10. PR #80–#92: audit split, canary istorice, E2E, stage fix, bindinguri, zero slot, canary fix. **PR #92** (merged SHA \`10818d487facbcf1ba66d7f92322926e9b76508a\`) a pregătit canary 5%, read-only E2E și rollback. Toate 4 verificările PR au trecut.

**Limita dovezii:** testul autentificat demonstrează capabilități API, fișierele și două magneturi originale, nu garantează disponibilitate permanentă, fiecare rezultat sau că butonul „Resolve” a fost testat de utilizator pe iPhone. Un utilizator obișnuit poate primi în continuare versiunea cu bug în 95% din trafic.

### 5. ARHITECTURĂ REALĂ
- \`app/\`: aplicația Android upstream Kotlin/Compose/Ktor/Jsoup/Koin, păstrată pentru upstream; app ID \`com.prajwalch.torrentsearch\`, minSdk 25, targetSdk 37, Java 17, Gradle daemon JetBrains Runtime 21. Nu „moderniza” gratuit.
- \`web/\`: PWA mobilă vanilla HTML/CSS/JS, manifest, service worker, selecție indexere, bookmarks, căutări, rezultate, linkuri magnet, \`.torrent\` când sursa le oferă; localStorage pentru preferințe și pairing; nu torrent engine. \`web/app.js\` include fixul PR #89. Serviciul public \`https://index.alexlab.media\` cu API pe același domeniu.
- \`worker/\`: Cloudflare ES Modules, \`worker/src/index.mjs\`, \`catalog.mjs\`, \`providers.mjs\`, \`legacy-specs.mjs\`, \`legacy-adapters.mjs\`, \`html-rock64.mjs\`, \`btdigg-rock64.mjs\`, \`eztv-rock64.mjs\`, \`provider-recovery.mjs\`, \`request-headers.mjs\`, \`source-audit.mjs\`; binding static \`ASSETS\`, API: \`GET /api/health\`, \`GET /api/providers\`, \`GET /api/search\`, \`POST /api/resolve\` și relay Flud.
- Upstream Kotlin \`BuiltinSearchProvidersModule.kt\` are **exact 46 ID-uri**, toate 46 cu adapter implementat, dar **NU înseamnă 46 indexere live funcționale**. Auditul istoric 13 octombrie #38373699387 a numărat 13 cu rezultate / 12 goale-neconfirmate / 21 erori. Nu elimina ID-uri după eșecuri izolate, nu substitui rezultate din alt provider, nu inventa uptime.
- **Rock64 comun ARM64 (~4 GB RAM, Armbian / Debian Trixie)**, rețea LAN istoric \`192.168.0.216\`, găzduiește și NexaPanel, Plex/CarPlay, alte servicii. Fără restarturi, updateuri de sistem, tuneluri, DNS, router, iptables, VPN, fstrim sau modificări pe microSD fără autorizare.
- BTDigg: numai sursă **originală \`btdig.com\`**, serviciu \`magnetra-btdigg.service\` pe **\`127.0.0.1:8796\`**, Cloudflare HTTPS \`https://btdigg-rock64.alexlab.media\`; token privat în env al serviciului, Worker secret \`BTDIGG_GATEWAY_TOKEN\`.
- EZTV: gateway local **\`127.0.0.1:8797\`**, \`MIN_GAP=3s\`; original provider \`eztvx\`, în spatele dispatcherului comun.
- Gateway central Magnetra: **\`127.0.0.1:8798\`**, Cloudflare HTTPS \`https://magnetra-rock64.alexlab.media\` cu secret Worker \`MAGNETRA_GATEWAY_TOKEN\`, allowlist \`eztvx\`, \`oxtorrent\`, \`torrent9\`. Fără open proxy, nu muta BTDigg de pe 8796.
- Cloudflare Worker \`BTDIGG_GATEWAY_TOKEN\`, \`MAGNETRA_GATEWAY_TOKEN\`, \`ASSETS\`: nu afișa valori, nu le pune în logs/frontend/GitHub/URL. Origin/path HTTPS allowlist strict, stop redirects off-origin.
- Flud Companion, proiect distinct \`Zuzuitu/flud-companion\`, relay HTTPS fix \`https://flud-remote.alexlab.media\` către Shield/Flud: PWA nu trimite automat magnet la căutare, Resolve sau teste. Distinge queue 202 de confirmarea Bridge/Shield; \`requestId\` idempotent. Nu modifica proiectul Companion fără autorizare separată.

### 6. BTDIGG — INCIDENT SEPARAT, ÎNCĂ DESCHIS
BTDigg pe iPhone a raportat **\`RATE_LIMIT\` / 429**, iar în trecut prima căutare a raportat \`BTDIGG_SOURCE_TIMEOUT\` HTTP 504 (~12 secunde) și alta după **aproximativ un minut** a avut rezultate. Nu presupune automat că termenul de căutare a fost identic. E2E anterior pe 249d și vechea versiune a demonstrat **10 rezultate originale** pentru \`ubuntu\` fiecare, run https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39134428856, dar NU fiabilitate 24/7. Un alt run #39119359606 a demonstrat timeout real 504. Root cause DNS/TCP/TLS/TTFB/body rămâne necunoscut.

Cod actual \`rock64/btdigg_gateway.py\`: \`TIMEOUT_SECONDS=12\`, \`MIN_SEARCH_INTERVAL=5\`, \`CACHE_SECONDS=20*60\` (**cache success-only**), \`CACHE_MAX_ENTRIES=4\`, \`CACHE_MAX_BYTES=6_000_000\`, singleflight, no retry la 429/timeout, loopback only. Worker timeout separat \`AbortSignal.timeout(16000)\`; PWA \`BTDIGG_MIN_GAP_MS=5500\`. 429 poate proveni din cooldownul local 8796 sau chiar din upstream, NU se distinge doar din toast.

**Următoarea investigație separată:** \`READ_ONLY_ROCK64_DNS_TCP_TLS_TTFB_BODY_TIMING\`, DOAR când este aprobată. Inspectează instalat-vs-GitHub, systemd/restarts/listener/CPU/RAM cu ieșiri sanitizate, apoi o singură cerere controlată către gazda originală, timpi DNS/TCP/TLS/TTFB/body/total și tipul excepției, fără secrete/HTML/URL-uri magnet. Nu crește fără dovezi timeout, nu repeta 429, nu modifica tunelul sau gateway-ul și nu înlocui BTDigg cu alt indexer. Pentru testele canary 540b **nu interoga BTDigg automat**.

### 7. REGULI ABSOLUTE / SECURITATE
- **€0 costuri noi**; fără paid APIs, abonamente, proiecte externe și fără schimbări de Free Cloudflare tier.
- Niciun secret, bearer, token, cheie sau pairing în chat, fișier public, log, URL sau PWA.
- Niciun proxy deschis; rutare HTTP doar pentru hosturi/provider IDs allowlist. Nu urma redirecturi publicitare/externe și nu încerca bypass anti-bot/CAPTCHA/429.
- Nu șterge indexerele, bazele de date, originale, nu rescrie catalogul 46, nu redenumi atribuirea providerilor, nu genera magneturi false, nu adăuga automat rezultate.
- Nu trimite magnet către Flud/Shield automat; doar comandă explicită a proprietarului și validare de acknowledgement.
- Fără schimbări DNS, router, tunnel, \`systemd\`, \`Rock64\`, vecini \`NexaPanel\`/\`Plex\`, VPN, firewall, microSD, cron sau configurare secret neaprobată.
- Nu modifica Android upstream pentru fixul PWA și nu lansa versiuni temporare one-shot inutile.
- **Cod prin branch → PR → CI → merge**, nu push direct \`main\`; actualizează \`docs/PROJECT_STATE.md\` + \`config/project-invariants.json\` + checker + handoff când starea live se schimbă. No deployment în PR doc-only.
- Nu inventa succes: separă teste sintetice de logurile autentice; nici \`HTTP 200\` singur nu demonstrează magnet valid.

### 8. PRIORITĂȚILE PENTRU NOUL CHAT — ÎN ORDINE
**P0 — confirmă starea.** Citește \`main\` și ultimele Actions/runs înainte de orice schimbare. **Așteptat verificat la acest checkpoint**: 249d 95% / 540b 5%, canary #39323736403 PASS, E2E #39324007635 PASS. Recitește \`AGENTS.md\` și promptul curent; dacă un workflow ulterior a schimbat splitul, ia realitatea nouă ca adevăr. Confirmă dacă utilizatorul a testat iPhone; la 5% o căutare normală poate vedea vechiul 249d, deci nu interpreta un singur eșec ca regresie 540b.

**P1 — pregătește promovarea CONTROLATĂ 540b la 100% (NU executa fără aprobare separată).** Verifică dacă există deja workflow compatibil cu **perechea NOUĂ**; vechile \`release-magnetra-candidate-100.yml\` și \`deploy-magnetra-canary-5.yml\` au ID-uri hardcodate pentru perechea istorică a9df/249d și **NU trebuie refolosite**. Dacă nu există, implementează workflow manual cu \`CANCEL\` default și două acțiuni explicite: \`CONFIRM_PROMOTE_540B_100\` numai din exact \`249d95/540b5\`, și \`CONFIRM_RESTORE_249D_100\` numai din perechea cunoscută în canary/producție. La promovare: \`249d@0% / 540b@100%\`; ambele păstrate în active deployment. Verifică **ID-uri imuabile, 3 bindinguri, SHA assets, 46 IDs, E2E deja trecut, race/deployment ID, postflight real API**, fără alte versiuni, fără reîncărcare cod, fără publicare generică \`deploy-pwa\`. Scrie teste offline de lipsă aprobare, variații % necunoscute, rollback, CLI failure/concurență. Branch+PR+CI+merge, apoi cere explicit aprobarea pentru **mutarea traficului la 100%**; nu pretinde că aprobarea de 5% autorizează 100%.
**P2 — după owner-approved 100%:** citește logul real al promovării, confirmă din API exact 540b 100% / 249d 0%, verifică PWA \`/app.js\` public (SHA, fără cache false), catalog 46/46, căutare 2026 OxTorrent/Torrent9 și \`/api/resolve\` original pentru câte un item, apoi cere o singură verificare reală de iPhone „Resolve” pentru ambele surse. Niciun magnet nu e trimis automat către Flud. Dacă există regresie severă verificată, folosește doar workflow de rollback pentru perechea 249d/540b cu aprobare.
**P3 — BTDigg 429**, separat după stabilizarea release-ului; loguri sanitizate, local-vs-upstream, read-only timing, cauză probată înainte de fix, fără spam și fără modificări altor servicii Rock64.
**P4 — restul:** auditează selectiv indexerele, UX mobil, deep-link/copy și Flud Companion doar prin teste sigure și aprobări, fără a confunda 46 adaptere cu 46 surse sănătoase.

### 9. WORKFLOW-URI DEJA EXISTENTE ȘI CÂND SE FOLOSESC
- Canary 5% activare sau restaurare **249d/540b**: https://github.com/Zuzuitu/AlexLab-Magnetra/actions/workflows/magnetra-resolve-fix-canary-5.yml — \`CONFIRM_FIX_540B_CANARY_5\` / \`CONFIRM_RESTORE_249D_100\` (restaurarea doar din canary, NU pentru 100%-new fără cod nou potrivit).
- E2E read-only canary pe versiuni identificate: https://github.com/Zuzuitu/AlexLab-Magnetra/actions/workflows/verify-magnetra-fix-canary-5-e2e.yml — \`RUN_READONLY_FIX_540B_CANARY\`.
- Audit versiune 540b read-only: https://github.com/Zuzuitu/AlexLab-Magnetra/actions/workflows/inspect-magnetra-resolve-fix-stage.yml ; este proiectat pentru starea PRE-DEPLOY 249d100, deci **nu rula acum** și nu interpreta FAIL la 95/5 ca problemă nouă.
- Slot 0% și zero E2E sunt istorice, deja executate. **NU reporni workflow-uri de release vechi pentru a9df/249d** în starea 249d/540b.
- Fără \`[deploy-pwa]\` în mesajele commiturilor acestui checkpoint; \`Deploy Magnetra PWA\` trebuie să fie \`skipped\`.

### 10. INSTRUCȚIUNEA IMEDIATĂ PENTRU ASISTENTUL DIN CHATUL NOU
**Nu începe de la zero.** Deschide repository-ul și verifică starea reală 95/5. Apoi pregătește independent, prin branch/PR/teste, un workflow protejat pentru *exact* noua pereche de versiuni **249d↔540b** cu opțiuni 100% promote și rollback, fără să execute operațiunea. Prezintă dovezile, limitele, linkul GitHub și cere aprobarea proprietarului numai pentru schimbarea efectivă de trafic. Nu confunda BTDigg \`RATE_LIMIT\` cu bugul \`Resolve\` deja remediat în 540b; nu modifica BTDigg ca efect secundar. Continuă profesionist până la PR merge, nu te opri la un plan teoretic.

**Chei căutare istoric / conservare:** \`PR #77\`, \`BTDIGG_SOURCE_TIMEOUT\`, \`12 secunde\`, \`aproximativ un minut\`, \`MAGNETRA_GATEWAY_TOKEN\`, \`46\`, \`READ_ONLY_ROCK64_DNS_TCP_TLS_TTFB_BODY_TIMING\`. Acestea descriu dovezi și restricții istorice, nu implică faptul că BTDigg a fost reparat definitiv.

**Ultima observație fermă:** **95% producție veche 249d + 5% cod corectat 540b, E2E PASS**. **100% 540b = NEAUTORIZAT / NEEXECUTAT**. iPhone QA post-promovare încă în așteptare.
