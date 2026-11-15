#!/usr/bin/env bash
# Owner-initiated, exact-version update of the EXISTING Chromium-backed
# 8796 gateway ONLY. Default --check is read-only. No BTDigg source searches.
set -Eeuo pipefail
umask 077

usage(){
  echo 'Usage: sudo bash rock64/update-btdigg-chromium-bridge.sh --check | --apply --owner-approved' >&2
  exit 2
}
if [[ "$#" -eq 1 && "$1" == --check ]]; then
  MODE=check
elif [[ "$#" -eq 2 && "$1" == --apply && "$2" == --owner-approved ]]; then
  MODE=apply
else
  usage
fi
(( EUID == 0 )) || { echo 'STOP: run under sudo.' >&2; exit 2; }
fail(){ echo "STOP: $*" >&2; exit 1; }

ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd -P)"
[[ "$ROOT" == /home/runner/magnetra-cffi-live-20261028 ]] ||
  fail 'Unexpected checkout path; source/install not trusted.'
SOURCE="$ROOT/rock64/btdigg_gateway.py"
DEST=/opt/magnetra-btdigg/btdigg_gateway.py
SERVICE=magnetra-btdigg.service
BASE_UNIT=/etc/systemd/system/magnetra-btdigg.service
CFFI_DROP=/etc/systemd/system/magnetra-btdigg.service.d/50-magnetra-cffi.conf
CHROMIUM_DROP=/etc/systemd/system/magnetra-btdigg.service.d/60-magnetra-chromium.conf
ENV_FILE=/etc/magnetra-btdigg/gateway.env
BACKUP=/opt/magnetra-btdigg/.gateway-before-visible-denial-20261115.py
OLD_BLOB=f188d69f6b9fa40c7a81f498b5bb2ae0c4b9f0e5
NEW_BLOB=3553454a227614d5d108aa548a074a4536eb74e1

for tool in git systemctl python3 cmp grep mktemp install mv; do
  command -v "$tool" >/dev/null 2>&1 || fail "Missing preflight tool: $tool"
done
for path in "$ROOT" "$SOURCE" "$DEST" "$BASE_UNIT" "$CFFI_DROP" \
            "$CHROMIUM_DROP" "$ENV_FILE" /opt/magnetra-btdigg; do
  [[ ! -L "$path" ]] || fail 'Protected path cannot be a symlink.'
done
for path in "$SOURCE" "$DEST" "$BASE_UNIT" "$CFFI_DROP" \
            "$CHROMIUM_DROP" "$ENV_FILE"; do
  [[ -s "$path" && -f "$path" ]] || fail 'Protected gateway file missing.'
done
[[ "$(git hash-object -- "$SOURCE")" == "$NEW_BLOB" ]] ||
  fail 'Checkout does not contain the reviewed source blob.'
grep -qxF 'Description=Magnetra private BTDigg-only gateway (Rock64)' "$BASE_UNIT" ||
  fail 'Unexpected 8796 systemd unit.'
grep -qxF 'Environment=MAGNETRA_BTDIGG_CHROMIUM_BRIDGE=1' "$CHROMIUM_DROP" ||
  fail 'Chromium opt-in missing.'
grep -qxF 'ExecStart=/usr/bin/python3 -I /opt/magnetra-btdigg/btdigg_gateway.py' "$CHROMIUM_DROP" ||
  fail 'Chromium effective command not pinned.'
grep -qxF 'LoadCredential=browser_token:/etc/magnetra-btdigg/browser-token' "$CHROMIUM_DROP" ||
  fail 'Chromium private credential not pinned.'
systemctl is-active --quiet "$SERVICE" ||
  fail 'Production BTDigg gateway is not active.'
DROPS="$(systemctl show "$SERVICE" -p DropInPaths --value)" ||
  fail 'Cannot inspect effective drop-ins.'
read -r -a DROP_ARRAY <<< "$DROPS"
(( ${#DROP_ARRAY[@]} == 2 )) ||
  fail 'Unexpected number of gateway overrides.'
CFFI_SEEN=0
CHROMIUM_SEEN=0
for drop in "${DROP_ARRAY[@]}"; do
  case "$drop" in
    "$CFFI_DROP") CFFI_SEEN=1 ;;
    "$CHROMIUM_DROP") CHROMIUM_SEEN=1 ;;
    *) fail 'Unknown gateway override; refusing to modify service.' ;;
  esac
done
(( CFFI_SEEN == 1 && CHROMIUM_SEEN == 1 )) ||
  fail 'Expected CFFI + Chromium migration overrides not active.'
EFFECTIVE_EXEC="$(systemctl show "$SERVICE" -p ExecStart --value)" ||
  fail 'Cannot inspect effective launch command.'
[[ "$EFFECTIVE_EXEC" == *"/usr/bin/python3"* &&
   "$EFFECTIVE_EXEC" == *"/opt/magnetra-btdigg/btdigg_gateway.py"* &&
   "$EFFECTIVE_EXEC" != *"btdigg_cffi_gateway.py"* ]] ||
  fail 'Effective gateway does not execute isolated Chromium bridge.'

