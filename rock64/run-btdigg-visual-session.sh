#!/usr/bin/env bash
# Human-controlled BTDigg browser session. No scraping, no CAPTCHA solving.
# noVNC: Tailscale IPv4:6088 only; VNC: loopback 127.0.0.1:5993 only.
set -Eeuo pipefail
umask 077

# Default stays temporary/manual. --persistent-backend is opt-in and
# uses a private on-disk Chromium profile plus an authenticated loopback API.
case "${1:-}" in
  "") VISUAL_MODE=temporary ;;
  "--persistent-backend") VISUAL_MODE=persistent ;;
  *) printf 'ERROR: Unsupported mode\n' >&2; exit 2 ;;
esac
export MAGNETRA_VISUAL_MODE="$VISUAL_MODE"

fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

[[ "$(id -u)" != 0 ]] || fail 'Run as the unprivileged Rock64 runner, not root.'
for tool in tailscale xvfb-run xauth x11vnc websockify chromium python3; do
  command -v "$tool" >/dev/null 2>&1 || fail "Missing $tool (install the missing Debian package first)."
done
[[ -f /usr/share/novnc/vnc.html ]] || fail 'No /usr/share/novnc/vnc.html; check Debian novnc installation.'

TS_IP="$(tailscale ip -4 2>/dev/null | head -n1)"
[[ -n "$TS_IP" ]] || fail 'Tailscale has no IPv4. Check tailscaled and tailscale status.'
python3 - "$TS_IP" <<'PY' || fail 'Not a valid Tailscale IPv4 address.'
import ipaddress, sys
try:
    octets = ipaddress.IPv4Address(sys.argv[1]).packed
    assert octets[0] == 100 and 64 <= octets[1] < 128
except (ValueError, AssertionError):
    sys.exit(1)
PY

mkdir -p "$HOME/.cache"
SESSION_DIR="$(mktemp -d "$HOME/.cache/magnetra-btdigg-gui.XXXXXXXX")"
chmod 700 "$SESSION_DIR"
export MAGNETRA_TS_IP="$TS_IP" MAGNETRA_SESSION_DIR="$SESSION_DIR"

if [[ "$VISUAL_MODE" == persistent ]]; then
  STATE_DIR="$HOME/.local/state/magnetra-btdigg-browser"
  [[ ! -L "$STATE_DIR" ]] || fail 'Persistent state directory cannot be a symlink.'
  mkdir -p "$STATE_DIR/profile"
  [[ ! -L "$STATE_DIR/profile" ]] || fail 'Browser profile cannot be a symlink.'
  chmod 700 "$STATE_DIR" "$STATE_DIR/profile"
  TOKEN_FILE="$STATE_DIR/gateway.token"
  if [[ ! -f "$TOKEN_FILE" ]]; then
    python3 - "$TOKEN_FILE" <<'PY'
import os, secrets, sys
path = sys.argv[1]
try:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
except FileExistsError:
    sys.exit(0)
with os.fdopen(fd, "w") as out:
    out.write(secrets.token_urlsafe(48))
PY
  fi
  [[ ! -L "$TOKEN_FILE" && -f "$TOKEN_FILE" ]] || fail 'Gateway credential file invalid.'
  chmod 600 "$TOKEN_FILE"
  export MAGNETRA_BTDIGG_TOKEN="$(cat "$TOKEN_FILE")"
  export MAGNETRA_BTDIGG_BROWSER_OPT_IN=1
  export MAGNETRA_BTDIGG_BROWSER_PORT=8798
  export MAGNETRA_BROWSER_PROFILE="$STATE_DIR/profile"
  export MAGNETRA_BROWSER_PYTHON="$HOME/.venvs/magnetra-browser/bin/python"
  export MAGNETRA_BROWSER_ENTRY="$(pwd -P)/rock64/btdigg_browser_backend.py"
  [[ -x "$MAGNETRA_BROWSER_PYTHON" && -f "$MAGNETRA_BROWSER_ENTRY" ]] ||
    fail 'Playwright venv or browser backend not present.'
  "$MAGNETRA_BROWSER_PYTHON" -c 'import playwright.sync_api' ||
    fail 'Playwright dependency missing in browser venv.'
  PASS_FILE="$STATE_DIR/vnc.pass"
  if [[ ! -f "$PASS_FILE" ]]; then
    printf '\nSet a private VNC password (first 8 characters are used by VNC).\n'
    x11vnc -storepasswd "$PASS_FILE" || fail 'Could not store VNC password.'
  fi
  [[ ! -L "$PASS_FILE" && -f "$PASS_FILE" ]] || fail 'VNC password file invalid.'
  chmod 600 "$PASS_FILE"
  export MAGNETRA_VNC_PASS="$PASS_FILE"
  printf 'Persistent browser profile enabled (private Rock64 user directory).\n'
