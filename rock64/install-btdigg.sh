#!/usr/bin/env bash
# Idempotent, guarded local installation. Only dedicated Magnetra paths/units.
set -euo pipefail
umask 077

if (( EUID != 0 )); then
  echo "Run as sudo ./rock64/install-btdigg.sh from a verified Magnetra checkout." >&2
  exit 1
fi

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ! -s "$ROOT/rock64/btdigg_gateway.py" || ! -s "$ROOT/rock64/magnetra-btdigg.service" ]]; then
  echo "STOP: not inside a complete Magnetra checkout." >&2
  exit 1
fi
command -v python3 >/dev/null
command -v systemctl >/dev/null

# Ensure we never install into another project's folder or mutate their units.
DEST=/opt/magnetra-btdigg
CFG=/etc/magnetra-btdigg
UNIT=/etc/systemd/system/magnetra-btdigg.service
if [[ -L "$DEST" || -L "$CFG" || -L "$UNIT" ]]; then
  echo "STOP: unexpected symbolic link on protected Magnetra path." >&2
  exit 1
fi
if [[ -f "$UNIT" ]] && ! grep -qF 'Description=Magnetra private BTDigg-only gateway (Rock64)' "$UNIT"; then
  echo "STOP: service name already belongs to a different program." >&2
  exit 1
fi

python3 -m unittest discover -s "$ROOT/rock64" -p 'test_*.py' -v
python3 -m py_compile "$ROOT/rock64/btdigg_gateway.py"
install -d -m 0755 "$DEST"
install -d -m 0700 "$CFG"
install -m 0644 "$ROOT/rock64/btdigg_gateway.py" "$DEST/btdigg_gateway.py"
install -m 0644 "$ROOT/rock64/check-btdigg.py" "$DEST/check-btdigg.py"
install -m 0644 "$ROOT/rock64/magnetra-btdigg.service" "$UNIT"

if [[ ! -e "$CFG/gateway.env" ]]; then
  # Atomic creation, no secret printed, no committed token, no shell-history copy.
  python3 - "$CFG/gateway.env" <<'PY'
import os, secrets, sys
p = sys.argv[1]
fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, "w", encoding="ascii") as f:
    f.write("MAGNETRA_BTDIGG_TOKEN=" + secrets.token_urlsafe(48) + "\n")
PY
fi
chmod 0600 "$CFG/gateway.env"
python3 - "$CFG/gateway.env" <<'PY'
import re, sys
with open(sys.argv[1], encoding="ascii") as f:
    data=f.read()
if not re.fullmatch(r'MAGNETRA_BTDIGG_TOKEN=[A-Za-z0-9_-]{48,256}\n',data):
    raise SystemExit("STOP: existing secret file invalid; refusing to replace it.")
PY

systemctl daemon-reload
systemctl enable --now magnetra-btdigg.service
systemctl is-active --quiet magnetra-btdigg.service
echo "PASS: private gateway installed and running on 127.0.0.1:8796."
echo "Next (one-time genuine-source check, does not show credentials):"
echo "  sudo python3 /opt/magnetra-btdigg/check-btdigg.py"
echo "Never paste /etc/magnetra-btdigg/gateway.env into chat."
