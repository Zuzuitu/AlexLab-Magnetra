# Magnetra Companion immutable version diagnostics (23 Oct 2026)

Owner's real Rock64 synthetic status call with a version override returned HTTP 502. This does not prove the zero-percent candidate was invoked, since Cloudflare can silently fall back to weighted traffic when an override is not applied.

Authorize ONLY the standalone synthetic-only staging diagnostic in merged PR #145 (commit 6e90344a5147ff0529764ae70f031993c8108d16), after all four CI checks passed.

This activation may upload a new immutable Magnetra version and replace the existing ac71 0% staged slot, but MUST keep the existing a088 version serving **100%** continuously. It may never promote to 5% or 100%, send a magnet, use real device tokens, rotate secrets, or change another Cloudflare Worker, Shield, Rock64, DNS, BTDigg, or YouTube.

The probe uses fixed fake credentials and a header marker only emitted by the new version. If a GitHub-hosted request is blocked or returns the old Worker, the diagnostic fails closed without changing 100% production traffic. The uploaded version ID is to be recorded and independently tested from Rock64 before any further rollout.

## Second and final zero-only stage after confirmed TypeError diagnosis

Owner submitted the decisive real staging response on Rock64: `HTTP 502` with `x-alexlab-companion-probe: binding-request-type_error`, proving `47bbcec3-a4fc-4830-aa5e-33c55356a30b` executed and its `new Request(...)` failed before the relay was called. Workerd only accepts `redirect: manual` or `follow`; the previous `redirect: error` was incompatible. Reviewed fix [PR #146](https://github.com/Zuzuitu/AlexLab-Magnetra/pull/146) merged as `01be9341940b2c0c70242084e6dea0c10d211571`, preserving redirect confidentiality by refusing 300–399 responses explicitly.

Authorize exactly one zero-traffic immutable fixed-candidate upload, conditional on `a088@100 / 47bb@0` and the four correct bindings. Verify new version with real Cloudflare stage override and **synthetic credentials only**, print immutable candidate ID, then validate unchanged assets and catalog if egress permits. Production stays old version 100% throughout; no canary/full promotion, real token, magnet, DNS, Flud/Shield or Rock64 changes. Fail closed on preflight mismatch or failed probe. A later separate owner-approved rollout may only occur after a verified fake-token HTTP 401 and a checked rollback plan.
