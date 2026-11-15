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
if [[ -n "$(ss -H -ltn '( sport = :6089 )')" ]]; then
 fail 'Loopback adapter port 6089 already bound; no changes.'
fi

if [[ "$MODE" == check ]]; then
 echo 'READY: noVNC 6088 alive, 8444 unused, Chromium untouched.'
 echo 'NO_CHANGES; NO_BTDIGG_REQUESTS; TAILSCALE_SERVE_443=UNCHANGED'
 exit 0
fi

python3 -B -m unittest rock64.test_btdigg_novnc_private_relay -q ||
 fail 'Offline relay tests failed before installation.'
mkdir -p "$HOME/.config/systemd/user"
chmod 700 "$HOME/.config/systemd/user"
if [[ ! -e "$UNIT" ]]; then
 install -m 0644 "$TEMPLATE" "$UNIT"
fi
systemctl --user daemon-reload
systemctl --user enable --now magnetra-btdigg-novnc-private.service ||
 fail 'Private 6089 relay did not start.'
[[ "$(systemctl --user is-active magnetra-btdigg-novnc-private.service)" == active ]] ||
 fail 'Private 6089 adapter is not active.'
# GET only for the existing noVNC static entrypoint, never BTDigg itself.
HTTP_CODE="$(curl --noproxy '*' -sS -o /dev/null -w '%{http_code}' \
 --connect-timeout 3 --max-time 8 http://127.0.0.1:6089/vnc.html)" ||
 fail 'Private relay does not serve noVNC static assets.'
[[ "$HTTP_CODE" == 200 ]] ||
 fail 'Private relay noVNC HTML is not HTTP 200.'
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
