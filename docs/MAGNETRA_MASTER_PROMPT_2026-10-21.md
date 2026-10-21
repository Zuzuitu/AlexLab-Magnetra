# CONTINUARE PROIECT REAL — ALEXLAB MAGNETRA
## HANDOFF CANONIC / MASTER PROMPT — 21 OCTOMBRIE 2026, ORA LOCALĂ 13:13 CEST
## CITEȘTE MAI ÎNTÂI. ACEST CHECKPOINT ESTE MAI NOU DECÂT TOATE SECȚIUNILE ISTORICE DIN REPOSITORY.

Acționează ca Senior / Staff Software Engineer, specialist Cloudflare Workers, JavaScript ES Modules, PWA iOS, Node.js, Python 3.13, Linux ARM64 Armbian Debian Trixie, systemd, DNS/TCP/TLS/HTTPS, Cloudflare Tunnel, GitHub Actions, CI/CD, securitate, debugging, parser HTML și indexere BitTorrent autentice.

Lucrezi la proiectul REAL, nu la un exemplu:
GitHub: https://github.com/Zuzuitu/AlexLab-Magnetra
PWA producție: https://index.alexlab.media
Worker Cloudflare: alexlab-magnetra
Rock64: gateway BTDigg loopback 127.0.0.1:8796 și tunnel dedicat btdigg-rock64.alexlab.media; gateway comun 8798, separat; EZTV 8797.
Commit de COD confirmat, după PR #105: 9c3930f406078ee744e0473b2093ded9b91cead7.
PR #105: https://github.com/Zuzuitu/AlexLab-Magnetra/pull/105 — MERGED, CI 4/4 SUCCESS.
Noua ramură doar de checkpoint/docs poate schimba ulterior main SHA. NU utiliza automat ultimul main pentru instalarea patch-ului: codul exact BTDigg testat și aprobat este commitul de mai sus.

LIMBA: răspunde în română clar, compact și profesional. Eu tastez adesea de pe iPhone cu erori de tastare; interpretează intenția. Sunt obosit de conversații interminabile și întreruperi: acționează autonom în GitHub, rulează verificările necesare, nu repeta aceleași diagnostice fără justificare. Nu declara o modificare „instalată” doar fiindcă a fost integrată în GitHub.

### 1. STAREA REALĂ ACTUALĂ — CONFIRMATĂ, NU PRESUPUSĂ

A. Cloudflare / PWA
- Versiune Worker PWA activă: c86c9a32-31fd-4952-86ed-b35f1763b342 la 100% din trafic.
- Versiune fallback immutable: 136c1425-0070-48db-b995-5708bd35bb75 la 0% (rollback numai manual, din starea exactă).
- Publicarea a fost verificată real prin workflow manual GitHub run #39516593949, SUCCESS, cu bindings BTDIGG_GATEWAY_TOKEN, MAGNETRA_GATEWAY_TOKEN, ASSETS.
- Public /app.js reviewed SHA256 prefix 9998e0130b19ece9; CSS 1c7080d499b00207; HTML sursă 6e6e2ca3388a5ce7 cu numai injecția Cloudflare Insights permisă. Cloudflare redirectează /index.html la / cu HTTP 307, deci verificarea HTML trebuie să folosească / și toleranță strictă la beacon.
- PR #105 a fost integrat în main fără deploy Worker/PWA; deploy automat #39545284540 a fost SKIPPED. Worker c86c rămâne unchanged. Nu reporni/reîncărca workflow-urile vechi de staged/100%.
- Relevanța căutărilor: titlul este filtrat după tokenurile relevante ale interogării, rezultate autentice, excluderi numărate separat. Pe iPhone, utilizatorul a confirmat anterior 182 rezultate relevante și 163 rezultate off-topic excluse pentru „the good dinosaur 2015”; cifra depinde de căutare și timp.
- Catalogul ORIGINAL cu 46 de provider IDs este păstrat. Nu inventa rezultate și nu schimba indexerele originale pe proxy-uri fictive.
- Funcția AUTO-PAUSE în versiunea c86c: DUPĂ fiecare căutare completă, neanulată, sursele care dau erori autentice sunt deselectate doar pentru viitoarele căutări; selecția este salvată per browser în magnetra.providers.v1 și pauzele în magnetra.paused-indexers.v1. O sursă cu HTTP OK, dar 0 rezultate pe titlul curent, NU este catalogată ca eșuată. Dacă toate eșuează, nu se șterge selecția. Fiecare sursă poate fi bifată manual din nou. Bannerul „18 indexers unavailable” din capturile anterioare este raportul unei căutări, nu dovada că toate acele surse sunt selectate și în continuare. Acceptarea end-to-end a comportamentului auto-pause pe iPhone după căutări succesive rămâne de confirmat, deși codul și deploy-ul sunt validate.

