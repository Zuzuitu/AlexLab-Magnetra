#!/usr/bin/env bash
# Read-only, no secrets, no configuration mutation.
# Determines whether the existing BTDigg tunnel can be considered for
# one additional Cloudflare published application route.
set -uo pipefail
export LC_ALL=C
echo '=== EXISTING MAGNETRA SERVICES (no changes) ==='
for unit in magnetra-btdigg.service magnetra-btdigg-tunnel.service magnetra-eztv.service magnetra-eztv-tunnel.service; do
  state="$(systemctl is-active "$unit" 2>/dev/null || true)"
  case "$state" in active|inactive|failed|activating|deactivating) ;; *) state=not-found-or-unknown;; esac
  printf '%s: %s\n' "$unit" "$state"
done
echo '=== LOOPBACK LISTENERS ==='
for port in 8796 8797 8798; do
  count="$(ss -H -ltn "sport = :$port" 2>/dev/null | wc -l | tr -d ' ')" || count=unavailable
  case "$count" in 0|1|2|3|4|5|6|7|8|9) ;; *) count=unknown;; esac
  printf 'port_%s_listener_count: %s\n' "$port" "$count"
done
echo '=== LOCAL HEALTH UNAUTHENTICATED ==='
for port in 8796 8797; do
  result="$(curl --noproxy '*' -sS --max-time 3 -o /dev/null -w '%{http_code}' "http://127.0.0.1:$port/healthz" 2>/dev/null || true)"
  case "$result" in 401|403|404|000|200) ;; *) result=other;; esac
  printf 'port_%s_health_http: %s\n' "$port" "$result"
done
echo '=== NEXT CONFIGURATION GATE ==='
echo 'Check in Cloudflare Dashboard whether existing BTDigg hostname belongs to a remotely managed tunnel that permits a second Published application route.'
echo 'Never share or display tunnel tokens, service environment, or existing tunnel credentials.'
echo 'Do not install another connector, restart any units or alter DNS yet.'
