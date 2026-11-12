#!/usr/bin/env python3
"""Offline contract: Android CI never rebuilds APKs for Rock64/PWA edits.

The release-signing workflow remains owner-triggered; these tests do not
execute GitHub Actions or any Gradle/Android task.
"""
import fnmatch
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = (
    ".github/workflows/debug_build.yml",
    ".github/workflows/staging_build.yml",
)
RELEVANT = (
    "app/src/main/AndroidManifest.xml",
    "app/build.gradle.kts",
    "gradle/wrapper/gradle-wrapper.properties",
    "gradlew",
    "gradlew.bat",
    "build.gradle.kts",
    "settings.gradle.kts",
    "gradle.properties",
    *WORKFLOWS,
)
IRRELEVANT = (
    "rock64/btdigg_browser_backend.py",
    "rock64/test_btdigg_browser_backend.py",
    "worker/src/index.mjs",
    "web/app.js",
    "docs/PROJECT_STATE.md",
    "docs/NEXT_CHAT_HANDOFF.md",
    "README.md",
    "scripts/check-project-invariants.py",
    ".github/workflows/pwa.yml",
)


class AndroidCIPathFilterTests(unittest.TestCase):
    def test_android_jobs_only_run_for_android_inputs_or_manual_dispatch(self):
        for workflow in WORKFLOWS:
            with self.subTest(workflow=workflow):
                content = (ROOT / workflow).read_text(encoding="utf-8")
                trigger = content.split("\non:\n", 1)
                self.assertEqual(len(trigger), 2, "on: missing")
                pre_jobs = trigger[1].split("\njobs:\n", 1)
                self.assertEqual(len(pre_jobs), 2, "jobs: missing")
                section = pre_jobs[0]
                self.assertNotIn("paths-ignore:", section)
                self.assertIn("retention-days: 1", content,
                              "temporary APKs must not use 90-day retention")
                self.assertRegex(section, r"(?m)^  workflow_dispatch:\s*$")
                found = {}
                for event in ("push", "pull_request"):
                    match = re.search(
                        rf"(?ms)^  {event}:\n(.*?)(?=^  (?:push|pull_request|workflow_dispatch):|\Z)",
                        section,
                    )
                    self.assertIsNotNone(match, f"{event} trigger missing")
                    event_cfg = match.group(1)
                    self.assertIn('branches: [ "main" ]', event_cfg)
                    self.assertIn("    paths:\n", event_cfg)
                    patterns = re.findall(r"(?m)^      - '([^']+)'\s*$", event_cfg)
                    self.assertTrue(patterns)
                    found[event] = patterns
                    for file in RELEVANT:
                        self.assertTrue(
                            any(fnmatch.fnmatchcase(file, p) for p in patterns),
                            f"{event} misses Android input: {file}",
                        )
                    for file in IRRELEVANT:
                        self.assertFalse(
                            any(fnmatch.fnmatchcase(file, p) for p in patterns),
                            f"{event} incorrectly triggers on: {file}",
                        )
                self.assertEqual(found["push"], found["pull_request"])

    def test_release_build_stays_manual(self):
        release = (ROOT / ".github/workflows/release_build.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("on: workflow_dispatch", release)
        self.assertNotIn("\n  push:\n", release)
        self.assertNotIn("\n  pull_request:\n", release)


if __name__ == "__main__":
    unittest.main()
