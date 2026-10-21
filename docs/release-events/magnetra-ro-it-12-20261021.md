# Magnetra — autorizare publicare PWA RO/IT și 12 surse

Cerere explicită a proprietarului, 21 octombrie 2026: ascunderea celor 15 indexere suplimentare enumerate în conversație (34 ascunse / 12 vizibile din cele 46 originale), prioritizarea BTDigg/Torrent9/OxTorrent și interfață publică numai în română (implicit) și italiană (la alegere), fără etichete de audit/test.

Această activare nu modifică backendul, serviciile Rock64, gateway-urile BTDigg/OxTorrent/Torrent9, Cloudflare DNS sau Cloudflare Tunnel, secrete, router ori Flud Companion. Catalogul original de 46 surse rămâne intact.

Condiție strictă pentru activare: PR-ul de release separat (#120) trebuie să fie deja MERGED cu CI 4/4 PASS. Codul de release verifică exact versiunile imutabile 6dad@100 / 9bbb@0, hashul public original app.js, bindingurile, JS/CSS/HTML și noul i18n.js, catalogul 46 la slot 0 și după full, canary 5%, apoi 100%, cu rollback limitat. Workflow exclusiv pentru acest fișier și markerul `[magnetra-ro-it-12-publish-20261021]`.

Această înregistrare dovedește intenția autorizată, nu succesul publicării. Succesul trebuie stabilit numai din rularea efectivă Cloudflare și postflight.
