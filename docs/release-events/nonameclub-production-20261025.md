# NoNameClub exact owner iPhone source fix — OWNER APPROVED, activation gated

Date: 25 October 2026, Europe/Rome.

The owner has confirmed the existing 0Magnet iPhone fix works and reported
a distinct NoNameClub problem for
https://nnmclub.to/forum/viewtopic.php?t=1896364.

Evidence: live exact original resolver #40140578589 PASS; live NoNameClub
PWA search card #40141421228 has exact original details, bad auxiliary
magnetSource due to URL(undefined) conversion, and original details
resolves valid magnet. PR #178 fixes allowedExternal absent URL in
worker/src/legacy-adapters.mjs and gives nonameclub details-first in
web/app.js. Main code merged at ea303cb1c4c5e9881953e0652623e4414cbf76f0.
All four CI passed, generic PWA deployment SKIPPED.

Owner approval was received in the new chat by the owner resuming the 25 October
full engineering handoff and requesting continuation through the guarded release.
This is the separate reviewed activation record; it must not deploy from the PR.
Only a reviewed squash merge with the unique release marker can trigger the
one-shot main-branch workflow after all required CI and offline tests PASS. Preserve known-good 0Magnet active
763defbe-38aa-4299-acf1-1639a59e7be6@100 and prior TheRarBg
916d0671-b9c5-432d-8724-aed27bc22c4f@0 (last observed, verify live
before mutation). Guard four Cloudflare binding types, account and
source checks, 46 providers, exact NoNameClub card no bogus auxiliary,
source detail magnet valid, and frontend asset SHA. Immutable 0,5,100
canary and fail-safe previous 0Magnet version rollback only for known
traffic states. No modifications to Flud, Shield, Rock64, DNS, tunnels,
log credentials, paid APIs, torrent downloads, original site login.
Physical Safari iPhone acceptance remains required after release.

## Owner approval and release control — 25 October 2026

- Approved scope: publish only the existing NoNameClub `allowedExternal` missing optional URL guard and `ensureMagnet` original `details` preference from merged code PR #178. No new scraper, provider changes or browser redesign.
- Preparation is now merged from clean/reconciled PR #181 (commit `046e1a934e1f09cebf6f5221b0fd32b4e31e280c`), after all four canonical CI and offline regression gates PASS. Superseded PR #179 had conflicts against checkpoint PR #180 and was not force-merged.
- At preparation merge, `Deploy Magnetra PWA` and NoNameClub guarded-release both SKIPPED, without activation marker.
- Production baseline `763defbe-38aa-4299-acf1-1639a59e7be6@100%` and historical rollback `916d0671-b9c5-432d-8724-aed27bc22c4f@0%` are LAST OBSERVED only; the guarded workflow MUST re-check actual live Cloudflare split, account/origin, four bindings and published asset before any mutation. If changed, stop without writing.
- The activation is authorized only on a reviewed main push with the unique marker in the squash commit and this event file in its changed paths. Do not place the marker in a PR head commit and do not run consumed release workflows.
- Allowed production sequence: immutable candidate upload (keep vars) → 0% audit → 5% canary → 100% verification; safe rollback to previous known-good 0Magnet when candidate state is identified and failure occurs. Never auto-correct unknown state.
- Test metadata only on the exact user NoNameClub original `https://nnmclub.to/forum/viewtopic.php?t=1896364` and `Lupin` card. No `.torrent` download, no magnet/BTIH disclosure, no Flud/Shield transfer or authentication bypass.
- After server-side full release, owner physical iPhone/Safari verification remains **pending**. Cyrillic charset issue is a separate follow-up.
