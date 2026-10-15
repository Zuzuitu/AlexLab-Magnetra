#!/usr/bin/env bash
# Explicit owner-approved, first-install only. No changes to old daemons or tunnels.
set -Eeuo pipefail
umask 077
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1

die() { printf 'STOP: %s\n' "$1" >&2; exit 1; }
(( EUID == 0 )) || die 'root privileges required for the owner-approved installation'
for cmd in python3 systemctl install mkdir ss; do
  command -v "$cmd" >/dev/null 2>&1 || die "missing required command: $cmd"
done

ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd -P)"
SRC="$ROOT/rock64/magnetra_gateway.py"
CHECK="$ROOT/rock64/check-magnetra-gateway.py"
SERVICE="$ROOT/rock64/magnetra-gateway.service"
DEST=/opt/magnetra-gateway
CFG=/etc/magnetra-gateway
UNIT=/etc/systemd/system/magnetra-gateway.service
EZTV_ENV=/etc/magnetra-eztv/gateway.env

for path in "$SRC" "$CHECK" "$SERVICE"; do
  [[ -f "$path" && -s "$path" && ! -L "$path" ]] || die 'source checkout incomplete or symlinked'
done
for path in "$DEST" "$CFG" "$UNIT"; do
  [[ ! -e "$path" && ! -L "$path" ]] || die 'dedicated destination already exists; refusing to overwrite'
done
[[ "$(systemctl show -p LoadState --value magnetra-gateway.service)" == not-found ]] ||
  die 'magnetra-gateway.service already exists in systemd'
for unit in magnetra-btdigg.service magnetra-btdigg-tunnel.service magnetra-eztv.service; do
  systemctl is-active --quiet "$unit" || die 'required existing Magnetra service is not active'
done

# Read-only preflight: credentials, existing service health, whole-port collision.
# Nothing is written until this entire Python preflight and offline test pass.
python3 -B - "$SRC" "$CHECK" "$SERVICE" "$EZTV_ENV" <<'PY'
import ast
import http.client
import os
import pathlib
import re
import socket
import stat
import sys

src, checker, service, env = map(pathlib.Path, sys.argv[1:])
for path in (src, checker):
    ast.parse(path.read_text(encoding="utf-8"), filename=path.name)
unit = service.read_text(encoding="utf-8")
required = (
    "DynamicUser=yes", "EnvironmentFile=/etc/magnetra-gateway/gateway.env",
    "EnvironmentFile=/etc/magnetra-eztv/gateway.env",
    "ExecStart=/usr/bin/python3 -I /opt/magnetra-gateway/magnetra_gateway.py",
    "MemoryMax=128M", "CPUQuota=20%", "ProtectSystem=strict",
    "NoNewPrivileges=yes", "PrivateTmp=yes",
)
if not all(s in unit for s in required):
    raise SystemExit("STOP: unreviewed central systemd unit")
if "magnetra-btdigg" in unit.lower() or "cloudflared" in unit.lower():
    raise SystemExit("STOP: shared-service reference in central unit")
directory = env.parent
for path, directory_expected in ((directory, True), (env, False)):
    st = path.lstat()
    if st.st_uid != 0 or (st.st_mode & 0o022):
        raise SystemExit("STOP: insecure existing EZTV credential permissions")
    if directory_expected and not stat.S_ISDIR(st.st_mode):
        raise SystemExit("STOP: invalid EZTV credential directory")
    if not directory_expected and (
        not stat.S_ISREG(st.st_mode) or st.st_mode & 0o077 or st.st_size > 400
    ):
        raise SystemExit("STOP: invalid EZTV credential file")
fd = os.open(env, os.O_RDONLY | os.O_NOFOLLOW)
try:
    original = os.read(fd, 401).decode("ascii")
finally:
    os.close(fd)
if not re.fullmatch(r"MAGNETRA_EZTV_TOKEN=[A-Za-z0-9_-]{48,256}\n", original):
    raise SystemExit("STOP: existing EZTV token format incompatible")

for port in (8796, 8797):
    try:
        c = http.client.HTTPConnection("127.0.0.1", port, timeout=3)
        c.request("GET", "/healthz")
        res = c.getresponse()
        res.read(1024)
        result = res.status
        c.close()
    except (OSError, TimeoutError):
        result = 0
    if result != 401:
        raise SystemExit("STOP: existing gateway unauthenticated health is not 401")
s = socket.socket()
try:
    s.bind(("127.0.0.1", 8798))
except OSError:
    raise SystemExit("STOP: 127.0.0.1:8798 already in use")
finally:
    s.close()
print("PASS: existing 8796/8797 auth and central port 8798 preflight")
PY

[[ -z "$(ss -H -ltn '( sport = :8798 )')" ]] ||
  die 'port 8798 already has a listener on some interface'
python3 -B -m unittest discover -s "$ROOT/rock64" -p 'test_magnetra_*.py' -q

CREATED_DEST=0
CREATED_CFG=0
CREATED_UNIT=0
FINISHED=0
rollback() {
  result=$?
  trap - EXIT
  if (( FINISHED == 0 )); then
    if (( CREATED_UNIT == 1 )); then
      systemctl disable --now magnetra-gateway.service >/dev/null 2>&1 || true
      rm -f -- "$UNIT"
      systemctl daemon-reload >/dev/null 2>&1 || true
    fi
    if (( CREATED_CFG == 1 )); then rm -rf --one-file-system -- "$CFG"; fi
    if (( CREATED_DEST == 1 )); then rm -rf --one-file-system -- "$DEST"; fi
    printf 'STOP: central-only installation failed; new files rolled back. Existing services untouched.\n' >&2
  fi
  exit "$result"
}
trap rollback EXIT

mkdir -m 0755 -- "$DEST"
CREATED_DEST=1
mkdir -m 0700 -- "$CFG"
CREATED_CFG=1
install -m 0444 -- "$SRC" "$DEST/magnetra_gateway.py"
install -m 0444 -- "$CHECK" "$DEST/check-magnetra-gateway.py"
python3 -B - "$CFG/gateway.env" "$EZTV_ENV" <<'PY'
import os
import pathlib
import re
import secrets
import sys

target, source = map(pathlib.Path, sys.argv[1:])
existing = source.read_text(encoding="ascii")
match = re.fullmatch(r"MAGNETRA_EZTV_TOKEN=([A-Za-z0-9_-]{48,256})\n", existing)
if not match:
    raise SystemExit("STOP: existing token rejected")
token = secrets.token_urlsafe(48)
if token == match.group(1):
    raise SystemExit("STOP: unexpected credential collision")
fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
with os.fdopen(fd, "w", encoding="ascii") as output:
    output.write("MAGNETRA_GATEWAY_TOKEN=" + token + "\n")
PY
install -m 0644 -- "$SERVICE" "$UNIT"
CREATED_UNIT=1
systemctl daemon-reload
systemctl enable --now magnetra-gateway.service >/dev/null
systemctl is-active --quiet magnetra-gateway.service ||
  die 'central service failed to start'

# The installer performs ONLY a local smoke check; source-positive acceptance
# is a separate read-only invocation that makes bounded genuine EZTV requests.
python3 -B "$DEST/check-magnetra-gateway.py" --smoke
FINISHED=1
printf 'PASS: new gateway 127.0.0.1:8798 installed; 8796/8797 retained.\n'
printf 'NEXT (read-only genuine-source acceptance, no identifiers printed):\n'
printf '  sudo python3 -B /opt/magnetra-gateway/check-magnetra-gateway.py\n'
printf 'No Cloudflare route, Worker secret or PWA deployment was changed.\n'
