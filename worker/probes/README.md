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


## iPhone / Safari workaround: Cloudflare native Git connection (no code paste)

Owner created `magnetra-1042-probe` through Cloudflare Dashboard, but its
Monaco editor on iOS cannot read the clipboard ("Unable to read from the
browser's clipboard"). Do not require the owner to manually type/paste this
script, and do not attach the PRODUCTION Magnetra Worker to this source.

This directory now includes a strictly scoped `wrangler.jsonc`:
- Worker name: `magnetra-1042-probe` (matches TEMPORARY existing Worker).
- Entry point: `tunnel-1042-probe.mjs`, fixed unauth `/healthz` probe.
- Custom domain: `magnetra-probe.alexlab.media`, only if not already used.
- `workers_dev=false`, no asset bundle, secret, binding, cron, variable or
  production route.

After PR review and green CI merge, owner may open Cloudflare
**Workers & Pages → magnetra-1042-probe → Settings → Builds → Connect**
and explicitly authorize Cloudflare's Git integration on **only** GitHub
`Zuzuitu/AlexLab-Magnetra`, branch `main`, root directory
`worker/probes` (NOT `/` or `worker`). Choose deployment command
`npx wrangler deploy` if required; the Wrangler config for that root
determines the script name and single temporary custom domain.
No manual editor/paste necessary. Check build logs and the resulting
Custom Domain; Git connections may need one new push to trigger a build.
Do not stage meaningless dummy production changes just to trigger builds.

This is an account-scoped Git access action: the owner must approve any
Cloudflare-GitHub authorization explicitly. On screen, halt if asked to
select another Worker or repo, if Cloudflare requests paid-plan upgrade, or
if `magnetra-probe.alexlab.media` is already occupied.

After the ONE real same-zone `/probe` test, disconnect Git Builds in
**Settings → Builds → Disconnect** and remove temporary Worker/domain
via the Dashboard, checking that the existing BTDigg and Magnetra routes,
production `index.alexlab.media` and all 46 indexers remain untouched.


## 2026-10-16 — Temporary Git Builds actually connected on iPhone; first build pending

The owner supplied Cloudflare Dashboard screenshots confirming that the **existing
temporary Worker** `magnetra-1042-probe` is now Git-connected to
`Zuzuitu/AlexLab-Magnetra`, production branch `main`, Root directory
`worker/probes`, deploy command `npx wrangler deploy` and no build command
or build environment variables/secrets. Its Settings → Builds page explicitly
says **"You can now push a commit to your Git repository to start your first
build."** Its preview builds were disabled before connecting. This records
the first-connection checkpoint, NOT a successful deployment or 1042 result.

This small **probe-directory** checkpoint change, after protected PR review,
successful CI, and merge to `main`, is the owner-authorized first Git push
for Cloudflare Builds to observe. Inspect the resulting Cloudflare Build status
and logs; success must be confirmed, never inferred from the GitHub merge.
An existing selected build API token had display name
`calcidatum-build-token`: the label alone does not prove permission scope;
DO NOT rotate or broaden existing project credentials without checking an
actual failed build. In all cases do not change the protected production
Worker, its authentication secret, the shared tunnel, or the 46 providers.

Once the **temporary** Build succeeds and the temporary Custom Domain exists,
a single request to `https://magnetra-probe.alexlab.media/probe` should
report the redacted probe outcome. Disconnect Builds and delete ONLY the
temporary Worker / temporary Custom Domain after the test.