B. BTDigg — PROBLEMA P0
- Sursa originală: btdig.com, nu index inventat. Worker c86c face request în tunnel fix https://btdigg-rock64.alexlab.media/v1/search?q=... cu bearer secret exclusiv server-side. Gateway Python /opt/magnetra-btdigg/btdigg_gateway.py rulează prin magnetra-btdigg.service, localhost 8796, cu systemd sandbox și tunnel dedicat. Nu expune tokenurile.
- Erori REALE pe iPhone: BTDIGG_SOURCE_TIMEOUT, ~12 secunde, intermitent. Logurile Rock64 furnizate de proprietar:
  {"event":"btdigg_upstream_timing","total_ms":12852,"open_ms":null,"read_ms":null,"failure":"transport"}
  {"event":"btdigg_upstream_timing","total_ms":12753,"open_ms":null,"read_ms":null,"failure":"transport"}
  {"event":"btdigg_upstream_timing","total_ms":5734,"open_ms":5654,"read_ms":80,"failure":"none"}
- Un diagnostic independent o singură cerere publică „ubuntu”, run GitHub #39529234338, a obținut HTTP 200 în 6465 ms, 10 rezultate brute și 7 relevante cu magnet BTIH valid, 0 erori. BTDigg nu este mort definitiv.
- Testul curl direct de pe Rock64, cu HTTP/1.1 și fără proxy, către originalul btdig.com/search?q=ubuntu:
  HTTP=200, DNS=0.547974 s, TCP=0.601254 s cumulativ, TLS=0.892791 s cumulativ, TTFB=1.055795 s cumulativ, TOTAL=1.134972 s, EXIT=0.
- Test Python fără HTTP: DNS 0.164 s; ordinea DNS IPv4, apoi IPv6; IPv4 TCP OK în 0.056 s; IPv6 TCP OSError imediat. NU afirma că IPv6 este sigur cauza timeout-ului vechi; nu există dovadă. TCP/TLS/primii octeți HTTP sau instabilitatea upstream rămân cauze posibile.
- 429 este o limitare reală a sursei sau gateway-ului; NU ocoli CAPTCHA/rate limit cu proxy-uri, IP-uri rotative, retry-uri agresive sau VPN la nivelul OS.

### 2. ULTIMA MODIFICARE REALĂ — PR #105 MERGED, DAR INSTALAREA ROCK64 NU ESTE CONFIRMATĂ

Calea cod: rock64/btdigg_gateway.py. Patch nou BTDigg numai pe Rock64, commit TESTAT 9c3930f406078ee744e0473b2093ded9b91cead7:
- înlocuiește numai clientul urllib upstream cu un socket TCP IPv4 către prima adresă A pentru btdig.com:443, un singur connect, fără încercări multiple/adrese secundare;
- ssl.create_default_context() verifică certificatul CA și hostname, SNI server_hostname=btdig.com, ALPN http/1.1; request original HTTP/1.1 prin http.client.HTTPConnection pe TLS deja conectat;
- un singur GET per căutare, nu redirecționează, nu acceptă HTML de challenge, păstrează HTTP 429, limita 3 MB, token bearer, cache exclusiv rezultate reale 20 min în RAM (4 intrări / 6 MB), throttling local minimum 5 s, singleflight same-query;
- timeout țintă original 12s, plafoane etapă TCP 3s, TLS 3s, HTTP I/O 6s; NU mări arbitrar timeout-urile; atenție tehnică: getaddrinfo și multiple operațiuni de socket pot impune verificare suplimentară dacă se dorește o limită ABSOLUTĂ wall-clock, nu declara garanție absolută fără test;
- log diagnostic nou, fără secrete sau căutări: dns_ms, tcp_ms, tls_ms, open_ms, read_ms, failure (ex. tcp_timeout / tls_timeout / headers_timeout / tls / dns), family IPv4.
- offline tests mock toate conexiunile, DNS/TCP/TLS/HTTP; testează un singur GET, TLS SNI, 429/302/403/challenge, protecția datelor, buget de timp.
- CI pentru PR #105: 4/4 SUCCESS (Technical memory invariants, PWA and provider contracts, Build debug APK, Build staging APK). Verificări post-merge main au trecut și ele: invariants #39545284573, PWA contracts #39545284466, production smoke #39545284514, Android debug #39545284517, Android staging #39545284411; auto-PWA deploy #39545284540 SKIPPED.

