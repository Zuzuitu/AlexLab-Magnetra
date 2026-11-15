#!/usr/bin/env bash
# Owner activation ONLY for BTDigg gateway 8796 private CAPTCHA status.
# Does NOT restart Chromium 18896, noVNC 6088 or other applications.
set -Eeuo pipefail
umask 077
usage(){
 echo 'Usage: bash rock64/activate-btdigg-captcha-gateway.sh --check | --apply --owner-approved' >&2
 exit 2
}
if [[ "$#" == 1 && "$1" == --check ]]; then MODE=check
elif [[ "$#" == 2 && "$1" == --apply && "$2" == --owner-approved ]]; then MODE=apply
else usage
fi
fail(){ echo "STOP: $*" >&2; exit 1; }
[[ "$(id -un)" == runner && "$EUID" -ne 0 ]] ||
 fail 'Run as non-root runner.'
ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"
[[ "$ROOT" == "$HOME/magnetra-cffi-live-20261028" ]] ||
 fail 'Unexpected private Rock64 checkout.'
cd "$ROOT"
SOURCE="$ROOT/rock64/btdigg_gateway.py"
DEST=/opt/magnetra-btdigg/btdigg_gateway.py
BACKUP=/opt/magnetra-btdigg/.gateway-before-human-verification-20261115.py
STAGE=/opt/magnetra-btdigg/.gateway-staged-human-verification-20261115.py
SERVICE=magnetra-btdigg.service
OLD_BLOB=ce372bdf73b895e5105e83a77bad47229d070c02
NEW_BLOB=c1c0aa40554a96948921210ad6f4f0c1e8af31bf

for command in git sudo python3 systemctl; do
 command -v "$command" >/dev/null || fail "Missing $command"
done
[[ -f "$SOURCE" && -f "$DEST" && ! -L "$SOURCE" && ! -L "$DEST" ]] ||
 fail 'Invalid source or installed gateway.'
[[ "$(git hash-object -- "$SOURCE")" == "$NEW_BLOB" ]] ||
 fail 'New source does not match reviewed exact blob.'
CURRENT_BLOB="$(git hash-object -- "$DEST")"
[[ "$CURRENT_BLOB" == "$OLD_BLOB" || "$CURRENT_BLOB" == "$NEW_BLOB" ]] ||
 fail 'Installed gateway is not the reviewed previous/current build.'
for x in "$BACKUP" "$STAGE"; do
 [[ ! -L "$x" ]] || fail 'Protected path is a symlink.'
done
[[ ! -e "$STAGE" ]] || fail 'Stale staged gateway exists.'
if [[ -e "$BACKUP" ]]; then
 [[ -f "$BACKUP" && "$(sudo git hash-object -- "$BACKUP")" == "$OLD_BLOB" ]] ||
  fail 'Prior backup does not match reviewed old gateway.'
fi
systemctl --user is-active --quiet magnetra-btdigg-browser.service ||
 fail 'Persistent Chromium is not running; no restart performed.'
sudo systemctl is-active --quiet "$SERVICE" ||
 fail 'Private production gateway is not active.'
DROPS="$(sudo systemctl show "$SERVICE" -p DropInPaths --value)" ||
 fail 'Unable to inspect gateway overrides.'
[[ " $DROPS " == *" /etc/systemd/system/magnetra-btdigg.service.d/60-magnetra-chromium.conf "* ]] ||
 fail 'Chromium bridge override is absent.'
local_health(){
 sudo python3 - <<'PY'
import re
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import URLError
try:
 s=Path("/etc/magnetra-btdigg/gateway.env").read_text(encoding="ascii")
 m=re.fullmatch(r"MAGNETRA_BTDIGG_TOKEN=([A-Za-z0-9_-]{48,256})\n",s)
 if m is None: raise SystemExit(1)
 with urlopen(Request("http://127.0.0.1:8796/healthz",
        headers={"Authorization":"Bearer "+m.group(1)}),timeout=2) as r:
  if r.status!=200 or r.read(100)!=b'{"ok":true}': raise SystemExit(1)
except (OSError,URLError,UnicodeError):
 raise SystemExit(1)
PY
}
local_health || fail 'Authenticated 8796 baseline health not PASS.'
if [[ "$MODE" == check ]]; then
 echo "READY: production 8796 healthy; installed=$CURRENT_BLOB; new source verified."
 echo 'NO_CHANGES; CHROMIUM_18896=UNCHANGED; NO_SOURCE_SEARCH'
 exit 0
fi
if [[ "$CURRENT_BLOB" == "$NEW_BLOB" ]]; then
 echo 'ALREADY_APPLIED: reviewed CAPTCHA 8796 gateway installed.'
 exit 0
fi
python3 -B -m unittest rock64.test_btdigg_gateway rock64.test_btdigg_chromium_bridge -q ||
 fail 'Offline gateway regression tests failed.'
if [[ ! -e "$BACKUP" ]]; then
 sudo install -m 0600 "$DEST" "$BACKUP"
fi
[[ "$(sudo git hash-object -- "$BACKUP")" == "$OLD_BLOB" ]] ||
 fail 'Could not verify exact rollback backup.'
sudo install -m 0644 "$SOURCE" "$STAGE"
[[ "$(sudo git hash-object -- "$STAGE")" == "$NEW_BLOB" ]] ||
 fail 'Staging blob verification failed.'
ROLLBACK=0
finish(){
 local code=$?
 trap - EXIT
 if (( ROLLBACK == 1 )); then
  echo 'ROLLBACK: restoring prior 8796 gateway.' >&2
  sudo install -m 0644 "$BACKUP" "$DEST" || true
  sudo systemctl restart "$SERVICE" || true
  if local_health; then
   echo 'ROLLBACK_GATEWAY_HEALTH=PASS' >&2
  else
   echo 'ROLLBACK_GATEWAY_HEALTH=NOT_VERIFIED' >&2
  fi
 fi
 sudo rm -f -- "$STAGE" || true
 exit "$code"
}
trap finish EXIT
ROLLBACK=1
sudo mv -- "$STAGE" "$DEST"
sudo systemctl restart "$SERVICE" ||
 fail 'Gateway 8796 restart failed.'
HEALTHY=0
for _ in {1..30}; do
 if sudo systemctl is-active --quiet "$SERVICE" && local_health; then
  HEALTHY=1
  break
 fi
 sleep 0.5
done
[[ "$HEALTHY" == 1 ]] || fail 'New gateway 8796 failed authenticated health.'
[[ "$(sudo git hash-object -- "$DEST")" == "$NEW_BLOB" ]] ||
 fail 'Installed gateway drifted from reviewed build.'
ROLLBACK=0
echo 'BTDIGG_8796=HUMAN_VERIFICATION_428_READY'
echo 'CHROMIUM_18896=UNCHANGED; PRIVATE_CAPTCHA_SESSION_PRESERVED'
echo 'NO_SOURCE_SEARCH; NO_CLOUDFLARE_DEPLOY; OTHER_SERVICES_UNCHANGED'
