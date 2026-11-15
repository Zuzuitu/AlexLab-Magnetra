# PWA release: BTDigg one guarded new-tab recovery per owner search

Date: 2026-11-15. Scope: the owner-requested PWA-only correction from
source PR #296 and release-guard PR #297.

Owner reported live iPhone in-PWA noVNC showing BTDigg HTTP-body
Too Many Requests, with no CAPTCHA to solve. Existing PWA erroneously
presented 'Am verificat - Reîncearcă' and the new-tab recovery required
another explicit user search after the existing 30-second guarded window.

Release behavior:
- A single owner-initiated BTDigg PWA search may send ONE delayed
  same-query BTDigg-only follow-up if it sees the distinct
  BTDIGG_VISIBLE_REFUSAL error (a page-level refusal without an observed
  origin HTTP 429). The PWA waits 30 seconds from the refusal.
- The already-running private Chromium 18896 backend independently
  decides whether it is safe to open exactly one canonical BTDigg tab.
- A second refusal, genuine origin HTTP 429, CAPTCHA, transport error,
  timeout, cancellation or hidden PWA cannot trigger further automatic
  requests. Existing source cooldowns and verified source guards remain.
- The rate-limit dialog offers Chromium inspection only, not a false
  CAPTCHA confirmation. A genuine CAPTCHA still requires manual owner
  interaction through the existing private HTTPS/Tailscale noVNC viewer.

Release and smoke:
- Production deploy uses the exact trigger subject
  [deploy-pwa] btdigg-visible-refusal-one-shot-20261115
- GET-only assertions verify /, /app.js, /i18n.js, /styles.css and
  private iframe CSP without sending any provider search.
- Do not perform the broad 46-provider live audit for this scoped UI
  release. Its normal path remains unchanged for other deployments.
- No Rock64 Chromium restart, gateway upgrade, tailnet change, Plex,
  NexaCore or Flud mutation. Live result/new-tab behavior must still be
  confirmed by the owner after this deploy.