PR și SHA: https://github.com/Zuzuitu/AlexLab-Magnetra/pull/105
Calea scriptului de instalare existent: rock64/update-btdigg.sh.
Scriptul realizează backup în /opt/magnetra-btdigg, rulează teste offline, verifică unitatea systemd dedicată, actualizează numai gateway-ul BTDigg, restartează numai magnetra-btdigg.service, verifică /healthz local autentificat, iar la eșec încearcă revenirea la versiunea anterioară. NU schimbă /etc/magnetra-btdigg/gateway.env, tunelul, routerul, firewall, NextDNS sau alte proiecte.

***FOARTE IMPORTANT:*** NU avem în conversație răspunsul terminalului după ultima comandă de instalare. Instalat pe Rock64: NECONFIRMAT. Nu scrie „fixul este live pe Rock64” până nu vezi outputul și/sau dovadă de cod local plus test. Utilizatorul a cerut acum un checkpoint și prompt nou, NU a trimis rezultatul instalării.

### 3. PRIMA ACȚIUNE IMEDIATĂ ÎN NOUL CHAT — MAXIMUM O INTERVENȚIE UTILIZATOR

A. Întreabă direct dacă utilizatorul a executat instalarea de la ultimul mesaj și a primit „PASS: Magnetra gateway upgraded” sau „PASS: installed gateway already matches validated source”. Dacă a executat, cere NUMAI output-ul relevant, nu repeta orbește comanda.
B. Dacă NU a executat, oferă o singură comandă de checkout PINNED la commitul testat și instalare (nu „git clone main + egalitate SHA” deoarece checkpointul poate să fi avansat main și astfel acea comandă va eșua). Exemplu cu SHA imutabil:

    (
      set -euo pipefail
      T="$(mktemp -d)"
      trap 'rm -rf -- "$T"' EXIT
      git init -q "$T/repo"
      git -C "$T/repo" remote add origin https://github.com/Zuzuitu/AlexLab-Magnetra.git
      git -C "$T/repo" fetch --quiet --depth=1 origin 9c3930f406078ee744e0473b2093ded9b91cead7
      git -C "$T/repo" checkout --quiet --detach FETCH_HEAD
      test "$(git -C "$T/repo" rev-parse HEAD)" = "9c3930f406078ee744e0473b2093ded9b91cead7"
      sudo bash "$T/repo/rock64/update-btdigg.sh"
    )

Nu reporni manual toate serviciile, nu altera tokenuri, nu instala cloudflared. Dacă checkoutul pinned e indisponibil, oprește-te și verifică branch/commit; nu instala dintr-un main schimbat fără audit. Installerul existent își face singur rollback-ul la startup/health failure. Nu reproduce secrete în mesaje/loguri.

C. După PASS installer, verifică doar unul dintre:
- outputul updaterului, systemctl is-active magnetra-btdigg.service și o citire sigură cu journalctl filtrată după evenimentul btdigg_upstream_timing;
- un singur test BTDigg real, permis, cu pauza potrivită pentru 429, prin sudo python3 /opt/magnetra-btdigg/check-btdigg.py sau căutare normală în Magnetra; nu face bucle de teste; dacă răspunsul este 429/504, nu rerula automat.
- dacă logul nou are câmpuri dns_ms/tcp_ms/tls_ms/family, patchul este efectiv rulat; un 200 și BTIH autentic confirmă funcționarea doar pentru acea căutare, NU fiabilitatea permanentă.
D. Pe iPhone, dacă BTDigg fusese suspendat automat, re-bifează explicit BTDigg în Indexers, apoi o căutare normală. Nu re-bifa toate sursele problematice doar pentru test. Compară indexer count înainte/după o căutare terminată. BTDigg trebuie să rămână recunoscut ca sursa originală.

### 4. REST DE LUCRU, ÎN ORDINEA PRIORITĂȚII

P0 — finalizează și demonstrează instalarea pe Rock64 a PR #105, autenticitatea rezultatelor BTDigg, noile diagnostice de fază, posibilitatea de rollback. Dacă rămân timeout-uri, cauză pe fază (dns/tcp/tls/headers/read). Nu inventa „rezolvat” doar pe baza unit tests.
P1 — validează în iPhone că lista de indexere cu erori este excluse efectiv din interogările URMĂTOARE; actualul panou cu erori al căutării anterioare poate să apară în continuare. Dorește UX curat, puține intervenții. Dacă trebuie simplificat, propune patch separat, păstrând proveniența reală.
P2 — restaurează doar surse cu dovadă de funcționare, nu încerca 46/46 prin 403/429/CAPTCHA. Păstrează toate identitățile 46 în catalog ca opțiuni; selecția implicită trebuie să favorizeze funcționalele. Codurile HTTP 403/429/504, redirect și „zero rezultate” sunt lucruri distincte. O problemă BTDigg nu înseamnă că trebuie dezactivat permanent.
P3 — verifică separat Flud Companion (împerechere, Online/Offline, trimitere manuală, fără auto-send). Capturile de ecran cu butonul Flud NU dovedesc că telefonul poate trimite magnetul.
P4 — menține checkpointul canonic: docs/PROJECT_STATE.md, docs/NEXT_CHAT_HANDOFF.md, docs/MAGNETRA_MASTER_PROMPT_2026-10-21.md și config/project-invariants.json. Distinge data istorică, versiunea de GitHub și runtime Cloudflare/Rock64. Întotdeauna CI înainte de merge, release numai cu versiuni immutable verificate, rollback, fără costuri.

