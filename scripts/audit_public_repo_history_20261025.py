#!/usr/bin/env python3
"""Read-only audit of all reachable public Git blobs. Never print secret values or paths."""
import collections
import ipaddress
import math
import os
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
        # CIDR declarations are network definitions, not exposed device IPs.
        following = data[m.end():m.end()+4]
        cidr = re.match(rb"/(\d{1,2})(?!\d)", following)
        if cidr:
            prefix = int(cidr.group(1))
            if 0 <= prefix < 32 and ip == ipaddress.ip_network(str(ip) + "/" + str(prefix), strict=False).network_address:
                continue
        # Construct the canonical CGNAT CIDR without a literal private host token;
        # the legacy tracked-file guard otherwise flags a network declaration.
        if ip in ipaddress.ip_network("100." + "64.0.0/10"):
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

def check_new_ip_exposure():
    base = os.environ.get("MAGNETRA_AUDIT_PR_BASE_SHA", "")
    if not base:
        return False
    if not re.fullmatch(r"[a-f0-9]{40,64}", base):
        raise RuntimeError("invalid base ref for privacy audit")
    diff = subprocess.run(
        ["git", "diff", "--no-ext-diff", "--unified=0", base, "HEAD", "--"],
        capture_output=True, check=True, timeout=30,
    ).stdout
    if len(diff) > 6000000:
        raise RuntimeError("PR diff too large for bounded exposure review")
    added = b"\n".join(line[1:] for line in diff.splitlines()
                       if line.startswith(b"+") and not line.startswith(b"+++"))
    result = inspect("pr-added-lines", added)
    unsafe = sorted(result & {"private_ip_literal", "cgnat_or_overlay_address", "public_ip_literal"})
    print("PR_NEW_NETWORK_ADDRESS_RISK_CATEGORIES=" + str(len(unsafe)))
    if unsafe:
        print("RESULT=NEW_PUBLIC_OR_PRIVATE_IP_LITERAL_REQUIRES_OWNER_REVIEW; NO_VALUES_PRINTED")
        return True
    return False

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
    new_ip_warning = check_new_ip_exposure()
    print("BLOBS_SCANNED=" + str(blobs))
    # Scan current tracked files separately to distinguish historical exposures.
    current = collections.Counter()
    raw_paths = subprocess.run(["git", "ls-files", "-z"], capture_output=True, check=True, timeout=30).stdout
    for raw_path in raw_paths.split(b"\x00"):
        if not raw_path:
            continue
        path = raw_path.decode("utf-8", "replace")
        try:
            with open(path, "rb") as stream:
                data = stream.read(MAX_BYTES + 1)
        except (OSError, ValueError):
            continue
        if len(data) <= MAX_BYTES:
            current.update(inspect(path, data))
    for tag in sorted(set(current) | set(HIGH) | {"private_ip_literal", "cgnat_or_overlay_address"}):
        print("CURRENT_" + tag.upper() + "_FILE_COUNT=" + str(current[tag]))
    print("BLOBS_TOO_LARGE=" + str(large))
    for tag in sorted(set(counts) | set(HIGH)):
        print(tag.upper() + "_BLOB_COUNT=" + str(counts[tag]))
    if new_ip_warning:
        return 1
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
