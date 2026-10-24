# NoNameClub exact owner iPhone source fix — release staged, NOT APPROVED

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

New reviewed gated release needs **separate explicit owner approval**.
Before approval, neither push the unique activation marker nor create a
Cloudflare new version/deployment. Preserve known-good 0Magnet active
763defbe-38aa-4299-acf1-1639a59e7be6@100 and prior TheRarBg
916d0671-b9c5-432d-8724-aed27bc22c4f@0 (last observed, verify live
before mutation). Guard four Cloudflare binding types, account and
source checks, 46 providers, exact NoNameClub card no bogus auxiliary,
source detail magnet valid, and frontend asset SHA. Immutable 0,5,100
canary and fail-safe previous 0Magnet version rollback only for known
traffic states. No modifications to Flud, Shield, Rock64, DNS, tunnels,
log credentials, paid APIs, torrent downloads, original site login.
Physical Safari iPhone acceptance remains required after release.
