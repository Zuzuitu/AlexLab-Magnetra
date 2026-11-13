#!/usr/bin/env bash
# Owner-invoked, opt-in production 8796 -> existing verified Chromium 18896.
# Does not navigate BTDigg, restart Chromium, change Cloudflare or log secrets.
set -Eeuo pipefail
umask 077
[[ "$#" -eq 1 && "$1" == "--enable" ]] || { echo "STOP: explicit --enable required" >&2; exit 2; }
(( EUID == 0 )) || { echo "STOP: run with sudo" >&2; exit 2; }
fail() { echo "STOP: $*" >&2; exit 1; }
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
GATEWAY=/opt/magnetra-btdigg/btdigg_gateway.py
CONFIG=/etc/magnetra-btdigg/gateway.env
BROWSER_TOKEN=/home/runner/.local/state/magnetra-btdigg-browser/gateway.token
CREDENTIAL=/etc/magnetra-btdigg/browser-token
DROP_DIR=/etc/systemd/system/magnetra-btdigg.service.d
DROP="$DROP_DIR/20-owner-chromium-bridge.conf"
SERVICE=magnetra-btdigg.service
for path in "$GATEWAY" "$CONFIG" "$BROWSER_TOKEN"; do
  [[ -f "$path" && ! -L "$path" ]] || fail "Protected existing file missing or symlinked."
done
[[ ! -e "$DROP" && ! -L "$DROP" ]] || fail "Bridge drop-in already exists; no overwrite."
[[ ! -e "$CREDENTIAL" && ! -L "$CREDENTIAL" ]] || fail "Browser service credential already exists."
[[ -d /etc/magnetra-btdigg && ! -L /etc/magnetra-btdigg ]] || fail "Protected configuration directory invalid."
[[ ! -L "$DROP_DIR" ]] || fail "Unexpected override directory symlink."
systemctl is-active --quiet "$SERVICE" || fail "Production gateway not active."
cmp -s "$ROOT/rock64/btdigg_gateway.py" "$GATEWAY" || fail "Installed source is not reviewed Chromium bridge gateway."

# Check current user-owned browser state locally without navigation.
python3 - "$BROWSER_TOKEN" <<'PY' || fail "Chromium not independently verified; production unchanged."
import json,re,stat,sys
from pathlib import Path
from urllib.request import Request,urlopen
p=Path(sys.argv[1]); st=p.stat()
if not stat.S_ISREG(st.st_mode) or st.st_mode & 0o077:
    raise SystemExit("STOP: browser token permissions invalid")
token=p.read_text(encoding="ascii").strip()
if not re.fullmatch(r"[A-Za-z0-9_-]{48,256}",token):
    raise SystemExit("STOP: browser credential invalid")
req=Request("http://127.0.0.1:18896/v1/browser-state",method="GET",
    headers={"authorization":"Bearer "+token,"accept":"application/json"})
try:
    with urlopen(req,timeout=4) as response:
        raw=response.read(4097)
        if response.status!=200 or len(raw)>4096: raise ValueError("response")
    state=json.loads(raw)
except (OSError,ValueError,TypeError):
    raise SystemExit("STOP: browser status unavailable")
# Modern browser: explicit visible denial detection. Legacy: a *single*
# already verified result tab, with no in-process navigation refusal.
# No refresh or navigation is performed here.
modern=(isinstance(state,dict)
        and state.get("visible_source_rate_limited") is False
        and state.get("new_searches_paused") is False)
legacy=(isinstance(state,dict)
        and "visible_source_rate_limited" not in state
        and type(state.get("open_tabs")) is int
        and state["open_tabs"]==1
        and state.get("verified_tabs")==1
        and state.get("new_searches_paused") is False
        and state.get("last_navigation_status") is None)
verified=(isinstance(state,dict)
          and state.get("browser_connected") is True
          and type(state.get("verified_tabs")) is int
          and state["verified_tabs"]>=1
          and state.get("selected_tab_verified") is True)
if not verified or not (modern or legacy):
    raise SystemExit("STOP: current browser lacks verified results or shows refusal")
print("CHROMIUM_READY: true; no source navigation")
PY

# Production health preflight, not a source query.
python3 - "$CONFIG" <<'PY' || fail "Production authenticated gateway unhealthy."
import re,sys
from pathlib import Path
from urllib.request import Request,urlopen
m=re.fullmatch(r"MAGNETRA_BTDIGG_TOKEN=([A-Za-z0-9_-]{48,256})\n",
               Path(sys.argv[1]).read_text(encoding="ascii"))
if not m: raise SystemExit(1)
req=Request("http://127.0.0.1:8796/healthz",
            headers={"authorization":"Bearer "+m.group(1)})
with urlopen(req,timeout=4) as response:
    if response.status!=200 or response.read(100)!=b'{"ok":true}':
        raise SystemExit(1)
print("EXISTING_GATEWAY_HEALTH_PASS")
PY

install -d -m 0700 "$DROP_DIR"
STAGE_TOKEN="$(mktemp /etc/magnetra-btdigg/.chromium-token.XXXXXXXX)"
STAGE_DROP="$(mktemp "$DROP_DIR/.chromium.XXXXXXXX")"
ROLLBACK_NEEDED=0
finish(){
  local code=$?
  trap - EXIT
  rm -f -- "$STAGE_TOKEN" "$STAGE_DROP"
  if (( ROLLBACK_NEEDED )); then
    rm -f -- "$DROP" "$CREDENTIAL"
    systemctl daemon-reload || true
    systemctl restart "$SERVICE" || true
    echo "ROLLBACK_ATTEMPTED: reviewed default gateway restored" >&2
  fi
  exit "$code"
}
trap finish EXIT
install -m 0600 "$BROWSER_TOKEN" "$STAGE_TOKEN"
cat > "$STAGE_DROP" <<'EOF'
[Service]
Environment=MAGNETRA_BTDIGG_CHROMIUM_BRIDGE=1
LoadCredential=browser_token:/etc/magnetra-btdigg/browser-token
EOF
chmod 0600 "$STAGE_DROP"
ROLLBACK_NEEDED=1
mv -- "$STAGE_TOKEN" "$CREDENTIAL"
mv -- "$STAGE_DROP" "$DROP"
systemctl daemon-reload
systemctl restart "$SERVICE"
systemctl is-active --quiet "$SERVICE" || fail "Production process did not restart."
python3 - "$CONFIG" <<'PY' || fail "Post-activation health failed."
import re,sys,time
from pathlib import Path
from urllib.request import Request,urlopen
m=re.fullmatch(r"MAGNETRA_BTDIGG_TOKEN=([A-Za-z0-9_-]{48,256})\n",
               Path(sys.argv[1]).read_text(encoding="ascii"))
if not m: raise SystemExit(1)
req=Request("http://127.0.0.1:8796/healthz",
            headers={"authorization":"Bearer "+m.group(1)})
for _ in range(10):
    try:
        with urlopen(req,timeout=2) as response:
            if response.status==200 and response.read(100)==b'{"ok":true}':
                print("CHROMIUM_BRIDGE_ENABLED: health pass, no search")
                raise SystemExit(0)
    except OSError:
        pass
    time.sleep(0.3)
raise SystemExit(1)
PY
ROLLBACK_NEEDED=0
echo "PASS: 8796 now uses verified Chromium on 18896. No BTDigg search performed."
