#!/usr/bin/env python3
"""Opt-in ALTERNATIVE Magnetra BTDigg gateway entrypoint; NOT deployed.

Reuses the original authenticated loopback server, SearchProvider's bounded
positive cache, in-flight deduplication, backoff, and 429 reporting.
An explicit environment gate keeps this disabled by default. The existing
stdlib gateway and systemd ExecStart remain unchanged in production.

Only deploy after owner approval AND BTDigg authorized programmatic access.
"""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent


def _load(name: str):
    # Works under Python -I / isolated venv without importing other projects
    # or mutating global sys.path.
    path = HERE / (name + ".py")
    if path.is_symlink() or not path.is_file():
        raise RuntimeError("BTDigg source module absent or symlinked")
    spec = importlib.util.spec_from_file_location("magnetra_" + name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("BTDigg source module unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def create_provider(*, transport=None, clock=None):
    """Construct same bounded source wrapper with optional test-only transport."""
    original = _load("btdigg_gateway")
    candidate = _load("btdigg_cffi_candidate")
    fetcher = candidate.fetch_one if transport is None else lambda q: candidate.fetch_one(q, client=transport)
    return original.SearchProvider(fetcher=fetcher, clock=clock)


def main():
    if os.environ.get("MAGNETRA_BTDIGG_CFFI_OPT_IN") != "1":
        raise SystemExit("STOP: alternative BTDigg gateway opt-in not approved")
    if os.environ.get("MAGNETRA_BTDIGG_SOURCE_PERMISSION_CONFIRMED") != "1":
        raise SystemExit("STOP: BTDigg source authorization not confirmed")
    token = os.environ.get("MAGNETRA_BTDIGG_TOKEN", "")
    if not re.fullmatch(r"[A-Za-z0-9_-]{48,256}", token):
        raise SystemExit("STOP: invalid original BTDigg gateway credential")
    # Fail before binding if isolated Python environment lacks dependency.
    try:
        from curl_cffi import requests as _requests
    except ImportError:
        raise SystemExit("STOP: isolated cffi dependency unavailable") from None
    if _requests is None:
        raise SystemExit("STOP: isolated cffi dependency unavailable")
    original = _load("btdigg_gateway")
    server = original.LimitedHTTPServer(
        (original.BIND, original.PORT),
        original.handler_class(token, create_provider()),
    )
    print("Experimental Magnetra BTDigg local-only gateway started", flush=True)
    try:
        server.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
