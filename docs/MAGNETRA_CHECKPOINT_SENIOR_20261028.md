# Magnetra — CHECKPOINT AUTORITATIV + PROMPT COMPLET PENTRU ALT CHAT
Data: 28 octombrie 2026, Europe/Rome | Versiune handoff: 2026-10-28-H1
Proiect: AlexLab Magnetra | Repo public: https://github.com/Zuzuitu/AlexLab-Magnetra
PWA: https://index.alexlab.media
Regula de bază: surse reale, rezultate reale, fără magneturi/informații inventate; niciun deploy nedovedit.

====================================================================
A. PROMPT DE START — LIPIT IN NOUL CHAT
====================================================================
Ești Principal / Staff Software Engineer responsabil de AlexLab Magnetra. Continuă exact din acest checkpoint tehnic, fără a reintroduce indexere ascunse, fără a strica Flud, fără a presupune că modificările din GitHub au fost publicate și fără a inventa rezultate, autorizații API ori succes în producție. Ai permisiunea să citești/verifici repo și CI; modificările trebuie făcute pe branch separat, prin PR, teste offline + audit de securitate. Nu executa update Rock64, Cloudflare, DNS, API keys, tokenuri, WAF, router, tunnel sau acțiuni distructive fără aprobare explicită și preflight cu rollback. Răspunde în română, cu pași concreți și teste măsurabile. Citește mai întâi PR #224 (merged), PR #223 (Draft), docs/PROJECT_STATE.md, docs/NEXT_CHAT_HANDOFF.md, worker/src/release-fallback.mjs, worker/src/search-query-policy.mjs, web/app.js și rock64/btdigg_gateway.py. Compară întotdeauna starea curentă cu acest checkpoint, deoarece HEAD/CI/Cloudflare pot evolua.

Obiectiv prioritar: finalizarea profesională a căutării multi-indexer cu exact-match înaintea alternativelor ordonate, plus evaluarea realistă a BTDigg pe Rock64 în condiții de acces permis. Nu numi sistemul «stable» până când testele proprietarului iPhone + Cloudflare și disponibilitatea efectivă a surselor au fost validate.

====================================================================
B. STARE GITHUB CONFIRMATĂ LA 28 OCT 2026
====================================================================
Repo: Zuzuitu/AlexLab-Magnetra, public.
Main SHA verificat: 848cce8e0255665e6ab885a63f65927a31b19e74.
PR #217: merged — normalizare query pentru release-uri lungi.
PR #218: merged — restaurare potrivire strictă a metadatelor cerute.
PR #219: merged — documentarea accesului BTDigg autorizat / API «on demand».
PR #220: CLOSED, NOT MERGED, SUPERSEDED — draft experimental vechi, cu modificări duplicate; NU continua de aici.
PR #221: merged, squash f1464feff5b9d28e4e892912381c16a24c537e9c — exact PSA întâi, apoi alternative de calitate în 11 indexere.
PR #222: merged, squash bf0a260aab141c70c2017fcc02559404b4d8f59b — restrânge fallback-ul la cele 11 vizibile; celelalte 35 nu primesc alternative.
PR #224: merged, squash 848cce8e0255665e6ab885a63f65927a31b19e74 — ranking global codec/rezoluție/profunzime/grup; teste API/PWA. https://github.com/Zuzuitu/AlexLab-Magnetra/pull/224
PR #223: OPEN, DRAFT, NOT MERGED — candidatul unificat BTDigg curl_cffi izolat; HEAD 82cf7ad94007e7504458b4f59d653fd52c56b7a3; 5 suite PR CI confirmate PASS. https://github.com/Zuzuitu/AlexLab-Magnetra/pull/223
PR #223 poate necesita rebase din main după #224 înainte de orice integrare. Nu integra #220 și nu confunda #223 cu un serviciu live.
Ultimele CI main verificate pentru SHA 848cce8...: PWA/providers PASS; invariants PASS; Android debug PASS; Android staging PASS; production smoke PASS; workflow «Deploy Magnetra PWA» SKIPPED. Testele CI NU implică deploy.
Ultimul release Cloudflare verificat anterior prin workflow manual #40483725991: b39a0393-bbf8-4ba3-9d32-7c1390aa867f @100%; rollback anterior fdffdc78-0bd3-4721-a5b1-11f515c52bd1 @0%. Acestea sunt valori istorice, NU pretinde că sunt încă active fără o citire live nouă. Modificările #217–#224 NU sunt dovedite publicate; ultimul deploy automat pentru noul HEAD a fost skipped.
PWA service worker în codul main: alexlab-magnetra-v14.
Repo docs vechi pot conține date istoric depășite / antet de octombrie 27; acest fișier nou are prioritate pentru starea din 28 octombrie, dar orice schimbare viitoare trebuie reverificată.

