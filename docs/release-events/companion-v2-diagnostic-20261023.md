# Magnetra Companion immutable version diagnostics (23 Oct 2026)

Owner's real Rock64 synthetic status call with a version override returned HTTP 502. This does not prove the zero-percent candidate was invoked, since Cloudflare can silently fall back to weighted traffic when an override is not applied.

Authorize ONLY the standalone synthetic-only staging diagnostic in merged PR #145 (commit 6e90344a5147ff0529764ae70f031993c8108d16), after all four CI checks passed.

This activation may upload a new immutable Magnetra version and replace the existing ac71 0% staged slot, but MUST keep the existing a088 version serving **100%** continuously. It may never promote to 5% or 100%, send a magnet, use real device tokens, rotate secrets, or change another Cloudflare Worker, Shield, Rock64, DNS, BTDigg, or YouTube.

The probe uses fixed fake credentials and a header marker only emitted by the new version. If a GitHub-hosted request is blocked or returns the old Worker, the diagnostic fails closed without changing 100% production traffic. The uploaded version ID is to be recorded and independently tested from Rock64 before any further rollout.
