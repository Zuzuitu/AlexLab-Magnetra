# One-time AlexLab Magnetra Flud Companion FIXED immutable promotion — 23 Oct 2026

The owner explicitly requested actual real production publication earlier in this conversation, and independently verified the exact staged candidate from Rock64 at 2026-10-23 16:08:33 UTC:
- Requested 0%-staged immutable candidate: `4e4730a1-3334-4b1a-98da-966f807d5078`.
- Response: `HTTP/2 401`, `x-alexlab-companion-probe: upstream-http-401`, JSON `{"error":"Unauthorized"}` on synthetic fake credentials only. This proves the corrected Worker reached the authorized Flud Remote relay through its new `FLUD_RELAY` Service Binding.
- Reviewed release PR #147 merged as `c7faa72c801e9b1373e31bc087c47d0ae66e7816`; Worker/PWA regressions and canonical invariants passed.
- Owner confirmed both Cloudflare Workers belong to the same account. Do not share or use user Remote token in automated tests.

One-time release authorization: `[magnetra-companion-4e47-publish-20261023]`.

Use only `scripts/promote_companion_fixed_4e47_20261023.py` against exact Cloudflare baseline previous immutable `a088fa41-233d-48d3-bd4c-52be6194fda8` @100 and validated immutable `4e4730a1-3334-4b1a-98da-966f807d5078` @0. First promote old95/new5 with Cloudflare deployment metadata verification; then old0/new100 and confirm exact final metadata, leaving prior immutable version as rollback. Auto-restore previous @100 on a recognized post-write failure; stop on unknown/concurrent changes. No uploads, secret rotations, torrent or magnet sends, DNS, Flud Remote, Shield, YouTube, Rock64, or indexer changes. The real paired Shield status and delivery ACK remain owner acceptance after release.

The production result must be verified from Cloudflare deployment logs, not inferred from this activation commit.
