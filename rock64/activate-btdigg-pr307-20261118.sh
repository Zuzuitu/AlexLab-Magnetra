#!/usr/bin/env bash
# Owner-controlled Rock64 activation of #306 (gateway) and #307 (browser).
# No BTDigg source requests. Restarts only 8796, then 18896, when approved.
set -Eeuo pipefail
umask 077
fail(){ echo "STOP: $*" >&2; exit 1; }
[[ $# -ge 1 ]] || fail 'Usage: --check OR --apply --owner-approved --accept-session-reset'
mode="$1"
case "$mode:$#" in
  --check:1) ;;
  --apply:3) [[ "$2" == --owner-approved && "$3" == --accept-session-reset ]] ||
    fail 'Explicit approval and session-reset acknowledgment required.' ;;
  *) fail 'Usage: --check OR --apply --owner-approved --accept-session-reset' ;;
esac

[[ "$(id -un)" == runner && "$EUID" -ne 0 ]] || fail 'Run as runner.'
cd "$(dirname "$0")/.." || fail 'Repository missing.'
[[ "$(pwd -P)" == /home/runner/magnetra-cffi-live-20261028 ]] ||
  fail 'Wrong checkout.'
[[ "$(git branch --show-current)" == main ]] || fail 'Expected main.'
git merge-base --is-ancestor 8b9b634691226cb3f87967297c4ac56e905ae1b3 HEAD ||
  fail 'PR #307 commit not in deployed main ancestry.'
[[ -z "$(git status --porcelain --untracked-files=no)" ]] ||
  fail 'Local tracked changes; no mutation.'
src=rock64/btdigg_gateway.py
browser=rock64/btdigg_browser_backend.py
dest=/opt/magnetra-btdigg/btdigg_gateway.py
backup=/opt/magnetra-btdigg/.gateway-pr307-pre-upgrade.py
old=dee9113bcc1591c7dc535ecf72021ed38d04a3ed
new=cd9fa5ae77388b6f4d639f6e6ef83a05266b8e37
browser_sha=fdb7346fa60d09f6ff163d6f8e6c23873253af37
gw=magnetra-btdigg.service
bu=magnetra-btdigg-browser.service

[[ -f "$src" && -f "$browser" && ! -L "$src" && ! -L "$browser" ]] ||
  fail 'Source files missing or symlinked.'
[[ "$(git hash-object "$src")" == "$new" &&
   "$(git hash-object "$browser")" == "$browser_sha" ]] ||
  fail 'Reviewed source SHA mismatch.'
sudo test -f "$dest" && ! sudo test -L "$dest" ||
  fail 'Installed gateway missing or symlinked.'
! sudo test -L "$backup" || fail 'Backup path is a symlink.'
installed="$(sudo git hash-object "$dest")"
[[ "$installed" == "$old" || "$installed" == "$new" ]] ||
  fail 'Unexpected installed gateway SHA.'
if sudo test -e "$backup"; then
  [[ "$(sudo git hash-object "$backup")" == "$old" ]] ||
    fail 'Existing backup hash mismatch.'
fi
sudo systemctl is-active --quiet "$gw" || fail 'Gateway 8796 inactive.'
systemctl --user is-active --quiet "$bu" || fail 'Browser 18896 inactive.'
[[ "$(sudo systemctl show "$gw" -p ExecStart --value)" == *"/opt/magnetra-btdigg/btdigg_gateway.py"* ]] ||
  fail 'Gateway ExecStart unexpected.'
browser_exec="$(systemctl --user show "$bu" -p ExecStart --value)"
[[ "$browser_exec" == *"run-btdigg-visual-session.sh"* &&
   "$browser_exec" == *"--persistent-backend"* ]] ||
  fail 'Browser ExecStart unexpected.'
before_pid="$(systemctl --user show "$bu" -p MainPID --value)"
[[ "$before_pid" =~ ^[1-9][0-9]*$ ]] || fail 'Browser MainPID invalid.'

