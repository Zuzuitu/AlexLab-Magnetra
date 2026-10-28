# Magnetra 2026-10-28 — explicit owner online release activation

- Reviewed feature: PR #226 / main commit c724a7f9ee98a325577c1b0a5231acb9dc605f89.
- Guarded release tooling: PR #227 / main commit db6ce9cfea604cf7dd656362f9e9d64f11b01710.
- User explicitly requested an immediate public iPhone test after verified CI.
- Authorized action: one guarded stage 0%, canary 5%, promotion 100% with old Worker retained at 0% and rollback on verified failure.
- GitHub release job must fail closed on unexpected Cloudflare split, missing Flud bindings, wrong reviewed source/assets, failed catalog or concurrent deployment.
- No change to DNS, Rock64, tokens, tunnel, Flud devices or torrent results. Live publication is not claimed until Cloudflare postflight passes.
