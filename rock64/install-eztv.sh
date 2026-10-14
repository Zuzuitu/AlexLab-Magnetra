#!/usr/bin/env bash
# Explicit opt-in ONLY. Installs a new dedicated service, never upgrades other units.
set -euo pipefail
umask 077
if (( EUID != 0 )); then
  echo "Run only after approving the separate EZTV service installation." >&2
  exit 1
fi
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
DEST=/opt/magnetra-eztv
CFG=/etc/magnetra-eztv
UNIT=/etc/systemd/system/magnetra-eztv.service
SRC="$ROOT/rock64/eztv_gateway.py"
SYSTEMD="$ROOT/rock64/magnetra-eztv.service"
for file in "$SRC" "$SYSTEMD"; do
  [[ -s "$file" && ! -L "$file" ]] || { echo "STOP: missing/untrusted EZTV source"; exit 1; }
done
for path in "$DEST" "$CFG" "$UNIT"; do
  [[ ! -L "$path" ]] || { echo "STOP: symlink on dedicated EZTV path"; exit 1; }
done
if [[ -e "$UNIT" ]]; then
  echo "STOP: service already installed; refusing to overwrite or restart."
  exit 1
fi
for command in python3 systemctl install; do
  command -v "$command" >/dev/null || { echo "STOP: missing $command"; exit 1; }
done
python3 -B -m unittest discover -s "$ROOT/rock64" -p 'test_eztv_gateway.py' -v
python3 -B - "$SRC" <<'PY'
import ast, pathlib, socket, sys
ast.parse(pathlib.Path(sys.argv[1]).read_text(encoding="utf8"))
s=socket.socket()
try:
    s.bind(("127.0.0.1",8797))
except OSError:
    raise SystemExit("STOP: 127.0.0.1:8797 is unavailable; nothing installed")
finally:
    s.close()
PY
install -d -m 0755 "$DEST"
install -d -m 0700 "$CFG"
install -m 0644 "$SRC" "$DEST/eztv_gateway.py"
if [[ ! -e "$CFG/gateway.env" ]]; then
  python3 - "$CFG/gateway.env" <<'PY'
import os, secrets, sys
fd=os.open(sys.argv[1],os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,"w",encoding="ascii") as f:
    f.write("MAGNETRA_EZTV_TOKEN="+secrets.token_urlsafe(48)+"\n")
PY
fi
python3 - "$CFG/gateway.env" <<'PY'
import pathlib,re,sys
p=pathlib.Path(sys.argv[1])
if not re.fullmatch(r'MAGNETRA_EZTV_TOKEN=[A-Za-z0-9_-]{48,256}\n',p.read_text(encoding='ascii')):
    raise SystemExit("STOP: existing EZTV credential file invalid; not replaced")
PY
chmod 0600 "$CFG/gateway.env"
install -m 0644 "$SYSTEMD" "$UNIT"
systemctl daemon-reload
systemctl enable --now magnetra-eztv.service
systemctl is-active --quiet magnetra-eztv.service
echo "PASS: dedicated EZTV API service on 127.0.0.1:8797"
echo "No tunnel created. No Worker secret configured. BTDigg and other projects unchanged."
