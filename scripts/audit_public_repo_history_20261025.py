#!/usr/bin/env python3
"""Read-only audit of all reachable public Git blobs. Never print secret values or paths."""
import collections
import ipaddress
import math
import re
import subprocess
import sys

MAX_BYTES = 2000000
HIGH = ("private_key", "credential_file", "token_pattern", "literal_credential", "embedded_auth")
SECRET_NAMES = re.compile(r"(?i)(?:^|/)(?:\.env(?:\.[^/]*)?|id_(?:rsa|ed25519|ecdsa)|credentials\.json|[^/]+\.(?:pem|p12|pfx|jks|keystore))$")
KEY = re.compile(rb"-----BEGIN (?:OPENSSH |RSA |EC |DSA |ENCRYPTED )?PRIVATE KEY-----")
TOKEN = re.compile(rb"\b(?:gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{35,}|sk-[A-Za-z0-9_-]{30,})\b")
ASSIGN = re.compile(rb"(?i)\b(?:api[_-]?key|api[_-]?token|access[_-]?token|refresh[_-]?token|password|passwd|passkey|client[_-]?secret|auth[_-]?secret|webhook[_-]?secret|private[_-]?key)\b[\s\"']*[:=]\s*[\"']([^\"'\r\n]{14,200})[\"']")
BEARER = re.compile(rb"(?i)\b(?:Bearer|Basic)\s+([A-Za-z0-9_+/=-]{24,200})\b")
URL_AUTH = re.compile(rb"(?i)https?://[^\s/@:]{3,80}:[^\s/@]{8,100}@")
IPV4 = re.compile(rb"(?<![0-9.])(?:\d{1,3}\.){3}\d{1,3}(?![0-9.])")
HOSTNAME = re.compile(rb"(?i)\b[a-z0-9-]+\.alexlab\.media\b")
EXAMPLES = ("example", "placeholder", "replace", "changeme", "dummy", "test", "fake", "mock", "xxx", "your_", "redacted", "not-real", "<", "env.", "secrets.", "os.environ", "process.env")

def entropy(v):
    n = collections.Counter(v)
    return -sum((c / len(v)) * math.log2(c / len(v)) for c in n.values()) if v else 0

def probable_credential(v):
    lower = v.decode("utf-8", "ignore").lower()
    return (len(v) >= 16 and not any(x in lower for x in EXAMPLES)
            and re.search(rb"[A-Za-z]", v) is not None
            and re.search(rb"[0-9]", v) is not None
            and entropy(v) >= 3.6)

def inspect(path, data):
    result = set()
    if SECRET_NAMES.search(path) and not re.search(r"(?i)(?:example|sample|template|dist)$", path):
        result.add("credential_file")
    if b"\x00" in data[:1024]:
        return result
    if KEY.search(data):
        result.add("private_key")
    if TOKEN.search(data):
        result.add("token_pattern")
    if URL_AUTH.search(data):
        result.add("embedded_auth")
    if any(probable_credential(m.group(1)) for m in ASSIGN.finditer(data)) or any(probable_credential(m.group(1)) for m in BEARER.finditer(data)):
        result.add("literal_credential")
    if HOSTNAME.search(data):
        result.add("public_architecture_hostname")
    for m in IPV4.finditer(data):
        try:
            ip = ipaddress.IPv4Address(m.group().decode("ascii"))
        except ipaddress.AddressValueError:
            continue
        if ip.is_loopback or ip.is_multicast or ip.is_link_local or ip.is_unspecified:
            continue
        if ip in ipaddress.ip_network("100.64.0.0/10"):
            result.add("cgnat_or_overlay_address")
        elif ip.is_private:
            if not any(ip in ipaddress.ip_network(x) for x in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24")):
                result.add("private_ip_literal")
        else:
            result.add("public_ip_literal")
    return result

def read_exact(stream, count):
    blocks = []
    while count:
        buf = stream.read(min(65536, count))
        if not buf:
            raise RuntimeError("git object stream truncated")
        blocks.append(buf)
        count -= len(buf)
    return b"".join(blocks)

def run():
    raw = subprocess.run(["git", "rev-list", "--objects", "--all"], capture_output=True, check=True, timeout=90).stdout
    objects = {}
    for line in raw.decode("utf-8", "replace").splitlines():
        oid, sep, path = line.partition(" ")
        if sep and path and re.fullmatch(r"[a-f0-9]{40,64}", oid):
            objects.setdefault(oid, path)
    if not objects or len(objects) > 250000:
        raise RuntimeError("Git object count outside safe audit bounds")
    counts = collections.Counter()
    large = blobs = 0
    with subprocess.Popen(["git", "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=0) as proc:
        for oid, path in objects.items():
            proc.stdin.write((oid + "\n").encode("ascii"))
            proc.stdin.flush()
            header = proc.stdout.readline().decode("ascii", "replace").split()
            if len(header) != 3 or header[0] != oid:
                raise RuntimeError("Git object response mismatch")
            kind, size = header[1], int(header[2])
            if kind != "blob":
                read_exact(proc.stdout, size + 1)
                continue
            blobs += 1
            if size > MAX_BYTES:
                large += 1
                read_exact(proc.stdout, size + 1)
                if SECRET_NAMES.search(path):
                    counts["credential_file"] += 1
                continue
            data = read_exact(proc.stdout, size)
            if proc.stdout.read(1) != b"\n":
                raise RuntimeError("Invalid Git blob terminator")
            counts.update(inspect(path, data))
        proc.stdin.close()
    print("MAGNETRA_PUBLIC_HISTORY_AUDIT: reached Git blobs only; no paths, IP addresses, keys or values emitted")
    print("BLOBS_SCANNED=" + str(blobs))
    print("BLOBS_TOO_LARGE=" + str(large))
    for tag in sorted(set(counts) | set(HIGH)):
        print(tag.upper() + "_BLOB_COUNT=" + str(counts[tag]))
    if any(counts[k] for k in HIGH):
        print("RESULT=SECURITY_REVIEW_REQUIRED; DO_NOT_PUBLISH_MATCHING_SECRET_VALUES")
        return 1
    if large:
        print("RESULT=PARTIAL_AUDIT_REQUIRES_LARGE_BLOB_REVIEW")
        return 2
    print("RESULT=NO_HIGH_CONFIDENCE_SECRET_PATTERNS; PUBLIC_ARCHITECTURE_MUST_BE_REVIEWED_SEPARATELY")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(run())
    except (OSError, RuntimeError, subprocess.SubprocessError):
        print("RESULT=INCOMPLETE_AUDIT; NO SECRET MATERIAL PRINTED")
        sys.exit(2)