====================================================================
C. CERINȚE FUNCȚIONALE NENEGOCIABILE
====================================================================
1. Interfață PWA RO/IT, preferințe reale utilizator, iPhone Add to Home, 50 rezultate/pagină.
2. 46 adaptoare originale în backend, 11 indexere CURATED vizibile în PWA, 35 ascunse; SubsPlease rămâne ascuns. Cele 11 confirmate în worker/src/search-query-policy.mjs: 0magnet, audiobookbay, btdigg, internetarchive, knaben, nonameclub, oxtorrent, thepiratebay, therarbag, torrent9, torrentscsv. Nu reintroduce cele 35 în PWA.
3. «Selectează toate» selectează 11; când toate sunt selectate, aceeași comandă le deselectează. Păstrează pauzarea indexerelor cu erori, dar nu prezenta «zero rezultate» ca disponibilitate.
4. Logo -> Home. Păstrează toate funcțiile Flud Companion, pairing, magnet, copy/share, bookmarks, sursa reală, NoNameClub origin magnet, PWA cache safearea.
5. Nu inventa BTIH, magnet, seeders, date, calitate. Nu confunda un link de subtitrare cu disponibilitatea unui torrent. Doar rânduri reale de la indexer.
6. Nu modifica proiectele adiacente Rock64/NexaPanel/YouTube/Plex sau configurațiile lor.

====================================================================
D. DECIZIA FINALĂ DE CĂUTARE: EXACT → ALTERNATIVE ORDONATE
====================================================================
Exemplu folosit de proprietar:
The.Dog.Stars.2026.1080p.10bit.WEBRip.6CH.x265.HEVC-PSA

Prioritatea este TITLU + AN (obligatorii mereu), apoi potrivirea originală integrală. Dacă nu se găsește release-ul complet (inclusiv grup PSA, WEBRip, 6CH etc.) în indexerele care au răspuns, se arată alternativă REALĂ cu un ranking explicit, NU o listă amestecată.

Ordine concretă solicitată și codificată în #224:
T0: exact release, de ex. 1080p x265 10bit PSA.
T1: 1080p x265 10bit, alt grup / altă sursă release.
T2: aceeași rezoluție și codec, dar bit depth diferit, etichetat.
T3: 1080p x264 (sau H.264 compatibil), dacă x265 dorit nu este găsit la 1080p.
T4: 720p x265, preferând dacă există același grup (PSA); apoi alte grupuri/codecuri.
T5+: rezoluții inferioare în ordine descrescătoare, apoi mai mari, necunoscute penalizate.
Tie-break conform codului: rezoluție ÎNAINTE de codec, apoi bit depth, apoi grup.
Prin urmare 1080p x264 înainte de 720p x265 — cerință explicită.
Expune vizibil diferențele reale față de original: resolution, codec, bitDepth, group și metadata reală. Nu numi «x265» un fișier care afișează doar HEVC/H.265 (compatibilitate, nu identitate encoder). Nu considera un codec sau o rezoluție absentă drept potrivire exactă. Nu arăta anul sau titlul greșite.
PWA așteaptă finalizarea tuturor providerilor selectați; dacă există orice rezultat exact, îl preferă global și nu amestecă fallback-uri. Dacă nu, afișează doar candidații de la CEL MAI BUN fallbackRank disponibil în toate sursele care au răspuns. Când unele indexere au eroare, spune «în indexerele care au răspuns», nu «nu există nicăieri».
Fallback-ul operează PE rândurile deja returnate: nu există retry automat către toate indexerele cu 10 căutări de calitate; NU promite că fiecare tier a fost verificat independent.
Pentru cele 10 surse vizibile generice, worker/src/search-query-policy.mjs trimite o singură interogare broad titlu/an și clasează release-urile returnate. Excepție BTDigg: o singură căutare cu numele LITERAL COMPLET, deoarece exact asta a reușit în testul fizic; deci BTDigg poate să NU întoarcă alte variante în aceeași căutare. Nu susține fals că fallback-ul BTDigg acoperă toate combinațiile. Îmbunătățirile de query fără cereri suplimentare necesită analiză și aprobare.
35 indexere ascunse folosesc în continuare comportamentul legacy strict; fallback-ul curat nu se aplică lor.

Fișiere principale: worker/src/query-relevance.mjs, worker/src/release-fallback.mjs, worker/src/search-query-policy.mjs, worker/src/index.mjs, web/app.js, web/i18n.js, web/sw.js. Teste: worker/test/release-fallback.test.mjs, search-query-policy.test.mjs, query-relevance.test.mjs, pwa-interactions.test.mjs. Codul #224 a fost verificat în CI; nu avem încă dovadă de test real iPhone pentru acest release.

