#!/usr/bin/env python3
"""Read-only real-source 136c 5%-canary acceptance. No deployment or retries."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlencode

from deploy_magnetra_relevance_136c_slot import (
    CURRENT, NEW, snapshot, verify_version, request, Stop as SourceStop,
)
from deploy_magnetra_relevance_136c_canary import FIVE

QUERY="the good dinosaur 2015"
GROUPS=(("knaben","torrentscsv"),("torrent9","oxtorrent","ytsmx"))

class Stop(Exception):
    pass

def check_group(group):
    path="/api/search?"+urlencode({"q":QUERY,"providers":",".join(group),"category":"all"})
    data=request(path)
    rows, stats, errors=data.get("results"), data.get("stats"), data.get("errors")
    if not all(isinstance(item,list) for item in (rows,stats,errors)):
        raise Stop("SOURCE_RESPONSE_SHAPE_BAD")
    if len(stats)!=len(group) or len(rows)>300 or data.get("total")!=len(rows):
        raise Stop("SOURCE_RESULT_COUNT_BAD")
    excluded=0
    for s in stats:
        if not isinstance(s,dict) or s.get("provider") not in group:
            raise Stop("SOURCE_STAT_ID_INVALID")
        n,raw,removed=s.get("count"),s.get("rawCount"),s.get("excludedOffTopic")
        if not all(type(x)==int and x>=0 for x in (n,raw,removed)) or raw!=n+removed:
            raise Stop("SOURCE_RELEVANCE_COUNT_BAD")
        excluded+=removed
    if len({x.get("provider") for x in stats})!=len(group) or data.get("excludedOffTopic")!=excluded:
        raise Stop("SOURCE_STAT_TOTALS_BAD")
    for row in rows:
        if not isinstance(row,dict) or row.get("provider") not in group:
            raise Stop("SOURCE_ROW_ID_INVALID")
        actual=set(re.findall(r"[a-z0-9]+",str(row.get("name","")).lower()))
        if not {"good","dinosaur","2015"}.issubset(actual):
            raise Stop("OFFTOPIC_TITLE_LEAKED")
    print("CANARY_GROUP:"+",".join(group)+" MATCHES="+str(len(rows))+
          " EXCLUDED="+str(excluded)+" ERRORS="+str(len(errors))+
          " TITLE_GATE=PASS")
    return bool(rows) and not errors

def execute():
    dep,shares=snapshot()
    print("LIVE_CANARY_SHARES: 540b="+str(shares.get(CURRENT))+" 136c="+str(shares.get(NEW)))
    if shares!=FIVE:raise Stop("NOT_EXACT_540B95_136C5")
    verify_version(CURRENT)
    verify_version(NEW)
    local=(Path(__file__).resolve().parent.parent/"web/app.js").read_bytes()
    served=request("/app.js",as_json=False)
    if hashlib.sha256(local).digest()!=hashlib.sha256(served).digest():
        raise Stop("NEW_136C_STAGED_JS_MISMATCH")
    print("CANARY_136C_IMMUTABLE_JS: PASS "+hashlib.sha256(local).hexdigest()[:16])
    names=request("/api/providers").get("providers")
    if not isinstance(names,list) or len(names)!=46 or len({r.get("id") for r in names if isinstance(r,dict)})!=46:
        raise Stop("CANARY_CATALOG_NOT_46")
    print("CANARY_ORIGINAL_CATALOG: PASS 46 IDs")
    all_positive=True
    for group in GROUPS:
        ok=check_group(group)
        all_positive=all_positive and ok
    after,latest=snapshot()
    if dep["id"]!=after["id"] or latest!=FIVE:
        raise Stop("CLOUDFLARE_CHANGED_DURING_TEST")
    print("CANARY_LIVE_ORIGINAL_SOURCE_E2E: "+("PASS" if all_positive else "PARTIAL_SOURCE_UNAVAILABLE"))
    print("READ_ONLY_ONLY: no traffic write, source retries, download, Flud or Rock64.")
    return 0 if all_positive else 2

if __name__=="__main__":
    try:
        sys.exit(execute())
    except (Stop,SourceStop) as e:
        print("CANARY_READONLY_STOP: "+str(e))
        sys.exit(1)
    except (ValueError,TypeError,KeyError,OSError):
        print("CANARY_READONLY_STOP: SANITIZED_METADATA_OR_TRANSPORT")
        sys.exit(1)
