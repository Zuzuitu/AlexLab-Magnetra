#!/usr/bin/env bash
# Opt-in PRIVATE Tailscale HTTPS view of already-running Chromium noVNC.
# Does not restart Chromium, change Tailscale Serve :443, use Funnel,
# modify Cloudflare/DNS or create source searches.
set -Eeuo pipefail
umask 077

usage(){
 echo 'Usage: bash rock64/install-btdigg-private-novnc-https.sh --check | --apply --owner-approved' >&2
 exit 2
}
if [[ "$#" == 1 && "$1" == --check ]]; then
 MODE=check
elif [[ "$#" == 2 && "$1" == --apply && "$2" == --owner-approved ]]; then
 MODE=apply
else
 usage
fi
fail(){ echo "STOP: $*" >&2; exit 1; }
[[ "$(id -un)" == runner && "$EUID" -ne 0 ]] ||
 fail 'Must run as unprivileged runner.'
ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"
[[ "$ROOT" == "$HOME/magnetra-cffi-live-20261028" ]] ||
 fail 'Unexpected checkout; no changes.'
cd "$ROOT"
PY="$ROOT/rock64/btdigg_novnc_private_relay.py"
TEMPLATE="$ROOT/rock64/magnetra-btdigg-novnc-private.service"
UNIT="$HOME/.config/systemd/user/magnetra-btdigg-novnc-private.service"

for bin in systemctl sudo tailscale python3 ss curl install cmp; do
 command -v "$bin" >/dev/null 2>&1 || fail "Missing tool $bin"
done
[[ -f "$PY" && -f "$TEMPLATE" && ! -L "$PY" && ! -L "$TEMPLATE" ]] ||
 fail 'Expected reviewed relay source/unit not present.'
if [[ -e "$UNIT" ]]; then
 [[ ! -L "$UNIT" && -f "$UNIT" ]] ||
  fail 'Existing service unit is not a regular file.'
 cmp -s "$TEMPLATE" "$UNIT" ||
  fail 'Service unit has changed from the reviewed template.'
fi
systemctl --user is-active --quiet magnetra-btdigg-browser.service ||
 fail 'Existing Chromium 18896 service not active. Do not restart it.'
[[ -n "$(ss -H -ltn '( sport = :6088 )')" ]] ||
 fail 'Existing tailnet-only noVNC 6088 listener unavailable.'
TS_IP="$(tailscale ip -4)" ||
 fail 'Tailscale is not running.'
python3 - "$TS_IP" <<'PY' || fail 'Invalid local Tailscale IPv4'
import ipaddress,sys
try:
 ip=ipaddress.IPv4Address(sys.argv[1])
 octets=ip.packed
 assert octets[0] == 100 and 64 <= octets[1] < 128
except (ValueError,AssertionError):
 sys.exit(1)
PY
# Refuse to overwrite a pre-existing Serve/Funnel port or another local app.
STATUS="$(sudo tailscale serve status --json)" ||
 fail 'Cannot inspect current private Tailscale Serve configuration.'
if [[ "$STATUS" == *':8444'* || "$STATUS" == *'"8444"'* ]]; then
 fail 'Tailscale port 8444 already configured; do not overwrite its route.'
fi
[[ -z "$(ss -H -ltn '( sport = :8444 )')" ]] ||
 fail 'HTTPS port 8444 already bound; no changes.'
# A previous safe installation may have started the isolated adapter
# successfully, but our immediate curl raced its socket bind. Accept ONLY
# the reviewed, running user-systemd service which owns loopback 6089.
# Other listeners remain fail-closed and are never replaced or restarted.
SERVICE=magnetra-btdigg-novnc-private.service
ADAPTER_PRESENT=0
LISTENER="$(ss -H -ltnp '( sport = :6089 )')"
if [[ -n "$LISTENER" ]]; then
 [[ -f "$UNIT" && ! -L "$UNIT" ]] ||
  fail 'Port 6089 occupied without reviewed user service.'
 cmp -s "$TEMPLATE" "$UNIT" ||
  fail 'Port 6089 occupied with a different service unit.'
 systemctl --user is-active --quiet "$SERVICE" ||
  fail 'Port 6089 occupied but reviewed relay service is not active.'
 MAIN_PID="$(systemctl --user show "$SERVICE" -p MainPID --value)"
 [[ "$MAIN_PID" =~ ^[1-9][0-9]*$ ]] ||
  fail 'Unable to verify running relay PID.'
 [[ "$LISTENER" == *"127.0.0.1:6089"* &&
    "$LISTENER" == *"pid=$MAIN_PID,"* ]] ||
  fail 'Port 6089 listener is not the reviewed loopback relay process.'
 ADAPTER_PRESENT=1
fi

