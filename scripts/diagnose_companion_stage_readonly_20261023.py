#!/usr/bin/env python3
"""One-shot read-only HTTP response category probe for immutable staged Companion.

Exact baseline required. Never writes Cloudflare state or sends magnets.
Only fake credentials. Logs HTTP status and finite error *category*, never raw
response text, tokens, private URLs or exception details.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request

from deploy_magnetra_auto_pause_once import Stop, snapshot, stable, NoRedirect

ACTIVE = "a088fa41-233d-48d3-bd4c-52be6194fda8"
CANDIDATE = "ac71bb51-b681-458b-8f40-980d4621fe62"
SLOT = {ACTIVE: 100, CANDIDATE: 0}
ROOT = "https://index.alexlab.media"
RELAY = "https://flud-remote.alexlab.media"
DEVICE = "MAGNETRA_DIAG_NOTREAL_1234"
TOKEN = "TEST_TOKEN_NOT_REAL_12345678901234567890"


def http_probe(url, method, headers, body=None):
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    opener = urllib.request.build_opener(NoRedirect())
    try:
        with opener.open(req, timeout=20) as response:
            code = response.status
            raw = response.read(2049)
    except urllib.error.HTTPError as exc:
        code = exc.code
        raw = exc.read(2049)
    except (urllib.error.URLError, OSError, TimeoutError):
        raise Stop("HTTP_PROBE_TRANSPORT_ERROR") from None
    if len(raw) >= 2049:
        raise Stop("HTTP_RESPONSE_TOO_LARGE")
    try:
        data = json.loads(raw)
    except (UnicodeError, ValueError, TypeError):
        return code, "NON_JSON"
    if not isinstance(data, dict):
        return code, "INVALID_SHAPE"
    error = data.get("error")
    if error == "Unauthorized":
        category = "UNAUTHORIZED"
    elif error == "Companion remote relay is unavailable.":
        category = "RELAY_FETCH_FAILED"
    elif error == "Companion relay returned an invalid response.":
        category = "RELAY_INVALID_RESPONSE"
    elif error == "Cross-origin submission not permitted.":
        category = "CROSS_ORIGIN_REJECTED"
    elif error == "Invalid Companion device ID.":
        category = "INVALID_DEVICE_ID"
    elif error == "Invalid Companion Remote token.":
        category = "INVALID_TOKEN"
    elif error:
        category = "OTHER_ERROR"
    elif data.get("ok") is True:
        category = "OK_UNEXPECTED_FAKE"
    else:
        category = "UNEXPECTED_PAYLOAD"
    return code, category


def run():
    before, observed = snapshot()
    if set(observed).issubset({
        ACTIVE,
        CANDIDATE,
        "056d8394-79b0-459a-b93e-b5f5a8a7295d",
    }):
        compact = ",".join(
            ("ACTIVE" if v == ACTIVE else "CANDIDATE" if v == CANDIDATE
             else "PRIOR_ROLLBACK") + "=" + str(int(p))
            for v, p in sorted(observed.items())
        )
        print("CLOUDFLARE_CURRENT_TRAFFIC:" + compact, flush=True)
    else:
        print("CLOUDFLARE_CURRENT_TRAFFIC:UNRECOGNIZED", flush=True)
    if observed != SLOT:
        print("STAGED_SLOT_GATE:NOT_MATCHED", flush=True)
        raise Stop("STAGED_SLOT_NOT_PRESENT")
    print("STAGED_SLOT_GATE:PASS", flush=True)
    direct, direct_kind = http_probe(
        RELAY + "/api/v1/device/" + DEVICE + "/status",
        "GET",
        {"Authorization": "Bearer " + TOKEN, "Accept": "application/json"}
    )
    print("DIRECT_FLUD_RELAY_HTTP:" + str(direct), flush=True)
    print("DIRECT_FLUD_RELAY_CATEGORY:" + direct_kind, flush=True)
    if (direct, direct_kind) == (401, "UNAUTHORIZED"):
        print("DIRECT_FLUD_RELAY_FAKE_STATUS:401_UNAUTHORIZED_PASS", flush=True)
    elif direct == 403:
        # Observed on GitHub-hosted runner; may be edge/security policy.
        # It is not evidence that the internal Worker-to-Worker binding fails.
        print("DIRECT_FLUD_RELAY_GITHUB_NETWORK:403_INCONCLUSIVE", flush=True)
    else:
        print("DIRECT_FLUD_RELAY_GITHUB_NETWORK:UNVERIFIED", flush=True)
    # Continue with the *separate* immutable-version Worker service-binding
    # probe using fake credentials; still fail closed if it is not 401.
    body = json.dumps({"deviceId": DEVICE, "token": TOKEN}).encode()
    staged, staged_kind = http_probe(
        ROOT + "/api/companion/status",
        "POST",
        {"Origin": ROOT, "Content-Type": "application/json",
         "Accept": "application/json",
         "Cloudflare-Workers-Version-Overrides": 'alexlab-magnetra="' + CANDIDATE + '"'},
        body
    )
    print("STAGED_MAGNETRA_STATUS_HTTP:" + str(staged))
    print("STAGED_MAGNETRA_STATUS_CATEGORY:" + staged_kind)
    stable(before, SLOT)
    print("DEPLOYMENT_REMAINS_OLD100_CANDIDATE0_PASS")
    print("READ_ONLY_DIAGNOSTIC: no deployment, no token changes, no magnet sends")
    if (staged, staged_kind) != (401, "UNAUTHORIZED"):
        raise Stop("CANDIDATE_STAGED_NOT_401")
    print("COMPANION_STAGED_CONNECTIVITY_PASS")
    return 0


def main():
    try:
        return run()
    except (Stop, ValueError, KeyError, TypeError, OSError):
        print("COMPANION_STAGED_DIAGNOSTIC_STOP_UNVERIFIED")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
