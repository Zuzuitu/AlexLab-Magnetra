#!/usr/bin/env python3
"""Owner-gated release of approved BTDigg local pacing fix #262.

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

REVIEWED="437d7fa370b5558e362e718fe042e289cb12d931"
ACTION="CONFIRM_MAGNETRA_BTDIGG_PACING_20261113_RELEASE"
INSPECT_ENV="MAGNETRA_BTDIGG_PACING_READONLY_INSPECT"
ACTION_ENV="MAGNETRA_BTDIGG_PACING_RELEASE_ACTION"
MARKER="[magnetra-btdigg-pacing-20261113] "
EVENT="docs/release-events/magnetra-btdigg-pacing-20261113.md"
ALLOWED_DIFF={
 "scripts/release_magnetra_btdigg_pacing_20261113.py",
 "scripts/test_release_magnetra_btdigg_pacing_20261113.py",
 ".github/workflows/magnetra-btdigg-pacing-20261113.yml",
 EVENT,
}
REQUIRED_DIFF=ALLOWED_DIFF
FROZEN={
 "worker/src/provider-recovery.mjs":"dd60281577f8411c62a27d18c44a5c3066be4e19",
 "worker/src/index.mjs":"6590c287a6468927c510ed2350478f7636e20d66",
 "worker/src/btdigg-rock64.mjs":"e129ce1d5a2076cae398b8c6418e601342b0a5f7",
 "worker/src/verified-source-cache.mjs":"1a9122024989f3004308b2c4fd2c2dea445df679",
 "web/app.js":"1ba24f1ec49d424c1ad3556a7b3ed3dd9fbdf0c5",
 "web/i18n.js":"27d1b938b0842b2469d4f2c7cf9ee22ad3d6b12d",
 "web/sw.js":"9de724a52407c42230863c6b84133258a432f473",
 "worker/wrangler.jsonc":"8217d12692843792f210dc3f683b422d3553c9fc",
}
REQUIRED_SECRETS=("BTDIGG_GATEWAY_TOKEN","MAGNETRA_GATEWAY_TOKEN")

def _git(*args):
    try:
        return subprocess.run(["git",*args],cwd=ROOT,capture_output=True,
                              text=True,check=True,timeout=15).stdout.strip()
    except (OSError,subprocess.SubprocessError):
        raise Stop("PINNED_REVIEWED_GIT_HISTORY_NOT_VERIFIED") from None

def approval_baseline():
    # The unique activation commit must change only this approval event.
    if not _git("log","-1","--pretty=%s").startswith(MARKER):
        raise Stop("OWNER_ACTIVATION_COMMIT_MARKER_MISSING")
    changed=set(_git("diff-tree","--no-commit-id","--name-only","-r","HEAD").splitlines())
    if changed!={EVENT}:
        raise Stop("ACTIVATION_COMMIT_MUST_CHANGE_EVENT_ONLY")
    content=(ROOT/EVENT).read_text(encoding="utf8")
    import re
    pattern=r"status: APPROVED\nexpected_active_version: ("+UUID.pattern+r")\n"
    match=re.fullmatch(pattern,content,re.I)
    if match is None:
        raise Stop("APPROVED_BASELINE_UUID_MISSING")
    return match.group(1).lower()

def source_guard():
    _git("merge-base","--is-ancestor",REVIEWED,"HEAD")
    changed=set(_git("diff","--name-only",REVIEWED,"HEAD").splitlines())
    if not REQUIRED_DIFF.issubset(changed) or not changed.issubset(ALLOWED_DIFF):
        raise Stop("UNREVIEWED_SOURCE_AFTER_262")
    for file,sha in FROZEN.items():
        if _git("hash-object",file)!=sha:
            raise Stop("PINNED_BLOB_MISMATCH:"+file)
    cfg=json.loads((ROOT/"worker/wrangler.jsonc").read_text(encoding="utf8"))
    if (cfg.get("name")!="alexlab-magnetra"
        or cfg.get("main")!="src/index.mjs"
        or cfg.get("routes")!=[{"pattern":"index.alexlab.media","custom_domain":True}]
        or cfg.get("assets")!={"directory":"../web","binding":"ASSETS"}
        or cfg.get("services")!=[{"binding":"FLUD_RELAY","service":"flud-remote-relay"}]):
        raise Stop("WORKER_ROUTE_ASSETS_OR_FLUD_BINDING_CHANGED")
    app=(ROOT/"web/app.js").read_text(encoding="utf8")
    worker=(ROOT/"worker/src/provider-recovery.mjs").read_text(encoding="utf8")
    if ('e.code==="RATE_LIMIT"' not in app or "recordBTDigg429()" not in app
        or "BTDIGG_LOCAL_PACING" not in app
        or 'code:"BTDIGG_LOCAL_PACING"' not in worker):
        raise Stop("BTDIGG_PACING_SOURCE_CONTRACT_CHANGED")
    print("PINNED_SOURCE_AND_OWNER_ACTIVATION_PASS:#262")
    return cfg

def readonly_baseline():
    # GET-only Cloudflare version metadata, no source searches and no writes.
    _deployment,shares=snapshot()
    old=candidate_baseline(shares)
    critical_binding_guard(old)
    print("BTDIGG_PACING_READONLY_BASELINE:"+old+"@100")
    return 0

def upload(config,old):
    data=dict(config)
    data["secrets"]={"required":list(REQUIRED_SECRETS)}
    temporary=ROOT/"worker/.wrangler-btdigg-pacing-20261113.jsonc"
    if temporary.exists() or temporary.is_symlink():
        raise Stop("EPHEMERAL_CONFIG_ALREADY_PRESENT")
    temporary.write_text(json.dumps(data,indent=2)+"\n",encoding="utf8")
    os.chmod(temporary,0o600)
    try:
        try:
            p=subprocess.run(["npx","--yes","wrangler@4.102.0","versions","upload",
                "--config",str(temporary),"--keep-vars",
                "--message","Magnetra #262: local pacing distinct from upstream 429"],
                cwd=ROOT,capture_output=True,text=True,timeout=220,check=False)
        except (OSError,subprocess.TimeoutExpired):
            raise Stop("BTDIGG_PACING_UPLOAD_UNVERIFIED") from None
        if p.returncode:raise Stop("BTDIGG_PACING_UPLOAD_FAILED")
        new=uploaded_version_id(p.stdout+"\n"+p.stderr)
        if new==old:raise Stop("NEW_VERSION_EQUALS_CURRENT")
        print("BTDIGG_PACING_IMMUTABLE_STAGE:"+new)
        return new
    finally:
        temporary.unlink(missing_ok=True)

def publish():
    config=source_guard()
    before,shares=snapshot()
    old=candidate_baseline(shares)
    if old!=approval_baseline():
        raise Stop("APPROVED_CLOUDFLARE_BASELINE_CHANGED")
    critical_binding_guard(old)
    catalog_guard(None)
    stable(before,shares)
    print("BTDIGG_PACING_PREFLIGHT_PASS:old@100",old)
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
        print("BTDIGG_PACING_ZERO_PERCENT_PASS")

        canary={old:95,new:5}
        wrote=_wrangler_deploy([old+"@95%",new+"@5%"],
                               "BTDigg 429 bounded five-percent canary")
        canary_dep=wait_for(zero_dep,zero,canary,wrote)
        verify_all_assets(new,canary_dep,canary)
        critical_binding_guard(new)
        stable(canary_dep,canary)
        print("BTDIGG_PACING_FIVE_PERCENT_PASS")

        full={old:0,new:100}
        wrote=_wrangler_deploy([old+"@0%",new+"@100%"],
                               "BTDigg 429 PWA live 100; previous 0 for rollback")
        full_dep=wait_for(canary_dep,canary,full,wrote)
        verify_public_with_html_settle(full_dep,full)
        catalog_guard(None)
        critical_binding_guard(new)
        critical_binding_guard(old)
        stable(full_dep,full)
        print("MAGNETRA_BTDIGG_PACING_ONLINE_100_PASS:"+new)
        print("NO_BTDIGG_UPSTREAM_QUERIES_BY_RELEASE:owner-live-behavior-pending")
        return 0
    except (Stop,ValueError,KeyError,TypeError,OSError):
        print("BTDIGG_PACING_RELEASE_FAILED:attempt bounded verified rollback")
        rollback_if_safe(old,new)
        return 1

def main():
    if os.environ.get(INSPECT_ENV)=="1" and os.environ.get(ACTION_ENV)!=ACTION:
        try:return readonly_baseline()
        except (Stop,ValueError,KeyError,TypeError,OSError):
            print("BTDIGG_PACING_READONLY_UNVERIFIED")
            return 1
    if os.environ.get(ACTION_ENV)!=ACTION or os.environ.get(INSPECT_ENV)=="1":
        print("NO_EXPLICIT_OWNER_RELEASE_ACTION:no-Cloudflare-mutation")
        return 2
    try:return publish()
    except (Stop,ValueError,KeyError,TypeError,OSError):
        print("BTDIGG_PACING_PREUPLOAD_STOP:no-traffic-change")
        return 1

if __name__=="__main__":
    sys.exit(main())
