#!/usr/bin/env bash
# BTDigg simple-checkbox gateway rollout; exact-version, owner-approved.
# --check is read-only. --apply restarts 8796 ONLY; never Chromium 18896.
set -Eeuo pipefail
umask 077

fail(){ printf 'STOP: %s\n' "$*" >&2; exit 1; }
usage(){ echo 'Usage: bash rock64/rollout-btdigg-checkbox-8796-20261116.sh --check | --apply --owner-approved' >&2; exit 2; }
(( $# > 0 )) || usage
MODE="$1"
if [[ "$MODE" == "--check" && "$#" == 1 ]]; then :;
elif [[ "$MODE" == "--apply" && "$#" == 2 && "$2" == "--owner-approved" ]]; then :;
else usage; fi

[[ "$EUID" -ne 0 && "$(id -un)" == runner ]] || fail 'Run as runner, not root.'
ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd -P)"
[[ "$ROOT" == /home/runner/magnetra-cffi-live-20261028 ]] || fail 'Unexpected checkout.'
cd "$ROOT"
[[ "$(git branch --show-current)" == main ]] || fail 'Checkout is not main.'
[[ -z "$(git status --porcelain --untracked-files=no)" ]] || fail 'Tracked local changes present.'
git merge-base --is-ancestor b7425d590156ebf361c1381aad41c27ff11ccd58 HEAD ||
  fail 'PR #302 missing from checked-out main.'
BROWSER=rock64/btdigg_browser_backend.py
SOURCE=rock64/btdigg_gateway.py
DEST=/opt/magnetra-btdigg/btdigg_gateway.py
BACKUP=/opt/magnetra-btdigg/.gateway-before-checkbox-20261116.py
SERVICE=magnetra-btdigg.service
USER_SERVICE=magnetra-btdigg-browser.service
OLD=c1c0aa40554a96948921210ad6f4f0c1e8af31bf
NEW=dee9113bcc1591c7dc535ecf72021ed38d04a3ed
BROWSER_NEW=4290f440e73fff409b9f86fa4e0324f9775b5794

for file in "$BROWSER" "$SOURCE"; do
  [[ -f "$file" && ! -L "$file" ]] || fail 'Symlink or missing source.'
done
[[ "$(git hash-object -- "$BROWSER")" == "$BROWSER_NEW" ]] ||
  fail 'Browser source not reviewed version.'
[[ "$(git hash-object -- "$SOURCE")" == "$NEW" ]] ||
  fail 'Gateway source not reviewed version.'
[[ ! -L "$DEST" && -f "$DEST" ]] || fail 'Installed gateway unsafe.'
[[ ! -L "$BACKUP" ]] || fail 'Rollback backup symlink.'
INSTALLED="$(git hash-object -- "$DEST")"
[[ "$INSTALLED" == "$OLD" || "$INSTALLED" == "$NEW" ]] ||
  fail 'Installed gateway differs from expected old/new.'
if sudo test -e "$BACKUP"; then
  [[ "$(sudo git hash-object -- "$BACKUP")" == "$OLD" ]] ||
    fail 'Existing private backup differs from reviewed OLD.'
fi
systemctl --user is-active --quiet "$USER_SERVICE" || fail 'Chromium service not active.'
sudo systemctl is-active --quiet "$SERVICE" || fail 'Gateway service not active.'
EFFECTIVE="$(sudo systemctl show "$SERVICE" -p ExecStart --value)"
[[ "$EFFECTIVE" == *"/opt/magnetra-btdigg/btdigg_gateway.py"* ]] ||
  fail 'Effective gateway command unexpected.'
DROPS="$(sudo systemctl show "$SERVICE" -p DropInPaths --value)"
[[ " $DROPS " == *" /etc/systemd/system/magnetra-btdigg.service.d/60-magnetra-chromium.conf "* ]] ||
  fail 'Active Chromium bridge override absent.'
PID="$(systemctl --user show "$USER_SERVICE" -p MainPID --value)"
[[ "$PID" =~ ^[1-9][0-9]*$ ]] || fail 'No active browser service PID.'

health(){
  sudo python3 - <<'PY'
import re
from pathlib import Path
from urllib.request import Request,urlopen
s=Path("/etc/magnetra-btdigg/gateway.env").read_text(encoding="ascii")
m=re.fullmatch(r"MAGNETRA_BTDIGG_TOKEN=([A-Za-z0-9_-]{48,256})\n",s)
if m is None: raise SystemExit(1)
r=Request("http://127.0.0.1:8796/healthz",
          headers={"Authorization":"Bearer "+m.group(1)})
try:
    with urlopen(r,timeout=3) as response:
        if response.status!=200 or response.read(100)!=b'{"ok":true}':
            raise SystemExit(1)
except OSError:
    # Expected while systemd has restarted but Python has not bound 8796.
    # Caller retries privately; avoid noisy tracebacks for a normal startup.
    raise SystemExit(1)
PY
}
wait_health(){
  for i in {1..30}; do
    if sudo systemctl is-active --quiet "$SERVICE" && health; then return 0; fi
    sleep 0.5
  done
  return 1
}
health || fail 'Original 8796 authenticated health failed.'
# Private browser-state is read-only: never sends a source search.
STATUS="$(python3 -B rock64/check-btdigg-browser-backend.py --browser-status)" ||
  fail '18896 private browser status inaccessible.'
printf '%s' "$STATUS" | python3 -c '
import json,sys
s=json.load(sys.stdin);b=s.get("browser_state",{})
assert s.get("local_gateway_status")==200
assert s.get("search_performed") is False
assert b.get("browser_connected") is True
assert b.get("open_tabs")==1 and b.get("selected_tab_index")==0
' || fail 'Browser is not in expected connected single-tab state.'

echo "GATEWAY_INSTALLED=$INSTALLED"
echo "GATEWAY_SOURCE=$NEW"
echo "BROWSER_SOURCE=$BROWSER_NEW"
echo "BROWSER_RUNNING_PID=$PID"
echo 'BTDIGG_REQUESTS=0'

if [[ "$MODE" == --check ]]; then
  echo 'READONLY_CHECK=PASS; NO_RESTARTS'
  exit 0
fi
if [[ "$INSTALLED" == "$NEW" ]]; then
  echo 'GATEWAY_ALREADY_NEW=TRUE; NO_RESTARTS'
  exit 0
fi
python3 -B -m unittest rock64.test_btdigg_browser_backend \
  rock64.test_btdigg_chromium_bridge rock64.test_btdigg_gateway -q ||
  fail 'Offline regressions failed before any mutation.'
if ! sudo test -e "$BACKUP"; then
  sudo install -m 0600 "$DEST" "$BACKUP"
fi
[[ "$(sudo git hash-object -- "$BACKUP")" == "$OLD" ]] ||
  fail 'Cannot prove exact rollback backup.'
STAGE="$(sudo mktemp /opt/magnetra-btdigg/.checkbox-staged.XXXXXXXX)"
ROLLBACK=0
finish(){
  code="$?"
  trap - EXIT
  if (( ROLLBACK == 1 )); then
    echo 'ROLLBACK: restoring prior reviewed gateway' >&2
    sudo install -m 0644 "$BACKUP" "$DEST" || true
    sudo systemctl restart "$SERVICE" || true
    if wait_health; then echo 'ROLLBACK_HEALTH=PASS' >&2
    else echo 'ROLLBACK_HEALTH=FAILED' >&2; fi
  fi
  sudo rm -f "$STAGE"
  exit "$code"
}
trap finish EXIT
sudo install -m 0644 "$SOURCE" "$STAGE"
[[ "$(sudo git hash-object -- "$STAGE")" == "$NEW" ]] ||
  fail 'Staged gateway differs from reviewed version.'
ROLLBACK=1
sudo mv -f "$STAGE" "$DEST"
sudo systemctl restart "$SERVICE"
wait_health || fail 'New gateway authenticated health failed.'
[[ "$(sudo git hash-object -- "$DEST")" == "$NEW" ]] ||
  fail 'Installed gateway drifted from reviewed version.'
[[ "$(systemctl --user show "$USER_SERVICE" -p MainPID --value)" == "$PID" ]] ||
  fail 'Browser process changed unexpectedly.'
ROLLBACK=0
echo 'GATEWAY_8796=UPDATED; BROWSER_18896=UNTOUCHED'
echo 'NOTE=18896 still needs an explicit controlled restart to load PR302.'
