# BTDigg browser-driven search: same Chromium tab

## Live symptom / diagnosis

On 13 November 2026, the owner's manual noVNC Chromium searched BTDigg successfully from the source's visible search box. Magnetra PWA successfully replayed pre-existing verified DOM rows for The Dog Stars 2026; its first different search returned 503, latched the legacy browser, and was not able to trigger a second navigation. The owner then manually searched 1080p successfully on the same browser. The existing Playwright code used context.new_page() and candidate.goto() for different queries, rather than operating the visible BTDigg search form. The exact HTTP/DOM cause of its 503 remains unknown (legacy browser lacks new telemetry).

## Source-only change

A new query in btdigg_browser_backend.py is now handled on the **already verified, existing Chromium tab**:
- Read source-owned page URL and genuine same-row result/magnet DOM; reuse an exact already-visible query without any new upstream request.
- Require no prior navigation latch, no visible source refusal, and a still-verified page.
- Locate exactly one search field matching input[name="q"]; fill the new query and press Enter once inside an 8-second Playwright expect_navigation. This uses the same browser session, cookies and form; no new page, direct goto, imported cookies, IP modification or CAPTCHA handling.
- Require HTTP 200, exact canonical BTDigg result URL and actual result+magnet markup, otherwise latch and stop. Preserve real source 429 vs 503, plus sanitized reason codes. Do not automatically retry or repeatedly refresh.
- Keep 18896 authenticated and bound to loopback, with no CDP/debugging listener; production 8796 and Cloudflare PWA contracts remain unchanged.

There is **no claim of live success yet**. Mocked browser controls and CI tests establish only that the new source code executes the intended path.

## Operations

Git pull alone does not replace the running Chromium process. The old 18896 process holds its in-memory 503 latch, so the browser session will need a **separate owner-approved graceful restart** using the same private persistent profile, retaining cookies (subject to Chromium shutdown and profile integrity). Never delete ~/.local/state/magnetra-btdigg-browser/profile, reset cookies, change network identity or repeat blocked searches.

First confirm the updated source/CI and existing tmux session. Then use owner-controlled shutdown/restart and observe /v1/browser-state to ensure a genuine selected tab is verified. If not verified, manually open one BTDigg search via noVNC; do not automatically navigate until verified. Once the browser is ready, issue **one** new PWA search and inspect its result. Health 200 or a cached hit does not prove new search succeeded.

The optional 503 manual-replay-only bypass is not part of this change: the user's goal is a true new search, not reading a tab they must manually prepare. Existing CFFI 50 + Chromium 60 override and CFFI rollback backup are preserved.
