#!/usr/bin/env bash
# Owner-run, zero-upstream-request, diagnostics-only patch for existing cffi.
# It refuses unknown/custom installations; never overwrites the base gateway.
set -Eeuo pipefail
umask 077
if (( EUID != 0 )); then
  echo "STOP: run with sudo; no changes made" >&2; exit 2
fi
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE=magnetra-btdigg.service
DEST=/opt/magnetra-btdigg
TARGET="$DEST/btdigg_cffi_candidate.py"
SOURCE="$ROOT/rock64/btdigg_cffi_candidate.py"
OVERRIDE=/etc/systemd/system/magnetra-btdigg.service.d/50-magnetra-cffi.conf
SECRETS=/etc/magnetra-btdigg/gateway.env
PYTHON="$DEST/.venv-cffi-0.17.0/bin/python"
PREVIOUS_BLOB=8f70fefa6a06159626afc6c9ad7eb3c6b530d8d0
# venv/bin/python is often a legitimate symlink to the system interpreter.
# Check its executability and isolated imports below; other paths must be real.
for p in "$DEST" "$TARGET" "$SOURCE" "$OVERRIDE" "$SECRETS"; do
  if [[ -L "$p" ]]; then echo "STOP: symlink on protected path" >&2; exit 1; fi
done
for p in "$TARGET" "$SOURCE" "$OVERRIDE" "$PYTHON" "$SECRETS"; do
  if [[ ! -f "$p" || ! -s "$p" ]]; then echo "STOP: missing source/active install" >&2; exit 1; fi
done
if ! grep -qxF 'ExecStart=/opt/magnetra-btdigg/.venv-cffi-0.17.0/bin/python -I /opt/magnetra-btdigg/btdigg_cffi_gateway.py' "$OVERRIDE"; then
  echo "STOP: service does not have the known cffi entrypoint" >&2; exit 1
fi
if [[ "$(git hash-object -- "$TARGET")" != "$PREVIOUS_BLOB" ]]; then
  echo "STOP: installed candidate differs from reviewed #232 source; no overwrite" >&2; exit 1
fi
systemctl is-active --quiet "$SERVICE" || {
  echo "STOP: current service is not active" >&2; exit 1
}
"$PYTHON" -I -c 'import curl_cffi; from curl_cffi import requests'
# All source tests are offline; no BTDigg request, no secrets read here.
python3 -B -m unittest discover -s "$ROOT/rock64" -p 'test_btdigg_cffi_*.py' -q
"$PYTHON" -I - "$SOURCE" <<'PY'
import ast, pathlib, sys
ast.parse(pathlib.Path(sys.argv[1]).read_text(encoding="utf8"))
print("CFFI_DIAGNOSTIC_SOURCE_SYNTAX_PASS")
PY

# Root-owned files only. Keep backup until authenticated /healthz passes.
NEW="$(mktemp "$DEST/.btdigg-cffi-diagnostics-new.XXXXXXXX")"
BACKUP="$(mktemp "$DEST/.btdigg-cffi-diagnostics-old.XXXXXXXX")"
changed=0
committed=0
restore() {
  local status=$?
  trap - EXIT
  if (( changed && ! committed )); then
    echo "DIAGNOSTIC_HEALTH_FAILED: restoring previous tested candidate" >&2
    if [[ -s "$BACKUP" ]]; then
      local restore_temp
      restore_temp="$(mktemp "$DEST/.btdigg-cffi-restore.XXXXXXXX")"
      install -m 0644 "$BACKUP" "$restore_temp"
      mv -f -- "$restore_temp" "$TARGET"
      systemctl restart "$SERVICE" || true
    fi
  fi
  rm -f -- "$NEW" "$BACKUP"
  exit "$status"
}
trap restore EXIT
install -m 0644 "$SOURCE" "$NEW"
cp -p -- "$TARGET" "$BACKUP"
mv -f -- "$NEW" "$TARGET"
changed=1
systemctl restart "$SERVICE"
systemctl is-active --quiet "$SERVICE"

# Existing loopback-only auth + health, no external source search.
"$PYTHON" -I - "$SECRETS" <<'PY'
import re, sys, time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
with open(sys.argv[1], encoding="ascii") as f:
    match = re.fullmatch(r"MAGNETRA_BTDIGG_TOKEN=([A-Za-z0-9_-]{48,256})\n",f.read())
if match is None:
    raise SystemExit("STOP: credential file format unexpected")
req=Request("http://127.0.0.1:8796/healthz",
            headers={"Authorization":"Bearer "+match.group(1)})
for _ in range(15):
    try:
        with urlopen(req,timeout=2) as response:
            if response.status==200 and response.read(1000)==b'{"ok":true}':
                print("CFFI_DIAGNOSTIC_LOCAL_HEALTH_PASS")
                break
    except (OSError, ValueError):
        pass
    time.sleep(.25)
else:
    raise SystemExit("STOP: authenticated local health failed")
PY
committed=1
echo "CFFI_DIAGNOSTIC_INSTALLED: existing transport unchanged; next real owner search will log only safe outcome metadata"
echo 'NO_UPSTREAM_SEARCH_WAS_SENT_BY_INSTALLER'
