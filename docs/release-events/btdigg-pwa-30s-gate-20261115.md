# BTDigg PWA 30-second client cooldown — release authorization

Date: 2026-11-15
Scope: BTDigg PWA-only localStorage cooldown previously remained at
60 / 120 / 300 seconds, contrary to owner's explicit 30-second preference.

Owner-provided live read-only evidence after 14:05:34 CET:
- Chromium 18896 active, new browser backend
- pwa_tab_recovery_reason=blank_after_boot
- pwa_tab_recovery_ready=true, wait_seconds=0
- pwa_tab_recovery_attempts=0
- Gateway 8796 active

Interpretation: the current browser process has not attempted a new tab.
The longer PWA suppression is confirmed in the source, but whether that
explains the user's most recent test is not yet established.

PR #288 capped BTDigg's LOCAL PWA cooldown at 30 seconds, invalidates
legacy 60-300s records and updates unit + deployed-asset smoke tests.
Server-side Retry-After in the Worker is preserved.

Activation marker:
  [deploy-pwa] btdigg-pwa-30s-gate-20261115

After merging this PR with that exact squash subject, the existing
Cloudflare Worker+PWA workflow must PASS deployment, production HTTPS/API
smoke and deployed JavaScript GET-only checks. The generic 46-provider
live source audit is intentionally skipped for only this scoped marker.

No automatic BTDigg query, CAPTCHA solving, Rock64 restart, TPB source
requests or provider fallback. Acceptance still needs ONE owner PWA search
after the local cooldown, then a READ-ONLY Chromium browser status.
The pwa_tab_recovery_attempts field is the decisive browser-side check.
