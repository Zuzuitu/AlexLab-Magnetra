# Magnetra Companion Binding — Owner-Authorized One-Shot Release, 23 Oct 2026

The owner explicitly requested the real preparation and publication of the Magnetra → Flud Remote fix after confirming both Workers appear in the same Cloudflare dashboard account.

Reviewed implementation: PR #141, merged as `bd01227d97fb40a5a244e3055113934ac7ae2518`. All six required PR checks passed.

One-time release authorization: `[magnetra-companion-binding-publish-20261023]`.

The unique workflow may change ONLY `alexlab-magnetra` Worker traffic after all guards pass. It must:
- Fail closed unless the actual immutable production split is exactly a088@100% and 056d@0%.
- Verify both worker names in one Cloudflare account and preserve existing ASSETS, BTDIGG_GATEWAY_TOKEN and MAGNETRA_GATEWAY_TOKEN binding identities.
- Upload a new immutable version with FLUD_RELAY service binding and preserve existing secret bindings.
- Stage exactly 0% and verify unchanged reviewed assets, all 46 API source identities, and a real internal status call returning 401 for **fake** test credentials; it must never send magnets or use real user tokens.
- Promote 5% and then 100% only after each guard passes; keep the old immutable production version for rollback.
- Refuse concurrent/unknown deployments, do not modify other Workers, Shield, Rock64, DNS or any credential.
- Record actual release outcome from action logs and Cloudflare metadata; file creation itself does not prove publication.

No automatic retry or bypass of a failed guard is authorized.
