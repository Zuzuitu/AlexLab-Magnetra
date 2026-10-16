#!/usr/bin/env bash
# Explicit-owner-only, guarded one-time 8798 central upgrade.
# Does not edit or restart BTDigg 8796, EZTV 8797 or Cloudflare Tunnel.
set -Eeuo pipefail
umask 077
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
stop() { printf 'STOP: %s\n' "$*" >&2; exit 1; }
[[ $# -eq 1 && "$1" == "--install" ]] || stop 'explicit --install required'
(( EUID == 0 )) || stop 'root required after owner authorization'
for cmd in python3 systemctl install mktemp cp rm stat mv grep; do
 command -v "$cmd" >/dev/null || stop "missing $cmd"
done
ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd -P)"
BASE=/opt/magnetra-gateway
ACTIVE="$BASE/magnetra_gateway.py"
HTML="$BASE/magnetra_html_egress.py"
SOURCE="$ROOT/rock64/magnetra_gateway.py"
HTML_SOURCE="$ROOT/rock64/magnetra_html_egress.py"
UNIT=/etc/systemd/system/magnetra-gateway.service
for path in "$ACTIVE" "$SOURCE" "$HTML_SOURCE" "$UNIT" "$BASE/check-magnetra-gateway.py"; do
 [[ -s "$path" && -f "$path" && ! -L "$path" ]] || stop 'gateway source/installation incomplete or symlinked'
done
[[ -d "$BASE" && ! -L "$BASE" ]] || stop 'unexpected gateway directory'
for path in "$BASE" "$ACTIVE" "$UNIT"; do
 [[ "$(stat -c %u "$path")" == 0 ]] || stop 'gateway path must be root-owned'
done
[[ ! -e "$HTML" && ! -L "$HTML" ]] || stop 'already upgraded or module collision; refuse to overwrite'
grep -Fq 'ExecStart=/usr/bin/python3 -I /opt/magnetra-gateway/magnetra_gateway.py' "$UNIT" ||
 stop 'systemd unit changed; cannot upgrade'
for unit in magnetra-gateway.service magnetra-eztv.service magnetra-btdigg.service magnetra-btdigg-tunnel.service; do
 systemctl is-active --quiet "$unit" || stop "required service inactive: $unit"
done
python3 -B -m unittest discover -s "$ROOT/rock64" -p 'test_*.py' -q
python3 -B - "$SOURCE" "$HTML_SOURCE" <<'PY'
import ast,pathlib,sys
for raw in sys.argv[1:]:
 p=pathlib.Path(raw)
 ast.parse(p.read_text(encoding="utf8"),filename=p.name)
PY
python3 -B - <<'PY'
import http.client
for port in (8796,8797,8798):
 c=http.client.HTTPConnection("127.0.0.1",port,timeout=3)
 try:
  c.request("GET","/healthz")
  response=c.getresponse()
  response.read(512)
  if response.status!=401:raise SystemExit(f"STOP: unauthenticated health {port} != 401")
 finally:c.close()
print("PREFLIGHT_OK: existing 8796, 8797, 8798 authentication intact")
PY

BACKUP="$(mktemp -d /var/tmp/magnetra-8798-rollback.XXXXXXXX)"
cp -p -- "$ACTIVE" "$BACKUP/original.py"
DONE=0
rollback(){
 rc=$?
 trap - EXIT
 if (( DONE == 0 )); then
  install -m 0444 -- "$BACKUP/original.py" "$BASE/.rollback.py" || true
  mv -f -- "$BASE/.rollback.py" "$ACTIVE" || true
  rm -f -- "$HTML"
  systemctl restart magnetra-gateway.service >/dev/null 2>&1 || true
  printf 'STOP: central upgrade failed; original 8798 source restored. Check service status.\n' >&2
 fi
 rm -rf --one-file-system -- "$BACKUP"
 exit "$rc"
}
trap rollback EXIT

install -m 0444 -- "$HTML_SOURCE" "$BASE/.html-new.py"
mv -f -- "$BASE/.html-new.py" "$HTML"
install -m 0444 -- "$SOURCE" "$BASE/.gateway-new.py"
mv -f -- "$BASE/.gateway-new.py" "$ACTIVE"
systemctl restart magnetra-gateway.service
systemctl is-active --quiet magnetra-gateway.service || stop 'central service restart failed'
python3 -B - <<'PY'
import http.client
for port in (8796,8797,8798):
 c=http.client.HTTPConnection("127.0.0.1",port,timeout=3)
 try:
  c.request("GET","/healthz")
  response=c.getresponse()
  response.read(512)
  if response.status!=401:raise SystemExit(f"STOP: post-install auth changed on {port}")
 finally:c.close()
print("POST_INSTALL_OK: unauthenticated health returns 401 for all three ports")
PY
DONE=1
printf 'PASS: isolated 8798 code upgraded. EZTV/BTDigg/tunnel not changed.\n'
printf 'No Cloudflare secret or protected PWA deployment was performed.\n'
