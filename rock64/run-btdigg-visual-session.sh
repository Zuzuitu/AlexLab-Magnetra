#!/usr/bin/env bash
# Human-controlled BTDigg browser session. No scraping, no CAPTCHA solving.
# noVNC: Tailscale IPv4:6088 only; VNC: loopback 127.0.0.1:5993 only.
set -Eeuo pipefail
umask 077

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

printf '\nSet a temporary VNC password (at least 8 characters; VNC uses the first 8).\n'
if ! x11vnc -storepasswd "$SESSION_DIR/vnc.pass"; then
  rm -rf -- "$SESSION_DIR"
  fail 'Could not create VNC password.'
fi
chmod 600 "$SESSION_DIR/vnc.pass"

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
    "$MAGNETRA_SESSION_DIR/vnc.pass" -rfbport 5993 -forever -shared \
    -noxdamage -quiet >"$MAGNETRA_SESSION_DIR/vnc.log" 2>&1 &
  VNC_PID=$!

  websockify --web=/usr/share/novnc \
    "$MAGNETRA_TS_IP:6088" 127.0.0.1:5993 \
    >"$MAGNETRA_SESSION_DIR/websockify.log" 2>&1 &
  WS_PID=$!

  sleep 2
  kill -0 "$VNC_PID" 2>/dev/null || { echo "ERROR: x11vnc failed to start" >&2; exit 1; }
  kill -0 "$WS_PID" 2>/dev/null || { echo "ERROR: websockify failed to bind Tailscale IPv4:6088" >&2; exit 1; }

  chromium --user-data-dir="$MAGNETRA_SESSION_DIR/chromium-profile" \
    --no-first-run --no-default-browser-check --new-window \
    --window-size=1200,740 --window-position=15,15 \
    "https://btdig.com/search?order=0&q=The+Dog+Stars+2026" \
    >"$MAGNETRA_SESSION_DIR/chromium.log" 2>&1 &
  CHROME_PID=$!
  sleep 2
  kill -0 "$CHROME_PID" 2>/dev/null || { echo "ERROR: Chromium exited unexpectedly" >&2; exit 1; }

  printf "\n=== BTDIGG INTERACTIVE BROWSER ===\n"
  printf "Open the Tailscale iPhone app, then Safari:\n"
  printf "http://%s:6088/vnc.html?autoconnect=1&resize=remote\n" "$MAGNETRA_TS_IP"
  printf "Enter your VNC password. Interact with CAPTCHA manually if shown.\n"
  printf "Close Chromium or press Ctrl+C here to end and delete this temporary profile.\n"
  wait "$CHROME_PID"
'
