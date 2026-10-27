#!/usr/bin/env bash
# AlexLab Magnetra — read-only local BTDigg gateway diagnosis.
# No external requests, credentials, service restarts, configuration writes or routing.
set -euo pipefail
SERVICE="magnetra-btdigg.service"
printf '=== MAGNETRA BTDIGG READ-ONLY DIAGNOSTIC ===\n'
printf 'SERVICE_ACTIVE: '
if systemctl is-active --quiet "$SERVICE"; then
  printf 'yes\n'
else
  printf 'no\n'
fi
printf 'SERVICE_STATE: '
systemctl show "$SERVICE" -p ActiveState -p SubState --no-pager 2>/dev/null \
  | tr '\n' ' '; printf '\n'
printf 'UPSTREAM_TIMING_EVENTS_LAST_120_MIN:\n'
# Parse ONLY known safe structured event fields. No raw journal lines ever printed.
journalctl -u "$SERVICE" --since "-120 minutes" -o cat --no-pager 2>/dev/null \
  | python3 -c '
import collections,json,sys
rows=[]
safe=("failure","total_ms","dns_ms","tcp_ms","tls_ms","open_ms","read_ms")
for raw in sys.stdin:
    try:
        start=raw.find("{")
        if start<0:
            continue
        obj=json.loads(raw[start:])
        if not isinstance(obj,dict) or obj.get("event")!="btdigg_upstream_timing":
            continue
        row={}
        for key in safe:
            value=obj.get(key)
            if key=="failure":
                if isinstance(value,str) and value.replace("_","").isalnum() and len(value)<=36:
                    row[key]=value
            elif type(value) in (int,float) and 0<=value<=120000:
                row[key]=round(value,1)
        rows.append(row)
    except (ValueError,TypeError):
        continue
counts=collections.Counter(row.get("failure","unknown") for row in rows)
print("event_count:",len(rows))
print("failure_counts:",json.dumps(dict(sorted(counts.items())),sort_keys=True))
for row in rows[-8:]:
    print("event:",json.dumps(row,sort_keys=True))
if not rows:
    print("NO_RECENT_STRUCTURED_TIMING_EVENTS: check user-initiated BTDigg activity and service journal permissions")
'
printf 'END_READ_ONLY_DIAGNOSTIC\n'
