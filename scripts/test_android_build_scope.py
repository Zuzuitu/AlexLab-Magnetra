#!/usr/bin/env python3
"""Offline confidence for automatic APK build scope, including fail-open policy."""
import importlib.util
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from unittest import TestCase, main
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "android_scope", HERE / "android_build_scope.py"
)
SCOPE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCOPE)
ROOT = HERE.parent


class AndroidBuildScopeTests(TestCase):
    def test_non_android_changes_skip_gradle(self):
        for path in ("rock64/btdigg_browser_backend.py",
                     "worker/src/index.mjs", "web/app.js",
                     "docs/PROJECT_STATE.md", "config/project-invariants.json",
                     "scripts/android_build_scope.py"):
            self.assertFalse(SCOPE.affects_android(path), path)
        self.assertFalse(SCOPE.build_required(
            "pull_request", ("rock64/test_btdigg_browser_backend.py",)))
        self.assertFalse(SCOPE.build_required(
            "push", ("web/sw.js", "docs/NEXT_CHAT_HANDOFF.md")))

    def test_all_android_modifications_trigger_real_apk(self):
        for path in (
            "app/src/main/AndroidManifest.xml",
            "app/src/main/kotlin/example/File.kt",
            "app/build.gradle.kts",
            "gradle/libs.versions.toml",
            "gradle/wrapper/gradle-wrapper.properties",
            "gradlew",
            "settings.gradle.kts",
            "build.gradle.kts",
            "gradle.properties",
            "fastlane/metadata/android/en-US/title.txt",
            "buildSrc/src/main/kotlin/BuildConfig.kt",
            "build-logic/convention/build.gradle.kts",
            ".github/workflows/debug_build.yml",
            ".github/workflows/staging_build.yml",
            ".github/workflows/release_build.yml",
        ):
            with self.subTest(path=path):
                self.assertTrue(SCOPE.affects_android(path))
                self.assertTrue(SCOPE.build_required("pull_request", (path,)))

    def test_uncertain_or_manual_events_fail_open(self):
        for event, paths in [
            ("workflow_dispatch", ()),
            ("schedule", ()),
            ("pull_request", None),
            ("push", None),
        ]:
            with self.subTest(event=event):
                self.assertTrue(SCOPE.build_required(event, paths))
        self.assertFalse(SCOPE.build_required("push", ()))

    def test_pull_request_uses_merge_base_and_push_uses_exact_diff(self):
        old, new = "a" * 40, "b" * 40
        for event, expected in [
            ("pull_request", old + "..." + new),
            ("push", old + ".." + new),
        ]:
            with self.subTest(event=event):
                completed = subprocess.CompletedProcess(
                    [], 0, b"rock64/foo.py\x00app/src/a.kt\x00", b""
                )
                with patch.object(SCOPE.subprocess, "run", return_value=completed) as run:
                    self.assertEqual(
                        SCOPE.changed_paths(event, old, new),
                        ("rock64/foo.py", "app/src/a.kt"),
                    )
                command = run.call_args.args[0]
                self.assertEqual(command, [
                    "git", "diff", "--name-only", "-z", expected, "--"
                ])
                self.assertFalse(run.call_args.kwargs.get("shell", False))

    def test_invalid_revision_and_diff_errors_build_instead_of_skipping(self):
        old, new = "a" * 40, "b" * 40
        for before in ("", "bad", "0" * 40):
            self.assertIsNone(SCOPE.changed_paths("push", before, new))
        with patch.object(
            SCOPE.subprocess, "run",
            side_effect=subprocess.CalledProcessError(128, ["git", "diff"]),
        ):
            self.assertIsNone(SCOPE.changed_paths("pull_request", old, new))
        with patch.object(SCOPE.subprocess, "run", side_effect=TimeoutError()):
            self.assertIsNone(SCOPE.changed_paths("push", old, new))
        self.assertTrue(SCOPE.build_required("push", None))

    def test_workflows_keep_required_status_checks_but_gate_expensive_steps(self):
        for file in ("debug_build.yml", "staging_build.yml"):
            content = (ROOT / ".github" / "workflows" / file).read_text()
            self.assertIn("pull_request:", content)
            self.assertIn("workflow_dispatch:", content)
            self.assertIn("fetch-depth: 0", content)
            self.assertIn("id: android_scope", content)
            self.assertIn("scripts/android_build_scope.py", content)
            self.assertIn("python3 scripts/check-project-invariants.py", content)
            self.assertIn("Skip APK build for non-Android changes", content)
            # Every expensive step (JDKs, Gradle, rename/upload) is gated.
            for name in (
                "Set up JDK 17",
                "Set up JetBrains Runtime 21",
                "Grant execute permission for gradlew",
                "Assemle debug APK with gradlew" if file == "debug_build.yml"
                    else "Assemble staging APK with gradlew",
                "Rename APK file to torrentsearch-debug.apk" if file == "debug_build.yml"
                    else "Rename APK file to torrentsearch-staging.apk",
                "Upload debug APK" if file == "debug_build.yml" else "Upload staging APK",
            ):
                from_here = content.index("- name: " + name)
                next_step = content.find("\n    - name:", from_here + 1)
                section = content[from_here:next_step if next_step > 0 else None]
                self.assertIn(
                    "if: steps.android_scope.outputs.build_required == 'true'",
                    section,
                    (file, name),
                )


if __name__ == "__main__":
    main()
