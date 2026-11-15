#!/usr/bin/env bash
# Owner-driven upgrade, only Magnetra BTDigg 18896/8796.
# --check: read-only preflight. --apply --owner-approved: explicit restarts.
# Does not deploy Cloudflare, change other services, solve CAPTCHA, or retry
# BTDigg searches in a loop. Chromium may restore its saved page at startup.
set -Eeuo pipefail
umask 077

usage(){
  echo 'Usage: bash rock64/activate-btdigg-idle-recovery.sh --check | --apply --owner-approved' >&2
  exit 2
}
if [[ "$#" -eq 1 && "$1" == "--check" ]]; then
  MODE=check
elif [[ "$#" -eq 2 && "$1" == "--apply" && "$2" == "--owner-approved" ]]; then
  MODE=apply
else
  usage
fi
[[ "$(id -un)" == runner && "$EUID" -ne 0 ]] ||
  { echo 'STOP: launch as the unprivileged runner user.' >&2; exit 2; }
fail(){ echo "STOP: $*" >&2; exit 1; }

ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"
[[ "$ROOT" == "$HOME/magnetra-cffi-live-20261028" ]] ||
  fail 'Unexpected Rock64 checkout directory.'
cd "$ROOT"
BROWSER="$ROOT/rock64/btdigg_browser_backend.py"
CHECKER="$ROOT/rock64/check-btdigg-browser-backend.py"
GATEWAY="$ROOT/rock64/btdigg_gateway.py"
INSTALLED=/opt/magnetra-btdigg/btdigg_gateway.py
BACKUP=/opt/magnetra-btdigg/.gateway-before-idle-recovery-20261115.py
STAGE=/opt/magnetra-btdigg/.gateway-staged-idle-recovery-20261115.py
USER_SERVICE=magnetra-btdigg-browser.service
GATEWAY_SERVICE=magnetra-btdigg.service

# Exact Git blob IDs from reviewed main after PR #283.
BROWSER_BLOB=aeef396fa509fd0984d909619c5d22b271d9435c
CHECKER_BLOB=8f30d449bd7ceb2ead24a191366f77bdf6500c2a
GATEWAY_BLOB=d2af8118c95eeb6a5f3ecb848471263442ff440d
OLD_INSTALLED_BLOB=3553454a227614d5d108aa548a074a4536eb74e1

for command in git python3 systemctl sudo ss; do
  command -v "$command" >/dev/null 2>&1 || fail "Missing tool: $command"
done
for path in "$BROWSER" "$CHECKER" "$GATEWAY" "$INSTALLED"; do
  [[ -f "$path" && ! -L "$path" ]] || fail 'Reviewed file missing or symlink.'
done
[[ "$(git hash-object -- "$BROWSER")" == "$BROWSER_BLOB" ]] ||
  fail 'Browser source is not the reviewed idle-recovery build.'
[[ "$(git hash-object -- "$CHECKER")" == "$CHECKER_BLOB" ]] ||
  fail 'Browser checker is not the reviewed version.'
[[ "$(git hash-object -- "$GATEWAY")" == "$GATEWAY_BLOB" ]] ||
  fail 'Gateway source is not the reviewed Chromium recovery bridge.'
systemctl --user is-active --quiet "$USER_SERVICE" ||
  fail 'Private Chromium service is not active.'
sudo systemctl is-active --quiet "$GATEWAY_SERVICE" ||
  fail 'Production gateway is not active.'
[[ -n "$(ss -H -ltn '( sport = :18896 )')" ]] ||
  fail 'No Chromium loopback listener on 18896.'
[[ -n "$(ss -H -ltn '( sport = :8796 )')" ]] ||
  fail 'No production gateway loopback listener on 8796.'
[[ "$(systemctl --user show "$USER_SERVICE" -p FragmentPath --value)" == \
  "$HOME/.config/systemd/user/$USER_SERVICE" ]] ||
  fail 'Unexpected private Chromium systemd unit.'
[[ "$(systemctl --user show "$USER_SERVICE" -p ExecStart --value)" == \
  *"/rock64/run-btdigg-visual-session.sh --persistent-backend"* ]] ||
  fail 'User service does not start the pinned Chromium launcher.'
DROPS="$(sudo systemctl show "$GATEWAY_SERVICE" -p DropInPaths --value)" ||
  fail 'Cannot verify gateway systemd overrides.'
[[ " $DROPS " == *" /etc/systemd/system/magnetra-btdigg.service.d/60-magnetra-chromium.conf "* ]] ||
  fail 'Chromium gateway override is missing.'
INSTALLED_BLOB="$(git hash-object -- "$INSTALLED")" ||
  fail 'Cannot fingerprint installed gateway.'
[[ "$INSTALLED_BLOB" == "$OLD_INSTALLED_BLOB" || "$INSTALLED_BLOB" == "$GATEWAY_BLOB" ]] ||
  fail 'Unexpected installed gateway; refusing replacement.'
[[ ! -L "$BACKUP" && ! -L "$STAGE" ]] ||
  fail 'Unsafe backup/staging symlink.'
if [[ -e "$BACKUP" ]]; then
  [[ -f "$BACKUP" ]] || fail 'Existing private backup is not a file.'
  [[ "$(sudo git hash-object -- "$BACKUP")" == "$OLD_INSTALLED_BLOB" ]] ||
    fail 'Existing backup is not the reviewed previous gateway.'
