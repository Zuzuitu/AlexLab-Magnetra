# One-time staged Magnetra → Flud Remote diagnostic, 23 October 2026

Following owner-authorized publication attempt #39977046464, the new immutable Service Binding candidate (ac71bb51-b681-458b-8f40-980d4621fe62) was staged at 0% but its fake-token status probe failed. Real production remains a088@100 / ac71@0, with rollback 056d still stored.

This commit authorizes **read-only diagnostics only**. It does not authorize a second deploy or automatic retry.

The corresponding workflow must:
- Verify exact staged version split a088@100 / ac71@0.
- Send one GET to the public Flud Remote status route with intentionally fake credentials, then one POST to the 0%-staged Magnetra status route using the Cloudflare version override and the same fake credentials.
- Print only finite HTTP code/category and preserve 100/0 unchanged.
- Never expose real credentials or send a magnet.
