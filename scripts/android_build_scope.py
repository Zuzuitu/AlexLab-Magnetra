#!/usr/bin/env python3
"""Fail-open GitHub Actions scope gate for optional Android debug/staging APK builds.

Every PR still runs both named CI workflows and the project invariants.
Gradle/JDK/APK upload run only for relevant Android diffs or manual dispatch.
This script never contacts external APIs; it uses the checked-out Git history.
"""
from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess

ANDROID_PREFIXES = (
    "app/",
    "gradle/",
    "buildSrc/",
    "build-logic/",
    "fastlane/",
)
ANDROID_FILES = frozenset({
    "build.gradle",
    "build.gradle.kts",
    "settings.gradle",
    "settings.gradle.kts",
    "gradle.properties",
    "gradlew",
    "gradlew.bat",
    ".github/workflows/debug_build.yml",
    ".github/workflows/staging_build.yml",
    ".github/workflows/release_build.yml",
})
SHA_PATTERN = re.compile(r"[0-9a-fA-F]{40}\Z")


def affects_android(path: str) -> bool:
    """Return true for source, Gradle toolchain, packaging, or CI changes."""
    clean = path.replace("\\", "/")
    return clean in ANDROID_FILES or clean.startswith(ANDROID_PREFIXES)


def changed_paths(event: str, before: str, after: str) -> tuple[str, ...] | None:
    """A None result means uncertainty and MUST trigger a real build."""
    if event not in ("pull_request", "push"):
        return None
    if (not SHA_PATTERN.fullmatch(before or "")
            or not SHA_PATTERN.fullmatch(after or "")
            or before == "0" * 40):
        return None
    # Three dots for PR: compare merge base to PR head, not unrelated changes
    # that entered main while the PR was open. Push uses exact old..new range.
    diff = before + ("..." if event == "pull_request" else "..") + after
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "-z", diff, "--"],
            capture_output=True,
            check=True,
            timeout=30,
        )
        return tuple(
            entry.decode("utf-8", errors="surrogateescape")
            for entry in result.stdout.split(b"\x00")
            if entry
        )
    except (OSError, subprocess.SubprocessError, UnicodeError):
        return None


def build_required(event: str, paths: tuple[str, ...] | None) -> bool:
    # Manual runs, unsupported events and uncertain history fail open.
    return event not in ("pull_request", "push") or paths is None or any(
        affects_android(path) for path in paths
    )


def main() -> None:
    event = os.environ.get("MAGNETRA_CI_EVENT", "")
    paths = changed_paths(
        event,
        os.environ.get("MAGNETRA_CI_BASE_SHA", ""),
        os.environ.get("MAGNETRA_CI_HEAD_SHA", ""),
    )
    required = build_required(event, paths)
    value = "true" if required else "false"
    print(
        "ANDROID_BUILD_SCOPE=" + ("BUILD" if required else "SKIP")
        + " (reason="
        + ("manual_or_unverified_diff" if paths is None else "changed_paths")
        + ")"
    )
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with Path(output).open("a", encoding="utf-8") as stream:
            stream.write("build_required=" + value + "\n")


if __name__ == "__main__":
    main()
