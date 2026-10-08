# Provider availability audit — AlexLab Magnetra

## Machine-readable snapshot used by the PWA

The current dated source selection snapshot lives in `worker/src/source-audit.mjs`, generated from production workflow **37816874771**. It records **12 sources with results, 12 empty/unverified and 22 errors**, corresponding to a single `ubuntu` search at 2026-10-08 17:29 UTC. The PWA displays this observation explicitly as historical and uses it to offer a fast, practical source-selection option. It does not claim current uptime.

## Second production audit — deployed source recovery

_Observation: 2026-10-08, deploy workflow run **37816874771**, commit `060ce27a2ba36310e7e5bc814c025633aba10cff`._

| Outcome | Count | Change vs previous |
| --- | ---: | --- |
| Search returned results | **12** | No change |
| Empty / unverified | **12** | −1 |
| Provider-side error | **22** | +1 |
| API transport failure | **0** | No change |

BTDigg: `TIMEOUT`; the API includes an owned-source browser link. Other errors are mostly `ACCESS_DENIED` (HTTP 403), with `REDIRECT_BLOCKED`, `RATE_LIMIT`, `UPSTREAM_ERROR` and some `TIMEOUT` statuses.

Sukebei Nyaa moved from empty/unverified to timeout, accounting for the increase from 21 to 22 errors. Most remaining classifications were consistent with earlier audit observations. One TokyoToshokan response lacked the typed code (`UNCLASSIFIED`) although the underlying error was HTTP 403; this needs re-verification rather than an invented explanation.

Cloudflare HTTPS, homepage, manifest, health API and all 46 catalog entries passed. Those checks establish deployment integrity, **not live success for all torrent indexers**. Source fallback is manual direct-browser search and correctly attributed independent alternatives. The new clipboard-to-Flud action still requires the owner's on-device confirmation.

---


_Observation: 2026-10-08, Cloudflare production deployment workflow run 37769029530. Query: `ubuntu` (single bounded call per indexer). This is a snapshot, not an uptime guarantee._

## Summary

| Outcome | Count | Meaning |
| --- | ---: | --- |
| At least one result | 12 | A query returned one or more results; magnet extraction/handoff was **not** necessarily validated. |
| Empty / unverified | 13 | The `ubuntu` search returned zero rows; cannot conclude that provider is broken. |
| External/source error | 21 | Cloudflare could not complete the request; inspect source-specific error below. |

### Returned search rows (12)

AudioBookBay, Dmhy, Btsow, Internet Archive, Knaben, EpubLibre, LinuxTracker, NoNameClub, ThePirateBay, TorrentsCSV, TheRarBg, 0Magnet.

### Empty or unverified (13)

AniLibria, AnimeTosho, BangumiMoe, BlueRoms, FileMood, FitGirlRepacks, MegaPeer, Mikan, NekoBT, SubsPlease, Sukebei Nyaa, Rutor, YTS.

### Errors (21)

| Provider ID | Initial live Worker result | Observed root or qualification |
| --- | --- | --- |
| `btdigg` | Timeout | Both `btdig.com` and `www.btdig.com` independently returned **HTTP 429** on a GitHub-hosted network probe. |
| `xxxtracker` | Timeout | Upstream request did not complete within Worker deadline; no verified alternative endpoint. |
| `anirena` | Redirect blocked | GitHub probe also returned HTTP 403 with `cf-mitigated: challenge`. |
| `bitsearch` | Redirect blocked | GitHub probe also returned HTTP 403 with `cf-mitigated: challenge`. |
| `limetorrents` | Redirect blocked | GitHub probe also returned HTTP 403 with `cf-mitigated: challenge`. |
| `torrentdownloadinfo` | Redirect blocked | GitHub probe also returned HTTP 403 with `cf-mitigated: challenge`. |
| `bt4g` | HTTP 403 | External service refused Worker request; challenge status not independently established. |
| `extdotto` | HTTP 403 | External service refused Worker request. |
| `eztvx` | HTTP 403 | External service refused Worker request. |
| `mypornclub` | HTTP 403 | External service refused Worker request. |
| `oxtorrent` | HTTP 403 | External service refused Worker request. |
| `1337x` | HTTP 403 | External service refused Worker request. |
| `tokyotoshokan` | HTTP 403 | External service refused Worker request. |
| `torrent9` | HTTP 403 | External service refused Worker request. |
| `torrentdatabase` | HTTP 403 | External service refused Worker request. |
| `torrentdownloads` | HTTP 403 | External service refused Worker request. |
| `torrentkitty` | HTTP 403 | External service refused Worker request. |
| `uindex` | HTTP 403 | External service refused Worker request. |
| `nyaasi` | HTTP 429 | Rate limited. Automatic repeated requests are not justified. |
| `torrentz` | HTTP 530 | Upstream server/proxy error. |
| `xxxclub` | HTTP 520 | Upstream server/proxy error. |

## Remediation

- Typed error diagnostics, instead of generic timeouts and silent error omission.
- **Open source search** uses exact provider-owned HTTPS query URLs (where available).
- **Search with available indexers** launches a *separate, correctly attributed* search in the independent Knaben/TorrentsCSV/ThePirateBay/Internet Archive sources.
- BTDigg request timeout reduced to 6.5 seconds after independent HTTP 429 evidence.
- No paid CAPTCHA service, no unrestricted proxy, no automatic rate-limit retries.
- All 46 provider implementations remain in the canonical catalogue.

## Reverification

Run the existing `scripts/audit-live-providers.py` only for explicitly approved production deployments. It now records typed `code` and whether a direct search recovery URL exists for each error. Update this snapshot after a real comparative audit; do not treat successful CI selector tests as live provider availability.
