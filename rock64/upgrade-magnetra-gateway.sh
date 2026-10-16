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
  if systemctl restart magnetra-gateway.service >/dev/null 2>&1; then
    if python3 -B "$ROOT/rock64/wait-magnetra-8798.py" --rollback; then
      printf 'ROLLBACK_VERIFIED: original 8798 source restored and HTTP 401 accepted.\n' >&2
    else
      printf 'STOP: original source restored, but 8798 readiness UNVERIFIED. Inspect service status.\n' >&2
    fi
  else
    printf 'STOP: rollback restart FAILED; original source restored but service requires inspection.\n' >&2
  fi
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
# Type=simple only confirms the process was launched, NOT that 8798 is listening.
# Wait at most 12 seconds for unauthenticated GET /healthz -> 401 on localhost.
# Only local socket connect refusals are retried; never upstream HTTP/429.
python3 -B "$ROOT/rock64/wait-magnetra-8798.py" --post-restart ||
  stop 'new 8798 listener did not become safely ready'
# Existing independent BTDigg/EZTV services must still deny unauthenticated access.
python3 -B - <<'PY'
import http.client
for port in (8796, 8797):
 c=http.client.HTTPConnection("127.0.0.1", port, timeout=3)
 try:
  c.request("GET", "/healthz")
  response=c.getresponse()
  response.read(512)
  if response.status != 401:
   raise SystemExit(f"STOP: independent gateway {port} unauthenticated health != 401")
 finally:
  c.close()
print("POST_INSTALL_OK: BTDigg 8796, EZTV 8797 and central 8798 each require authentication")
PY
# A source-owned search + details magnet must work via the actual 8798 listener
# before marking the upgrade complete; a failure triggers automatic rollback.
python3 -B "$ROOT/rock64/check-magnetra-html.py" || stop 'real 8798 source validation failed'
DONE=1
printf 'PASS: isolated 8798 code upgraded. EZTV/BTDigg/tunnel not changed.\n'
printf 'No Cloudflare secret or protected PWA deployment was performed.\n'
