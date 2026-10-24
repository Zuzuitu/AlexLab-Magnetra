"""Offline read-only Cloudflare Version URL audit safety fixtures."""
import os
import unittest
from pathlib import Path
from unittest.mock import patch

import diagnose_therarbag_iphone_version_url_20261024 as diag


class PreviewAuditTests(unittest.TestCase):
    def test_preview_host_requires_explicit_active_setting_and_bounded_subdomain(self):
        self.assertIsNone(diag.preview_host({"subdomain": "sample"}, {"previews_enabled": False}))
        self.assertIsNone(diag.preview_host({"subdomain": "sample"}, {}))
        host = diag.preview_host({"subdomain": "sample"}, {"previews_enabled": True})
        self.assertEqual(host, "139d97f7-alexlab-magnetra.sample.workers.dev")
        for value in ("../../evil", "sample.example", "a"*64, "a_b", ""):
            with self.subTest(value=value), self.assertRaises(diag.Stop):
                diag.preview_host({"subdomain": value}, {"previews_enabled": True})

    def test_cloudflare_api_allowlist_refuses_unreviewed_calls(self):
        with patch.dict(os.environ, {"CLOUDFLARE_API_TOKEN": "test",
                                      "CLOUDFLARE_ACCOUNT_ID": "0"*32}):
            with self.assertRaises(diag.Stop):
                diag.api_get("/workers/scripts/bad-worker/subdomain")

    def test_network_preview_path_guard_has_no_side_effects(self):
        for path in ("/api/companion/magnet", "/api/resolve", "https://evil.com", "/private"):
            with self.subTest(path=path), self.assertRaises(diag.Stop):
                diag.fixed_preview_get("139d97f7-alexlab-magnetra.sample.workers.dev",
                                       path, accept="application/json", max_bytes=100)
        with self.assertRaises(diag.Stop):
            diag.fixed_preview_get("evil.example", "/api/health",
                                   accept="application/json", max_bytes=100)

    def test_approval_gate_prevents_any_cloudflare_read(self):
        with patch.dict(os.environ, {"MAGNETRA_THERARBAG_PREVIEW_AUDIT_ACTION": ""}), \
             patch.object(diag, "proof") as proof:
            self.assertEqual(diag.main(), 2)
            proof.assert_not_called()

    def test_disabled_preview_is_noop_and_not_error_or_fake_url(self):
        original = {"id": "unchanged"}
        def resource(path):
            if path == "/deployments": return {"unused": True}
            return {"success": True, "result": {"id": diag.VERSION,
                "resources": {"bindings": [
                    {"name": name, "type": next(iter(allowed))}
                    for name, allowed in diag.EXPECTED_BINDINGS.items()
                ]}}}
        with patch.object(diag, "_get_api", side_effect=resource), \
             patch.object(diag, "_current_deployment", return_value=original), \
             patch.object(diag, "_shares", return_value=diag.EXPECTED_SPLIT), \
             patch.object(diag, "api_get", side_effect=[
                 {"subdomain": "sample"}, {"previews_enabled": False}
             ]), patch.object(diag, "fixed_preview_get") as preview:
            self.assertIs(diag.proof(), False)
            preview.assert_not_called()

    def test_success_requires_identical_reviewed_app_and_46_provider_health(self):
        original = {"id": "unchanged"}
        js = (diag.ROOT / "web/app.js").read_bytes()
        payloads = [("application/json", b'{"ok":true,"ported":46,"total":46}'),
                    ("application/javascript", js)]
        with patch.object(diag, "_get_api", return_value={"unused": True}), \
             patch.object(diag, "_current_deployment", return_value=original), \
             patch.object(diag, "_shares", return_value=diag.EXPECTED_SPLIT), \
             patch.object(diag, "verify_binding_payload"), \
             patch.object(diag, "api_get", side_effect=[
                 {"subdomain": "sample"}, {"previews_enabled": True}
             ]), patch.object(diag, "fixed_preview_get", side_effect=payloads) as network:
            self.assertIs(diag.proof(), True)
            self.assertEqual(network.call_count, 2)
            self.assertEqual(network.call_args_list[0].args[1], "/api/health")
            self.assertEqual(network.call_args_list[1].args[1], "/app.js")

    def test_wrong_traffic_split_stops_before_version_url(self):
        with patch.object(diag, "_get_api", return_value={"unused": True}), \
             patch.object(diag, "_current_deployment", return_value={"id": "old"}), \
             patch.object(diag, "_shares", return_value={diag.ACTIVE:95, diag.VERSION:5}), \
             patch.object(diag, "api_get") as api:
            with self.assertRaises(diag.Stop):
                diag.proof()
            api.assert_not_called()


if __name__ == "__main__":
    unittest.main()