health(){
  sudo python3 - <<'PY'
import re
from pathlib import Path
from urllib.request import Request, urlopen
secret=Path("/etc/magnetra-btdigg/gateway.env").read_text(encoding="ascii")
m=re.fullmatch(r"MAGNETRA_BTDIGG_TOKEN=([A-Za-z0-9_-]{48,256})\n",secret)
if m is None: raise SystemExit(1)
r=Request("http://127.0.0.1:8796/healthz",
          headers={"Authorization":"Bearer "+m.group(1)})
try:
    with urlopen(r,timeout=3) as res:
        if res.status!=200 or res.read(100)!=b'{"ok":true}':
            raise SystemExit(1)
except OSError:
    raise SystemExit(1)
PY
}
wait_health(){
  for i in {1..30}; do
    if sudo systemctl is-active --quiet "$gw" && health; then return 0; fi
    sleep 0.5
  done
  return 1
}
health || fail 'Authenticated 8796 health failed before rollout.'
state="$(python3 -B rock64/check-btdigg-browser-backend.py --browser-status)"
python3 - "$state" <<'PY' || fail 'Authenticated browser preflight failed.'
import json,sys
s=json.loads(sys.argv[1]); b=s.get("browser_state",{})
assert s.get("local_gateway_status")==200
assert s.get("search_performed") is False
assert b.get("browser_connected") is True
assert b.get("open_tabs")==1 and b.get("selected_tab_index")==0
PY

echo "GATEWAY_INSTALLED=$installed"
echo "GATEWAY_TARGET=$new"
echo "BROWSER_TARGET=$browser_sha"
echo "BROWSER_PID_BEFORE=$before_pid"
echo 'BTDIGG_REQUESTS=0'
if [[ "$mode" == --check ]]; then
  echo 'READONLY_CHECK=PASS'
  echo 'Apply can lose the currently verified BTDigg tab; persistent profile is never removed.'
  exit 0
fi

if [[ "$installed" == "$old" ]]; then
  if ! sudo test -e "$backup"; then
    sudo install -m 0600 "$dest" "$backup" || fail 'Gateway backup failed.'
  fi
  [[ "$(sudo git hash-object "$backup")" == "$old" ]] ||
    fail 'Gateway backup invalid.'
  stage="$(sudo mktemp /opt/magnetra-btdigg/.pr307-stage.XXXXXXXX)"
  if ! sudo install -m 0644 "$src" "$stage"; then
    sudo rm -f "$stage"
    fail 'Gateway staging failed.'
  fi
  if [[ "$(sudo git hash-object "$stage")" != "$new" ]]; then
    sudo rm -f "$stage"
    fail 'Staged gateway SHA mismatch.'
  fi
  sudo mv -f "$stage" "$dest" || fail 'Gateway atomic replace failed.'
  sudo systemctl restart "$gw" || true
  if ! wait_health; then
    echo 'New gateway failed health, restoring reviewed old version.' >&2
    sudo install -m 0644 "$backup" "$dest" || fail 'Gateway rollback copy FAILED.'
    sudo systemctl restart "$gw" || true
    if wait_health; then fail 'Rollback healthy; deployment stopped.'
    else fail 'Gateway rollback health FAILED.'; fi
  fi
  [[ "$(sudo git hash-object "$dest")" == "$new" ]] ||
    fail 'Installed gateway SHA changed.'
  [[ "$(systemctl --user show "$bu" -p MainPID --value)" == "$before_pid" ]] ||
    fail 'Unexpected Chromium restart during gateway update.'
  echo 'GATEWAY_8796=UPDATED_HEALTHY'
else
  echo 'GATEWAY_8796=ALREADY_CURRENT'
fi

# The owner explicitly approved losing the currently verified in-memory tab.
# Restart ONCE. Never delete profile and never launch an extra source query.
echo 'CHROMIUM_18896=RESTARTING_ONCE'
systemctl --user restart "$bu" || fail 'Chromium restart command failed.'
for i in {1..30}; do
  status="$(python3 -B rock64/check-btdigg-browser-backend.py --browser-status)"
  if python3 - "$status" <<'PY'
import json,sys
try:
    s=json.loads(sys.argv[1]);b=s.get("browser_state",{})
    assert s.get("local_gateway_status")==200
    assert b.get("browser_connected") is True
    assert isinstance(b.get("checkbox_last_outcome"),str)
    assert type(b.get("checkbox_click_count")) is int
    assert 0<=b["checkbox_click_count"]<=128
except (AssertionError,ValueError,TypeError):
    raise SystemExit(1)
PY
  then
    echo 'CHROMIUM_18896=NEW_CODE_READY'
    systemctl --user show "$bu" -p ActiveState -p MainPID -p NRestarts
    echo "$status"
    echo 'LIVE_CAPTCHA_ACCEPTANCE=NOT_YET_PROVEN'
    exit 0
  fi
  sleep 2
done
echo 'CHROMIUM_NEW_DIAGNOSTIC=NOT_READY; no second restart attempted.' >&2
systemctl --user show "$bu" -p ActiveState -p SubState -p MainPID >&2
exit 1
