#!/usr/bin/env python3
"""One-shot guarded Magnetra BTDigg HTTP429 UX release (zero / five / full).

No upstream BTDigg searches. Only static assets, provider catalog, Worker
version metadata and fixed configuration are inspected; unknown live splits
or concurrently changed deployments fail closed. Never changes Rock64.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import subprocess
import sys

from deploy_magnetra_auto_pause_once import (
    Stop, ROOT, UUID, snapshot, stable, wait_for, uploaded_version_id,
    _wrangler_deploy,
)
from release_magnetra_20261028 import (
    candidate_baseline, critical_binding_guard, rollback_if_safe,
)
from release_magnetra_ro_it_12 import (
    verify_all_assets, verify_public_with_html_settle,
)
from release_magnetra_hide_anime_mikan import catalog_guard

REVIEWED="7dfdd1bc8c84b83bdb5ea5ea06bfb030d4c8b457"
ACTION="CONFIRM_MAGNETRA_BTDIGG_429_20261105_RELEASE"
ALLOWED_DIFF={
 "web/app.js","web/i18n.js","web/sw.js",
 "worker/test/auto-pause-indexers.test.mjs",
 "worker/test/pwa-interactions.test.mjs",
 "worker/test/btdigg-manual-removal.test.mjs",
 "worker/test/ios-pwa-safearea.test.mjs",
 "worker/test/provider-recovery.test.mjs",
 ".github/workflows/magnetra-btdigg-429-release-20261105.yml",
 "scripts/release_magnetra_btdigg_429_20261105.py",
 "scripts/test_release_magnetra_btdigg_429_20261105.py",
 "docs/release-events/magnetra-btdigg-429-20261105.md",
}
REQUIRED_DIFF={"web/app.js","web/i18n.js","web/sw.js"}
REQUIRED_SECRETS=("BTDIGG_GATEWAY_TOKEN","MAGNETRA_GATEWAY_TOKEN")

def source_guard():
    try:
        subprocess.run(["git","merge-base","--is-ancestor",REVIEWED,"HEAD"],
                       cwd=ROOT,check=True,capture_output=True,timeout=10)
        diff=subprocess.run(["git","diff","--name-only",REVIEWED,"HEAD"],
                            cwd=ROOT,check=True,capture_output=True,text=True,timeout=10)
    except (OSError, subprocess.SubprocessError):
        raise Stop("BASEREF_UNVERIFIED") from None
    actual=set(diff.stdout.splitlines())
    if not REQUIRED_DIFF.issubset(actual) or not actual.issubset(ALLOWED_DIFF):
        raise Stop("UNREVIEWED_DIFF_OR_MISSING_429_ASSET")
    cfg=json.loads((ROOT/"worker/wrangler.jsonc").read_text(encoding="utf8"))
    if (cfg.get("name")!="alexlab-magnetra"
        or cfg.get("main")!="src/index.mjs"
        or cfg.get("routes")!=[{"pattern":"index.alexlab.media","custom_domain":True}]
        or cfg.get("assets")!={"directory":"../web","binding":"ASSETS"}
        or cfg.get("services")!=[{"binding":"FLUD_RELAY","service":"flud-remote-relay"}]):
        raise Stop("WORKER_ROUTE_OR_SERVICE_BINDING_CHANGED")
    js=(ROOT/"web/app.js").read_text(encoding="utf8")
    i18n=(ROOT/"web/i18n.js").read_text(encoding="utf8")
    sw=(ROOT/"web/sw.js").read_text(encoding="utf8")
    for marker in ("id!==\"btdigg\"","recordBTDigg429","btdiggCooldownRemainingMs",
                   "RATE_LIMIT_COOLDOWN","magnetra.btdigg-cooldown.v1",
                   "const RESULTS_PER_PAGE=50","audiobookbay"):
        if marker not in js:raise Stop("BTDIGG_OWNER_PWA_BEHAVIOR_UNVERIFIED")
    if ('alexlab-magnetra-v15' not in sw
        or "BTDigg is rate-limited. It stays selected" not in i18n
        or 'url.pathname.startsWith("/api/")' not in sw):
        raise Stop("BTDIGG_CACHE_I18N_OR_API_SAFETY_UNVERIFIED")
    print("429_REVIEWED_DIFF_AND_ORIGIN_PASS:no-Rock64,no-indexer-changes")
    return cfg

def upload(config,old):
    data=dict(config)
    data["secrets"]={"required":list(REQUIRED_SECRETS)}
    temporary=ROOT/"worker/.wrangler-btdigg-429-20261105.jsonc"
    if temporary.exists() or temporary.is_symlink():
        raise Stop("EPHEMERAL_CONFIG_ALREADY_PRESENT")
    temporary.write_text(json.dumps(data,indent=2)+"\n",encoding="utf8")
    os.chmod(temporary,0o600)
    try:
        try:
            p=subprocess.run(["npx","--yes","wrangler@4.102.0","versions","upload",
                "--config",str(temporary),"--keep-vars",
                "--message","Magnetra BTDigg 429: preserve selection and no-retry PWA cooldown"],
                cwd=ROOT,capture_output=True,text=True,timeout=220,check=False)
        except (OSError,subprocess.TimeoutExpired):
            raise Stop("BTDIGG_429_UPLOAD_UNVERIFIED") from None
        if p.returncode:raise Stop("BTDIGG_429_UPLOAD_FAILED")
        new=uploaded_version_id(p.stdout+"\n"+p.stderr)
        if new==old:raise Stop("NEW_VERSION_EQUALS_CURRENT")
        print("BTDIGG_429_IMMUTABLE_STAGE:"+new)
        return new
    finally:
        temporary.unlink(missing_ok=True)

def publish():
    config=source_guard()
    before,shares=snapshot()
    old=candidate_baseline(shares)
    critical_binding_guard(old)
    catalog_guard(None)
    stable(before,shares)
    print("BTDIGG_429_PREFLIGHT_PASS:old@100",old)
    new=None
    try:
        new=upload(config,old)
        critical_binding_guard(new)
        stable(before,shares)
        zero={old:100,new:0}
        wrote=_wrangler_deploy([old+"@100%",new+"@0%"],
                               "BTDigg 429 guarded zero-percent candidate")
        zero_dep=wait_for(before,shares,zero,wrote)
        verify_all_assets(new,zero_dep,zero)
        catalog_guard(new)
        stable(zero_dep,zero)
        print("BTDIGG_429_ZERO_PERCENT_PASS")

        canary={old:95,new:5}
        wrote=_wrangler_deploy([old+"@95%",new+"@5%"],
                               "BTDigg 429 bounded five-percent canary")
        canary_dep=wait_for(zero_dep,zero,canary,wrote)
        verify_all_assets(new,canary_dep,canary)
        critical_binding_guard(new)
        stable(canary_dep,canary)
        print("BTDIGG_429_FIVE_PERCENT_PASS")

        full={old:0,new:100}
        wrote=_wrangler_deploy([old+"@0%",new+"@100%"],
                               "BTDigg 429 PWA live 100; previous 0 for rollback")
        full_dep=wait_for(canary_dep,canary,full,wrote)
        verify_public_with_html_settle(full_dep,full)
        catalog_guard(None)
        critical_binding_guard(new)
        critical_binding_guard(old)
        stable(full_dep,full)
        print("MAGNETRA_BTDIGG_429_ONLINE_100_PASS:"+new)
        print("NO_BTDIGG_UPSTREAM_QUERIES_BY_RELEASE:owner-live-behavior-pending")
        return 0
    except (Stop,ValueError,KeyError,TypeError,OSError):
        print("BTDIGG_429_RELEASE_FAILED:attempt bounded verified rollback")
        rollback_if_safe(old,new)
        return 1

def main():
    if os.environ.get("MAGNETRA_BTDIGG_429_ACTION")!=ACTION:
        print("NO_EXPLICIT_OWNER_RELEASE_ACTION:no-Cloudflare-requests")
        return 2
    try:return publish()
    except (Stop,ValueError,KeyError,TypeError,OSError):
        print("BTDIGG_429_PREUPLOAD_STOP:no-traffic-change")
        return 1

if __name__=="__main__":
    sys.exit(main())
