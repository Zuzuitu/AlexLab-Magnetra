#!/usr/bin/env python3
"""One-shot read-only EZTV JSON schema probe from the Rock64 egress.

No downloads, magnets, hashes, filenames, source bodies, credentials or routes
are printed, stored or sent to a third party. Python stdlib only.
"""
import json
import re
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

BASE = "https://eztvx.to/api/get-torrents"
URLS = (
    ("imdb", BASE + "?imdb_id=460681&limit=2&page=1"),
    ("recent", BASE + "?limit=2&page=1"),
)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36",
    "Accept": "application/json",
    "Accept-Encoding": "identity",
}
MAX_BODY = 1_000_000
FIELDS = {"imdb_id", "torrents", "torrents_count", "limit", "page",
          "error", "errors", "message", "status", "success", "data"}
ROW_FIELDS = {"title", "filename", "magnet_url", "hash", "imdb_id",
              "seeds", "peers", "size_bytes"}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def shape(value):
    if not isinstance(value, dict):
        return {"root": type(value).__name__}
    rows = value.get("torrents")
    if not isinstance(rows, list):
        rows = None
    first = rows[0] if rows and isinstance(rows[0], dict) else {}
    echo = value.get("imdb_id")
    return {
        "root": "object",
        "recognized_keys": sorted(FIELDS.intersection(value)),
        "other_key_count": len(set(value).difference(FIELDS)),
        "torrents_type": type(value.get("torrents")).__name__
                          if "torrents" in value else "missing",
        "torrents_count": len(rows) if rows is not None else None,
        "imdb_echo_matches": str(echo).removeprefix("tt") == "460681"
                              if echo is not None else None,
        "first_row_fields": sorted(ROW_FIELDS.intersection(first)),
        "first_row_imdb_matches": str(first.get("imdb_id")).removeprefix("tt") == "460681"
                                   if "imdb_id" in first else None,
        "valid_magnets_in_page": sum(
            bool(re.match(r"^magnet:\?xt=urn:btih:(?:[a-f0-9]{40}|[a-z2-7]{32})(?:&|$)",
                          r.get("magnet_url", ""), re.I))
            for r in (rows or []) if isinstance(r, dict)
            and isinstance(r.get("magnet_url"), str)
        ),
        "api_error_fields_present": bool({"error", "errors", "message"}.intersection(value)),
    }


def probe(label, url):
    out = {"probe": label}
    request = Request(url, headers=HEADERS, method="GET")
    opener = build_opener(ProxyHandler({}), NoRedirect())
    try:
        with opener.open(request, timeout=9) as response:
            out["http_status"] = response.status
            out["content_type"] = response.headers.get("content-type", "").split(";")[0][:60]
            if int(response.headers.get("content-length") or 0) > MAX_BODY:
                out["body"] = "too-large"
            else:
                body = response.read(MAX_BODY + 1)
                if len(body) > MAX_BODY:
                    out["body"] = "too-large"
                elif out["content_type"].lower() != "application/json":
                    out["body"] = "not-json-content-type"
                else:
                    try:
                        out["shape"] = shape(json.loads(body))
                    except (ValueError, UnicodeError):
                        out["body"] = "malformed-json"
    except HTTPError as error:
        out["http_status"] = error.code
        out["content_type"] = error.headers.get("content-type", "").split(";")[0][:60]
        out["blocked_or_redirected"] = True
    except (URLError, OSError, TimeoutError):
        out["network_error"] = "request-failed-or-timeout"
    print(json.dumps(out, separators=(",", ":")))


if __name__ == "__main__":
    for label, url in URLS:
        probe(label, url)
