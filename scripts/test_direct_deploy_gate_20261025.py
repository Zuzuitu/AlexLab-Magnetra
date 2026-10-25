"""Ensure descriptive commit messages cannot accidentally trigger direct production deploys."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DeploymentGuardTests(unittest.TestCase):
    def test_direct_deploy_requires_marker_prefix(self):
        workflow = (ROOT / ".github/workflows/deploy-pwa.yml").read_text(encoding="utf-8")
        self.assertIn("startsWith(github.event.head_commit.message, '[deploy-pwa] ')", workflow)
        self.assertNotIn("contains(github.event.head_commit.message, '[deploy-pwa]')", workflow)
        self.assertFalse("release: notes\n\nno generic [deploy-pwa] trigger".startswith("[deploy-pwa] "))
        self.assertTrue("[deploy-pwa] intentional release".startswith("[deploy-pwa] "))

    def test_approval_file_is_checked_after_checkout(self):
        workflow = (ROOT / ".github/workflows/pwa-45-indexers-50-production-20261025.yml").read_text(encoding="utf-8")
        release = workflow.split("  guarded-release:", 1)[1]
        self.assertLess(release.index("uses: actions/checkout@v7.0.1"),
                        release.index("test -s docs/release-events/pwa-45-indexers-50-production-20261025.md"))


if __name__ == "__main__":
    unittest.main()
