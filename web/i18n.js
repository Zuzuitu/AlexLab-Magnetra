"use strict";
// Public UI only: RO (default), IT. No external translation service or requests.
(function(){
const DICTIONARY={
  "Exact release not found in responding indexers. Showing only the highest-ranked available alternatives. Different specifications are labeled.":{
    "ro":"Varianta exactă nu a fost găsită în indexerele care au răspuns. Sunt afișate doar alternativele disponibile cel mai apropiate, cu diferențele marcate.",
    "it":"Release esatta non trovata negli indici che hanno risposto. Sono mostrate solo le alternative disponibili più vicine, con le differenze evidenziate."
  },
  "Alternative release":{"ro":"Versiune alternativă","it":"Release alternativa"},
  "Different: {terms}":{"ro":"Diferă: {terms}","it":"Differenze: {terms}"},
  "resolution":{"ro":"rezoluția","it":"risoluzione"},
  "codec":{"ro":"codecul","it":"codec"},
  "bit depth":{"ro":"adâncimea de culoare","it":"profondità colore"},
  "group":{"ro":"grupul","it":"gruppo"},
  "release naming":{"ro":"versiunea release-ului","it":"versione della release"},
  "Some indexers searched by title: {query}. Matching is checked against the original request.":{
    "ro":"Unele indexere au căutat după titlu: {query}. Potrivirea este verificată față de căutarea originală.",
    "it":"Alcuni indici hanno cercato per titolo: {query}. Le corrispondenze sono verificate rispetto alla richiesta originale."
  },
  "No exact {group} release found in responding indexers. Showing alternatives matching {terms}.":{
    "ro":"Niciun release exact {group} găsit în indexerele care au răspuns. Sunt afișate alternative cu {terms}.",
    "it":"Nessuna release esatta {group} trovata negli indici che hanno risposto. Sono mostrate alternative con {terms}."
  },
  "Alternative group / release":{
    "ro":"Grup / versiune alternativă",
    "it":"Gruppo / release alternativa"
  },
  "requested":{"ro":"cerut","it":"richiesta"},
  "Searched sources by title: {query}. Results must match every requested release term; verify the file details.":{
    "ro":"Indexere interogate după titlul: {query}. Rezultatele trebuie să conțină toate detaliile cerute (calitate și grup). Verifică fișierul înainte de descărcare.",
    "it":"Fonti interrogate per titolo: {query}. I risultati devono contenere tutti i dettagli richiesti (qualità e gruppo). Verifica il file prima di scaricarlo."
  },
  "ThePirateBay is limiting requests right now. Try again later.":{"ro":"ThePirateBay limitează momentan solicitările. Reîncearcă mai târziu.","it":"ThePirateBay limita temporaneamente le richieste. Riprova più tardi."},
  "Saved source result ({n} min old)":{"ro":"Rezultat memorat din sursă (acum {n} min)","it":"Risultato salvato dalla fonte ({n} min fa)"},
  "Saved authentic results shown because the source is temporarily unavailable.":{"ro":"Sunt afișate rezultate autentice memorate; sursa nu a răspuns acum.","it":"Risultati autentici salvati: la fonte non ha risposto ora."},
  "{source}: saved results from {n} minutes ago; not live.":{"ro":"{source}: rezultate salvate acum {n} minute, nu în timp real.","it":"{source}: risultati salvati {n} minuti fa, non in tempo reale."},
  "Results pages":{"ro":"Pagini rezultate","it":"Pagine dei risultati"},
  "Previous page":{"ro":"← Anterioară","it":"← Precedente"},
  "Next page":{"ro":"Următoarea →","it":"Successiva →"},
  "Page {page} of {pages} · {start}–{end} of {total}":{
    "ro":"Pagina {page} din {pages} · {start}–{end} din {total}",
    "it":"Pagina {page} di {pages} · {start}–{end} di {total}"
  },
  "Selected all {n} indexers.":{"ro":"Selectate toate cele {n} surse.","it":"Selezionate tutte le {n} fonti."},
  "Deselected all {n} indexers.":{"ro":"Deselectate toate cele {n} surse.","it":"Deselezionate tutte le {n} fonti."},
  "Deselect all available":{"ro":"Deselectează toate","it":"Deseleziona tutte"},

  "Date TV:": {
    "ro": "Date TV:",
    "it": "Dati TV:"
  },
  "Sources that return errors are unchecked after a completed search. You can reactivate them at any time.": {
    "ro": "Sursele cu erori se dezactivează automat după căutare. Le poți reactiva oricând.",
    "it": "Le fonti con errori vengono disattivate automaticamente dopo la ricerca. Puoi riattivarle in qualsiasi momento."
  },
  "Select verified sources": {
    "ro": "Selectează sursele verificate",
    "it": "Seleziona fonti verificate"
  },
  "Check Shield connection": {
    "ro": "Verifică legătura Shield",
    "it": "Verifica connessione Shield"
  },
  "AlexLab Magnetra — torrent metasearch and Flud Companion handoff.": {
    "ro": "AlexLab Magnetra — caută torrente și trimite magneturi în Flud Companion.",
    "it": "AlexLab Magnetra — cerca torrent e invia magnet a Flud Companion."
  },
  "Search...": {
    "ro": "Caută...",
    "it": "Cerca..."
  },
  "Search torrents...": {
    "ro": "Caută torrente...",
    "it": "Cerca torrent..."
  },
  "Search torrents": {
    "ro": "Căutare torrente",
    "it": "Ricerca torrent"
  },
  "Search": {
    "ro": "Caută",
    "it": "Cerca"
  },
  "Search →": {
    "ro": "Caută →",
    "it": "Cerca →"
  },
  "Find what you need.": {
    "ro": "Găsește ce cauți.",
    "it": "Trova quello che cerchi."
  },
  "Send it anywhere.": {
    "ro": "Trimite oriunde.",
    "it": "Invia ovunque."
  },
  "One search, multiple indexers. Discover magnet links and send them straight to your Flud Companion.": {
    "ro": "O singură căutare, mai multe surse. Găsește linkuri magnet și trimite-le către Flud Companion.",
    "it": "Una ricerca, più fonti. Trova link magnet e inviali a Flud Companion."
  },
  "METASEARCH ENGINE": {
    "ro": "MOTOR DE CĂUTARE",
    "it": "MOTORE DI RICERCA"
  },
  "ALEXLAB / SEARCH SYSTEM": {
    "ro": "ALEXLAB / CĂUTARE",
    "it": "ALEXLAB / RICERCA"
  },
  "CATEGORY": {
    "ro": "CATEGORIE",
    "it": "CATEGORIA"
  },
  "All categories": {
    "ro": "Toate categoriile",
    "it": "Tutte le categorie"
  },
  "Movies": {
    "ro": "Filme",
    "it": "Film"
  },
  "Series": {
    "ro": "Seriale",
    "it": "Serie TV"
  },
  "Apps": {
    "ro": "Aplicații",
    "it": "Applicazioni"
  },
  "Games": {
    "ro": "Jocuri",
    "it": "Giochi"
  },
  "Anime": {
    "ro": "Anime",
    "it": "Anime"
  },
  "Music": {
    "ro": "Muzică",
    "it": "Musica"
  },
  "Books": {
    "ro": "Cărți",
    "it": "Libri"
  },
  "Other": {
    "ro": "Altele",
    "it": "Altro"
  },
  "Adult": {
    "ro": "Adulți",
    "it": "Adulti"
  },
  "SORT BY": {
    "ro": "SORTEAZĂ DUPĂ",
    "it": "ORDINA PER"
  },
  "Most seeders": {
    "ro": "Cele mai multe surse",
    "it": "Più seed"
  },
  "Newest first": {
    "ro": "Cele mai noi",
    "it": "Più recenti"
  },
  "Largest first": {
    "ro": "Cele mai mari",
    "it": "Più grandi"
  },
  "Name A–Z": {
    "ro": "Nume A–Z",
    "it": "Nome A–Z"
  },
  "Indexers": {
    "ro": "Surse",
    "it": "Fonti"
  },
  "Flud Companion · Not paired": {
    "ro": "Flud Companion · Neconectat",
    "it": "Flud Companion · Non associato"
  },
  "Flud Companion · Unavailable": {
    "ro": "Flud Companion · Indisponibil",
    "it": "Flud Companion · Non disponibile"
  },
  "Flud Companion · Online": {
    "ro": "Flud Companion · Conectat",
    "it": "Flud Companion · Connesso"
  },
  "Flud Companion · Offline": {
    "ro": "Flud Companion · Deconectat",
    "it": "Flud Companion · Disconnesso"
  },
  "↗ Paste magnet → Flud": {
    "ro": "↗ Lipește magnet → Flud",
    "it": "↗ Incolla magnet → Flud"
  },
  "☆ Bookmarks": {
    "ro": "☆ Favorite",
    "it": "☆ Preferiti"
  },
  "Bookmarks": {
    "ro": "Favorite",
    "it": "Preferiti"
  },
  "DISCOVERY": {
    "ro": "REZULTATE",
    "it": "RISULTATI"
  },
  "Search results": {
    "ro": "Rezultatele căutării",
    "it": "Risultati della ricerca"
  },
  "READY": {
    "ro": "PREGĂTIT",
    "it": "PRONTO"
  },
  "Enter a search to see results from your enabled indexers.": {
    "ro": "Introdu o căutare pentru rezultatele surselor selectate.",
    "it": "Inserisci una ricerca per vedere i risultati delle fonti selezionate."
  },
  "Search. Magnet. Done.": {
    "ro": "Caută. Magnet. Gata.",
    "it": "Cerca. Magnet. Fatto."
  },
  "Based on TorrentSearch (MIT) ↗": {
    "ro": "Bazat pe TorrentSearch (MIT) ↗",
    "it": "Basato su TorrentSearch (MIT) ↗"
  },
  "SEARCH SOURCES": {
    "ro": "SURSE DE CĂUTARE",
    "it": "FONTI DI RICERCA"
  },
  "Loading source catalog…": {
    "ro": "Se încarcă sursele…",
    "it": "Caricamento delle fonti…"
  },
  "After each completed search, indexers that returned errors are automatically unchecked for future searches on this device. Indexers that return zero matching titles without an error stay enabled. You can re-enable a visible source manually or select all available indexers. Per your saved interface preferences, 19 repeatedly failing sources are hidden and cannot be selected here. All original 46 source adapters remain in the backend for compatibility; no provider is deleted. Statuses are historical observations, not live uptime.": {
    "ro": "Sursele care dau erori se dezactivează automat după căutare. Le poți reactiva oricând din această listă.",
    "it": "Le fonti che restituiscono errori vengono disattivate dopo la ricerca. Puoi riattivarle in qualsiasi momento da questo elenco."
  },
  "EZTV series-name lookup uses": {
    "ro": "Căutarea serialelor EZTV folosește",
    "it": "La ricerca delle serie EZTV usa"
  },
  "metadata to identify a show by IMDb ID; torrent results come only from EZTV.": {
    "ro": "pentru identificarea serialului; rezultatele provin doar de la EZTV.",
    "it": "per identificare la serie; i risultati provengono solo da EZTV."
  },
  "Select last-audit results": {
    "ro": "Selectează sursele verificate",
    "it": "Seleziona fonti verificate"
  },
  "Select all available": {
    "ro": "Selectează toate",
    "it": "Seleziona tutte"
  },
  "Done": {
    "ro": "Gata",
    "it": "Fatto"
  },
  "DIRECT HANDOFF": {
    "ro": "TRIMITERE DIRECTĂ",
    "it": "INVIO DIRETTO"
  },
  "Send a magnet directly to your NVIDIA Shield via your existing Remote relay.": {
    "ro": "Trimite un magnet către NVIDIA Shield prin conexiunea ta Flud Remote.",
    "it": "Invia un magnet a NVIDIA Shield tramite la connessione Flud Remote."
  },
  "Quick pairing (Remote QR link)": {
    "ro": "Asociere rapidă (link QR Remote)",
    "it": "Associazione rapida (link QR Remote)"
  },
  "Paste the Remote QR URL here": {
    "ro": "Lipește aici linkul QR Remote",
    "it": "Incolla qui il link QR Remote"
  },
  "Import QR pairing": {
    "ro": "Importă asocierea QR",
    "it": "Importa associazione QR"
  },
  "Device ID": {
    "ro": "ID dispozitiv",
    "it": "ID dispositivo"
  },
  "Remote Device ID": {
    "ro": "ID dispozitiv Remote",
    "it": "ID dispositivo Remote"
  },
  "Remote token": {
    "ro": "Token Remote",
    "it": "Token Remote"
  },
  "Remote bearer token": {
    "ro": "Token de acces Remote",
    "it": "Token di accesso Remote"
  },
  "Auto-start in Flud": {
    "ro": "Pornire automată în Flud",
    "it": "Avvio automatico in Flud"
  },
  "Only send automatically when the Companion accessibility helper is ready.": {
    "ro": "Trimite automat numai când funcția de accesibilitate Companion este pregătită.",
    "it": "Invia automaticamente solo quando l'assistente di accessibilità Companion è pronto."
  },
  "Pair once. Credentials stay in this browser's local storage and are sent only to the fixed Flud Companion relay through our same-origin API. Never put them in a URL.": {
    "ro": "Datele de asociere rămân în acest browser și sunt transmise doar către serviciul Flud Companion. Nu le introduce în linkuri publice.",
    "it": "I dati di associazione restano in questo browser e vengono inviati solo al servizio Flud Companion. Non inserirli in link pubblici."
  },
  "Forget pairing": {
    "ro": "Elimină asocierea",
    "it": "Rimuovi associazione"
  },
  "Save pairing": {
    "ro": "Salvează asocierea",
    "it": "Salva associazione"
  },
  "Test Shield connection": {
    "ro": "Verifică legătura Shield",
    "it": "Verifica connessione Shield"
  },
  "For local-only use or as a fallback, use “Copy magnet” and open your existing": {
    "ro": "Pentru utilizare locală sau de rezervă, copiază magnetul și deschide",
    "it": "Per l'uso locale o come alternativa, copia il magnet e apri"
  },
  "Flud Companion PWA ↗": {
    "ro": "Flud Companion PWA ↗",
    "it": "Flud Companion PWA ↗"
  },
  "DIRECT TO FLUD COMPANION": {
    "ro": "DIRECT CĂTRE FLUD COMPANION",
    "it": "DIRETTO A FLUD COMPANION"
  },
  "Send a magnet": {
    "ro": "Trimite un magnet",
    "it": "Invia un magnet"
  },
  "Paste a magnet copied from BTDigg or another website. It will be sent through your paired Flud Companion.": {
    "ro": "Lipește un magnet copiat de pe BTDigg sau alt site. Acesta va fi trimis prin Flud Companion.",
    "it": "Incolla un magnet copiato da BTDigg o da un altro sito. Verrà inviato tramite Flud Companion."
  },
  "Magnet link": {
    "ro": "Link magnet",
    "it": "Link magnet"
  },
  "Send to Flud →": {
    "ro": "Trimite în Flud →",
    "it": "Invia a Flud →"
  },
  "Configure Flud Companion": {
    "ro": "Configurează Flud Companion",
    "it": "Configura Flud Companion"
  },
  "Flud Companion settings": {
    "ro": "Setări Flud Companion",
    "it": "Impostazioni Flud Companion"
  },
  "Close": {
    "ro": "Închide",
    "it": "Chiudi"
  },
  "Romanian": {
    "ro": "Română",
    "it": "Romeno"
  },
  "Italian": {
    "ro": "Italiană",
    "it": "Italiano"
  },
  "BTDigg: waiting {n}s to respect source search limits…": {
    "ro": "BTDigg: așteaptă {n} s pentru limitarea cererilor…",
    "it": "BTDigg: attendi {n} s per rispettare i limiti delle richieste…"
  },
  "Server returned an invalid response": {
    "ro": "Serverul a returnat un răspuns nevalid.",
    "it": "Il server ha restituito una risposta non valida."
  },
  "Request failed ({code})": {
    "ro": "Cererea a eșuat ({code}).",
    "it": "Richiesta non riuscita ({code})."
  },
  "{n} failed indexer(s) paused automatically. Next searches use the remaining selected sources; tap Indexers to retry.": {
    "ro": "{n} surse dezactivate automat după erori. Căutările următoare folosesc restul surselor.",
    "it": "{n} fonti disattivate automaticamente dopo errori. Le prossime ricerche usano le fonti rimanenti."
  },
  "{n} sources available": {
    "ro": "{n} surse disponibile",
    "it": "{n} fonti disponibili"
  },
  "All visible indexers are already selected.": {
    "ro": "Toate sursele disponibile sunt deja selectate.",
    "it": "Tutte le fonti disponibili sono già selezionate."
  },
  "Paused": {
    "ro": "Pauzată",
    "it": "In pausa"
  },
  "{n} SAVED": {
    "ro": "{n} SALVATE",
    "it": "{n} SALVATI"
  },
  "{n} MATCHES": {
    "ro": "{n} REZULTATE",
    "it": "{n} RISULTATI"
  },
  "Saved bookmarks": {
    "ro": "Favorite salvate",
    "it": "Preferiti salvati"
  },
  "{n} unrelated source results excluded from this search. Only title-matching entries are shown.": {
    "ro": "{n} rezultate nerelevante eliminate. Sunt afișate doar titlurile potrivite.",
    "it": "{n} risultati non pertinenti esclusi. Sono mostrati solo i titoli corrispondenti."
  },
  "No bookmarks saved yet.": {
    "ro": "Nu ai favorite salvate.",
    "it": "Non hai ancora preferiti salvati."
  },
  "Search incomplete: {n} source(s) failed. No matching releases were found among responding sources.": {
    "ro": "Căutare incompletă: {n} surse nu au răspuns. Nu s-au găsit rezultate potrivite în sursele care au răspuns.",
    "it": "Ricerca incompleta: {n} fonti non hanno risposto. Nessun risultato corrispondente tra le fonti che hanno risposto."
  },
  "No matching titles. Try another title, fewer keywords or different indexers.": {
    "ro": "Niciun rezultat potrivit. Încearcă alt titlu sau alte surse.",
    "it": "Nessun risultato pertinente. Prova un altro titolo o altre fonti."
  },
  "{n} seeders": {
    "ro": "{n} surse",
    "it": "{n} seed"
  },
  "{n} peers": {
    "ro": "{n} participanți",
    "it": "{n} peer"
  },
  "Send to Flud": {
    "ro": "Trimite în Flud",
    "it": "Invia a Flud"
  },
  "Copy": {
    "ro": "Copiază",
    "it": "Copia"
  },
  "Share": {
    "ro": "Distribuie",
    "it": "Condividi"
  },
  "Resolve": {
    "ro": "Obține magnet",
    "it": "Ottieni magnet"
  },
  "Resolving…": {
    "ro": "Se obține magnetul…",
    "it": "Recupero del magnet…"
  },
  "Magnet resolved.": {
    "ro": "Magnet obținut.",
    "it": "Magnet recuperato."
  },
  "Magnet copied": {
    "ro": "Magnet copiat.",
    "it": "Magnet copiato."
  },
  "Copy failed": {
    "ro": "Copiere nereușită.",
    "it": "Copia non riuscita."
  },
  "Open in your installed torrent client": {
    "ro": "Deschide în aplicația de torrente instalată",
    "it": "Apri nel client torrent installato"
  },
  "Details ↗": {
    "ro": "Detalii ↗",
    "it": "Dettagli ↗"
  },
  "Provider has no supported magnet or details link.": {
    "ro": "Sursa nu oferă un link magnet compatibil.",
    "it": "La fonte non offre un link magnet compatibile."
  },
  "Provider did not return a valid magnet.": {
    "ro": "Sursa nu a furnizat un magnet valid.",
    "it": "La fonte non ha restituito un magnet valido."
  },
  "Queued ✓": {
    "ro": "În așteptare ✓",
    "it": "In coda ✓"
  },
  "Shield ✓": {
    "ro": "Shield ✓",
    "it": "Shield ✓"
  },
  "Retry send": {
    "ro": "Retrimite",
    "it": "Riprova invio"
  },
  "Sending…": {
    "ro": "Se trimite…",
    "it": "Invio in corso…"
  },
  "Shield acknowledged the magnet command.": {
    "ro": "Shield a confirmat primirea magnetului.",
    "it": "Shield ha confermato la ricezione del magnet."
  },
  "Shield rejected magnet: {reason}": {
    "ro": "Shield a refuzat magnetul: {reason}",
    "it": "Shield ha rifiutato il magnet: {reason}"
  },
  "Unknown error": {
    "ro": "Eroare necunoscută",
    "it": "Errore sconosciuto"
  },
  "Queued; waiting for Shield confirmation.": {
    "ro": "În așteptarea confirmării de la Shield.",
    "it": "In attesa della conferma da Shield."
  },
  "Pair Flud Companion first.": {
    "ro": "Asociază mai întâi Flud Companion.",
    "it": "Associa prima Flud Companion."
  },
  "This magnet is already being sent.": {
    "ro": "Acest magnet este deja în curs de trimitere.",
    "it": "Questo magnet è già in fase di invio."
  },
  "Relay did not confirm a queued command.": {
    "ro": "Serviciul nu a confirmat comanda.",
    "it": "Il servizio non ha confermato il comando."
  },
  "Relay returned no command receipt ID.": {
    "ro": "Serviciul nu a furnizat o confirmare a comenzii.",
    "it": "Il servizio non ha fornito una ricevuta del comando."
  },
  "Already queued in Companion.": {
    "ro": "Deja în coada Companion.",
    "it": "Già in coda su Companion."
  },
  "Magnet queued; awaiting Shield acknowledgement.": {
    "ro": "Magnet pus în coadă; se așteaptă confirmarea Shield.",
    "it": "Magnet aggiunto alla coda; in attesa della conferma da Shield."
  },
  "{n} source(s) unavailable · See alternatives": {
    "ro": "{n} surse indisponibile · Alternative",
    "it": "{n} fonti non disponibili · Alternative"
  },
  "BTDigg searches run from Rock64 at home, not from your phone. A temporary upstream limit, timeout or tunnel issue does not mean this indexer is permanently offline.": {
    "ro": "BTDigg poate fi temporar indisponibil. Încearcă mai târziu sau folosește altă sursă.",
    "it": "BTDigg può essere temporaneamente non disponibile. Riprova più tardi o usa un'altra fonte."
  },
  "Some external sites restrict searches from Cloudflare. Magnetra cannot bypass their verification. You can open a source directly or search independently through other indexers.": {
    "ro": "Unele site-uri limitează căutarea automată. Poți deschide sursa direct sau folosi alte surse.",
    "it": "Alcuni siti limitano le ricerche automatiche. Puoi aprire la fonte direttamente o usarne altre."
  },
  "BTDigg is limiting requests. Wait a few seconds before another search.": {
    "ro": "BTDigg limitează cererile. Așteaptă câteva secunde.",
    "it": "BTDigg limita le richieste. Attendi qualche secondo."
  },
  "Provider unavailable": {
    "ro": "Sursă indisponibilă.",
    "it": "Fonte non disponibile."
  },
  "Provider timed out": {
    "ro": "Sursa nu a răspuns la timp.",
    "it": "La fonte non ha risposto in tempo."
  },
  "Provider request rejected": {
    "ro": "Cererea a fost refuzată de sursă.",
    "it": "Richiesta rifiutata dalla fonte."
  },
  "Provider redirected": {
    "ro": "Sursa a redirecționat cererea.",
    "it": "La fonte ha reindirizzato la richiesta."
  },
  "Provider rate limited": {
    "ro": "Prea multe cereri către sursă.",
    "it": "Troppe richieste alla fonte."
  },
  "Open source search ↗": {
    "ro": "Deschide căutarea sursei ↗",
    "it": "Apri ricerca della fonte ↗"
  },
  "Visit source ↗": {
    "ro": "Vizitează sursa ↗",
    "it": "Visita la fonte ↗"
  },
  "Search with available indexers →": {
    "ro": "Caută cu sursele disponibile →",
    "it": "Cerca con le fonti disponibili →"
  },
  "No alternative indexers are available.": {
    "ro": "Nu există alte surse disponibile.",
    "it": "Non sono disponibili altre fonti."
  },
  "Cancelling the current search and starting alternatives.": {
    "ro": "Se oprește căutarea curentă și se pornesc alternativele.",
    "it": "Interruzione della ricerca corrente e avvio delle alternative."
  },
  "Cancelling search; keeping results already found…": {
    "ro": "Se oprește căutarea; rezultatele găsite rămân afișate…",
    "it": "Interruzione della ricerca; i risultati trovati rimangono visibili…"
  },
  "Enter at least two characters": {
    "ro": "Introdu cel puțin două caractere.",
    "it": "Inserisci almeno due caratteri."
  },
  "Select at least one indexer.": {
    "ro": "Selectează cel puțin o sursă.",
    "it": "Seleziona almeno una fonte."
  },
  "Cancel search ×": {
    "ro": "Oprește căutarea ×",
    "it": "Interrompi ricerca ×"
  },
  "Searching {n} indexers…": {
    "ro": "Se caută în {n} surse…",
    "it": "Ricerca in {n} fonti…"
  },
  "Searched {done}/{all} indexers · {n} relevant matches.": {
    "ro": "Verificate {done}/{all} surse · {n} rezultate relevante.",
    "it": "Esaminate {done}/{all} fonti · {n} risultati pertinenti."
  },
  "Magnetra could not reach this provider through the API.": {
    "ro": "Sursa nu a putut fi accesată.",
    "it": "Impossibile raggiungere la fonte."
  },
  "No matching results; some indexers failed.": {
    "ro": "Niciun rezultat; unele surse nu au răspuns.",
    "it": "Nessun risultato; alcune fonti non hanno risposto."
  },
  "No matching titles in selected indexers.": {
    "ro": "Niciun titlu potrivit în sursele selectate.",
    "it": "Nessun titolo corrispondente nelle fonti selezionate."
  },
  "{n} failing indexer(s) paused for future searches.": {
    "ro": "{n} surse cu erori dezactivate pentru căutările următoare.",
    "it": "{n} fonti con errori disattivate per le prossime ricerche."
  },
  "Search cancelled. Results already found are preserved.": {
    "ro": "Căutarea a fost oprită. Rezultatele găsite au fost păstrate.",
    "it": "Ricerca interrotta. I risultati trovati sono stati conservati."
  },
  "Shield online · Auto-start ready": {
    "ro": "Shield conectat · Pornire automată pregătită",
    "it": "Shield connesso · Avvio automatico pronto"
  },
  "Shield online · Auto-start not ready": {
    "ro": "Shield conectat · Pornire automată indisponibilă",
    "it": "Shield connesso · Avvio automatico non disponibile"
  },
  "Shield offline": {
    "ro": "Shield deconectat",
    "it": "Shield disconnesso"
  },
  "Back to search": {
    "ro": "← Înapoi la căutare",
    "it": "← Torna alla ricerca"
  },
  "No tested sources with results in the saved audit.": {
    "ro": "Nu există surse verificate disponibile.",
    "it": "Non ci sono fonti verificate disponibili."
  },
  "Selected {n} verified sources.": {
    "ro": "Selectate {n} surse verificate.",
    "it": "Selezionate {n} fonti verificate."
  },
  "Selected all {n} visible indexers; hidden sources stay excluded.": {
    "ro": "Selectate toate cele {n} surse disponibile.",
    "it": "Selezionate tutte le {n} fonti disponibili."
  },
  "Paste a valid magnet link.": {
    "ro": "Lipește un link magnet valid.",
    "it": "Incolla un link magnet valido."
  },
  "Only the approved Flud Companion relay is supported.": {
    "ro": "Doar serviciul Flud Companion configurat este acceptat.",
    "it": "È supportato solo il servizio Flud Companion configurato."
  },
  "Remote QR link has no valid pairing credentials.": {
    "ro": "Linkul QR nu conține date valide de asociere.",
    "it": "Il link QR non contiene dati di associazione validi."
  },
  "QR pairing imported. Tap Save pairing.": {
    "ro": "Asocierea QR a fost importată. Apasă Salvează asocierea.",
    "it": "Associazione QR importata. Premi Salva associazione."
  },
  "Invalid Remote QR URL": {
    "ro": "Link QR Remote nevalid.",
    "it": "Link QR Remote non valido."
  },
  "Check Device ID and Remote token.": {
    "ro": "Verifică ID-ul dispozitivului și tokenul Remote.",
    "it": "Controlla l'ID dispositivo e il token Remote."
  },
  "Companion paired in this browser.": {
    "ro": "Companion a fost asociat în acest browser.",
    "it": "Companion associato in questo browser."
  },
  "Save Remote QR pairing first.": {
    "ro": "Salvează mai întâi asocierea QR.",
    "it": "Salva prima l'associazione QR."
  },
  "Checking…": {
    "ro": "Se verifică…",
    "it": "Verifica in corso…"
  },
  "Shield online.": {
    "ro": "Shield este conectat.",
    "it": "Shield è connesso."
  },
  "Shield offline or unavailable; see pairing status.": {
    "ro": "Shield este deconectat sau indisponibil; verifică asocierea.",
    "it": "Shield è disconnesso o non disponibile; verifica l'associazione."
  },
  "Pairing removed from this browser.": {
    "ro": "Asocierea a fost eliminată din acest browser.",
    "it": "Associazione rimossa da questo browser."
  },
  "Ready. {n} sources available.": {
    "ro": "Pregătit. {n} surse disponibile.",
    "it": "Pronto. {n} fonti disponibili."
  },
  "API unavailable": {
    "ro": "Serviciul nu este disponibil.",
    "it": "Servizio non disponibile."
  },
  "Language": {
    "ro": "Limbă",
    "it": "Lingua"
  },
  "AlexLab Magnetra — Search. Magnet. Done.": {
    "ro": "AlexLab Magnetra — Caută. Magnet. Gata.",
    "it": "AlexLab Magnetra — Cerca. Magnet. Fatto."
  },
  "TheRarBg refused the details request (403). Open Details on the source site.": {
    "ro": "TheRarBg a refuzat accesul la detalii (403). Deschide „Detalii” pe site-ul sursă.",
    "it": "TheRarBg ha rifiutato la pagina dei dettagli (403). Apri «Dettagli» sul sito di origine."
  },
  "TheRarBg details page is missing (404). Open Details on the source site.": {
    "ro": "Pagina de detalii TheRarBg nu există (404). Deschide „Detalii” pe site-ul sursă.",
    "it": "La pagina dei dettagli TheRarBg non esiste (404). Apri «Dettagli» sul sito di origine."
  },
  "TheRarBg is limiting requests (429). Try this result later.": {
    "ro": "TheRarBg limitează cererile (429). Încearcă acest rezultat mai târziu.",
    "it": "TheRarBg limita le richieste (429). Riprova più tardi."
  },
  "TheRarBg details server returned 500. Try this result later.": {
    "ro": "Serverul de detalii TheRarBg a răspuns cu 500. Încearcă mai târziu.",
    "it": "Il server dei dettagli TheRarBg ha risposto 500. Riprova più tardi."
  },
  "TheRarBg details server returned 502. Try this result later.": {
    "ro": "Serverul de detalii TheRarBg a răspuns cu 502. Încearcă mai târziu.",
    "it": "Il server dei dettagli TheRarBg ha risposto 502. Riprova più tardi."
  },
  "TheRarBg details server returned 503. Try this result later.": {
    "ro": "Serverul de detalii TheRarBg a răspuns cu 503. Încearcă mai târziu.",
    "it": "Il server dei dettagli TheRarBg ha risposto 503. Riprova più tardi."
  },
  "TheRarBg details server returned 504. Try this result later.": {
    "ro": "Serverul de detalii TheRarBg a răspuns cu 504. Încearcă mai târziu.",
    "it": "Il server dei dettagli TheRarBg ha risposto 504. Riprova più tardi."
  },
  "TheRarBg requires browser verification. Open Details on the source site.": {
    "ro": "TheRarBg cere verificare în browser. Deschide „Detalii” pe site-ul sursă.",
    "it": "TheRarBg richiede la verifica nel browser. Apri «Dettagli» sul sito di origine."
  },
  "TheRarBg details page did not contain a supported magnet or unique info hash.": {
    "ro": "Pagina de detalii TheRarBg nu conține un magnet acceptat sau un hash unic verificabil.",
    "it": "La pagina dei dettagli TheRarBg non contiene un magnet supportato o un hash univoco verificabile."
  },
  "TheRarBg details request timed out. Try this result later.": {
    "ro": "Cererea de detalii TheRarBg a expirat. Încearcă mai târziu.",
    "it": "La richiesta dei dettagli TheRarBg è scaduta. Riprova più tardi."
  },
  "TheRarBg details redirected outside the approved source route.": {
    "ro": "Pagina de detalii TheRarBg a redirecționat în afara domeniului permis.",
    "it": "La pagina dei dettagli TheRarBg ha reindirizzato fuori dal dominio consentito."
  },
  "TheRarBg details page exceeded the safe size limit.": {
    "ro": "Pagina de detalii TheRarBg depășește limita sigură de dimensiune.",
    "it": "La pagina dei dettagli TheRarBg supera il limite di dimensione sicuro."
  },
  "TheRarBg details URL was rejected by source validation.": {
    "ro": "Adresa detaliilor TheRarBg nu a trecut verificarea sursei.",
    "it": "L'indirizzo dei dettagli TheRarBg non ha superato la verifica della fonte."
  },
  "Magnetra could not connect to TheRarBg details.": {
    "ro": "Magnetra nu se poate conecta la pagina de detalii TheRarBg.",
    "it": "Magnetra non riesce a collegarsi alla pagina dei dettagli TheRarBg."
  },
  "The magnet resolver is temporarily unavailable.": {
    "ro": "Serviciul de rezolvare a magneturilor este temporar indisponibil.",
    "it": "Il servizio di risoluzione dei magnet è temporaneamente non disponibile."
  },
  "Magnetra was blocked before receiving a server response (HTTP 403).": {
    "ro": "Cererea Magnetra a fost blocată înainte de răspunsul serverului (HTTP 403).",
    "it": "La richiesta Magnetra è stata bloccata prima della risposta del server (HTTP 403)."
  },
  "Magnetra received a non-JSON response while resolving the magnet.": {
    "ro": "Magnetra a primit un răspuns invalid la rezolvarea magnetului.",
    "it": "Magnetra ha ricevuto una risposta non valida durante la risoluzione del magnet."
  },
  "Your phone could not reach Magnetra's magnet resolver.": {
    "ro": "Telefonul nu a reușit să contacteze serviciul Magnetra pentru magneturi.",
    "it": "Il telefono non è riuscito a contattare il servizio Magnetra per i magnet."
  },
  "The magnet request was cancelled before completion.": {
    "ro": "Cererea pentru magnet a fost anulată înainte de finalizare.",
    "it": "La richiesta del magnet è stata annullata prima del completamento."
  },
  "TheRarBg could not provide this magnet. Open Details to try it on the source site.": {
    "ro": "TheRarBg nu a putut furniza magnetul. Deschide „Detalii” pentru a încerca direct pe site.",
    "it": "TheRarBg non ha fornito il magnet. Apri «Dettagli» per provare direttamente sul sito."
  }
};
const KEY="magnetra.language.v1";
const languages=["ro","it"];
let current="ro";
try{current=localStorage.getItem(KEY)==="it"?"it":"ro";}catch{}
const ROMANIAN_KEYS=new Map(Object.entries(DICTIONARY).map(([key,value])=>[value.ro,key]));
function sourceKey(value){return DICTIONARY[value]?value:ROMANIAN_KEYS.get(value);}
const savedNodes=[];
const savedAttrs=[];
const attrs=["placeholder","aria-label","title","content"];
function template(text,args){return String(text).replace(/\{(\w+)\}/g,(_,key)=>String(args?.[key]??""));}
function t(key,args){return template(DICTIONARY[key]?.[current]||key,args);}
function capture(){
 const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
 for(let n; (n=walker.nextNode());){
  const k=n.textContent.trim();
  const key=sourceKey(k);
  if(!key)continue;
  const spaces=n.textContent.match(/^(\s*)(.*?)(\s*)$/s);
  savedNodes.push([n,key,spaces?.[1]||"",spaces?.[3]||""]);
 }
 for(const el of document.querySelectorAll("[placeholder],[aria-label],[title],[content]")){
  for(const attr of attrs){const value=el.getAttribute(attr);if(value&&sourceKey(value))savedAttrs.push([el,attr,sourceKey(value)]);}
 }
}
function paint(){
 document.documentElement.lang=current;
 for(const [n,k,a,b] of savedNodes)n.textContent=a+t(k)+b;
 for(const [el,attr,k] of savedAttrs)el.setAttribute(attr,t(k));
 const sel=document.getElementById("languageSelect");if(sel){sel.value=current;sel.setAttribute("aria-label",t("Language"));}
 document.title=t("AlexLab Magnetra — Search. Magnet. Done.");
}
function set(next){if(!languages.includes(next))return false;current=next;try{localStorage.setItem(KEY,next);}catch{}paint();return true;}
function init(){capture();paint();}
window.MagnetraI18n={t,set,init,get language(){return current;},dictionary:DICTIONARY};
document.addEventListener("DOMContentLoaded",init);
})();