# Authenticated loopback /healthz only: no BTDigg navigation, no source calls.
local_health(){
  # Type=simple marks the process active before Python has bound its socket.
  # For a newly restarted service, poll only localhost /healthz (no BTDigg
  # source traffic). The initial preflight remains a one-shot health read.
  local tries="${1:-1}"
  python3 - "$ENV_FILE" "$tries" <<'PY'
import re,sys,time
from pathlib import Path
from urllib.request import Request,urlopen
m=re.fullmatch(r"MAGNETRA_BTDIGG_TOKEN=([A-Za-z0-9_-]{48,256})\n",
               Path(sys.argv[1]).read_text(encoding="ascii"))
if m is None: raise SystemExit(1)
tries=int(sys.argv[2])
if not 1 <= tries <= 30: raise SystemExit(1)
req=Request("http://127.0.0.1:8796/healthz",
            headers={"Authorization":"Bearer "+m.group(1)},method="GET")
for attempt in range(tries):
    try:
        with urlopen(req,timeout=2) as response:
            if response.status == 200 and response.read(100) == b'{"ok":true}':
                raise SystemExit(0)
    except OSError:
        pass
    if attempt+1 < tries:
        time.sleep(0.5)
raise SystemExit(1)
PY
}
local_health || fail 'Authenticated local health failed; no mutation.'
python3 - "$SOURCE" <<'PY' || fail 'Reviewed Python source syntax invalid.'
import ast,sys
from pathlib import Path
ast.parse(Path(sys.argv[1]).read_text(encoding="utf8"))
PY
OLD_INSTALLED="$(git hash-object -- "$DEST")" ||
  fail 'Cannot fingerprint current production code.'
if [[ "$OLD_INSTALLED" == "$NEW_BLOB" ]]; then
  echo 'ALREADY_APPLIED: production gateway matches reviewed source; no restart.'
  exit 0
fi
[[ "$OLD_INSTALLED" == "$OLD_BLOB" ]] ||
  fail 'Installed gateway is not the expected prior version; manual audit required.'
# A failed first update deliberately preserves a private rollback backup.
# Reuse it only when it is a real regular file with the EXACT old Git blob.
# Never overwrite, delete, or trust an unexpected preexisting backup.
BACKUP_REUSED=0
if [[ -e "$BACKUP" || -L "$BACKUP" ]]; then
  [[ -f "$BACKUP" && ! -L "$BACKUP" ]] ||
    fail 'Existing rollback backup is unsafe.'
  [[ "$(git hash-object -- "$BACKUP")" == "$OLD_BLOB" ]] ||
    fail 'Existing rollback backup does not match the exact prior gateway.'
  BACKUP_REUSED=1
fi

if [[ "$MODE" == check ]]; then
  echo 'READY: exact old/new code and Chromium overrides verified; no changes.'
  if (( BACKUP_REUSED )); then echo 'ROLLBACK_BACKUP=EXACT_OLD_VERSION_REUSED'; fi
  echo 'NEXT: sudo bash rock64/update-btdigg-chromium-bridge.sh --apply --owner-approved'
  exit 0
fi

# All tests are offline/local fixtures. No provider origin is contacted.
cd "$ROOT"
python3 -B -m unittest rock64.test_btdigg_gateway rock64.test_btdigg_chromium_bridge -q ||
  fail 'Offline gateway/bridge regression failed; no changes.'

STAGE="$(mktemp /opt/magnetra-btdigg/.visible-denial-new.XXXXXXXX)"
ROLLBACK=0
finish(){
  code=$?
  trap - EXIT
  if (( ROLLBACK == 1 )); then
    echo 'ROLLBACK: restoring exact prior BTDigg gateway.' >&2
    if [[ -s "$BACKUP" && ! -L "$BACKUP" ]]; then
      install -m 0644 "$BACKUP" "$DEST" || true
      systemctl restart "$SERVICE" || true
    fi
    if systemctl is-active --quiet "$SERVICE" && local_health 30; then
      echo 'ROLLBACK_GATEWAY_HEALTH=PASS' >&2
    else
      echo 'ROLLBACK_GATEWAY_HEALTH=NOT_VERIFIED' >&2
    fi
  fi
  rm -f -- "$STAGE"
  exit "$code"
}
trap finish EXIT
if (( BACKUP_REUSED == 0 )); then
  install -m 0600 "$DEST" "$BACKUP"
fi
[[ "$(git hash-object -- "$BACKUP")" == "$OLD_BLOB" ]] ||
  fail 'Private rollback backup not verified.'
install -m 0644 "$SOURCE" "$STAGE"
[[ "$(git hash-object -- "$STAGE")" == "$NEW_BLOB" ]] ||
  fail 'Staged code does not match reviewed blob.'
ROLLBACK=1
mv -f -- "$STAGE" "$DEST"
systemctl restart "$SERVICE"
systemctl is-active --quiet "$SERVICE" ||
  fail 'BTDigg 8796 service restart failed.'
local_health 30 || fail 'New 8796 gateway failed authenticated loopback health.'
ROLLBACK=0
echo 'PASS: updated ONLY the Chromium-backed 8796 gateway; rollback backup retained.'
echo 'NO_BTDIGG_SEARCH; CHROMIUM_UNTOUCHED; NO_CLOUDFLARE_DEPLOY.'
