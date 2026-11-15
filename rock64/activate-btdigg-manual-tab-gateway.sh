#!/usr/bin/env bash
# Owner-approved BTDigg 8796-only update to accept a verified manual tab.
# NEVER restarts Chromium 18896: preserves the currently solved CAPTCHA.
set -Eeuo pipefail
umask 077
usage(){ echo 'Usage: bash rock64/activate-btdigg-manual-tab-gateway.sh --check | --apply --owner-approved' >&2; exit 2; }
if [[ "$#" -eq 1 && "$1" == --check ]]; then
  MODE=check
elif [[ "$#" -eq 2 && "$1" == --apply && "$2" == --owner-approved ]]; then
  MODE=apply
else
  usage
fi
fail(){ echo "STOP: $*" >&2; exit 1; }
[[ "$(id -un)" == runner && "$EUID" -ne 0 ]] ||
  fail 'Run as nonroot runner; sudo is used only for the isolated gateway.'
ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd -P)"
[[ "$ROOT" == "$HOME/magnetra-cffi-live-20261028" ]] ||
  fail 'Unexpected checkout location.'
cd "$ROOT"
SOURCE="$ROOT/rock64/btdigg_gateway.py"
DEST=/opt/magnetra-btdigg/btdigg_gateway.py
BACKUP=/opt/magnetra-btdigg/.gateway-before-manual-tab-20261115.py
STAGE=/opt/magnetra-btdigg/.gateway-manual-tab-stage-20261115.py
SERVICE=magnetra-btdigg.service
USER_SERVICE=magnetra-btdigg-browser.service
OLD_BLOB=d2af8118c95eeb6a5f3ecb848471263442ff440d
NEW_BLOB=ce372bdf73b895e5105e83a77bad47229d070c02

for tool in git python3 sudo systemctl install sleep; do
  command -v "$tool" >/dev/null || fail "Missing tool: $tool"
done
for path in "$SOURCE" "$DEST" "$BACKUP" "$STAGE"; do
  [[ ! -L "$path" ]] || fail 'Protected path is a symlink.'
done
[[ -f "$SOURCE" && -f "$DEST" ]] || fail 'Required source or production file missing.'
[[ "$(git hash-object -- "$SOURCE")" == "$NEW_BLOB" ]] ||
  fail 'Source is not exact reviewed gateway blob.'
[[ "$(git hash-object -- "$DEST")" == "$OLD_BLOB" ||
   "$(git hash-object -- "$DEST")" == "$NEW_BLOB" ]] ||
  fail 'Installed gateway is not the reviewed prior/current blob.'
[[ ! -e "$STAGE" ]] || fail 'Previous staging file exists; audit first.'
sudo systemctl is-active --quiet "$SERVICE" ||
  fail 'Gateway 8796 systemd service is not active.'
systemctl --user is-active --quiet "$USER_SERVICE" ||
  fail 'Chromium 18896 systemd service is not active.'
DROPS="$(sudo systemctl show "$SERVICE" -p DropInPaths --value)"
[[ " $DROPS " == *" /etc/systemd/system/magnetra-btdigg.service.d/60-magnetra-chromium.conf "* ]] ||
  fail 'Expected private Chromium gateway override absent.'

local_health(){
  # Authenticated GET on localhost, with no BTDigg search or token output.
  sudo python3 - <<'PY'
import re
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import URLError,HTTPError
try:
    value=Path("/etc/magnetra-btdigg/gateway.env").read_text(encoding="ascii")
    match=re.fullmatch(r"MAGNETRA_BTDIGG_TOKEN=([A-Za-z0-9_-]{48,256})\n",value)
    if match is None: raise SystemExit(1)
    req=Request("http://127.0.0.1:8796/healthz",
                headers={"Authorization":"Bearer "+match.group(1)})
    with urlopen(req,timeout=2) as response:
        if response.status != 200 or response.read(100) != b'{"ok":true}':
            raise SystemExit(1)
except (OSError,URLError,HTTPError,UnicodeError):
    raise SystemExit(1)
PY
}
wait_health(){
  local count
  for count in {1..30}; do
    if sudo systemctl is-active --quiet "$SERVICE" && local_health; then
      return 0
    fi
    sleep 0.5
  done
  return 1
}
local_health || fail 'Gateway is not currently healthy; do not change it.'
if [[ -e "$BACKUP" ]]; then
  [[ -f "$BACKUP" && "$(sudo git hash-object -- "$BACKUP")" == "$OLD_BLOB" ]] ||
    fail 'Existing backup is not the verified prior gateway.'
fi

INSTALLED_BLOB="$(git hash-object -- "$DEST")"
if [[ "$MODE" == check ]]; then
  echo "READY: exact source and current 8796 gateway healthy (installed=$INSTALLED_BLOB)"
  echo 'CHROMIUM_18896=UNCHANGED; NO_SOURCE_REQUESTS; NO_RESTART'
  exit 0
fi
if [[ "$INSTALLED_BLOB" == "$NEW_BLOB" ]]; then
  echo 'ALREADY_APPLIED: 8796 source matches reviewed adoption fix; no restart.'
  exit 0
fi

# Offline fixtures only: no BTDigg origin navigation.
python3 -B -m unittest \
  rock64.test_btdigg_gateway \
  rock64.test_btdigg_chromium_bridge \
  rock64.test_btdigg_browser_backend -q ||
  fail 'Offline tests failed before any production changes.'
if [[ ! -e "$BACKUP" ]]; then
  sudo install -m 0600 "$DEST" "$BACKUP"
fi
[[ "$(sudo git hash-object -- "$BACKUP")" == "$OLD_BLOB" ]] ||
  fail 'Backup failed version verification.'
sudo install -m 0644 "$SOURCE" "$STAGE"
[[ "$(sudo git hash-object -- "$STAGE")" == "$NEW_BLOB" ]] ||
  fail 'Staged source hash changed; refusing activation.'

ROLLBACK=0
cleanup(){
  local code=$?
  trap - EXIT
  if (( ROLLBACK == 1 )); then
    echo 'ROLLBACK: restoring only prior gateway 8796 code.' >&2
    sudo install -m 0644 "$BACKUP" "$DEST" || true
    sudo systemctl restart "$SERVICE" || true
    if wait_health; then
      echo 'ROLLBACK_GATEWAY_HEALTH=PASS' >&2
    else
      echo 'ROLLBACK_GATEWAY_HEALTH=NOT_VERIFIED' >&2
    fi
  fi
  sudo rm -f -- "$STAGE" || true
  exit "$code"
}
trap cleanup EXIT
ROLLBACK=1
sudo mv -- "$STAGE" "$DEST"
sudo systemctl restart "$SERVICE" ||
  fail '8796 restart failed.'
wait_health || fail 'New 8796 authenticated health not verified.'
ROLLBACK=0
echo 'BTDIGG_8796=MANUAL_TAB_PREFLIGHT_READY'
echo 'CHROMIUM_18896=UNCHANGED; EXISTING_CAPTCHA_SESSION_PRESERVED'
echo 'NO_BTDIGG_SEARCH; NO_CLOUDFLARE_DEPLOY; NO_SHARED_SERVICE_RESTART'
