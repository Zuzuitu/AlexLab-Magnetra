# Release: BTDigg private in-PWA human verification — 2026-11-15

Owner request: recognize recurring BTDigg CAPTCHA and offer the existing
persistent Rock64 Chromium noVNC session *inside* Magnetra on iPhone.
Source PR #291 and scoped Cloudflare release-gate PR #292 have passed CI.

Release commit subject, only when this PR is squash-merged after checks:
[deploy-pwa] btdigg-private-verification-20261115

Scope: deploy the existing Cloudflare Worker and public PWA bundle.
No Rock64 services, Tailscale Serve port, noVNC, Plex, NexaCore or Flud
are changed by Cloudflare deploy. Postdeploy read-only GET /, GET /app.js
plus CSP verification is required. The generic 46-indexer search audit
is omitted for this narrowly-scoped BTDigg UI deployment, as it would
send unnecessary live provider requests. No source searches are run.

Result expected after separate Rock64 owner action:
- private gateway 8796 reports sanitized CAPTCHA required as 428;
- Cloudflare reports BTDIGG_CAPTCHA_REQUIRED;
- PWA displays 'Verifică BTDigg în Magnetra' when verification is needed;
- owner clicks to embed tailnet-only HTTPS noVNC 8444 via their local
  device's Tailscale connection, enters password in VNC and solves
  the source challenge manually, then requests a single retry;
- no CAPTCHA solver, no source reCAPTCHA bypass, no background polling.

Activation steps are documented in docs/BTDIGG-PWA-HUMAN-VERIFICATION.md.
No claim of completed iPhone iframe verification until the owner physically
configures the private HTTPS Serve endpoint and tests it.
