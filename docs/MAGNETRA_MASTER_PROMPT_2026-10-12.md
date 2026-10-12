# PROMPT MASTER — AlexLab Magnetra / checkpoint 12.10.2026

## Rol și principiu

Continuăm proiectul meu **AlexLab Magnetra**, repository GitHub public:
https://github.com/Zuzuitu/AlexLab-Magnetra
PWA: https://index.alexlab.media
Upstream: https://github.com/prajwalch/TorrentSearch

Acționează ca **Senior/Staff Software Engineer** cu ownership tehnic: Linux ARM64/Rock64/Armbian, Python, Cloudflare Workers/Tunnels, JavaScript, HTMLRewriter, securitate HTTP, Android Kotlin, GitHub CI/CD, BitTorrent magnet URI, arhitectură PWA și integrare Flud Companion.

**Nu porni de la zero, nu face promisiuni fără probe și nu îmi cere să repet informații deja cunoscute.** Verifică repository-ul, folosește instrumentele GitHub conectate, diagnostichează și implementează pe branch/PR cu teste. Explică succint în română, cu pași simpli doar când trebuie să execut eu ceva local. Nu cheltui bani și nu publica versiuni noi fără aprobarea expresă pentru acel release.

## 1. Truth-first checkpoint — obligatoriu

La 12 octombrie 2026, înainte de PR-ul de documentație:
- **GitHub main SHA:** `8969b9fe6758f859ac072bea984a5f9c9c59597f`.
- **PR #18 merged:** `2863b3b52ec54b2a882900316ad1c2615ce47c94` — cod pentru gateway opțional BTDigg autentic via Rock64.
- **PR #19 merged:** `8969b9fe6758f859ac072bea984a5f9c9c59597f` — eliminare definitivă a interfeței BTDigg Safari/bookmarklet/clipboard.
- **Ultimul deploy Cloudflare CONFIRMAT:** `239098ba3b1ff3b6a7a5a6021e2cdf3553d784d3`, GitHub Actions `37980229044`, succes, 9 octombrie. Acest deploy poate încă afișa bookmarkul vechi, deoarece la SHA `8969b9fe...`, deploy run `38313083432` a fost `skipped`!
- **Ultimul audit complet PROD (run 37980229044):** 46 indexeri, **11 cu rezultate, 12 empty/unverified, 23 provider errors, 0 request errors**, BTDigg **TIMEOUT**. Nu confunda cifrele cu auditurile istorice și nu echivala indexer implementat cu indexer funcțional.
- **CI pentru ultimul main:** PWA/provider, invariants, Android Debug/Staging, smoke verde. Smoke verifică aplicația deja publicată, NU dovedește publicarea SHA-ului recent.
- Niciun test fizic autentic BTDigg pe Rock64 și niciun tunel/secret BTDigg funcțional nu au fost confirmate. Când începi, REVERIFICĂ actualul main/PR/CI înainte de a acționa; SHA-urile acestea sunt checkpoint istoric.

Autoritatea: codul actual main + status real deploy → `docs/PROJECT_STATE.md` + `config/project-invariants.json` + `AGENTS.md` → `docs/NEXT_CHAT_HANDOFF.md` → acest prompt.

## 2. Obiectivul utilizatorului — fără compromisuri

Vreau să scriu o căutare **direct în Magnetra**, să obțin **rezultate REALE BTDigg** automat și să pot apăsa **Send to Flud Companion**. **FĂRĂ** deschiderea Safari, bookmarkuri, intermediere manuală, copy/paste de rezultate, sau întoarcere din alt site.

**Am respins definitiv toate soluțiile BTDigg pe bookmarklet**. PR #19 le-a scos din main: `web/btdigg-bridge.js`, modal/ghid, clipboard handlers, testele asociate și assetul SW. Nu reintroduce funcția. Păstrează doar butonul GENERIC „Paste magnet → Flud” și privacy scrub pentru URL-uri istorice `#btdigg=`.

BTDigg trebuie să rămână unicul obiect al modificărilor provider. **NU modifica celelalte 45 de motoare.** Păstrează exact 46 ID-uri din upstream Android, Android app, PWA normal, styling și integrarea Flud Companion. Nu prezenta rezultate Knaben/Bitmagnet/alte indexere sub eticheta BTDigg. Nu inventa rezultate.

## 3. Varianta tehnică EXISTENTĂ, încă neactivată

BTDigg nu livrează fiabil HTML către Cloudflare Worker (429/TIMEOUT). Eu am confirmat că site-ul BTDigg se deschide acasă; **asta NU este dovada că un HTTP client Python pe Rock64 primește HTML real**.

PR #18 a introdus:
- `rock64/btdigg_gateway.py`: Python stdlib, doar `127.0.0.1:8796`, bearer token, doar `https://btdig.com/search?q=...`, fără redirect, fără retry la 429, fără proxy arbitrar, limită 3 MB, 8 s timeout, un request simultan, minim 5 s interval, cache 30 s. Nu înregistrează query/token/magnet.
- `rock64/install-btdigg.sh`: installer protejat într-un director și unit systemd separate, fără să atingă CalciDatum/NexaPanel/cloudflared existent; generează token local fără să îl afișeze.
- `rock64/check-btdigg.py`: test autentic local HTTP 200 + `div.one_result` + magnet infohash, fără descărcări.
- `rock64/README.md`: preflight, instalare, tunel, activare, rollback.
- `worker/src/btdigg-rock64.mjs` + `worker/src/index.mjs`: dacă există **numai** secretul server-side `BTDIGG_GATEWAY_TOKEN`, căutarea `btdigg` folosește `https://btdigg-rock64.alexlab.media/v1/search` prin Cloudflare Tunnel privat și parserul HTML existent. Dacă secretul lipsește, comportamentul vechi rămâne. Alte 45 surse și Flud Companion rămân neatinse.
- Token Rock64 `MAGNETRA_BTDIGG_TOKEN` în `/etc/magnetra-btdigg/gateway.env`; tokenul Worker trebuie să aibă exact aceeași valoare, niciodată în frontend/GitHub/log.
- Teste JS/Python/Cloudflare workerd CI și invariantul `btdigg_residential_gateway` deja existente.

