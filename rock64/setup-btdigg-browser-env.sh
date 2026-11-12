#!/usr/bin/env bash
# Owner-invoked, isolated Python dependency setup for the BTDigg visual test.
# Default --check is read-only. --install never runs Chromium or queries BTDigg.
set -Eeuo pipefail
umask 077

PLAYWRIGHT_VERSION=1.65.1
VENV_BASE="$HOME/.venvs"
VENV="$VENV_BASE/magnetra-browser"
MODE="${1:---check}"
if [[ $# -gt 1 || "$MODE" != --check && "$MODE" != --install ]]; then
  printf 'Usage: bash rock64/setup-btdigg-browser-env.sh [--check|--install]\n' >&2
  exit 2
fi

fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
[[ -n "${HOME:-}" && "$HOME" == /* ]] || fail 'HOME must be an absolute directory.'
[[ -d "$HOME" && ! -L "$HOME" ]] || fail 'HOME must be a real directory.'
[[ ! -L "$VENV_BASE" && ! -L "$VENV" ]] || fail 'Refusing symlinked Python environment path.'
command -v python3 >/dev/null 2>&1 || fail 'python3 is unavailable.'
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' ||
  fail 'Python >= 3.10 required.'

ready() {
  [[ -x "$VENV/bin/python" ]] || return 1
  "$VENV/bin/python" -c \
    "from importlib.metadata import version; assert version('playwright') == '$PLAYWRIGHT_VERSION'; import playwright.sync_api" \
    >/dev/null 2>&1
}

if ready; then
  printf 'PLAYWRIGHT_ENV=READY VERSION=%s PATH=%s\n' "$PLAYWRIGHT_VERSION" "$VENV"
  exit 0
fi

if [[ "$MODE" == --check ]]; then
  printf 'PLAYWRIGHT_ENV=NOT_READY VERSION=%s (read-only check)\n' "$PLAYWRIGHT_VERSION"
  printf 'Next: bash rock64/setup-btdigg-browser-env.sh --install\n'
  exit 2
fi

[[ "$(id -u)" != 0 ]] || fail 'Install as unprivileged runner, never root.'
[[ "$(uname -s)" == Linux && "$(uname -m)" == aarch64 ]] ||
  fail 'This installer is restricted to the Rock64 Linux ARM64 host.'
[[ -x /usr/bin/chromium ]] || fail 'Install Debian chromium separately before continuing.'
[[ ! -e "$VENV" ]] ||
  fail 'Existing incomplete/different venv found; inspect manually, no overwrite.'
[[ ! -e "$VENV_BASE" || -d "$VENV_BASE" ]] || fail 'Invalid venv parent.'

FREE_KIB="$(df -Pk "$HOME" | awk 'NR==2 {print $4}')"
[[ "$FREE_KIB" =~ ^[0-9]+$ && "$FREE_KIB" -ge 524288 ]] ||
  fail 'At least 512 MiB disk space required for isolated dependency installation.'
if [[ ! -d "$VENV_BASE" ]]; then
  mkdir -m 700 -- "$VENV_BASE"
fi

# Deliberately no sudo, no system package changes and no playwright browser download.
python3 -m venv "$VENV" ||
  fail 'Could not create isolated venv (check Debian python3-venv).'
"$VENV/bin/python" -m pip --isolated install \
  --disable-pip-version-check --no-input --only-binary=:all: \
  --index-url https://pypi.org/simple \
  "playwright==$PLAYWRIGHT_VERSION" ||
  fail 'Playwright package install failed. Inspect this venv before any retry.'
ready || fail 'Installed package failed read-only import/version validation.'
printf 'PLAYWRIGHT_ENV=READY VERSION=%s (no source requests, no browser download)\n' "$PLAYWRIGHT_VERSION"
