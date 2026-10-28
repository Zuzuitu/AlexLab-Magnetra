#!/usr/bin/env bash
# One-time owner-operated switch ONLY for existing Magnetra BTDigg Rock64.
# No source search, token echo, tunnel/DNS/Flud modification or retries.
set -Eeuo pipefail
umask 022

if (( EUID != 0 )) || [[ "${1:-}" != "--activate" || "${2:-}" != "--permission-confirmed" ]]; then
  echo "STOP: use sudo bash rock64/activate-btdigg-cffi.sh --activate --permission-confirmed only after confirming source access permission." >&2
  exit 2
fi
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
DEST=/opt/magnetra-btdigg
UNIT=/etc/systemd/system/magnetra-btdigg.service
UNIT_DIR=/etc/systemd/system/magnetra-btdigg.service.d
OVERRIDE="$UNIT_DIR/50-magnetra-cffi.conf"
SERVICE=magnetra-btdigg.service
VENV="$DEST/.venv-cffi-0.17.0"
SECRET=/etc/magnetra-btdigg/gateway.env
for path in "$DEST" "$UNIT" "$UNIT_DIR" "$OVERRIDE" "$VENV" "$SECRET" \
   "$DEST/btdigg_gateway.py" "$DEST/btdigg_cffi_candidate.py" "$DEST/btdigg_cffi_gateway.py"; do
  if [[ -L "$path" ]]; then echo "STOP: unexpected symlink on protected path" >&2; exit 1; fi
done
for file in "$UNIT" "$SECRET" "$DEST/btdigg_gateway.py" \
  "$ROOT/rock64/btdigg_cffi_candidate.py" "$ROOT/rock64/btdigg_cffi_gateway.py"; do
  if [[ ! -s "$file" ]]; then echo "STOP: protected source missing" >&2; exit 1; fi
done
if [[ -e "$OVERRIDE" || -e "$VENV" || -e "$DEST/btdigg_cffi_candidate.py" || -e "$DEST/btdigg_cffi_gateway.py" ]]; then
  echo "STOP: cffi installation already present, manual audit required" >&2
  exit 1
fi
if [[ -n "$(systemctl show --property=DropInPaths --value "$SERVICE")" ]]; then
  echo "STOP: service has pre-existing overrides; preserve them" >&2
  exit 1
fi
grep -qxF 'Description=Magnetra private BTDigg-only gateway (Rock64)' "$UNIT" || exit 1
grep -qxF 'ExecStart=/usr/bin/python3 -I /opt/magnetra-btdigg/btdigg_gateway.py' "$UNIT" || exit 1
systemctl is-active --quiet "$SERVICE" || { echo "STOP: old BTDigg service not active" >&2; exit 1; }

# Run offline tests before installing or changing the service.
python3 -B -m unittest discover -s "$ROOT/rock64" -p 'test_btdigg_cffi_*.py' -q
python3 - "$ROOT/rock64/btdigg_cffi_candidate.py" "$ROOT/rock64/btdigg_cffi_gateway.py" <<'PY'
import ast, pathlib, sys
for file in sys.argv[1:]:
    ast.parse(pathlib.Path(file).read_text(encoding="utf-8"), filename=file)
print("OFFLINE_CFFI_SOURCE_VALID")
PY

# Dedicated, root-owned venv. The original global interpreter stays untouched.
python3 -m venv "$VENV"
if ! timeout 150 "$VENV/bin/python" -m pip --disable-pip-version-check --no-input \
       install --only-binary=:all: --no-cache-dir 'curl_cffi==0.17.0'; then
  rm -rf -- "$VENV"
  echo "STOP: pinned isolated curl_cffi install failed; old service unchanged" >&2
  exit 1
fi
if ! "$VENV/bin/python" -I -c 'import curl_cffi; from curl_cffi import requests'; then
  rm -rf -- "$VENV"
  echo "STOP: isolated cffi import failed; old service unchanged" >&2
  exit 1
fi
install -m 0644 "$ROOT/rock64/btdigg_cffi_candidate.py" "$DEST/btdigg_cffi_candidate.py"
install -m 0644 "$ROOT/rock64/btdigg_cffi_gateway.py" "$DEST/btdigg_cffi_gateway.py"

rollback_needed=0
cleanup() {
  local code=$?
  trap - EXIT
  if (( rollback_needed )); then
    echo "STOP: candidate failed localhost check; restoring original gateway" >&2
    rm -f -- "$OVERRIDE"
    systemctl daemon-reload || true
    systemctl restart "$SERVICE" || true
    if ! systemctl is-active --quiet "$SERVICE"; then
      echo "ERROR: original gateway did not restart; investigate locally" >&2
    fi
  fi
  if (( code != 0 )); then
    rm -f -- "$DEST/btdigg_cffi_candidate.py" "$DEST/btdigg_cffi_gateway.py"
    rm -rf -- "$VENV"
  fi
  exit "$code"
}
trap cleanup EXIT
mkdir -p -m 0755 "$UNIT_DIR"
cat > "$OVERRIDE" <<'EOF'
[Service]
Environment=MAGNETRA_BTDIGG_CFFI_OPT_IN=1
Environment=MAGNETRA_BTDIGG_SOURCE_PERMISSION_CONFIRMED=1
ExecStart=
ExecStart=/opt/magnetra-btdigg/.venv-cffi-0.17.0/bin/python -I /opt/magnetra-btdigg/btdigg_cffi_gateway.py
EOF
chmod 0644 "$OVERRIDE"
rollback_needed=1
systemctl daemon-reload
systemctl restart "$SERVICE"
systemctl is-active --quiet "$SERVICE"

# No external BTDigg request. Read the pre-existing token only in this local
# process and verify authenticated loopback /healthz, never print the token.
python3 - "$SECRET" <<'PY'
import re, sys, time
from urllib.request import Request, urlopen
with open(sys.argv[1], encoding="ascii") as handle:
    match = re.fullmatch(r"MAGNETRA_BTDIGG_TOKEN=([A-Za-z0-9_-]{48,256})\n", handle.read())
if not match: raise SystemExit("STOP: token file format changed")
req = Request("http://127.0.0.1:8796/healthz",
              headers={"Authorization": "Bearer " + match.group(1)})
for _ in range(15):
    try:
        with urlopen(req, timeout=2) as response:
            if response.status == 200 and response.read(1000) == b'{"ok":true}':
                print("CFFI_AUTHENTICATED_LOCAL_HEALTH_PASS")
                break
    except (OSError, ValueError):
        pass
    time.sleep(.25)
else:
    raise SystemExit("STOP: local health unavailable")
PY
rollback_needed=0
echo "CFFI_ROCK64_SERVICE_ACTIVE: local authenticated health PASS"
echo "LIVE_BTDIGG_SEARCH_PENDING: verify in Magnetra iPhone; no source request was made by installer"
