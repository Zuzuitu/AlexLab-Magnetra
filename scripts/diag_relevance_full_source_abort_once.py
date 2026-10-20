#!/usr/bin/env python3
"""One-shot read-only diagnosis of 136c full-release aborted source preflight.

Never prints source titles, magnets, source URLs, tokens or response bodies.
Never writes Cloudflare or retries 429/504; tests exact production 95/5 once.
"""
from __future__ import annotations
import json
import re
import sys
from urllib.parse import urlencode

from deploy_magnetra_relevance_136c_slot import (
    CURRENT, NEW, snapshot, request, Stop as SourceStop
)
from deploy_magnetra_relevance_136c_full import FIVE, screenshot_source_gate, Stop as FullStop

GROUP=("torrent9","oxtorrent","ytsmx")

def audit():
    dep,shares=snapshot()
    print("PRODUCTION_SHARES: 540b="+str(shares.get(CURRENT))+
          " 136c="+str(shares.get(NEW))+" identities="+str(len(shares)))
    if shares!=FIVE:
        print("STOP: expected 95/5 canary. No source network calls.")
        return 2
    query=urlencode({"q":"the good dinosaur 2015",
                     "providers":",".join(GROUP),"category":"all"})
    try:
        data=request("/api/search?"+query)
    except SourceStop as e:
        val=str(e)
        label=val if re.fullmatch(r"[A-Z0-9_]{4,75}",val) else "SANITIZED"
        print("PROVIDER_REQUEST: UNVERIFIED "+label)
        return 1
    print("HTTP_JSON: PASS")
    rows=data.get("results")
    stats=data.get("stats")
    errors=data.get("errors")
    print("SCHEMA: resultsList="+str(isinstance(rows,list))+
          " statsList="+str(isinstance(stats,list))+
          " errorsList="+str(isinstance(errors,list)))
    if not all(isinstance(x,list) for x in (rows,stats,errors)):
        return 1
    print("TOTALS: resultRows="+str(len(rows))+
          " statsRows="+str(len(stats))+
          " errors="+str(len(errors))+
          " declaredTotal="+str(data.get("total"))+
          " excludedOffTopic="+str(data.get("excludedOffTopic")))
    for item in stats:
        if isinstance(item,dict):
            name=item.get("provider","")
            if name in GROUP:
                print("STAT "+name+": ok="+str(item.get("ok"))+
                      " count="+str(item.get("count"))+
                      " rawCount="+str(item.get("rawCount"))+
                      " excluded="+str(item.get("excludedOffTopic")))
    for item in errors:
        if isinstance(item,dict):
            provider=item.get("provider","")
            raw=item.get("code","")
            code=str(raw) if re.fullmatch(r"[A-Z][A-Z0-9_]{1,63}",str(raw)) else "UNKNOWN"
            if provider in GROUP:
                print("ERROR "+provider+" code="+code)
    allowed={"good","dinosaur","2015"}
    title_bad=sum(1 for row in rows if isinstance(row,dict)
                  and not allowed.issubset(set(re.findall(r"[a-z0-9]+",str(row.get("name","")).lower()))))
    print("TITLE_GATE: excluded_bad_title_in_returned="+str(title_bad))
    try:
        # Interpret same safe shapes as the release gate, WITHOUT another HTTP call.
        if len(stats)!=3 or len(rows)>300 or errors or data.get("total")!=len(rows):
            raise FullStop("SCREENSHOT_SOURCE_UNVERIFIED_OR_ERRORS")
        ids=set(GROUP)
        excluded=0
        for stat in stats:
            if not isinstance(stat,dict) or stat.get("provider") not in ids:
                raise FullStop("SCREENSHOT_SOURCE_STAT_INVALID")
            vals=[stat.get("count"),stat.get("rawCount"),stat.get("excludedOffTopic")]
            if not all(type(v)==int and v>=0 for v in vals) or vals[1]!=vals[0]+vals[2]:
                raise FullStop("SCREENSHOT_SOURCE_RELEVANCE_COUNTS")
            excluded+=vals[2]
        if {s.get("provider") for s in stats}!=ids or data.get("excludedOffTopic")!=excluded:
            raise FullStop("SCREENSHOT_SOURCE_STAT_TOTALS")
        if title_bad or not rows:
            raise FullStop("SCREENSHOT_TITLE_OR_POSITIVE_UNVERIFIED")
        print("SAME_RELEASE_GATE: PASS")
        return 0
    except FullStop as e:
        print("SAME_RELEASE_GATE: "+str(e))
        return 1
if __name__=="__main__":
    try:sys.exit(audit())
    except (ValueError,TypeError,KeyError,SourceStop):
        print("DIAGNOSTIC_STOP: SANITIZED_METADATA_OR_TRANSPORT")
        sys.exit(1)
