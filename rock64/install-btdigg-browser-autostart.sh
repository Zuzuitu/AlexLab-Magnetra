#!/usr/bin/env bash
# Owner-opt-in, user-systemd autostart. Does NOT stop an active tmux browser,
# install packages, query BTDigg, or start the service immediately.
set -Eeuo pipefail
umask 077
usage() {
  echo 'Usage: bash rock64/install-btdigg-browser-autostart.sh --check|--install [--seed-query "prior verified search"]' >&2
  exit 2
}
[[ $# -ge 1 ]] || usage
MODE="$1"; shift
[[ "$MODE" == --check || "$MODE" == --install ]] || usage
SEED=""
if [[ $# -eq 2 && "$1" == --seed-query && "$MODE" == --install ]]; then
  SEED="$2"
elif [[ $# -ne 0 ]]; then
  usage
fi
fail() { printf 'STOP: %s\n' "$*" >&2; exit 1; }
[[ "$(id -u)" != 0 ]] || fail 'Run as the unprivileged Rock64 runner.'
[[ "$HOME" == /* && -d "$HOME" && ! -L "$HOME" ]] || fail 'Invalid HOME.'
command -v systemctl >/dev/null || fail 'systemctl unavailable.'
command -v loginctl >/dev/null || fail 'loginctl unavailable.'

ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"
RUN="$ROOT/rock64/run-btdigg-visual-session.sh"
SEEDER="$ROOT/rock64/btdigg_bootstrap_state.py"
[[ -f "$RUN" && ! -L "$RUN" && -f "$SEEDER" && ! -L "$SEEDER" ]] ||
  fail 'Reviewed project files are unavailable.'
[[ "$ROOT" == "$HOME"/magnetra-cffi-live-20261028 ]] ||
  fail 'Expected existing Rock64 project checkout was not found.'

UNIT_DIR="$HOME/.config/systemd/user"
UNIT="$UNIT_DIR/magnetra-btdigg-browser.service"
STATE_DIR="$HOME/.local/state/magnetra-btdigg-browser"

if [[ "$MODE" == --check ]]; then
  echo 'MODE=CHECK (no writes, browser untouched)'
  if [[ -f "$UNIT" && ! -L "$UNIT" ]]; then
    echo 'UNIT=PRESENT'
  else
    echo 'UNIT=ABSENT'
  fi
  if command -v tmux >/dev/null && tmux has-session -t magnetra-browser 2>/dev/null; then
    echo 'EXISTING_TMUX=ACTIVE (not touched)'
  else
    echo 'EXISTING_TMUX=NOT_OBSERVED'
  fi
  echo 'LINGER='"$(loginctl show-user "$(id -un)" -p Linger --value 2>/dev/null || echo unknown)"
  exit 0
fi

[[ ! -L "$UNIT_DIR" && ! -L "$UNIT" ]] || fail 'Refusing symlinked unit path.'
[[ ! -e "$UNIT" ]] || fail 'Unit already exists; inspect before changing.'
[[ -d "$STATE_DIR" && ! -L "$STATE_DIR" ]] ||
  fail 'Existing private BTDigg state directory missing.'
[[ -d "$STATE_DIR/profile" && ! -L "$STATE_DIR/profile" ]] ||
  fail 'Existing private Chromium profile missing.'
python3 -B -m unittest rock64.test_btdigg_bootstrap_state -q ||
  fail 'Offline state tests failed.'

# Optional seed is an existing owner-chosen query, NOT a network request.
if [[ -n "$SEED" ]]; then
  python3 -B "$SEEDER" --seed-query "$SEED" ||
    fail 'Private seed creation failed.'
fi
mkdir -p -m 0700 "$UNIT_DIR"
[[ ! -L "$UNIT_DIR" && ! -e "$UNIT" ]] || fail 'Unsafe unit destination.'
STAGE="$(mktemp "$UNIT_DIR/.btdigg-browser.XXXXXXXX")"
trap 'rm -f -- "$STAGE"' EXIT
cat > "$STAGE" <<EOF
[Unit]
Description=Magnetra BTDigg private Chromium browser (owner opt-in)
StartLimitIntervalSec=0

[Service]
Type=simple
WorkingDirectory=$ROOT
Environment=MAGNETRA_BTDIGG_RESTORE_ON_BOOT=1
Environment=PYTHONUNBUFFERED=1
ExecStart=/usr/bin/bash $RUN --persistent-backend
Restart=on-failure
RestartSec=45s
UMask=0077

[Install]
WantedBy=default.target
EOF
chmod 600 "$STAGE"
mv -n -- "$STAGE" "$UNIT" || fail 'Could not install reviewed unit.'
trap - EXIT
systemctl --user daemon-reload || fail 'Could not reload user systemd.'
systemctl --user enable magnetra-btdigg-browser.service ||
  fail 'Could not enable boot service.'
echo 'SERVICE=ENABLED_FOR_NEXT_BOOT'
echo 'RUNNING_BROWSER=UNCHANGED (no service start; tmux not touched)'
LINGER="$(loginctl show-user "$(id -un)" -p Linger --value 2>/dev/null || echo unknown)"
if [[ "$LINGER" != yes ]]; then
  echo 'ACTION_REQUIRED: sudo loginctl enable-linger '"$(id -un)"
  echo 'USER_SERVICE_START_ON_BOOT=NOT_GUARANTEED_UNTIL_LINGER_ENABLED'
else
  echo 'USER_SERVICE_START_ON_BOOT=ENABLED'
fi
echo 'BOOTSTRAP=AT_MOST_ONE_SOURCE_REQUEST_PER_OS_BOOT (no retries)'
