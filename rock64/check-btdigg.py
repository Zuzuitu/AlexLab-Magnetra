#!/usr/bin/env python3
"""One-time LOCAL check; run with sudo only after installing the gateway.

Never prints credentials, full magnet links, filenames or search metadata.
Never sends any command to Flud Companion.
"""
import re
import sys
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

TOKEN_FILE = "/etc/magnetra-btdigg/gateway.env"
LOCAL_URL = "http://127.0.0.1:8796/v1/search?q=ubuntu"


class Evidence(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = 0
        self.magnets = 0

    def handle_starttag(self, tag, attrs):
        pairs = dict(attrs)
        classes = (pairs.get("class") or "").split()
        if tag == "div" and "one_result" in classes:
            self.rows += 1
        href = pairs.get("href") or ""
        if tag == "a" and re.match(
            r"^magnet:\?xt=urn:btih:(?:[0-9a-f]{40}|[a-z2-7]{32})(?:&|$)",
            href, re.I
        ):
            self.magnets += 1


def main():
    try:
        with open(TOKEN_FILE, encoding="utf8") as source:
            text = source.read()
        token = next(
            line.split("=", 1)[1].strip()
            for line in text.splitlines()
            if line.startswith("MAGNETRA_BTDIGG_TOKEN=")
        )
        req = Request(LOCAL_URL, headers={"Authorization": "Bearer " + token})
        with urlopen(req, timeout=15) as response:
            status = response.status
            body = response.read(3_000_001)
        if len(body) > 3_000_000:
            print("FAIL: oversized BTDigg response")
            return 1
        evidence = Evidence()
        evidence.feed(body.decode("utf8", errors="replace"))
        print("Local Rock64 HTTP:", status)
        print("Real BTDigg search page rows:", evidence.rows)
        print("Magnet links found:", evidence.magnets)
        if status != 200 or not evidence.rows or not evidence.magnets:
            print("NOT VERIFIED: source selectors or upstream access still need investigation.")
            return 1
        print("PASS: real BTDigg result HTML reached Rock64 gateway.")
        return 0
    except HTTPError as exc:
        print("BTDigg Rock64 gateway returned HTTP", exc.code)
        return 1
    except (OSError, URLError, ValueError, StopIteration):
        print("Rock64 gateway not ready; check its local service and protected token file.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