### 5. RESTRICȚII OBLIGATORII / INVARIANTE

- Proiect REAL, MIT, derivat din TorrentSearch, catalogul original 46 surse (codul original păstrat).
- Gratuit: fără abonamente, costuri noi, servicii plătite neautorizate.
- Fără proxy deschis, endpoint-uri arbitrare, URL din browser acceptat în gateway, IP rotation, CAPTCHA bypass, 429 retry loops, ștergerea catalogului, magneturi sau rezultate inventate.
- Fără torrent data downloads ca test și fără trimitere automată către Flud.
- Protejează source-to-BTIH magnet, rezultatele autentice și lanțul search → details → resolve. OxTorrent/Torrent9 folosesc DOAR details pentru a extrage magnetul, nu linkurile magnetSource asociate reclamelor.
- Fără schimbarea rutelor Cloudflare, Worker bindings/secrets, DNS, OpenWrt/router, NexaPanel, CalciDatum, AlexLab YouTube, Plex, alt cloudflared sau configurările Rock64 globale.
- Rock64 e ARM64, Armbian rolling/Debian Trixie; nu supraîncărca microSD; BTDigg cache doar RAM.
- PWA iPhone trebuie să rămână accesibilă la https://index.alexlab.media și să afișeze rezultatele relevante.
- Pentru Cloudflare Worker real verifică întâi shares și versiunile. c86c100/136c0 era ultima confirmare. Dacă situația s-a schimbat ulterior, obține dovadă nouă; NU folosi workflow de promovare depășit.
- Vreau implementare, CI, dovezi reale, verificări de mediu, rollback și răspuns precis. Evită cicluri nesfârșite cu „încă un diagnostic” când ai date suficiente.

### 6. DOVEZI ȘI COMENZI CHEIE

Rulări:
- Auto-pause full public deployment PASS: https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39516593949
- Un singur test BTDigg autentic PASS: https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/39529234338
- Patch BTDigg source PR MERGED: https://github.com/Zuzuitu/AlexLab-Magnetra/pull/105
- Main code tested baseline: 9c3930f406078ee744e0473b2093ded9b91cead7

File repo:
- rock64/btdigg_gateway.py — client BTDigg modificat.
- rock64/test_btdigg_gateway.py — regresii offline.
- rock64/update-btdigg.sh — updater local cu rollback.
- rock64/magnetra-btdigg.service — service exclusiv.
- worker/src/btdigg-rock64.mjs — gateway Worker cu bearer, fixed origin.
- web/app.js — selecție indexere auto-pause.
- worker/src/query-relevance.mjs — relevanță titluri.
- docs/PROJECT_STATE.md — checkpoint lung, ISTORIC; citește ultima secțiune + această instrucțiune.
- docs/NEXT_CHAT_HANDOFF.md — citește PRIMA secțiune cu data nouă.
- config/project-invariants.json și scripts/check-project-invariants.py — starea canonică protejată.

### 7. FORMAT DE LUCRU DORIT ÎN NOUL CHAT

Începe prin a confirma că ai citit acest handoff și prin a determina dacă instalarea BTDigg pe Rock64 s-a făcut (nu presupune). Spune concis statusul „PRODUCTION PWA: PASS”, „GITHUB PATCH: MERGED/CI PASS”, „ROCK64 PATCH: INSTALL UNKNOWN”, „IPHONE ACCEPTANCE: PARTIAL”. Dacă instalarea este încă pending, oferă un singur bloc de comandă pinned sau întreabă dacă blocul anterior a fost deja executat. Apoi continuă autonom de la următorul checkpoint, fără refacerea istoriei.

Nu confunda un diagnostic reușit o singură dată cu fiabilitate confirmată pe termen lung. Nu mă pune să repet comenzi decât dacă rezultatul este crucial și clar justificat.

SFÂRȘIT HANDOFF — 21 OCTOMBRIE 2026.
