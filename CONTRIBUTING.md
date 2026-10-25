# Contributing to AlexLab Magnetra

Thanks for your interest in Magnetra. This repository is the public, MIT-licensed
AlexLab adaptation of [TorrentSearch](https://github.com/prajwalch/TorrentSearch).
The original project's contributors retain credit for their work; see the Git
history and [LICENSE](LICENSE). Changes to the upstream Android implementation
should remain easy to review and reconcile.

## Before proposing a change

1. Read [AGENTS.md](AGENTS.md) in full. It is the repository's contributor
   contract, including the required order of technical-memory review.
2. Read the canonical [project state](docs/PROJECT_STATE.md) and
   [invariants](config/project-invariants.json). The
   [handoff](docs/NEXT_CHAT_HANDOFF.md) is supplementary historical context.
3. Check the current `main` source and open pull requests; conversation
   summaries and old checkpoints are not authoritative.
4. Limit each pull request to one testable behavior or maintenance concern.

The Android application lives in `app/`, the installed/browser PWA in `web/`,
and the Cloudflare Worker/provider adapters in `worker/`. Do not quietly remove
or relabel any of the 46 provider IDs. Distinguish an implemented adapter from
an upstream source confirmed available in a dated test.

## Validation

Use the checks appropriate to the changed files. From the repository root:

```sh
python3 scripts/check-project-invariants.py
node --check web/app.js
node --test worker/test/*.test.mjs
```

The project additionally verifies selectors in the Cloudflare workerd runtime,
Android builds and production smoke tests through GitHub Actions. A new
provider or security fix needs targeted regression tests and no weakening of
existing checks merely to make the CI green.

Pull requests targeting `main` must pass all five repository-required checks:

- `invariants`
- `pwa-test`
- `exposure-audit`
- `debug-build`
- `staging-build`

Keep pull requests reviewable and resolve review conversations. Do not bypass
the active `main` ruleset, force-push it, or directly change it for routine work.

## Deployments and security

Merging source code is **not** approval to deploy. Production releases follow
the separately authorized, guarded, manual Cloudflare workflow with explicit
candidate verification and rollback. Do not include activation markers,
`[deploy-pwa]`, or one-shot release event updates in unrelated changes.
Never change deployment routing, signing identity, payment tier or credentials
as a side effect of a code cleanup.

Do not publish API tokens, Flud pairing links, device identifiers, private
addresses, signing files, Cloudflare credentials, real environment files,
passwords, or identifying diagnostics. Use only synthetic values in tests.
Report a suspected exposed credential privately to the repository owner;
do not post its value in a public PR or Actions log. Treat historical exposure
as requiring credential rotation, not merely a Git history edit.

## Maintenance and technical memory

Protect `AGENTS.md`, `docs/PROJECT_STATE.md`, `config/project-invariants.json`,
and the technical handoff. When a verified technical decision changes, update
the implementation, corresponding invariants, test guards, and canonical
checkpoint together as required by AGENTS.md. Historical deployment evidence
must never be rewritten as if it described current live traffic.

Remove dated one-shot workflows only when they are no longer used by the
current deployment or rollback path, referenced guards, or an open PR.
Retain reusable diagnostic scripts and their offline tests until their need is
separately evaluated. A cleaned public working tree does not imply the old
commits or GitHub Actions history have been erased.

## Submitting

Use a topic branch, a descriptive pull request title and a concise summary of
what changed, how it was tested, deployment impact, and rollback considerations
where relevant. No test, deployment, signing, or infrastructure action should
require secrets in a PR description.
