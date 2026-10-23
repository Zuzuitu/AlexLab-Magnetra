#!/usr/bin/env python3
"""Owner-triggered, zero-traffic-only Companion diagnostic version stage.

Precondition: existing a088100/ac710. Upload a new immutable version and replace
the previously staged ac71 zero-percent slot. Old a088 retains 100% traffic.
Use synthetic credentials and a finite response header to prove override
routing and distinguish a binding exception from previous-version fallback.
Never promote, send magnets, touch Shield/Rock64/relay, or print credentials.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from deploy_magnetra_auto_pause_once import (
    Stop, NoRedirect, current, stable, wait_for, _wrangler_deploy,
)
from release_magnetra_companion_binding_20261023 import (
    ACTIVE, TEST_DEVICE, TEST_TOKEN, upload, verify_version, verify_all_assets,
    catalog_guard, ORIGIN,
)
from inspect_companion_binding_readonly import validated_source, account_list, verify_account_scripts

OLD_ZERO="ac71bb51-b681-458b-8f40-980d4621fe62"
BASELINE={ACTIVE:100,OLD_ZERO:0}
ACTION="CONFIRM_COMPANION_V2_DIAGNOSTIC_ZERO_ONLY_20261023"
STAGE_HEADER="x-alexlab-companion-probe"
ALLOWED_STAGES=frozenset({
    "request-preparation-type_error","request-preparation-other",
    "binding-request-type_error","binding-request-other",
    "binding-fetch-type_error","binding-fetch-other",
    "binding-fetch-timeout","binding-fetch-aborted",
    "public-fetch-type_error","public-fetch-other",
    "public-fetch-timeout","public-fetch-aborted",
    "upstream-http-401","upstream-http-403","upstream-http-404",
    "upstream-http-500","upstream-http-502","upstream-invalid-json",
})


def source_guard():
    config=validated_source()
    code=open(__file__.replace("scripts/stage_companion_v2_diagnostic.py","worker/src/index.mjs"),
              encoding="utf-8").read()
    if ('"x-alexlab-companion-probe"' not in code
        or '"20261023-v2"' not in code
        or 'upstream-http-' not in code
        or 'upstream=await env.FLUD_RELAY.fetch(outbound)' not in code):
        raise Stop("FINITE_STAGE_SOURCE_NOT_REVIEWED")
    return config


def synthetic_status(version):
    body=json.dumps({"deviceId":TEST_DEVICE,"token":TEST_TOKEN}).encode()
    headers={
        "Origin":ORIGIN,
        "Content-Type":"application/json",
        "Accept":"application/json",
        "Accept-Encoding":"identity",
        "Cache-Control":"no-store",
        "X-AlexLab-Companion-Probe":"20261023-v2",
        "Cloudflare-Workers-Version-Overrides":'alexlab-magnetra="'+version+'"',
    }
    req=urllib.request.Request(ORIGIN+"/api/companion/status",
                                headers=headers,method="POST",data=body)
    try:
        with urllib.request.build_opener(NoRedirect()).open(req,timeout=22) as resp:
            status=resp.status
            stage=resp.headers.get(STAGE_HEADER)
            raw=resp.read(1025)
    except urllib.error.HTTPError as exc:
        status=exc.code
        stage=exc.headers.get(STAGE_HEADER)
        raw=exc.read(1025)
    except (urllib.error.URLError,TimeoutError,OSError):
        raise Stop("STAGE_PROBE_TRANSPORT_UNVERIFIED") from None
    if stage not in ALLOWED_STAGES:
        raise Stop("CANDIDATE_HEADER_ABSENT_OR_UNREVIEWED_VERSION_OVERRIDE")
    try:
        data=json.loads(raw)
    except (ValueError,UnicodeError):
        raise Stop("STAGE_PROBE_NON_JSON") from None
    if not isinstance(data,dict) or status not in (401,403,404,500,502):
        raise Stop("STAGE_PROBE_UNEXPECTED_HTTP")
    if status==401 and data.get("error")!="Unauthorized":
        raise Stop("STAGE_PROBE_UNVERIFIED_AUTH")
    if status==502 and data.get("error") not in (
            "Companion remote relay is unavailable.",
            "Companion relay returned an invalid response."):
        raise Stop("STAGE_PROBE_UNEXPECTED_502")
    print("CANDIDATE_OVERRIDE_PROVEN:PASS")
    print("COMPANION_DIAGNOSTIC_HTTP:"+str(status))
    print("COMPANION_DIAGNOSTIC_STAGE:"+stage)
    print("NO_REAL_TOKENS_OR_MAGNETS_USED")
    return status,stage


def run():
    config=source_guard()
    verify_account_scripts(account_list())
    original=current(BASELINE)
    verify_version(ACTIVE)
    verify_version(OLD_ZERO,True)
    stable(original,BASELINE)
    print("OLD_100_EXISTING_CANDIDATE_0_PREFLIGHT_PASS")
    new=upload(config)
    verify_version(new,True)
    stable(original,BASELINE)
    slot={ACTIVE:100,new:0}
    ok=_wrangler_deploy(
        [ACTIVE+"@100%",new+"@0%"],
        "Magnetra Companion finite stage diagnostic; old production stays 100%",
    )
    staged=wait_for(original,BASELINE,slot,ok)
    verify_version(new,True)
    verify_all_assets(new,staged,slot)
    catalog_guard(new)
    try:
        synthetic_status(new)
    finally:
        stable(staged,slot)
    print("PRODUCTION_OLD_100_NEW_0_VERIFIED")
    print("NO_CANARY_NO_PRODUCTION_PROMOTION")
    return 0


def main():
    if os.environ.get("MAGNETRA_COMPANION_V2_DIAG_ACTION")!=ACTION:
        print("STOP_EXPLICIT_DIAGNOSTIC_ACTIVATION_MISSING")
        return 2
    try:
        return run()
    except (Stop,ValueError,TypeError,KeyError,OSError):
        print("COMPANION_V2_DIAG_STOP_UNVERIFIED_PRODUCTION_PRESERVED_UNLESS_EXTERNAL_CHANGE")
        return 1


if __name__=="__main__":
    raise SystemExit(main())
