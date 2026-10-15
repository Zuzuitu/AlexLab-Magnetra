#!/usr/bin/env python3
"""Read-only focused follow-up to Rock64's 2026-10-15 11-indexer audit.

Four fixed original HTTPS sources only (3 redirects + Torrentz) and at most
five fixed official EZTV API calls. Never follows cross-origin redirects,
downloads torrent payloads, sends magnets, prints IMDb IDs/names/magnets/
hashes/raw response bodies, reads tokens, or alters services/host network.
"""
from __future__ import annotations

import errno
import json
import re
import socket
import ssl
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

UA = ("Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36")
SOURCE = "https://eztvx.to/api/get-torrents"
MAX_BYTES = 350_000
TIMEOUT = 8
MAX_CANDIDATES = 4
IMDB = re.compile(r"^(?:tt)?([0-9]{5,12})$", re.I)
MAGNET = re.compile(r"^magnet:\?xt=urn:btih:(?:[a-f0-9]{40}|[a-z2-7]{32})(?:&|$)", re.I)

@dataclass(frozen=True)
class SourceProbe:
    name: str
    url: str

TARGETS = (
    SourceProbe("torrentz", "https://torrentz2.nz/search?q=ubuntu"),
    SourceProbe("oxtorrent", "https://oxtorrent.co/recherche/ubuntu"),
    SourceProbe("torrent9", "https://www6.torrent9.to/search_torrent/ubuntu.html"),
    SourceProbe("bitsearch", "https://bitsearch.to/search?q=ubuntu&page=1&sortBy=seeders"),
)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def no_proxy_opener():
    return build_opener(ProxyHandler({}), NoRedirect())


def categorize_error(reason):
    """Safe label only; never return exception repr which may leak URLs."""
    if isinstance(reason, URLError):
        return categorize_error(reason.reason)
    if isinstance(reason, socket.gaierror):
        return "DNS_RESOLUTION_FAILURE"
    if isinstance(reason, ssl.SSLCertVerificationError):
        return "TLS_CERTIFICATE_FAILURE"
    if isinstance(reason, (socket.timeout, TimeoutError)):
        return "TIMEOUT"
    if isinstance(reason, ConnectionRefusedError):
        return "CONNECTION_REFUSED"
    if isinstance(reason, OSError):
        if reason.errno in (errno.ENETUNREACH, errno.EHOSTUNREACH):
            return "NETWORK_UNREACHABLE"
        if reason.errno in (errno.ECONNRESET, errno.EPIPE):
            return "CONNECTION_RESET"
    if isinstance(reason, ssl.SSLError):
        return "TLS_FAILURE"
    return "TRANSPORT_FAILURE"


def redirect_target(source_url, location):
    """Inspect only; NEVER fetch a redirect destination."""
    if not location:
        return {"redirect_class": "MISSING_LOCATION"}
    try:
        candidate = urlsplit(urljoin(source_url, location))
        original = urlsplit(source_url)
        if (candidate.scheme != "https" or not candidate.hostname or
                candidate.username or candidate.password or candidate.fragment or
                candidate.port not in (None, 443)):
            return {"redirect_class": "UNSAFE_OR_UNSUPPORTED"}
        same = candidate.hostname == original.hostname and candidate.port == original.port
        # Host is public original provider metadata, not a source path or token.
        return {"redirect_class": "SAME_ORIGIN" if same else "OFF_ORIGIN",
                "destination_host": candidate.hostname[:120]}
    except (ValueError, TypeError):
        return {"redirect_class": "MALFORMED_LOCATION"}


def inspect_html(source, opener=None):
    if source not in TARGETS:
        raise ValueError("Only exact original provider endpoints allowed")
    opener = opener or no_proxy_opener()
    request = Request(source.url, headers={"User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Encoding": "identity"}, method="GET")
    try:
        with opener.open(request, timeout=TIMEOUT) as response:
            return {"source": source.name, "http": response.status,
                    "result": "NO_REDIRECT", "body_not_examined": True}
    except HTTPError as exc:
        try:
            status = exc.code
            result = {"source": source.name, "http": status}
            if status in (301, 302, 303, 307, 308):
                result.update(redirect_target(source.url, exc.headers.get("location")))
            elif status in (403, 401):
                result["result"] = "ACCESS_DENIED"
            elif status == 429:
                result["result"] = "RATE_LIMIT"
            else:
                result["result"] = "HTTP_ERROR"
            return result
        finally:
            exc.close()
    except (URLError, OSError, TimeoutError) as exc:
        return {"source": source.name, "http": None, "result": categorize_error(exc)}


