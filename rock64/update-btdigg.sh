#!/usr/bin/env bash
# Guarded replacement of ONLY the installed Magnetra BTDigg Python gateway.
# Never rewrites tokens, tunnels, the router, or other project services.
set -Eeuo pipefail
umask 077

if (( EUID != 0 )); then
  echo "STOP: run with sudo from the verified Magnetra checkout." >&2
  exit 1
fi
ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd)"
SOURCE="$ROOT/rock64/btdigg_gateway.py"
DEST=/opt/magnetra-btdigg/btdigg_gateway.py
CFG=/etc/magnetra-btdigg/gateway.env
UNIT=/etc/systemd/system/magnetra-btdigg.service
SERVICE=magnetra-btdigg.service
for path in /opt/magnetra-btdigg /etc/magnetra-btdigg "$DEST" "$CFG" "$UNIT"; do
  if [[ -L "$path" ]]; then
    echo "STOP: unexpected symlink on protected Magnetra path." >&2
    exit 1
  fi
done
for path in "$SOURCE" "$DEST" "$CFG" "$UNIT"; do
  if [[ ! -s "$path" ]]; then
    echo "STOP: missing protected Magnetra file." >&2
    exit 1
  fi
done
grep -qxF 'Description=Magnetra private BTDigg-only gateway (Rock64)' "$UNIT" || {
  echo "STOP: existing systemd unit is not owned by Magnetra." >&2
  exit 1
}
grep -qxF 'ExecStart=/usr/bin/python3 -I /opt/magnetra-btdigg/btdigg_gateway.py' "$UNIT" || {
  echo "STOP: installed Python launch command differs." >&2
  exit 1
}
systemctl is-active --quiet "$SERVICE" || {
  echo "STOP: existing Magnetra gateway is not active; diagnose before replacing." >&2
  exit 1
}
python3 -B -m unittest discover -s "$ROOT/rock64" -p 'test_*.py' -q
python3 - "$SOURCE" <<'PY'
import ast, pathlib, sys
ast.parse(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"), filename=sys.argv[1])
PY
if cmp -s "$SOURCE" "$DEST"; then
  echo "PASS: installed gateway already matches validated source."
  exit 0
fi

STAGE="$(mktemp /opt/magnetra-btdigg/.gateway-new.XXXXXXXX)"
BACKUP="$(mktemp /opt/magnetra-btdigg/.gateway-old.XXXXXXXX)"
ROLLBACK_NEEDED=0
finish() {
  local exit_code=$?
  trap - EXIT
  if (( ROLLBACK_NEEDED )); then
    echo "STOP: gateway validation failed; restoring previous Magnetra code." >&2
    if [[ -s "$BACKUP" ]]; then
      install -m 0644 "$BACKUP" "$DEST"
      systemctl restart "$SERVICE" || true
    fi
  fi
  rm -f -- "$STAGE" "$BACKUP"
  exit "$exit_code"
}
trap finish EXIT
install -m 0644 "$DEST" "$BACKUP"
install -m 0644 "$SOURCE" "$STAGE"
ROLLBACK_NEEDED=1
mv -f -- "$STAGE" "$DEST"
systemctl restart "$SERVICE"
systemctl is-active --quiet "$SERVICE" || exit 1

# Local authenticated health check, without printing or exporting any token.
python3 - "$CFG" <<'PY'
import re
import sys
from urllib.request import Request, urlopen
try:
    with open(sys.argv[1], encoding="ascii") as f:
        line = f.read()
    match = re.fullmatch(r"MAGNETRA_BTDIGG_TOKEN=([A-Za-z0-9_-]{48,256})\n", line)
    if match is None:
        raise ValueError("invalid local credential file")
    req = Request("http://127.0.0.1:8796/healthz",
                  headers={"authorization": "Bearer " + match.group(1)})
    import time
    for attempt in range(10):
        try:
            with urlopen(req, timeout=3) as response:
                if response.status == 200 and response.read(1000) == b'{"ok":true}':
                    break
        except (OSError, ValueError):
            pass
        time.sleep(0.3)
    else:
        raise ValueError("gateway did not reach healthy state")
except Exception:
    raise SystemExit("STOP: private gateway health probe failed.")
print("PASS: Magnetra gateway responded to authenticated localhost health check.")
PY
ROLLBACK_NEEDED=0
echo "PASS: Magnetra gateway upgraded; existing tunnel and secrets untouched."
