#!/usr/bin/env bash
# One explicit owner-operated BTDigg diagnostic. No production install,
# daemon reload, service restart, token read, magnet print or automatic retries.
set -Eeuo pipefail
umask 077

if (( EUID == 0 )); then
  echo "STOP: run as a normal user, never sudo." >&2
  exit 2
fi
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
for path in "$ROOT/rock64/btdigg_cffi_candidate.py" \
            "$ROOT/rock64/diagnose_btdigg_cffi_exact.py"; do
  if [[ -L "$path" || ! -f "$path" ]]; then
    echo "STOP: missing or symlinked reviewed diagnostic." >&2
    exit 2
  fi
done
command -v python3 >/dev/null
command -v timeout >/dev/null
WORK="$(mktemp -d /tmp/magnetra-btdigg-once.XXXXXXXX)"
cleanup(){
  rm -rf -- "$WORK"
}
trap cleanup EXIT
python3 -m venv "$WORK/venv"
# Install a binary-only, pinned optional library INTO TMP; nothing global.
timeout 90 "$WORK/venv/bin/pip" --disable-pip-version-check --no-input \
  install --only-binary=:all: --quiet 'curl_cffi==0.17.0'
echo "ONE_SHOT_EXACT_RESULT_START"
timeout 25 "$WORK/venv/bin/python" "$ROOT/rock64/diagnose_btdigg_cffi_exact.py"
echo "ONE_SHOT_EXACT_RESULT_END"