def get_api(url, opener=None):
    # Caller uses exactly source-owned URL shape defined in this module.
    opener = opener or no_proxy_opener()
    request = Request(url, method="GET", headers={"User-Agent": UA,
        "Accept": "application/json", "Accept-Encoding": "identity"})
    try:
        with opener.open(request, timeout=TIMEOUT) as response:
            if response.status != 200:
                return {"http": response.status}, None
            if "application/json" not in (response.headers.get("content-type") or "").lower():
                return {"http": 200, "result": "NOT_JSON"}, None
            if int(response.headers.get("content-length") or 0) > MAX_BYTES:
                return {"http": 200, "result": "BODY_TOO_LARGE"}, None
            body = response.read(MAX_BYTES + 1)
            if len(body) > MAX_BYTES:
                return {"http": 200, "result": "BODY_TOO_LARGE"}, None
            try:
                parsed = json.loads(body)
            except (ValueError, UnicodeError):
                return {"http": 200, "result": "BAD_JSON"}, None
            if not isinstance(parsed, dict):
                return {"http": 200, "result": "UNEXPECTED_ROOT"}, None
            return {"http": 200}, parsed
    except HTTPError as exc:
        try:
            return {"http": exc.code, "result": "HTTP_ERROR"}, None
        finally:
            exc.close()
    except (URLError, OSError, TimeoutError) as exc:
        return {"http": None, "result": categorize_error(exc)}, None


def normalized_imdb(value):
    found = IMDB.fullmatch(str(value or ""))
    return str(int(found.group(1))) if found else None


def candidate_ids(recent):
    """At most four unique genuine recent IMDb entries; never print IDs."""
    rows = recent.get("torrents") if isinstance(recent, dict) else None
    if not isinstance(rows, list):
        return []
    selected = []
    for item in rows[:5]:
        if not isinstance(item, dict):
            continue
        imdb = normalized_imdb(item.get("imdb_id"))
        magnet = item.get("magnet_url")
        if imdb and imdb not in selected and isinstance(magnet, str) and MAGNET.match(magnet):
            selected.append(imdb)
        if len(selected) >= MAX_CANDIDATES:
            break
    return selected


def result_counts(payload, imdb):
    if not isinstance(payload, dict):
        return {"valid_echo": False, "declared_count": None,
                "page_rows": None, "matching_magnets": 0}
    declared = payload.get("torrents_count")
    if type(declared) not in (int, str) or not str(declared).isdigit():
        declared = None
    rows = payload.get("torrents")
    valid = 0
    if isinstance(rows, list):
        for item in rows:
            if not isinstance(item, dict) or normalized_imdb(item.get("imdb_id")) != imdb:
                continue
            magnet = item.get("magnet_url")
            if isinstance(magnet, str) and MAGNET.match(magnet):
                valid += 1
    return {"valid_echo": normalized_imdb(payload.get("imdb_id")) == imdb,
            "declared_count": int(declared) if declared is not None else None,
            "page_rows": len(rows) if isinstance(rows, list) else None,
            "matching_magnets": valid}


def run(opener=None):
    opener = opener or no_proxy_opener()
    print(json.dumps({"probe": "redirect-and-torrentz", "fixed_targets": 4,
                      "redirection_followed": False}))
    for source in TARGETS:
        print(json.dumps(inspect_html(source, opener)))
    recent_url = SOURCE + "?limit=5&page=1"
    status, recent = get_api(recent_url, opener)
    ids = candidate_ids(recent)
    print(json.dumps({"probe": "eztv-recent", **status,
                      "unique_genuine_imdb_samples": len(ids)}))
    for position, imdb in enumerate(ids, 1):
        # One fixed-origin filtered request per distinct recent sample.
        url = SOURCE + "?imdb_id=" + imdb + "&limit=100&page=1"
        status, data = get_api(url, opener)
        print(json.dumps({"probe": "eztv-filter-sample", "sample_number": position,
                          **status, **(result_counts(data, imdb) if data is not None else {})}))
    print(json.dumps({"done": True, "no_services_changed": True,
                      "note": "Source filter counts, not magnet availability, determine next action"}))


if __name__ == "__main__":
    run()
