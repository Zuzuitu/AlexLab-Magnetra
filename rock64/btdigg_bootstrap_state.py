#!/usr/bin/env python3
"""One-shot, opt-in BTDigg browser bootstrap state. No source access here.

Only a strict, private prior search QUERY is stored, never cookies, HTML,
source tokens or magnets. This module does no Chromium or network work.
"""
from __future__ import annotations

import os
from pathlib import Path
import stat
import sys
import tempfile

LAST_QUERY = "last-verified-query.txt"
BOOT_MARKER = "bootstrap-boot-id"
QUERY_MAX = 180
CONTROL = set(range(0x20)) | {0x7f}


def _safe_directory(directory):
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("invalid persistent state directory")
    info = directory.stat()
    if info.st_uid != os.geteuid() or info.st_mode & 0o077:
        raise ValueError("insecure persistent state directory")


def _query(value):
    if not isinstance(value, str) or not 2 <= len(value.strip()) <= QUERY_MAX:
        raise ValueError("invalid search query")
    value = value.strip()
    if any(ord(c) in CONTROL for c in value):
        raise ValueError("invalid search query")
    return value


def _load_file(path, max_bytes):
    if path.is_symlink():
        raise ValueError("symlinked state file")
    try:
        info = path.stat()
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid():
        raise ValueError("unsafe state file")
    if info.st_mode & 0o077 or info.st_size > max_bytes:
        raise ValueError("unsafe state file")
    with path.open("rb") as inp:
        body = inp.read(max_bytes + 1)
    if len(body) > max_bytes:
        raise ValueError("oversized state file")
    return body.decode("utf8")


def _write_file(directory, name, value):
    _safe_directory(directory)
    destination = directory / name
    if destination.is_symlink():
        raise ValueError("symlinked state target")
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf8", dir=directory,
            prefix=".magnetra-bootstrap-", delete=False
        ) as handle:
            tmp = Path(handle.name)
            os.fchmod(handle.fileno(), 0o600)
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, destination)
    finally:
        if tmp is not None:
            tmp.unlink(missing_ok=True)


class BootstrapState:
    def __init__(self, state_dir):
        self.directory = Path(state_dir)
        _safe_directory(self.directory)

    def last_query(self):
        try:
            text = _load_file(self.directory / LAST_QUERY, 800)
            return _query(text) if text is not None else None
        except (OSError, UnicodeError, ValueError):
            return None

    def remember_verified(self, query):
        """Only caller-verified canonical HTML may authorize saving a query."""
        _write_file(self.directory, LAST_QUERY, _query(query))

    def claim_boot_attempt(self, boot_id=None):
        """Never initiate a second automatic source visit in one OS boot."""
        if boot_id is None:
            boot_id = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
        import uuid
        parsed = str(uuid.UUID(boot_id))
        marker = self.directory / BOOT_MARKER
        prior = _load_file(marker, 64)
        if prior == parsed:
            return False
        # Durable marker is committed BEFORE the caller is allowed to navigate.
        _write_file(self.directory, BOOT_MARKER, parsed)
        return True


def main(argv):
    if len(argv) != 2:
        print("Usage: btdigg_bootstrap_state.py --seed-query <text>", file=sys.stderr)
        return 2
    source = BootstrapState(
        Path.home() / ".local/state/magnetra-btdigg-browser"
    )
    if source.last_query() is not None:
        print("SEED=EXISTS (no overwrite; no source requests)")
        return 0
    source.remember_verified(argv[1])
    print("SEED=WRITTEN (private local state; no source requests)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] != "--seed-query":
        print("Usage: btdigg_bootstrap_state.py --seed-query <text>",
              file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1:]))
