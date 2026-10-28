# BTDigg — authorized integration path (28 October 2026)

**Status: investigation only. No API credentials, spec, authorized API response or provider permission obtained. No production change.**

## Physical evidence

The project owner displayed the authentic BTDigg search page in Safari on iPhone, showing one exact release matching:
`The.Dog.Stars.2026.1080p.10bit.WEBRip.6CH.x265.HEVC-PSA`, approximately **1.73 GB**.
This proves BTDigg's indexed result is available from **that iPhone browsing session** only. The browser displays a VPN indicator. Do **not** assume the protected Rock64 server, Cloudflare Worker or the browser share the same IP, cookies, network access or anti-bot status. Do not store screenshots containing private browser state.

Redacted physical Rock64 journald observations: `magnetra-btdigg.service` active; one `btdigg_upstream_timing` event ended `http_429` at 1132 ms, another `tcp_timeout` at 3007 ms. The gateway currently performs one fixed-origin IPv4 TLS search with bounds and source-specific pacing, not a published JSON API. A server-side 429 and a failed TCP connection cannot be corrected by a different HTML selector or by falsely reporting zero index results.

## External research (not permission, contract or guarantee)

- The SearXNG engine for BTDigg explicitly states `official_api_documentation: {url: "https://btdig.com/contacts", comment: "on demand"}`, `use_official_api: False` and `results: HTML`. Its browser HTML search `/search?q=...` is **not** evidence of a documented public JSON endpoint: https://git.jordan.im/searxng/file/searx/engines/btdigg.py.html
- FrostWire maintainers independently note BTDigg HTML is restricted by Cloudflare and name **requesting the provider's API** as an option: https://github.com/frostwire/frostwire/issues/1064
- 429 reports exist independently: https://github.com/galaris/BTDigg-qBittorrent-plugin/issues/2
- Provider contact route: https://btdig.com/contacts (may itself return 429 from automated clients). The GitHub verified BTDigg organization lists a public address `github@btdig.com` at https://github.com/btdig. Confirm recipients independently before contacting.
- No outreach was sent; no pricing or API limits confirmed. The owner's rule forbids committing to paid external services without explicit consent.

## Integration gates (do not guess endpoint)

1. Obtain written API endpoint URL, official documentation, authorization terms, keys/token scheme, supported query syntax, response schemas, quotas/cost and permitted client applications from BTDigg. Stop if operator does not grant access. A guessed hidden API endpoint or anti-bot challenge bypass is NOT a valid shortcut.
2. Prove one authorized API search against non-sensitive test terms; validate provider-origin response and permission; never copy VPN cookies, challenge tokens or private browser sessions from iPhone to Rock64/Cloudflare.
3. Only then implement a fixed approved-origin, opt-in server-side adapter, with **no client-selected URL** and secrets encrypted in host/Worker configuration. Never place API token in PWA HTML/JS, URL parameters, logs, or public GitHub.
4. Execute one bounded request per chosen provider/search; cache only authentic successful results with source labels; preserve true errors and authorization denials. Do not automatically retry a source on 429. Respect any published `Retry-After` and agreed quotas.
5. Preserve exact-release intent: upstream may search `The Dog Stars 2026` once, but only return rows whose **actual source title** contains all user-requested terms `1080p`, `10bit`, `WEBRip`, `6CH`, `x265`, `HEVC`, `PSA` and year. Different groups/qualities are not equivalent. Do not invent BTIH/magnets or bypass title provenance.
6. Offline mocked contract and security tests; full PWA + Android CI; protected branch/PR; new owner-authorized, immutable Cloudflare release with fresh split/binding preflight, 0%/5%/100% validation and rollback. Physical iPhone + Flud acceptance is required separately.

## No-go actions and current release state

Do not increase concurrency against BTDigg, implement rotating proxy/VPN or browser anti-bot circumvention, reintroduce old manual BTDigg import paths, change the Rock64 token/tunnel/router, alter 11 curated visible/35 hidden sources, or claim the existing HTML gateway is a reliable API.

Strict exact-release intent was integrated via PR [#218](https://github.com/Zuzuitu/AlexLab-Magnetra/pull/218) after all five CI suites passed. The short-title upstream search from PR #217 and strict full-release filtering from PR #218 are **code-merged but not deployed**. Production at the last verified guarded run [#40483725991](https://github.com/Zuzuitu/AlexLab-Magnetra/actions/runs/40483725991) remains immutable `b39a0393-bbf8-4ba3-9d32-7c1390aa867f@100%` with `fdffdc78-0bd3-4721-a5b1-11f515c52bd1@0%` previous rollback. A future release must take a fresh live snapshot rather than assume these percentages still hold.

**Acceptance criterion:** BTDigg integration must return a genuine origin-owned exact release from an **authorized** and reliably available API when such a result exists. Green CI alone is not proof of site uptime. If no official API permission is obtainable, disclose that limitation rather than promise a nonexistent source-level fix.
