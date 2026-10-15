#!/usr/bin/env bash
# Install ONLY the optional new EZTV Cloudflare Tunnel systemd unit.
# Requires owner-created remotely managed Cloudflare Tunnel and Published application route.
set -Eeuo pipefail
umask 077
export LC_ALL=C
stop() { printf 'STOP: %s\n' "$*" >&2; exit 1; }

[[ "$(id -u)" == 0 ]] || stop "use sudo; only after creating the dedicated tunnel"
[[ -x /usr/local/bin/cloudflared ]] || stop "cloudflared not at expected path"
[[ -d /etc/magnetra-eztv && ! -L /etc/magnetra-eztv ]] || stop "EZTV credentials directory missing or linked"
[[ -f /etc/magnetra-eztv/gateway.env ]] || stop "EZTV gateway not installed"
systemctl is-active --quiet magnetra-eztv.service || stop "EZTV gateway not active"
systemctl is-active --quiet magnetra-btdigg.service || stop "BTDigg not active; do not alter it"
[[ "$(curl --noproxy '*' -sS -o /dev/null -w '%{http_code}' --max-time 3 http://127.0.0.1:8797/healthz)" == 401 ]] || stop "EZTV loopback auth check must give HTTP 401"

ver="$(/usr/local/bin/cloudflared --version)" || stop "cloudflared version unavailable"
digits="$(printf '%s\n' "$ver" | grep -oE '[0-9]{4}\.[0-9]{1,2}\.[0-9]+' | head -n 1)" || stop "cannot parse cloudflared version"
year="$(printf '%s' "$digits" | cut -d. -f 1)"
month="$(printf '%s' "$digits" | cut -d. -f 2)"
if (( 10#$year < 2025 )) || (( 10#$year == 2025 && 10#$month < 4 )); then
  stop "token-file requires cloudflared >= 2025.4.0; do not update global binary"
fi
/usr/local/bin/cloudflared tunnel run --help 2>&1 | grep -q -- '--token-file' || stop "installed cloudflared does not advertise --token-file"

token_path=/etc/magnetra-eztv/tunnel-token
unit_path=/etc/systemd/system/magnetra-eztv-tunnel.service
script_dir="$(cd -- "$(dirname -- "$0")" && pwd -P)"
source_unit="$script_dir/magnetra-eztv-tunnel.service"
[[ -f "$source_unit" && ! -L "$source_unit" ]] || stop "missing dedicated unit template beside this script"
[[ ! -e "$token_path" && ! -L "$token_path" ]] || stop "token already exists; will not overwrite"
[[ ! -e "$unit_path" && ! -L "$unit_path" ]] || stop "unit already exists; will not overwrite"
[[ "$(systemctl show -p LoadState --value magnetra-eztv-tunnel.service)" == not-found ]] || stop "name collision with existing service"
grep -Fqx 'LoadCredential=tunnel-token:/etc/magnetra-eztv/tunnel-token' "$source_unit" || stop "unexpected credential source"
grep -Fqx 'Environment=TUNNEL_TOKEN_FILE=%d/tunnel-token' "$source_unit" || stop "unexpected credential use"
grep -Fqx 'ExecStart=/usr/local/bin/cloudflared tunnel --no-autoupdate run' "$source_unit" || stop "unexpected tunnel binary/arguments"

printf '%s\n' 'The NEW Cloudflare tunnel token will be captured invisibly. Do not enter any existing BTDigg token.'
python3 -I - "$token_path" <<'PY'
import getpass
import os
import pathlib
import re
import sys
path = pathlib.Path(sys.argv[1])
try:
    fd = os.open("/dev/tty", os.O_RDWR)
except OSError:
    sys.exit("STOP: interactive TTY required; no changes made")
os.close(fd)
try:
    token = getpass.getpass("New EZTV tunnel token (hidden): ").strip()
except (EOFError, KeyboardInterrupt):
    sys.exit("STOP: cancelled; no changes made")
if not 64 <= len(token) <= 8192 or re.fullmatch(r"[A-Za-z0-9._=-]+", token) is None:
    sys.exit("STOP: invalid token length/shape; no changes made")
flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
if hasattr(os, "O_NOFOLLOW"):
    flags |= os.O_NOFOLLOW
try:
    fd = os.open(path, flags, 0o600)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb", closefd=False) as f:
            f.write(token.encode("ascii"))
            f.flush()
            os.fsync(f.fileno())
    finally:
        os.close(fd)
except OSError:
    sys.exit("STOP: unable to store token in root-only file")
finally:
    del token
print("PASS: new EZTV-only token secured in a root-only file")
PY

install -o root -g root -m 0644 -- "$source_unit" "$unit_path"
systemctl daemon-reload
systemctl enable --now magnetra-eztv-tunnel.service || stop "dedicated tunnel start failed; no other unit touched"
systemctl is-active --quiet magnetra-eztv-tunnel.service || stop "dedicated tunnel not active"
systemctl is-active --quiet magnetra-btdigg.service || stop "BTDigg is no longer active, investigate separately"
printf '%s\n' 'PASS: ONLY magnetra-eztv-tunnel.service installed, enabled and active.'
printf '%s\n' 'Verify Cloudflare Tunnel Healthy and public HTTPS unauthenticated /healthz returns HTTP 401.'
printf '%s\n' 'No Worker Secret, PWA production deploy, global tunnel or DNS change performed by this script.'
