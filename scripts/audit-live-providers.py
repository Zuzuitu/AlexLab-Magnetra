#!/usr/bin/env python3
"""One-time, low-concurrency audit of production provider search responses.

The audit never fetches torrent payloads, magnet links, files or the Flud
Companion authenticated endpoints. It distinguishes returned results, empty
responses, provider errors, and HTTP failures; it does not equate a 0-result
query with a broken provider. Upstream failures are reported, not converted
to an invariant failure.
"""
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import Request, urlopen
from urllib.parse import urlencode

ORIGIN = "https://index.alexlab.media"


def api(path):
    request = Request(ORIGIN + path, headers={
        "user-agent": "AlexLab-Magnetra-ProviderAudit/1.0",
        "accept": "application/json",
        "cache-control": "no-store"
    })
    with urlopen(request, timeout=25) as response:
        return json.loads(response.read(2_000_000).decode("utf-8"))


def check(id):
    query = urlencode({"q": "ubuntu", "providers": id, "category": "all"})
    try:
        response = api("/api/search?" + query)
        if response.get("errors"):
            return {"id": id, "state": "provider-error",
                    "reason": response["errors"][0].get("error", "unknown")[:130]}
        amount = len(response.get("results") or [])
        return {"id": id, "state": "results" if amount else "empty-or-unverified", "count": amount}
    except Exception as exc:
        return {"id": id, "state": "request-error", "reason": str(exc)[:130]}


def main():
    try:
        providers = api("/api/providers").get("providers")
        if not isinstance(providers, list) or len(providers) != 46:
            raise RuntimeError("unexpected provider catalog")
    except Exception as exc:
        print("AUDIT CONFIG ERROR:", str(exc), file=sys.stderr)
        return 1
    ids = [p["id"] for p in providers]
    results = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(check, id): id for id in ids}
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps(result, ensure_ascii=False), flush=True)
    counters = {state: sum(x["state"] == state for x in results)
                for state in ("results", "empty-or-unverified", "provider-error", "request-error")}
    print("AUDIT SUMMARY:", json.dumps(counters, sort_keys=True), flush=True)
    print("Live availability is not implied by adapter inventory, and an empty 'ubuntu' query is not failure.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
