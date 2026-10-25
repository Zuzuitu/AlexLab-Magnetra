# Magnetra iOS Home Screen safe-area — release preparation (NO TRAFFIC CHANGE)

25 October 2026 · Europe/Rome.

Owner supplied screenshot of Home Screen installed PWA with iOS time/battery/status icons overlapping the Magnetra masthead, leaving the upper-right Settings control difficult to tap.

Reviewed UI fix merged from PR #187: standalone-only 60px/safe-area padding, iOS navigator.standalone fallback, minimum 44px Settings/language targets, offline service worker cache v7, UI contract tests. Independent README personalization in the same PR does not affect live Worker behavior.

**PREPARATION ONLY:** this file intentionally contains no activation marker. No Cloudflare changes should be made when the release-preparation PR is merged. Activation requires a NEW separately reviewed `main` commit that modifies this event path and carries the unique one-shot workflow marker.

Exact last-observed production baseline before new writes: owner-approved NoNameClub `24642346-9db0-4cea-a56e-12e30f35569f@100%` and prior 0Magnet `763defbe-38aa-4299-acf1-1639a59e7be6@0%`. These must be verified LIVE with Cloudflare API and immutable binding names/types, account and origin. If any split or bindings differ, fail closed without publishing.

New immutable version upload then 0% candidate asset SHA proof (`/app.js`, `/styles.css`, `/sw.js`), health+catalogue 46, exact source-owned NoNameClub magnet and card; 5% canary; 100% with independently checked public JS/CSS/SW hashes. Previous owner-approved NoNameClub version remains rollback target. Unknown/concurrent states MUST NOT be auto-overwritten.

Scope is UI-only in installed iOS PWA; no search-provider mutations, Flud/Shield commands, tokens, Rock64 commands, tunnel/DNS edits, paid APIs or torrent downloads. Browser Safari normal layout stays unchanged. Physical iPhone Home Screen acceptance only after independently verified new 100% release.
