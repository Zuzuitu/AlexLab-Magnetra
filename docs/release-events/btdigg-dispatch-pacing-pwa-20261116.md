# BTDigg dispatch-anchored PWA spacing — scoped release 2026-11-16

## Owner-reported issue and scope
The owner reproduced an unwanted second full 30-second PWA delay after a successful BTDigg search that had already taken more than 30 seconds. PR #299 (f8200b6f7055d66914e21327922f58dd334f5f52) fixed the cause: the client now stamps the 30-second gate only at an actual BTDigg API request **dispatch**, and at the one separately guarded follow-up request if actually sent; completion, timeout, CAPTCHA, cancellation and error handling do not re-arm it. PR #300 (3b83d2bec9be4a38b525934dc719d541da7cb999) added the scoped release and GET-only production verification contract.

This is a PWA/Worker bundle release **only**, not an attempt to reconfigure Rock64 or the BTDigg source. Preserve the existing source-managed HTTP 429/Retry-After gates and the one-shot visible-refusal safety rules.

## Exact authorization marker
Squash merge this release document PR only after CI, with commit subject EXACTLY:

[deploy-pwa] btdigg-dispatch-pacing-20261116

That exact prefix is required by `.github/workflows/deploy-pwa.yml` to activate the Cloudflare deployment from a push to main. A normal PR commit does not deploy. Do not use generic `workflow_dispatch` for this rollout: its ordinary path can run the broad provider audit.

## CI and rollout gates
1. Before merge, review the branch diff: release documentation only, with unchanged `web/app.js`, Worker provider adapters, secrets, routes, tokens and Rock64 services.
2. Run the existing project invariants, JS provider and PWA contracts, offline BTDigg pacing smoke, and Wrangler dry-run in the CI path. Do not send real BTDigg or TPB searches.
3. Only if tests pass and main has not changed unexpectedly, use the exact marker as the squash **commit title**.
4. The push-deploy job must complete successfully, including existing read-only production API/manifest smoke and the scoped GET-only checks for `/`, `/app.js`, private CAPTCHA viewer CSP, one-shot retry UI, and dispatch-anchored pacing. For this marker the 46-provider search audit MUST be skipped.
5. Record the resulting release commit SHA, GitHub Actions run ID/conclusion and static production asset PASS separately. A green PR is **not** proof of a successful Cloudflare rollout.

## Behavior acceptance — offline and owner iPhone
- Success after 45 seconds => no additional local 30-second PWA wait before a distinct user search (assuming no authentic source cooldown).
- Success after 9 seconds => 21 seconds of the original dispatch-anchored gap remain.
- CAPTCHA after 65 seconds or cancellation/error => no new full 30-second local delay.
- A genuine HTTP 429 remains separate from local pacing and honors source/Worker controls and Retry-After.
- A visible refusal alone can cause one guarded same-query delayed follow-up after 30 seconds within the original user search, but not on CAPTCHA, actual HTTP 429, cancellation or hidden app.
- Only the owner can confirm a post-release iPhone interaction. Do not fabricate actual source availability, magnets, or browser-state.

## Operational isolation and rollback
This deployment must not restart Chromium 18896, gateway 8796, noVNC 6088/6089, Tailscale 8444/443, Plex, NexaCore, NexaPanel or Flud. No BTDigg live searches from CI. Check existing Cloudflare release metadata before rollback; rollback requires a separate deliberate owner-approved release, not an improvised secret or route change.

Do not mark the release complete until the actual Cloudflare push job and deployed static assets report PASS.
