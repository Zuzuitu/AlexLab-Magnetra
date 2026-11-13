#!/usr/bin/env bash
# Owner-only rollback of the exact known CFFI -> Chromium 60-drop-in migration.
# Preserves original CFFI 50-drop-in, existing Tailscale Chromium and Cloudflare.
set -Eeuo pipefail
umask 077
[[ $# -eq 1 && "$1" == "--rollback" ]] || {
  echo "STOP: use --rollback explicitly" >&2; exit 2;
}
(( EUID == 0 )) || { echo "STOP: run with sudo" >&2; exit 2; }
fail(){ echo "STOP: $*" >&2; exit 1; }

SERVICE=magnetra-btdigg.service
BASE=/opt/magnetra-btdigg/btdigg_gateway.py
BACKUP=/opt/magnetra-btdigg/.btdigg-base-before-chromium.py
OLD=/etc/systemd/system/magnetra-btdigg.service.d/50-magnetra-cffi.conf
CHROME=/etc/systemd/system/magnetra-btdigg.service.d/60-magnetra-chromium.conf
CREDENTIAL=/etc/magnetra-btdigg/browser-token
ENV=/etc/magnetra-btdigg/gateway.env
CFFI_EXEC=/opt/magnetra-btdigg/btdigg_cffi_gateway.py

for file in "$BASE" "$BACKUP" "$OLD" "$CHROME" "$CREDENTIAL" "$ENV"; do
  [[ -f "$file" && ! -L "$file" ]] || fail "Required CFFI backup, migration drop-in or credential missing."
done
DROPS="$(systemctl show "$SERVICE" -p DropInPaths --value)"
[[ "$DROPS" == *"$OLD"* && "$DROPS" == *"$CHROME"* ]] || fail "Expected CFFI and Chromium drop-ins not active."
[[ "$(wc -w <<< "$DROPS")" -eq 2 ]] || fail "Unknown additional drop-ins; manual review required."
grep -qxF 'Environment=MAGNETRA_BTDIGG_CHROMIUM_BRIDGE=1' "$CHROME" || fail "Chromium override not recognized."
grep -qxF 'ExecStart=/usr/bin/python3 -I /opt/magnetra-btdigg/btdigg_gateway.py' "$CHROME" || fail "Chromium ExecStart unknown."
grep -qxF 'LoadCredential=browser_token:/etc/magnetra-btdigg/browser-token' "$CHROME" || fail "Chromium credential not recognized."
grep -qxF 'ExecStart=/opt/magnetra-btdigg/.venv-cffi-0.17.0/bin/python -I /opt/magnetra-btdigg/btdigg_cffi_gateway.py' "$OLD" || fail "CFFI override changed."
EXEC="$(systemctl show "$SERVICE" -p ExecStart --value)"
[[ "$EXEC" == *"$BASE"* && "$EXEC" != *"$CFFI_EXEC"* ]] || fail "Current effective entrypoint is not Chromium base gateway."

# No source searches. Keep the original backup until CFFI health passes.
STAGE="$(mktemp /opt/magnetra-btdigg/.restore-btdigg.XXXXXXXX)"
trap 'rm -f -- "$STAGE"' EXIT
install -m 0644 "$BACKUP" "$STAGE"
mv -f -- "$STAGE" "$BASE"
rm -f -- "$CHROME"
systemctl daemon-reload
NEW_EXEC="$(systemctl show "$SERVICE" -p ExecStart --value)"
[[ "$NEW_EXEC" == *"$CFFI_EXEC"* ]] || fail "CFFI ExecStart did not resume; manual inspection required."
systemctl restart "$SERVICE"
systemctl is-active --quiet "$SERVICE" || fail "CFFI process failed restart."

python3 - "$ENV" <<'PY' || fail "Restored CFFI /healthz did not pass; inspect local logs."
import re,sys,time
from pathlib import Path
from urllib.request import Request,urlopen
match=re.fullmatch(r"MAGNETRA_BTDIGG_TOKEN=([A-Za-z0-9_-]{48,256})\n",
                   Path(sys.argv[1]).read_text(encoding="ascii"))
if match is None: raise SystemExit(1)
req=Request("http://127.0.0.1:8796/healthz",
            headers={"Authorization":"Bearer "+match.group(1)})
for _ in range(20):
    try:
        with urlopen(req,timeout=2) as r:
            if r.status==200 and r.read(100)==b'{"ok":true}':
                print("RESTORED_CFFI_AUTH_HEALTH_PASS")
                raise SystemExit(0)
    except OSError:
        pass
    time.sleep(.5)
raise SystemExit(1)
PY
rm -f -- "$CREDENTIAL" "$BACKUP"
echo "CFFI_RESTORED: original 50-drop-in retained, Chromium 60-drop-in removed."
echo "NO_BTDIGG_SEARCH_PERFORMED; Chromium session and PWA untouched."
