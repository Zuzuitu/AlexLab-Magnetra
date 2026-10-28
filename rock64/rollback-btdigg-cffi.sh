#!/usr/bin/env bash
# One-step owner rollback. Only reverses the known Magnetra cffi service override.
set -Eeuo pipefail
if (( EUID != 0 )); then echo "STOP: run via sudo" >&2; exit 2; fi
OVERRIDE=/etc/systemd/system/magnetra-btdigg.service.d/50-magnetra-cffi.conf
UNIT=/etc/systemd/system/magnetra-btdigg.service
SERVICE=magnetra-btdigg.service
[[ ! -L "$OVERRIDE" && -f "$OVERRIDE" && ! -L "$UNIT" ]] || { echo "STOP: unexpected override" >&2; exit 1; }
grep -qxF 'ExecStart=/opt/magnetra-btdigg/.venv-cffi-0.17.0/bin/python -I /opt/magnetra-btdigg/btdigg_cffi_gateway.py' "$OVERRIDE" || {
 echo "STOP: override is not the reviewed Magnetra candidate" >&2; exit 1;
}
grep -qxF 'ExecStart=/usr/bin/python3 -I /opt/magnetra-btdigg/btdigg_gateway.py' "$UNIT" || exit 1
rm -- "$OVERRIDE"
systemctl daemon-reload
systemctl restart "$SERVICE"
systemctl is-active --quiet "$SERVICE"
echo "BTDIGG_ORIGINAL_GATEWAY_RESTORED"