# Read-only preflight is resumable: no second relay and no Tailscale change.
if [[ "$MODE" == check ]]; then
 if [[ "$ADAPTER_PRESENT" == 1 ]]; then
  HTTP_CODE="$(curl --noproxy '*' -s -o /dev/null -w '%{http_code}' \
    --connect-timeout 2 --max-time 3 http://127.0.0.1:6089/vnc.html)" ||
   fail 'Existing isolated relay is not healthy.'
  [[ "$HTTP_CODE" == 200 ]] ||
   fail 'Existing relay returned an unexpected noVNC HTTP response.'
  echo 'READY: existing healthy owner-managed relay 6089, HTTPS 8444 unused.'
 else
  echo 'READY: noVNC 6088 alive, 6089 unused, 8444 unused.'
 fi
 echo 'NO_CHANGES; NO_BTDIGG_REQUESTS; CHROMIUM_18896=UNCHANGED'
 exit 0
fi

python3 -B -m unittest rock64.test_btdigg_novnc_private_relay -q ||
 fail 'Offline relay tests failed before installation.'
if [[ "$ADAPTER_PRESENT" == 0 ]]; then
 if [[ -e "$UNIT" ]]; then
  # A prior partially completed attempt installed and enabled this unit.
  # Do not start/replace it blindly if it crashed or was deliberately stopped.
  systemctl --user is-active --quiet "$SERVICE" ||
   fail 'Existing relay is inactive; inspect its journal before resuming.'
 else
  mkdir -p "$HOME/.config/systemd/user"
  chmod 700 "$HOME/.config/systemd/user"
  install -m 0644 "$TEMPLATE" "$UNIT"
  systemctl --user daemon-reload
  systemctl --user enable --now "$SERVICE" ||
   fail 'Private relay service did not start.'
 fi
fi
# Allow the fresh Python process to discover Tailscale and bind socket.
# systemctl Type=simple active does NOT mean the socket is already listening.
# Check only private noVNC, without any source requests, for a bounded interval.
RELAY_OK=0
for attempt in {1..20}; do
 if systemctl --user is-active --quiet "$SERVICE"; then
  LISTENER="$(ss -H -ltnp '( sport = :6089 )')"
  MAIN_PID="$(systemctl --user show "$SERVICE" -p MainPID --value)"
  if [[ "$MAIN_PID" =~ ^[1-9][0-9]*$ &&
        "$LISTENER" == *"127.0.0.1:6089"* &&
        "$LISTENER" == *"pid=$MAIN_PID,"* ]]; then
   HTTP_CODE="$(curl --noproxy '*' -s -o /dev/null -w '%{http_code}' \
    --connect-timeout 1 --max-time 2 http://127.0.0.1:6089/vnc.html)" || true
   if [[ "$HTTP_CODE" == 200 ]]; then RELAY_OK=1; break; fi
  fi
 fi
 sleep 0.4
done
if [[ "$RELAY_OK" != 1 ]]; then
 echo 'ADAPTER_DIAG_BEGIN' >&2
 systemctl --user show "$SERVICE" \
  -p ActiveState -p SubState -p Result -p ExecMainStatus -p NRestarts >&2 || true
 echo 'ADAPTER_DIAG_END' >&2
 fail 'Private noVNC relay did not become healthy; inspect its user journal.'
fi
# Configures ONLY new :8444 port. Explicit Serve, NOT Funnel/public.
sudo tailscale serve --bg --https=8444 http://127.0.0.1:6089 ||
 fail 'Tailscale HTTPS 8444 configuration failed; existing 443 unmodified.'
sudo tailscale serve status
echo 'BTDIGG_PRIVATE_NOVNC_HTTPS=CONFIGURED_PORT_8444'
echo 'CHROMIUM_18896=UNCHANGED; GATEWAY_8796=UNCHANGED'
echo 'NO_CAPTCHA_SOLVER; NO_BTDIGG_SEARCH; NO_FUNNEL'
# Print the node's actual private MagicDNS name only to the owner's terminal.
# No private hostname or credential is ever committed to this repository.
TAIL_DNS="$(tailscale status --json | python3 -c '
import json,re,sys
try:
 h=json.load(sys.stdin).get("Self",{}).get("DNSName","").rstrip(".")
 print(h if re.fullmatch(r"[a-z0-9-]+[.][a-z0-9-]+[.]ts[.]net",h) else "")
except (ValueError,TypeError,KeyError):
 print("")
' || true)"
if [[ -n "$TAIL_DNS" ]]; then
 echo "OPEN_PRIVATE_URL=https://$TAIL_DNS:8444/vnc.html"
else
 echo 'OPEN_PRIVATE_URL=Use the Rock64 MagicDNS FQDN from tailscale status, HTTPS port 8444 /vnc.html'
fi
