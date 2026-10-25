# Magnetra BTDigg + ThePirateBay: manually authorized release

Date: 2026-10-25. Source patch is already merged in main at `065e09989beb6a9072a68ba9ff7889692b127a7a`; NOT YET PRODUCTION DEPLOYED.

The PR for this document only installs the safe, explicit workflow, which is inert on ordinary pushes and has an owner-confirmation input. Do not dispatch until PR checks pass and the workflow is merged to main.

Workflow: `.github/workflows/magnetra-btdigg-tpb-guarded-production-20261025.yml`.
Action: `workflow_dispatch` on `main` with explicit `APPROVE_BTDIGG_TPB_GUARDED_RELEASE` selection.
Prerequisites: Cloudflare credentials from existing GitHub Actions secrets. No new paid services or infrastructure changes.

Guarded release checks, in order:
- Reviewed hashes for original 11-visible/35-hidden indexer PWA, 50 per page, service worker v10 and source-specific resilience.
- Exact previously confirmed Cloudflare Worker version distribution `74754dac-1842-47b2-8e6f-92a10731f124@100%`, `8d9c19f4-ca38-428b-888e-757ef578c829@0%`, account binding identities, no unexpected public PWA changes.
- Upload isolated immutable code version with all protected secrets and bindings intact. Verify 5 PWA assets and 46 backend provider identities at candidate 0%.
- Single original-provider positive magnet sample, independently from both BTDigg and ThePirateBay; stale cached results do not prove live availability. Abort before canary if either source fails.
- Owner's exact original NoNameClub page magnet and search card remain protected.
- Deploy 5% then 100%, each bounded by checks; retain previous 7475 release at 0% for rollback. On unsafe change, stop and preserve or restore known prior version. No DNS, Rock64, Flud, token, WAF or other service changes.

If a third-party source is down, a release STOP is correct, not a successful fix. A successful release still requires owner iPhone verification; it cannot guarantee original source uptime.

Manual phone navigation: `github.com/Zuzuitu/AlexLab-Magnetra/actions/workflows/magnetra-btdigg-tpb-guarded-production-20261025.yml`.
