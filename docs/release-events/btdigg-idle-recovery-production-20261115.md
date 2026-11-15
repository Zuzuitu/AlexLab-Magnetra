# BTDigg idle-tab recovery — Cloudflare production activation

Date: 2026-11-15
Scope: BTDigg-only behavioral change in existing Magnetra PWA/Worker.

Owner authorization: "Activeaza". Verified private Rock64 readouts:
- BTDIGG_18896=NEW_PRIVATE_SCHEMA_HEALTHY
- BTDIGG_8796=NEW_GATEWAY_HEALTHY
- Chromium initially blank_after_boot, not source-verified

Reviewed merged change sets:
- #282: 30-second owner-invoked fresh-tab recovery
- #283: a stale page already older than 30 seconds permits the FIRST PWA search immediately
- #284: Rock64 owner-run activation with private authenticated health
- #285: deploy workflow's scoped BTDigg read-only JS check, no 46-source search audit

Activation mechanism:
- Squash merge THIS reviewed release PR into protected main with commit subject
  `[deploy-pwa] btdigg-idle-recovery-20261115`.
- Existing GitHub workflow deploy-pwa.yml will deploy Cloudflare Worker+PWA only on
  this explicitly approved marker, after offline tests and Wrangler dry-run.
- Postdeploy: public health/manifest smoke plus GET-only /app.js content check.
  No automatic live BTDigg query, no TPB scan, no CAPTCHA automation.
- A live owner PWA query with verified source title/magnet pairs remains the
  acceptance test. Do not claim source has recovered based on asset deployment.
