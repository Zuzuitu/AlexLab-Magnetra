#!/usr/bin/env python3
"""Read-only, secret-free inventory of the effective Magnetra BTDigg systemd entrypoint.

No source HTTP requests, browser inspection, filesystem writes or service actions.
Print only predefined entrypoint categories and known override names.
"""
from __future__ import annotations

import json
from pathlib import PurePath
import subprocess

SERVICE="magnetra-btdigg.service"
BASE_SCRIPT="/opt/magnetra-btdigg/btdigg_gateway.py"
CFFI_SCRIPT="/opt/magnetra-btdigg/btdigg_cffi_gateway.py"


def classify(show_output: str) -> dict:
    fields={}
    for line in show_output.splitlines():
        key, sep, value=line.partition("=")
        if sep and key in ("ExecStart","DropInPaths","ActiveState"):
            fields[key]=value.strip()
    raw_exec=fields.get("ExecStart","")
    overrides=fields.get("DropInPaths","").split()
    if CFFI_SCRIPT in raw_exec:
        mode="cffi_override"
    elif BASE_SCRIPT in raw_exec:
        mode="base_gateway"
    else:
        mode="unknown"
    known={"50-magnetra-cffi.conf":"cffi", "20-owner-chromium-bridge.conf":"chromium"}
    names=[known.get(PurePath(x).name, "other") for x in overrides]
    return {
        "service_active": fields.get("ActiveState")=="active",
        "effective_entrypoint":mode,
        "override_count":len(overrides),
        "override_types":names,
        "base_updater_eligible":mode=="base_gateway" and not overrides,
        "chromium_bridge_enabled":(
            mode=="base_gateway" and "chromium" in names and "cffi" not in names
        ),
        "source_requests":0,
        "note":"No systemd, browser, network or source state was modified.",
    }


def main() -> None:
    try:
        p=subprocess.run(
            ["systemctl","show",SERVICE,
             "--property=ExecStart","--property=DropInPaths",
             "--property=ActiveState","--no-pager"],
            capture_output=True,text=True,check=True,timeout=7,
        )
        result=classify(p.stdout)
    except (OSError,subprocess.SubprocessError):
        result={"service_state":"unavailable","source_requests":0}
    print(json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()