====================================================================
E. BTDIGG — EVIDENȚE ȘI LIMITĂRI
====================================================================
Site original BTDigg în Safari a afișat release-ul exact PSA (~1,73 GB). Utilizatorul a confirmat explicit că NU folosea VPN; NU relua ipoteza VPN ca fapt.
Gateway-ul vechi Rock64: serviciu systemd magnetra-btdigg.service activ; adresele private, secretul gateway-ului și informațiile de tunel NU se pun în fișierele de handoff.
Jurnal owner real: un btdigg_upstream_timing «http_429» în 1132 ms, apoi «tcp_timeout» în 3007 ms, folosing transportul standard Python IPv4 TLS/HTTP/1.1. Nu știm de ce BTDigg a limitat acel client; nu inventa cauza.
Un plugin qBittorrent de la galaris este bazat pe urllib + parsare HTML și nu reprezintă API oficial; repo inactiv din 2024, 429 raportate. Discuție BurningMop: un utilizator raportează curl_cffi ca soluție punctuală; nu garantează disponibilitate.
Owner a testat personal, pe Rock64 ARM64, venv temporar «curl_cffi==0.17.0», impersonate=chrome, o singură cerere:
HTTP_STATUS: 200
EXACT_RELEASE_FOUND: True
MAGNET_MARKERS: 2
A doua verificare reală pe Rock64 a folosit scriptul temporar din branch experimental, cu HTMLParser și verificare a rândului integral:
ONE_SHOT_EXACT_RESULT_START
HTTP_STATUS: 200
VALID_SOURCE_ROWS: 1
EXACT_RELEASE_WITH_MAGNET: True
ONE_SHOT_EXACT_RESULT_END
Aceasta dovedește un rezultat real cu titlu exact + dimensiune + magnet valid ÎN ACELAȘI RÂND al HTML, pe o singură solicitare; «2 magnet markers» nu sunt două torente. Nu demonstrează stabilitate, autorizare la scraping sau o instalare funcțională în aplicația publică.
PR #223 are candidat izolat curl_cffi fără retry, proxy-rotation, CAPTCHA, autodeploy; timeouts, 3 MB limită, stream, auth fixă, cache/positive-only, localhost, opt-in dezactivat implicit și pornește doar cu confirmarea condițiilor de acces. Include hardening selector «div.one_result», teste workerd și diagnostice offline. Această integrare NU ESTE pe Rock64 în producție.
BTDigg API: SearXNG indică API oficial «on demand» prin pagina contacts; NU există endpoint/cheie/quota autorizată confirmate. A fost pregătit un draft email, dar NU presupune că a fost trimis ori că a venit răspuns. Sursa poate refuza automatizarea. Nu ocoli accesul cu rotire IP, cookie/challenge sau rețele care maschează blocajele; respectă 429.
PR #223 nu trebuie merged până la verificarea termenilor, a apropierii de main și aprobarea proprietarului pentru activarea unei implementări cu rollback. Nu schimba unit-ul vechi sau alte servicii fără aprobare.

====================================================================
F. TPB ȘI CELELALTE INDEXERE
====================================================================
ThePirateBay folosește API apibay.org; s-au observat 429. S-a introdus serializarea solicitărilor pe izolat Cloudflare, cooldown limitat și recuperare din cache pozitiv doar cu vârstă indicată. Nu promite protecție globală între isolate. Nu spama API cu încercări diferite sau retry-uri automate. Indexerele pot returna 403, timeout, zero, parțial — tratare distinctă în interfață.
Unele surse folosesc HTML, altele JSON/POST; nu introduce curl_cffi peste tot orbește: doar sursele care au motiv, compatibilitate și drept de acces. Preferă adaptoarele provider-specific și politici individuale.
Securitatea repository-ului public: nu expune IP-uri private, credențiale, tokenuri, cookies, URL-uri sensibile, căi personale, conținut magnet, configurații Flud. Istoric Git păstrat conform auditului; nu rescrie release-uri/commituri fără aprobarea owner.
Fără introducerea de servicii sau costuri noi. Nu șterge proiectul decât la cerere expresă, după prezentarea efectelor ireversibile.