fi
[[ ! -e "$STAGE" ]] || fail 'Stale staged gateway exists; inspect manually.'

# Authenticated localhost-only probe. Never submits a search.
gateway_health(){
  sudo python3 - <<'PY'
import re
from pathlib import Path
from urllib.request import Request, urlopen
p=Path("/etc/magnetra-btdigg/gateway.env")
m=re.fullmatch(r"MAGNETRA_BTDIGG_TOKEN=([A-Za-z0-9_-]{48,256})\n",
               p.read_text(encoding="ascii"))
if m is None: raise SystemExit(1)
r=Request("http://127.0.0.1:8796/healthz",
          headers={"Authorization":"Bearer "+m.group(1)})
with urlopen(r,timeout=2) as response:
    if response.status != 200 or response.read(100) != b'{"ok":true}':
        raise SystemExit(1)
PY
}

# Poll only private, authenticated browser state until the new schema loads.
browser_ready(){
  python3 - <<'PY'
import json,re
from pathlib import Path
from urllib.request import Request,urlopen
p=Path.home()/".local/state/magnetra-btdigg-browser/gateway.token"
if p.is_symlink() or not p.is_file() or p.stat().st_mode&0o077:
    raise SystemExit(1)
token=p.read_text().strip()
if not re.fullmatch(r"[A-Za-z0-9_-]{48,256}",token):
    raise SystemExit(1)
req=Request("http://127.0.0.1:18896/v1/browser-state",
            headers={"Authorization":"Bearer "+token})
with urlopen(req,timeout=2) as response:
    data=json.load(response)
if (data.get("browser_connected") is not True
    or type(data.get("pwa_tab_recovery_ready")) is not bool
    or type(data.get("visible_captcha_required")) is not bool):
    raise SystemExit(1)
PY
}

gateway_health || fail 'Current 8796 health is not verified.'
if [[ "$MODE" == check ]]; then
  echo 'READY: reviewed source, Chromium user service, 8796 gateway and private health verified.'
  echo "INSTALLED_GATEWAY_BLOB=$INSTALLED_BLOB"
  echo 'NO_CHANGES; NO_SOURCE_SEARCH.'
  exit 0
fi

# Offline test fixtures only. Tests do not contact the real source.
python3 -B -m unittest \
  rock64.test_btdigg_browser_backend \
  rock64.test_btdigg_bootstrap_state \
  rock64.test_btdigg_gateway \
  rock64.test_btdigg_chromium_bridge -q ||
  fail 'Offline regression tests failed before touching services.'

# Step 1: restart only the user-owned BTDigg browser so it loads new source.
# Keep 8796 untouched until private 18896 reports the new API contract.
systemctl --user restart "$USER_SERVICE" ||
  fail 'Browser user service restart failed; 8796 remains unchanged.'
BROWSER_READY=0
for attempt in {1..30}; do
  if systemctl --user is-active --quiet "$USER_SERVICE" && browser_ready; then
    BROWSER_READY=1
    break
  fi
  sleep 1
done
(( BROWSER_READY == 1 )) ||
  fail 'New browser API did not become ready; 8796 remains unchanged.'

# Step 2: back up and replace only the BTDigg 8796 Python gateway.
if [[ "$INSTALLED_BLOB" == "$OLD_INSTALLED_BLOB" ]]; then
  if [[ ! -e "$BACKUP" ]]; then
    sudo install -m 0600 "$INSTALLED" "$BACKUP"
  fi
  [[ "$(sudo git hash-object -- "$BACKUP")" == "$OLD_INSTALLED_BLOB" ]] ||
    fail 'Backup verification failed before replacement.'
  sudo install -m 0644 "$GATEWAY" "$STAGE"
  [[ "$(sudo git hash-object -- "$STAGE")" == "$GATEWAY_BLOB" ]] ||
    fail 'Staged gateway blob mismatch.'
  sudo mv -- "$STAGE" "$INSTALLED"
  if ! sudo systemctl restart "$GATEWAY_SERVICE"; then
    sudo install -m 0644 "$BACKUP" "$INSTALLED"
    sudo systemctl restart "$GATEWAY_SERVICE" || true
    fail 'Gateway restart failed; old gateway restoration attempted.'
  fi
fi

GATEWAY_READY=0
for attempt in {1..30}; do
  if sudo systemctl is-active --quiet "$GATEWAY_SERVICE" && gateway_health; then
    GATEWAY_READY=1
    break
  fi
  sleep 1
done
if (( GATEWAY_READY == 0 )); then
  echo 'ROLLBACK: 8796 health failed; restoring prior version.' >&2
  if [[ -f "$BACKUP" && ! -L "$BACKUP" ]]; then
    sudo install -m 0644 "$BACKUP" "$INSTALLED"
    sudo systemctl restart "$GATEWAY_SERVICE" || true
  fi
  fail 'New gateway not healthy. Browser was restarted; inspect its status.'
fi

echo 'BTDIGG_18896=NEW_PRIVATE_SCHEMA_HEALTHY'
echo 'BTDIGG_8796=NEW_GATEWAY_HEALTHY'
echo 'PWA_CLOUDFLARE=NOT_YET_DEPLOYED'
echo 'ONLY_BTDIGG_SERVICES_RESTARTED'
