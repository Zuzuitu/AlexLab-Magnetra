# Isolated Cloudflare Worker → Tunnel / 1042 probe (STAGED ONLY)

**No probe Worker has been deployed.** This is a self-contained, no-secret
Cloudflare Workers script in `tunnel-1042-probe.mjs`, with offline Node tests.
It is **not** imported by the production `worker/src/index.mjs` and cannot
be activated via the existing `worker/wrangler.jsonc` or PWA deployment.

## What it tests

A temporary Worker, **running on the same Cloudflare zone `alexlab.media`**,
makes exactly one `GET` to the fixed URL
`https://magnetra-rock64.alexlab.media/healthz`, with no Authorization
header, redirects disabled, and an eight-second timeout. Its single probe
route is `GET /probe`, with no querystring. It does not accept an input URL.
The output contains only a sanitized result identifier and HTTP status:
- `PASS_UNAUTHENTICATED_401`: Cloudflare Worker-to-new-hostname fetch returned
  the expected 401. This is NOT an authenticated gateway/magnet parity test.
- `CLOUDFLARE_1042`: Cloudflare responded or threw with an error 1042 marker.
- `TIMEOUT`, `TRANSPORT_ERROR`, `UNEXPECTED_REDIRECT`,
  `UNEXPECTED_HTTP`, `ERROR_BODY_UNREADABLE`: do NOT claim success.

Response bodies and private exception messages are never returned or logged;
1042 detection reads at most 8192 bytes of an error response.

## Strict deployment gate

Only after explicit owner approval: choose an unused, temporary
same-zone Custom Domain on `alexlab.media` for an independent test Worker
(and confirm the account's tier/limits), paste the standalone file into that
dedicated Worker, and invoke its `/probe` endpoint **once**. Do not use an
overlapping route or Custom Domain, especially not
`index.alexlab.media`, `magnetra-rock64.alexlab.media`, or BTDigg.
Immediately remove the temporary Worker and test hostname afterward.

A `workers.dev` or `wrangler dev --remote` preview may not reproduce the
same-zone routing restrictions; a passing result there is only a preliminary
signal, not the requested same-zone acceptance. Cloudflare's 1042 error may
also arise from Worker-to-Worker same-zone calls unrelated to the tunnel.

Do NOT:
- add any new tunnel or modify the two existing tunnel Published applications;
- put `MAGNETRA_GATEWAY_TOKEN` or another credential in the probe;
- change the production Worker or `global_fetch_strictly_public` compatibility;
- deploy the PWA or alter the original 46 provider configuration;
- assume 401 success proves authenticated provider results.

The probe source and its tests may be merged into GitHub as **inactive
diagnostic code**. A separate, explicit owner authorization is mandatory
before creating or deploying any Cloudflare Worker/Custom Domain.
