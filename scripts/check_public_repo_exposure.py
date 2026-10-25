#!/usr/bin/env python3
"""Fail-closed tracked-file exposure guard for the public Magnetra repository.

No network access, no token contents in stdout, and no public home-address
allowlist embedded in source. This is a defense-in-depth pattern scanner, not
a substitute for GitHub secret scanning or an audit of every historical blob.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

MAX_SCAN_BYTES = 2_000_000
PRIVATE_IPV4 = re.compile(
    rb"\b(?:10\.(?:\d{1,3}\.){2}\d{1,3}|"
    rb"192\.168\.\d{1,3}\.\d{1,3}|"
    rb"172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|"
    rb"100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7])\.\d{1,3}\.\d{1,3})\b"
)
# IPv6 ULA / link-local literals identify local infrastructure as well.
PRIVATE_IPV6 = re.compile(rb"(?<![a-fA-F0-9])(?:f[cd]|fe[89ab])[a-fA-F0-9]{2}:(?:[a-fA-F0-9:]{2,})", re.I)
SIGNATURES = {
    "private-key-pem": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----"),
    "github-personal-token": re.compile(rb"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{60,})\b"),
    "cloud-provider-access-key": re.compile(rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "google-api-key": re.compile(rb"\bAIza[0-9A-Za-z_-]{35}\b"),
    "slack-token": re.compile(rb"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
    "jwt-bearer": re.compile(rb"\beyJ[A-Za-z0-9_-]{20,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{8,}\b"),
    "literal-server-secret": re.compile(
        rb"\b(?:CLOUDFLARE_API_TOKEN|MAGNETRA_BTDIGG_TOKEN|MAGNETRA_EZTV_TOKEN|"
        rb"MAGNETRA_GATEWAY_TOKEN|BTDIGG_GATEWAY_TOKEN)\s*[:=]\s*['\"]?[A-Za-z0-9_-]{40,}"
    ),
    "internal-ipv4": PRIVATE_IPV4,
    "internal-ipv6": PRIVATE_IPV6,
}

SECRET_FILENAMES = {
    "gateway.env", "tunnel-token", "credentials.json",
    "id_rsa", "id_ed25519",
}
SECRET_SUFFIXES = (".pem", ".p12", ".pfx", ".jks", ".keystore")
MAX_RESULTS = 30


def scan_path(path: str, content: bytes) -> list[tuple[str, int]]:
    """Return only categories and line numbers, never matched values."""
    name = pathlib.PurePosixPath(path).name
    if (
        name in SECRET_FILENAMES
        or name.endswith(SECRET_SUFFIXES)
        or name == ".env"
        or name.startswith(".env.") and name != ".env.example"
    ):
        return [("credential-file-committed", 0)]
    if b"\x00" in content[:4096]:
        return []
    if len(content) > MAX_SCAN_BYTES:
        return [("text-scan-size-limit", 0)]
    findings = []
    for label, pattern in SIGNATURES.items():
        for hit in pattern.finditer(content):
            findings.append((label, content.count(b"\n", 0, hit.start()) + 1))
            if len(findings) >= MAX_RESULTS:
                return findings
    return findings


def tracked_files() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "-z"], check=True, capture_output=True,
    ).stdout
    return sorted(p.decode("utf-8", errors="strict") for p in out.split(b"\0") if p)


def main() -> int:
    failures = 0
    files = tracked_files()
    for path in files:
        p = pathlib.Path(path)
        if not p.is_file():
            continue
        try:
            content = p.read_bytes()
        except OSError:
            print(f"SECURITY_GUARD_UNREADABLE: {path}")
            return 2
        hits = scan_path(path, content)
        if hits:
            failures += len(hits)
            for label, line in hits[:MAX_RESULTS]:
                print(f"PUBLIC_REPO_EXPOSURE: {path}:{line} [{label}]")
    if failures:
        print(f"PUBLIC_REPO_EXPOSURE: STOP ({failures} categorized matches; no values printed)")
        return 1
    print(f"PUBLIC_REPO_EXPOSURE: PASS ({len(files)} tracked paths, no high-confidence matches)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
