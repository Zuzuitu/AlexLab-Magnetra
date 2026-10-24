# AlexLab Magnetra — one-shot TheRarBg iPhone diagnostic, VERSION ONLY
Date: 2026-10-24 (Europe/Rome)

Owner asked to begin the controlled diagnostic staging after all four PR #154
checks passed. PR #154 code is merged in main as 86e84ffccc59e02e5f0606bcb37b3bc8b9fde752;
its automatic Deploy Magnetra PWA job was correctly SKIPPED.

This is a unique release-event file to activate a reviewed, one-shot, gated
Cloudflare WORKER VERSION UPLOAD when the **merge commit message itself**
contains the exact marker:

[magnetra-therarbag-iphone-stage-only-20261024]

Scope:
- Require unchanged 36019925-2308-4f99-8223-13854012d372 at 100% and
  c201cbf9-2080-4a5b-9e40-723a8714d94c at 0% before upload.
- Verify same Cloudflare account, expected Worker name/domain/assets/services,
  and all four binding name/type pairs for both currently deployed versions.
- Check invariants, Node/provider tests, offline release tests and Wrangler dry-run.
- Upload one **immutable version only** with --keep-vars and both required
  secret NAMES. Verify all four binding name/type pairs on the uploaded candidate.
- Recheck the unchanged deployment ID and percentages after upload.
- No `wrangler deploy`, no `versions deploy`, no traffic shift, no Cloudflare
  DNS/Tunnel/Rock64/Shield/Flud mutation, no .torrent or magnet submission, no paid services.
- This does NOT put the diagnostic in an addressable 0% deployment slot and
  does NOT make the diagnostic visible to an ordinary iPhone browser.
  Exposing it later needs a separate owner-approved, exact-baseline 0% slot
  and verified version-override E2E before any canary or production change.
- If live Cloudflare metadata disagrees with these historical version IDs,
  STOP without upload. Never infer the split merely from the checkpoint.

Activation is not permitted by merely creating this file on a feature branch.
The one-shot workflow additionally requires reviewed main and its unique
merge-marker gate. This event must never contain the general PWA-deploy marker.
