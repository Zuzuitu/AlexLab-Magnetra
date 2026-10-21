# AlexLab Magnetra — owner-requested isolated TheRarBg magnet repair

Date: 2026-10-21. The user reported an iPhone PWA result TheRarBg with "Obține magnet" returning HTTP 502, and clarified that this failure is not BTDigg.

Owner's standing instruction on this project is to fix deployed Magnetra bugs safely and independently. PR #123 merged the isolated, source-owned TheRarBg resolver fallback and Romanian/Italian error message with 4/4 CI PASS. PR #124 merged a guarded rollout workflow with 4/4 CI PASS.

This single document is the **unique GitHub Actions activation path**, and a squash commit with marker `[magnetra-therarbag-magnet-publish-20261021]` is required. It changes no runtime code.

Preflight requires the verified immutable split `60112a3d-b478-4071-b087-ab793fbdfd60@100%` / `6dadc612-9660-4195-aeed-cdb658b22cf8@0%`, old production app.js SHA `44f1eac85e8550a7`, the existing three binding name/types, custom Worker route/assets, 46 unchanged source identities and unchanged Flud/Rock64 infrastructure.

Stage the new version at 0%, verify exact HTML with the bounded official Cloudflare beacon guard, app.js/styles.css/i18n.js content hashes, all 46 API IDs and binding types; canary 5%, then 100%. Retain old version at 0% for rollback, and refuse to rewrite unknown/concurrent traffic distributions.

Do not claim the individual iPhone TheRarBg link is fixed merely because release completes: an actual upstream HTTP 502 is still possible and browser acceptance remains separate.