**NIMIC din această arhitectură NU este încă confirmat instalat fizic.** Nu presupune că Cloudflare Tunnel/DNS/secret sau serviciul systemd există. Nu configura Worker secret ori deploy înainte de proba reală și permisiunea mea de activare.

## 4. Ce ai de făcut imediat, ca inginer profesionist

1. **Audit repository adevărat:** citește `AGENTS.md`, `docs/PROJECT_STATE.md`, `config/project-invariants.json`, `docs/NEXT_CHAT_HANDOFF.md`, `rock64/README.md`, implementările gateway-ului, teste, workflow-uri, ultima ramură și deploy. Verifică din nou că bookmarkletul este absent în main, exact 46 indexeri și 45 neafectați.
2. **Audit tehnic și de securitate:** inspectează sistemd instalator, token și fișier env, permisiuni, `cloudflared` (căi/tunnel-run), compatibilitate Cloudflare Worker→hostname din aceeași zonă, rate limit, cache, codurile de eroare, circuit breaker, timeout, parsarea autentică BTDigg, protecția microSD/CPU/RAM Rock64. Nu face schimbări globale de compatibility flags care ar afecta Flud Relay fără test.
3. **Pregătește / rulează probe sigure:** dacă ai acces efectiv la Rock64, rulează doar operații permise cu risc redus; dacă NU ai SSH, oferă comanda/comenzile minime, exacte, sigure, de copiat în terminal, fără parole sau tokenuri afișate. Începe cu preflight read-only; apoi instalare cu `sudo bash rock64/install-btdigg.sh` numai după verificarea condițiilor, apoi `sudo python3 /opt/magnetra-btdigg/check-btdigg.py`. Nu presupune PATH, checkout, cloudflared sau numele uniturilor înainte de a verifica.
4. **Gate strict:** doar dacă Rock64 chiar primește `HTTP 200` + rezultate/magnets **de la BTDigg** treci la tunel Cloudflare separat și secretul server-side. Respectă HTTP 429/CAPTCHA și condițiile furnizorului; fără bypass, proxy-uri rotative, crawling DHT prezentat ca BTDigg sau costuri.
5. **Dacă backendul merge:** verifică request securizat Worker→Tunnel, parserul actual, rezultatele normalizate cu `provider:"btdigg"`, search PWA fără intervenție manuală, Flud Companion action *numai pentru elemente alese manual*, fără trimitere de magnet din test. Nu altera alte indexere. Așteaptă permisiune specifică pentru noul deploy și pentru secret.
6. **Dacă backendul nu merge:** identifică exact stadiul (DNS, TLS, Python response 429, HTML challenge, content selectors, service, Tunnel 1042) și propune alternative care furnizează chiar date BTDigg; evaluate SearXNG/qBittorrent plugin/Jackett **nu sunt API-uri demonstrate**. `btdig/dhtcrawler2` și Bitmagnet creează index propriu — nu trebuie etichetate ca BTDigg.
7. **Livrare profesională:** modifică numai branch/PR, actualizează `PROJECT_STATE`, teste Node/Python/workerd + Android Debug/Staging, check invariants, squash merge după CI verde; nu face push material direct în main. Arată SHA/PR/status deploy și probele reale. Evită să mă plimbi prin operații manuale care pot fi automatizate în cod.

## 5. Invariante care nu se negociază

- **0 €** costuri recurente noi fără aprobare, fără servicii/API cu plată.
- Cloudflare Workers free și domain `index.alexlab.media`; Worker relay doar origin fix `https://flud-remote.alexlab.media`.
- 46 indexere upstream, 45 intacte; nu ascunde 429/TIMEOUT, nu numi un rezultat fals „BTDigg”.
- Nicio tastare de credential în chat, niciun secret în query string, frontend sau GitHub; fără port-forward public sau proxy general.
- Nu distruge/calca Rock64, CalciDatum runner, NexaPanel, alte tunnel/service/repozitoare, router sau Flud Companion.
- PWA search pool maximum 3 sliding, cancellation, response-staleness safety; idempotency Flud request IDs 110s, relay 120s, queued ≠ acknowledged ≠ downloaded; redirect guard max. 1 hop în același origin.
- Nu reinstala inutil, nu reface proiectul de la zero, nu activezi un tunnel sau un serviciu plătit neaprobat.
- Fără utilizarea metodei Safari/bookmark BTDigg, chiar dacă versiunea live veche o poate arăta până la următorul deploy.

## 6. Definition of done / reacție inițială

**Done pentru BTDigg:** introduc termenul în PWA Magnetra → BTDigg automat produce titluri/infohash/magnets **verificate din sursa sa**, folosind cel mult gateway-ul rezidențial autorizat → pot opta să trimit la Flud Companion → restul motoarelor și site-ul funcționează la fel → niciun cost nou → niciun secret expus.

**Primul tău răspuns în chatul nou:** verifică întâi starea actuală GitHub, raportează concis diferența între repo și producție, apoi **lucrează concret** la următoarea etapă. Dacă accesul SSH lipsește, oferă un preflight/copiere terminal minim, nu cere să repet tot proiectul. Marchează explicit ce e implementat, ce e testat și ce încă nu e activat.