else
  printf '\nSet a temporary VNC password (first 8 characters are used by VNC).\n'
  if ! x11vnc -storepasswd "$SESSION_DIR/vnc.pass"; then
    rm -rf -- "$SESSION_DIR"
    fail 'Could not create VNC password.'
  fi
  chmod 600 "$SESSION_DIR/vnc.pass"
  export MAGNETRA_VNC_PASS="$SESSION_DIR/vnc.pass"
fi

# xvfb-run handles Xauthority itself. The X11 server listens on no TCP port.
# The child runs in the foreground and cleans up all its processes on exit.
trap 'rm -rf -- "$SESSION_DIR"' EXIT
xvfb-run -a -s '-screen 0 1280x800x24 -nolisten tcp' bash -c '
  set -Eeuo pipefail
  VNC_PID=""; WS_PID=""; CHROME_PID=""
  cleanup() {
    for pid in "$CHROME_PID" "$WS_PID" "$VNC_PID"; do
      if [[ -n "$pid" ]]; then kill "$pid" 2>/dev/null || true; fi
    done
    for pid in "$CHROME_PID" "$WS_PID" "$VNC_PID"; do
      if [[ -n "$pid" ]]; then wait "$pid" 2>/dev/null || true; fi
    done
  }
  trap cleanup EXIT
  trap "exit 130" INT TERM

  x11vnc -norc -display "$DISPLAY" -localhost -rfbauth \
    "$MAGNETRA_VNC_PASS" -rfbport 5993 -forever -shared \
    -noxdamage -quiet >"$MAGNETRA_SESSION_DIR/vnc.log" 2>&1 &
  VNC_PID=$!

  websockify --web=/usr/share/novnc \
    "$MAGNETRA_TS_IP:6088" 127.0.0.1:5993 \
    >"$MAGNETRA_SESSION_DIR/websockify.log" 2>&1 &
  WS_PID=$!

  sleep 2
  kill -0 "$VNC_PID" 2>/dev/null || { echo "ERROR: x11vnc failed to start" >&2; exit 1; }
  kill -0 "$WS_PID" 2>/dev/null || { echo "ERROR: websockify failed to bind Tailscale IPv4:6088" >&2; exit 1; }

  if [[ "$MAGNETRA_VISUAL_MODE" == persistent ]]; then
    "$MAGNETRA_BROWSER_PYTHON" "$MAGNETRA_BROWSER_ENTRY" \
      >"$MAGNETRA_SESSION_DIR/bridge.log" 2>&1 &
    CHROME_PID=$!
  else
    chromium --user-data-dir="$MAGNETRA_SESSION_DIR/chromium-profile" \
      --no-first-run --no-default-browser-check --new-window \
      --window-size=1200,740 --window-position=15,15 \
      "https://btdig.com/search?order=0&q=The+Dog+Stars+2026" \
      >"$MAGNETRA_SESSION_DIR/chromium.log" 2>&1 &
    CHROME_PID=$!
  fi
  sleep 2
  kill -0 "$CHROME_PID" 2>/dev/null || { echo "ERROR: Chromium exited unexpectedly" >&2; exit 1; }

  printf "\n=== BTDIGG INTERACTIVE BROWSER ===\n"
  printf "Open the Tailscale iPhone app, then Safari:\n"
  printf "http://%s:6088/vnc.html?autoconnect=1&resize=remote\n" "$MAGNETRA_TS_IP"
  printf "Enter your VNC password. Interact with CAPTCHA manually if shown.\n"
  if [[ "$MAGNETRA_VISUAL_MODE" == persistent ]]; then
    printf "Local authenticated browser gateway is on loopback port 8798.\n"
    printf "Press Ctrl+C to stop it. Browser verification is saved in your private profile.\n"
    printf "No Cloudflare tunnel or Magnetra production route was changed.\n"
  else
    printf "Close Chromium or press Ctrl+C to end and delete this temporary profile.\n"
  fi
  wait "$CHROME_PID"
'
