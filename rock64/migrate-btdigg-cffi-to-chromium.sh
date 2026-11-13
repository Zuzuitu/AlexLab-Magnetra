#!/usr/bin/env bash
# Owner-controlled CFFI -> Chromium gateway migration. DEFAULT READ-ONLY.
# Never starts/stops Chromium, navigates BTDigg, rotates credentials or changes
# Cloudflare, DNS, tunnel, Flud or any non-BTDigg service.
set -Eeuo pipefail
umask 077

if [[ $# -eq 1 && "$1" == "--check" ]]; then
  MODE=check
elif [[ $# -eq 2 && "$1" == "--activate" && "$2" == "--owner-approved" ]]; then
  MODE=activate
else
  echo "STOP: use --check (read-only) or --activate --owner-approved (explicit migration)" >&2
  exit 2
fi
(( EUID == 0 )) || { echo "STOP: use sudo; owner-only operation." >&2; exit 2; }

fail() { echo "STOP: $*" >&2; exit 1; }
ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd -P)"
SERVICE=magnetra-btdigg.service
CFFI_DROP=/etc/systemd/system/magnetra-btdigg.service.d/50-magnetra-cffi.conf
CHROME_DROP=/etc/systemd/system/magnetra-btdigg.service.d/60-magnetra-chromium.conf
OLD_CHROME_DROP=/etc/systemd/system/magnetra-btdigg.service.d/20-owner-chromium-bridge.conf
BASE=/opt/magnetra-btdigg/btdigg_gateway.py
SOURCE="$ROOT/rock64/btdigg_gateway.py"
BACKUP=/opt/magnetra-btdigg/.btdigg-base-before-chromium.py
OLD_TOKEN=/home/runner/.local/state/magnetra-btdigg-browser/gateway.token
NEW_TOKEN=/etc/magnetra-btdigg/browser-token
GATEWAY_ENV=/etc/magnetra-btdigg/gateway.env
CFFI_PY=/opt/magnetra-btdigg/.venv-cffi-0.17.0/bin/python
CFFI_EXEC=/opt/magnetra-btdigg/btdigg_cffi_gateway.py

for file in "$CFFI_DROP" "$BASE" "$SOURCE" "$OLD_TOKEN" "$GATEWAY_ENV" "$CFFI_EXEC"; do
  [[ -f "$file" && ! -L "$file" ]] || fail "Expected protected file missing or symlinked."
done
for file in "$BACKUP" "$NEW_TOKEN" "$CHROME_DROP" "$OLD_CHROME_DROP"; do
  [[ ! -e "$file" && ! -L "$file" ]] || fail "Migration or prior Chromium override already exists; no overwrite."
done
[[ -x "$CFFI_PY" && -d /opt/magnetra-btdigg ]] || fail "Known isolated CFFI environment unavailable."
systemctl is-active --quiet "$SERVICE" || fail "CFFI service is not active."
DROPS="$(systemctl show "$SERVICE" -p DropInPaths --value)" || fail "Cannot read effective overrides."
[[ "$DROPS" == "$CFFI_DROP" ]] || fail "Unknown, missing or stacked systemd overrides; expected one CFFI override."
EXEC="$(systemctl show "$SERVICE" -p ExecStart --value)" || fail "Cannot read effective command."
[[ "$EXEC" == *"$CFFI_EXEC"* && "$EXEC" == *"$CFFI_PY"* ]] || fail "Effective ExecStart is not reviewed CFFI."
grep -qxF "ExecStart=$CFFI_PY -I $CFFI_EXEC" "$CFFI_DROP" || fail "CFFI drop-in diverges from reviewed command."
grep -qxF 'ExecStart=/usr/bin/python3 -I /opt/magnetra-btdigg/btdigg_gateway.py' /etc/systemd/system/magnetra-btdigg.service || fail "Base unit changed."
python3 - "$SOURCE" <<'PY' || fail "New gateway source failed local syntax check."
import ast,sys
from pathlib import Path
ast.parse(Path(sys.argv[1]).read_text(encoding="utf8"))
PY

# Authenticated localhost *read-only* browser state; never /v1/search.
# Source is still on Too Many Requests / verified_tabs=0: fail before writes.
if ! python3 - "$OLD_TOKEN" <<'PY'
import json,re,stat,sys
from pathlib import Path
from urllib.request import Request,urlopen
p=Path(sys.argv[1])
if p.is_symlink() or not p.is_file():
    raise SystemExit("BROWSER_READINESS=NOT_READY")
st=p.stat()
if not stat.S_ISREG(st.st_mode) or st.st_mode & 0o077 or st.st_size>300:
    raise SystemExit("BROWSER_READINESS=NOT_READY")
token=p.read_text(encoding="ascii").strip()
if not re.fullmatch(r"[A-Za-z0-9_-]{48,256}",token):
    raise SystemExit("BROWSER_READINESS=NOT_READY")
req=Request("http://127.0.0.1:18896/v1/browser-state",
            headers={"Authorization":"Bearer "+token,"Accept":"application/json"},
            method="GET")
try:
    with urlopen(req,timeout=4) as response:
        body=response.read(4097)
        if response.status!=200 or len(body)>4096:
            raise ValueError("invalid response")
    state=json.loads(body)
except (OSError,ValueError,TypeError):
    raise SystemExit("BROWSER_READINESS=NOT_READY")
verified=(type(state) is dict and state.get("browser_connected") is True
          and type(state.get("verified_tabs")) is int and state["verified_tabs"]>=1
          and state.get("selected_tab_verified") is True)
modern=(type(state) is dict
        and state.get("visible_source_rate_limited") is False
        and state.get("new_searches_paused") is False)
legacy=(type(state) is dict and "visible_source_rate_limited" not in state
        and type(state.get("open_tabs")) is int and state["open_tabs"]==1
        and state.get("verified_tabs")==1
        and state.get("new_searches_paused") is False
        and state.get("last_navigation_status") is None)
if not verified or not (modern or legacy):
    raise SystemExit("BROWSER_READINESS=NOT_READY")
print("BROWSER_READINESS=VERIFIED_LOCAL_TAB")
PY
then
  echo "STOP: BTDigg is not verified; CFFI remains active and unchanged. No browser search attempted." >&2
  exit 3
fi

# Authenticated production health; no BTDigg source query.
python3 - "$GATEWAY_ENV" <<'PY' || fail "Existing CFFI health unavailable; no mutation."
import re,sys
from pathlib import Path
from urllib.request import Request,urlopen
match=re.fullmatch(r"MAGNETRA_BTDIGG_TOKEN=([A-Za-z0-9_-]{48,256})\n",
                   Path(sys.argv[1]).read_text(encoding="ascii"))
if match is None: raise SystemExit("AUTH_CONFIG_INVALID")
req=Request("http://127.0.0.1:8796/healthz",
            headers={"Authorization":"Bearer "+match.group(1)})
with urlopen(req,timeout=4) as response:
    if response.status!=200 or response.read(100)!=b'{"ok":true}':
        raise SystemExit("CFFI_HEALTH_INVALID")
print("EXISTING_CFFI_HEALTH_PASS")
PY

if [[ "$MODE" == check ]]; then
  echo "CFFI_TO_CHROMIUM_PREFLIGHT=READY; no files or services changed."
  exit 0
fi

# All offline regressions must pass before activation.
python3 -B -m unittest rock64.test_btdigg_gateway rock64.test_btdigg_chromium_bridge -q

STAGED_BASE=
STAGED_DROP=
STAGED_TOKEN=
CHANGED=0
SUCCESS=0
cleanup() {
  local code=$?
  trap - EXIT
  if (( CHANGED == 1 && SUCCESS == 0 )); then
    echo "ROLLBACK_ATTEMPT: restore CFFI without touching browser." >&2
    if [[ -f "$BACKUP" && ! -L "$BACKUP" ]]; then
      install -m 0644 "$BACKUP" "$BASE" || true
    fi
    rm -f -- "$CHROME_DROP" "$NEW_TOKEN"
    systemctl daemon-reload || true
    systemctl restart "$SERVICE" || true
    if systemctl is-active --quiet "$SERVICE"; then
      echo "ROLLBACK_CFFI_SERVICE_ACTIVE: check authenticated /healthz separately" >&2
    else
      echo "ROLLBACK_CFFI_SERVICE_UNHEALTHY: manual inspection required" >&2
    fi
  fi
  for temp_file in "$STAGED_BASE" "$STAGED_DROP" "$STAGED_TOKEN"; do
    if [[ -n "$temp_file" ]]; then rm -f -- "$temp_file"; fi
  done
  if (( SUCCESS == 0 )); then
    rm -f -- "$BACKUP"
  fi
  exit "$code"
}
trap cleanup EXIT
STAGED_BASE="$(mktemp /opt/magnetra-btdigg/.chromium-gateway.XXXXXXXX)"
STAGED_DROP="$(mktemp /etc/systemd/system/magnetra-btdigg.service.d/.chromium-override.XXXXXXXX)"
STAGED_TOKEN="$(mktemp /etc/magnetra-btdigg/.chromium-token.XXXXXXXX)"
cp -p -- "$BASE" "$BACKUP"
chmod 0600 "$BACKUP"
install -m 0644 "$SOURCE" "$STAGED_BASE"
install -m 0600 "$OLD_TOKEN" "$STAGED_TOKEN"
cat > "$STAGED_DROP" <<'EOF'
[Service]
Environment=MAGNETRA_BTDIGG_CHROMIUM_BRIDGE=1
ExecStart=
ExecStart=/usr/bin/python3 -I /opt/magnetra-btdigg/btdigg_gateway.py
LoadCredential=browser_token:/etc/magnetra-btdigg/browser-token
EOF
chmod 0600 "$STAGED_DROP"
CHANGED=1
mv -f -- "$STAGED_BASE" "$BASE"
mv -- "$STAGED_TOKEN" "$NEW_TOKEN"
mv -- "$STAGED_DROP" "$CHROME_DROP"
systemctl daemon-reload
NEW_EXEC="$(systemctl show "$SERVICE" -p ExecStart --value)"
NEW_DROPS="$(systemctl show "$SERVICE" -p DropInPaths --value)"
[[ "$NEW_EXEC" == *"/usr/bin/python3"* && "$NEW_EXEC" == *"$BASE"* && "$NEW_EXEC" != *"$CFFI_EXEC"* ]] || fail "Effective override is not the reviewed Chromium gateway."
[[ "$NEW_DROPS" == *"$CFFI_DROP"* && "$NEW_DROPS" == *"$CHROME_DROP"* ]] || fail "Effective override set changed."
systemctl restart "$SERVICE"
systemctl is-active --quiet "$SERVICE" || fail "New gateway did not become active."

python3 - "$GATEWAY_ENV" <<'PY' || fail "Chromium gateway failed authenticated local health."
import re,sys,time
from pathlib import Path
from urllib.request import Request,urlopen
match=re.fullmatch(r"MAGNETRA_BTDIGG_TOKEN=([A-Za-z0-9_-]{48,256})\n",
                   Path(sys.argv[1]).read_text(encoding="ascii"))
if not match: raise SystemExit(1)
req=Request("http://127.0.0.1:8796/healthz",
            headers={"Authorization":"Bearer "+match.group(1)})
for _ in range(20):
    try:
        with urlopen(req,timeout=2) as response:
            if response.status==200 and response.read(100)==b'{"ok":true}':
                print("CHROMIUM_GATEWAY_AUTHENTICATED_HEALTH_PASS")
                raise SystemExit(0)
    except OSError:
        pass
    time.sleep(.5)
raise SystemExit(1)
PY
SUCCESS=1
echo "MIGRATION_CFFI_TO_CHROMIUM=ACTIVE; CFFI drop-in preserved, private backup retained."
echo "NO_BTDIGG_SEARCH_PERFORMED; Chrome/VNC/tmux unchanged. Rollback script is available."
