<div align="center">

<img src="./web/icon.svg" width="88" height="88" alt="AlexLab Magnetra — simbolul magnetului" />

# AlexLab Magnetra

**Caută. Magnet. Gata.**

Motor de căutare multi-sursă, PWA pentru iPhone și browser, integrat opțional cu Flud Companion.

[**Deschide aplicația**](https://index.alexlab.media) · [**Codul proiectului**](https://github.com/Zuzuitu/AlexLab-Magnetra) · [**Proiectul original (MIT)**](https://github.com/prajwalch/TorrentSearch)

[![PWA & provider contracts](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/workflows/pwa.yml/badge.svg)](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/workflows/pwa.yml)
[![Security invariants](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/workflows/invariants.yml/badge.svg)](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/workflows/invariants.yml)
[![Production smoke](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/workflows/production-smoke.yml/badge.svg)](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/workflows/production-smoke.yml)

</div>

---

## Ce este Magnetra?

**AlexLab Magnetra** este o extindere independentă a proiectului open-source [TorrentSearch](https://github.com/prajwalch/TorrentSearch), cu o interfață web nouă și infrastructură dedicată pentru căutarea în mai multe indexere. Nu este pagina oficială TorrentSearch și nu folosește însemnele, versiunile sau statisticile de descărcare ale proiectului original drept propriile realizări.

Pe iPhone se poate instala din **Safari → Share → Add to Home Screen**. Funcționează și în browser pe alte dispozitive. Codul Android provenit din proiectul original rămâne în repository, cu fluxuri GitHub Actions pentru buildurile Debug și Staging. Interfața PWA nu este aceeași aplicație cu interfața Android nativă.

## Ce am construit și modificat față de proiectul original

| Domeniu | TorrentSearch original | AlexLab Magnetra |
| --- | --- | --- |
| Interfață | Aplicație Android Kotlin / Jetpack Compose | **PWA proprie** cu design AlexLab, temă întunecată și aspect adaptat pentru iPhone |
| Căutare | Indexere integrate în aplicația Android | **Cloudflare Worker + adaptoare web**, cu inventar de **46** provideri; **12** afișați implicit în selectorul curatat |
| Limbi pentru PWA | Nu este această interfață web | Interfață Magnetra în **română și italiană** |
| Rezultate | Funcțiile native ale aplicației Android | Sortare, categorii, favorite locale, copiere/distribuire magnet și legătură către sursa originală |
| Reziliența surselor | Logică originală Android | Audit separat pe provideri, explicații pentru erori, oprire temporară a surselor cu probleme și verificări de URL |
| Magneturi | Acțiunile clientului Android | Corecții validate pentru **0Magnet, TheRarBg și NoNameClub**, inclusiv selectarea paginii autentice de detalii în locul legăturilor auxiliare greșite |
| Transfer la distanță | Integrarea originală nu este Flud Companion | Asociere **opțională** prin QR/token local și trimiterea manual confirmată către **Flud Companion** |
| Infrastructură | Aplicație client | Worker Cloudflare, gateway-uri cu destinații fixe și servicii de ieșire opționale pe dispozitiv propriu, cu autentificare |
| Publicare | Lansările proiectului upstream | Fluxuri GitHub Actions, controale de integritate, versiuni Worker verificabile, canary **0% → 5% → 100%** și rollback în release-urile controlate |

> **Atenție la cifre:** 46 reprezintă inventarul de adaptoare, nu 46 surse garantate disponibile în timp real. Cele 12 vizibile sunt configurația de selecție a interfeței; rezultatele depind de fiecare site și de momentul căutării.

## Experiența de utilizare

1. Deschizi [index.alexlab.media](https://index.alexlab.media) și introduci o căutare.
2. Alegi categoria, sortarea și sursele dorite.
3. Verifici rezultatele și poți obține, copia sau distribui un magnet valid.
4. Dacă ai deja Flud Companion asociat, poți iniția transferul către dispozitivul tău; altfel rămâne disponibilă copierea obișnuită.

Favoritele și setările de asociere ale PWA sunt stocate local în browserul folosit. Magnetra nu necesită un cont general AlexLab pentru căutarea publică. Nu promite acces la surse private și nu ocolește autentificarea furnizorilor.

## Arhitectura proiectului

```text
PWA (Safari / Home Screen / browser)
          │
          ▼
Cloudflare Worker (catalog, căutare, resolvere, validări)
          │
          ├── indexere publice cu origini fixe
          ├── gateway-uri opționale autentificate pentru sursele compatibile
          └── legătură Flud Companion doar când utilizatorul a configurat-o
```

**Structura repository-ului**

- `web/` — interfața PWA, stilurile, limbile, manifestul și service worker-ul.
- `worker/src/` și `worker/test/` — API, adaptori, contracte, validări și testare.
- `rock64/` — implementări pentru gateway-uri locale opționale, fără credențiale incluse.
- `app/` — codul aplicației Android și adaptările sale.
- `scripts/` — verificări de securitate, teste, diagnostice și pași de release controlați.
- `docs/` — istoric tehnic, checkpointuri și evidențe ale deciziilor.

## Securitate și administrare

Repository-ul este **public**; de aceea valorile reale ale tokenurilor, parolelor, cheilor private, perechilor QR și fișierelor de tunel **nu trebuie încărcate în Git**. Aplicația folosește origini fixe, limite de cerere, verificarea redirecționărilor și autentificare pentru serviciile private. Verificările CI includ teste de siguranță pentru adaptoare și un scanner care blochează fișierele de credențiale și adresele interne din codul urmărit de Git.

Workflow-urile obișnuite de verificare **nu trebuie confundate cu un release de producție**. Publicarea controlată necesită verificarea configurației, a versiunilor și a stării reale din Cloudflare; nu se reexecută arbitrar joburi de release consumate.

## Dezvoltare locală

**PWA / Worker:** proiectul are pagini statice în `web/`, API Worker în `worker/` și teste Node.js pentru contracte.

```bash
git clone https://github.com/Zuzuitu/AlexLab-Magnetra.git
cd AlexLab-Magnetra
node --test worker/test/*.test.mjs
python3 scripts/check-project-invariants.py
python3 scripts/check_public_repo_exposure.py
```

**Android:** este necesar SDK-ul Android și un JDK compatibil cu proiectul Gradle. Pentru un build de test:

```bash
./gradlew app:assembleDebug
```

Folosirea acestor comenzi nu publică automat Worker-ul. Configurația de producție și credențialele se administrează separat; nu copia tokenuri în issue-uri, Pull Request-uri sau loguri.

## Stadiu și următoarele îmbunătățiri

La checkpointul din **25 octombrie 2026**, corecțiile magnet pentru **0Magnet, TheRarBg și NoNameClub** au fost validate în producție, iar NoNameClub a fost confirmat funcțional pe iPhone. Se urmăresc în continuare compatibilitatea PWA pe iOS (safe area în modul Home Screen), afișarea corectă a caracterelor chirilice, auditarea surselor fluctuante și consolidarea verificărilor de securitate pentru repository-ul public.

Pentru starea tehnică detaliată vezi [`docs/PROJECT_STATE.md`](docs/PROJECT_STATE.md) și [`docs/NEXT_CHAT_HANDOFF.md`](docs/NEXT_CHAT_HANDOFF.md). Datele istorice sunt evidențe ale implementării, nu garanții de disponibilitate în timp real.

## Recunoaștere și licență

Magnetra pornește din codul **[prajwalch/TorrentSearch](https://github.com/prajwalch/TorrentSearch)**, distribuit sub licența **MIT**. Mulțumiri autorului și contribuitorilor proiectului original. Păstrăm fișierul [`LICENSE`](LICENSE) și atribuirea upstream. Integrarea și personalizarea AlexLab sunt dezvoltări distincte.

Magnetra nu găzduiește fișiere media sau conținut torrent; afișează rezultate și legături furnizate de servicii externe. Utilizatorul decide ce accesează și transferă.
