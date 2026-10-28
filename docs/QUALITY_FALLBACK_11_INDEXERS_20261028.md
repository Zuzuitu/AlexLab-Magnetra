# Magnetra — exact-first release matching with quality fallback

**Code only; NOT published.** The original user-entered release stays the authority for quality and provenance.

If the exact release group is found among selected sources, show **only exact matches**. If no selected source returns an exact match, show clearly labeled **quality alternatives** found in source-owned records, requiring the same film title/year, resolution (e.g. 1080p), codec/encoder (e.g. x265), and bit depth (e.g. 10bit). Fallback may differ on release group, audio channel count and WEBRip/WEB-DL. Never treat a fallback magnet as an exact PSA magnet.

User-confirmed real BTDigg one-request result: HTTP 200; 1 source row with exact filename and valid magnet. BTDigg remains on one exact literal filename query because that is the only mode owner-proven from Rock64. The other **10 visible** indexers receive one quality-focused title/year + technical terms query to discover exact or other-group releases. All results are split into separate fields: `results` (strict) and `alternatives` (quality only), with `releaseMatch="quality-alternative"`, no query retries. PWA waits until the full selected provider set has finished, then promotes alternatives only when exact is empty globally.

If BTDigg's exact query itself returns no rows, this mode cannot automatically discover other-group BTDigg torrents from that same query: we deliberately do not add a second automatic request to a rate-limiting source. User can initiate a separately explicit group-free search when needed. Other sources likewise cannot guarantee that the original server returns every eligible release, particularly with top-100 source limits.

One-source errors remain true errors; cached source results are marked stale, never fabricated; other 35 backend provider adapters retain the original search API schema/strategy. Do not re-enable 35 hidden PWA sources, modify Flud, Cloudflare, Rock64, tunnel, or service, or change page size 50. PWA service-worker cache bumps from v13 to v14. New release requires fresh guarded immutable 0→5→100 deployment and real iPhone acceptance; current last known production immutable version is `b39a0393-bbf8-4ba3-9d32-7c1390aa867f@100%` at 2026-10-27 guard, but must not be assumed unchanged at future release time.

The **experimental** `curl_cffi` gateway remains in separate Draft PR #220 and is **not** part of this change, because the source's programmatic-access permission is still unverified.
