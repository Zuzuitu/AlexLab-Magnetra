"""Offline contract tests; all credentials/addresses in fixtures are synthetic."""
import unittest
from check_public_repo_exposure import scan_path


class PublicRepositoryExposureGuardTests(unittest.TestCase):
    def test_literal_secret_formats_blocked(self):
        fake_github_token = ("ghp_" + "X" * 36).encode("ascii")
        self.assertIn(("github-personal-token", 1), scan_path("sample.txt", fake_github_token))
        fake_worker_secret = ("MAGNETRA_GATEWAY_TOKEN=" + "Z" * 56).encode("ascii")
        self.assertIn(("literal-server-secret", 1), scan_path("sample.txt", fake_worker_secret))

    def test_local_addresses_are_blocked_without_embedding_real_address(self):
        synthetic_lan = ".".join(("192", "168", "250", "250")).encode("ascii")
        synthetic_overlay = ".".join(("100", "101", "250", "250")).encode("ascii")
        self.assertIn(("internal-ipv4", 1), scan_path("notes.md", synthetic_lan))
        self.assertIn(("internal-ipv4", 1), scan_path("notes.md", synthetic_overlay))
        self.assertEqual([], scan_path("notes.md", b"127.0.0.1 1.1.1.1"))

    def test_private_material_and_secret_files_are_blocked(self):
        header = b"-----BEGIN " + b"OPENSSH PRIVATE KEY-----"
        self.assertIn(("private-key-pem", 1), scan_path("random.md", header))
        self.assertIn(("credential-file-committed", 0), scan_path("etc/gateway.env", b""))
        self.assertIn(("credential-file-committed", 0), scan_path(".env.production", b""))
        self.assertIn(("credential-file-committed", 0), scan_path("android/release.jks", b""))

    def test_template_and_variable_references_remain_safe(self):
        self.assertEqual([], scan_path(".env.example", b"EXAMPLE_TOKEN=replace-me\n"))
        ref = b"CLOUDFLARE_API_TOKEN: " + b"$" + b"{{ secrets.CLOUDFLARE_API_TOKEN }}"
        self.assertEqual([], scan_path("workflow.yml", ref))
        self.assertEqual([], scan_path("adapter.js", b'headers: {"authorization":"Bearer "+secret}\n'))

    def test_sanitized_categories_never_contain_original_value(self):
        secret = ("github_pat_" + "A" * 70).encode("ascii")
        findings = scan_path("sample.txt", b"line\n" + secret)
        self.assertEqual(findings, [("github-personal-token", 2)])
        self.assertNotIn(secret.decode("ascii"), str(findings))


if __name__ == "__main__":
    unittest.main()