====================================================================
G. CE ESTE REALIZAT VS CE RĂMÂNE
====================================================================
REALIZAT:
- Codul pentru ranking exact→alternative conform ultimelor cerințe este merged în main (#224); 11/35 conservat (#222).
- CI pe main la 848cce8: PWA/provider, invariants, smoke, Android debug/staging PASS; deploy workflow SKIPPED.
- BTDigg curl_cffi una sau două verificări punctuale cu HTTP 200, inclusiv title + size + magnet same row din sursa originală.
- PR #223 are izolare și teste offline + toate cele 5 suite PR CI PASS, dar rămâne Draft/open.
NEFINALIZAT:
- Confirmarea permisului/termenilor de integrare automată BTDigg ori accesului API oficial.
- Rebase/review #223 cu main actual #224, audit de regresii, fără merge/activate automat.
- Modul BTDigg în live Rock64: provision pinned dependency în venv dedicat, systemd opt-in fail closed, preflight, backup fișier/config, restore, health, limite CPU/memorie, restart doar cu owner approval; traseul Flud/Cloudflare existent intact. Dacă nu se autorizează integrarea, păstrează candidate-ul experimental.
- Deployment Cloudflare PWA al codului merged #224, cu verificare reală split/version/bindings, preflight immutable, canary 0→5→100, rollback, documentarea workflow-ului; explicit user-authorized. Nu porni generic «Deploy Magnetra PWA» în orb.
- Test fizic end-to-end iPhone pe titlul PSA: 11 indexere, rezultate exacte, fallback global 1080p x265 10bit alte grupuri / 1080p x264 / 720p x265 PSA și fallback diferențe afișate, 50 rezultate/pag., Flud, Home, Add to Home; test TPB no-429 promise, error UI.
- Acoperire cu teste pentru surse 429/403/timeout, rezultatele 0 vs indisponibile, cache pozitiv, query cu greșeală «doa» (NU autocorecta fără acord), JSON + HTML, Flud original.
- Decide dacă problema de disponibilitate BTDigg permite proiectul să fie util. Dacă nu, raportează limitările cinstit; nu declara stable doar pentru smoke PASS.

====================================================================
H. PLAN DE ACȚIUNE PENTRU NOUL CHAT (ORDINE)
====================================================================
P0. READ-ONLY AUDIT. Citește GitHub main SHA, PR #223 status + diff, CI, code actual și Cloudflare live read-only dacă e disponibil. Confirmă că repo este public; nu posta secrets. Compară contractul real cu acest handoff.
P1. VALIDARE FALLBACK. Rulează unit/workerd/PWA + acceptance matrix. Verifică exact > x265 alte grupuri > x264 la 1080p > x265 720p grup PSA, etc., în funcție de semantica actuală rank; semnalează diferențe de intenție în loc de a le masca. Fără cereri suplimentare către indexere. Verifică criterii neclasificate și titlu/an eronat.
P2. BTDIGG READINESS. Dacă termenii permit, planifică migrarea izolată #223 pe branch nou actualizat de main: păstrează gateway old ca fallback, local private auth, fără secrete în GitHub/log, rollback și gate de acces explicit. Dacă accesul nu e confirmat, nu activa automatizarea; folosește doar testele deja autorizate.
P3. RELEASE READINESS. Verifică pipeline protejat, versiunea Cloudflare actuală și bindings efective; pregătește workflow reversibil și aprobare explicită owner pentru scrieri. Code merge≠production.
P4. ACCEPTANCE OWNER. iPhone Safari/PWA/Add-to-Home + Flud, caz pozitiv exact și caz fallback, clasificație source errors. Nu promite BTDigg fiabil dintr-un singur răspuns 200.
P5. DOCUMENTAȚIE FINALĂ. Actualizează docs/PROJECT_STATE.md, docs/NEXT_CHAT_HANDOFF.md / README cu rezultatele real verificate, separat de planuri, și salvează checkpoint nou.
Stop conditions: lipsă tokenuri/permisiuni, upstream 429, conflict de SHA/CI, imposibilitate de rollback, pagini fără magnet original, proprietarul nu aprobă deployment; oprește-te sigur.

====================================================================
I. LINKURI DE REFERINȚĂ
====================================================================
Repo: https://github.com/Zuzuitu/AlexLab-Magnetra
PR ranking: https://github.com/Zuzuitu/AlexLab-Magnetra/pull/224
PR BTDigg experimental: https://github.com/Zuzuitu/AlexLab-Magnetra/pull/223
PR fallback: https://github.com/Zuzuitu/AlexLab-Magnetra/pull/221
PR hidden scope: https://github.com/Zuzuitu/AlexLab-Magnetra/pull/222
PR BTDigg documentare: https://github.com/Zuzuitu/AlexLab-Magnetra/pull/219
Run production precedent: https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/40483725991
Document autorizare: docs/BTDIGG_AUTHORIZED_API_PATH_20261028.md
PWA: https://index.alexlab.media
Sfârșit checkpoint. Nicio modificare de producție nu a fost efectuată prin acest handoff.
