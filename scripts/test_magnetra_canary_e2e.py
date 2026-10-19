#!/usr/bin/env python3
"""Offline fail-closed tests for the 95/5 read-only HTML E2E."""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import call, patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import importlib.util

path = Path(__file__).with_name("check-magnetra-canary-e2e.py")
spec = importlib.util.spec_from_file_location("magnetra_canary_gate", path)
gate = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = gate
spec.loader.exec_module(gate)

OLD = "a9df4429-1111-4111-8111-111111111111"
NEW = gate.VERSION
BINDINGS = [{"name": name, "type": typ} for name, typ in (
    ("BTDIGG_GATEWAY_TOKEN", "secret_text"),
    ("MAGNETRA_GATEWAY_TOKEN", "secret_key"),
    ("ASSETS", "assets"),
)]
VERSION = {"success": True, "result": {"id": NEW, "resources": {"bindings": BINDINGS}}}


def record(percent_old=95, percent_new=5, old=OLD, ident="slot1"):
    return {"success": True, "result": {"deployments": [{
        "id": ident, "created_on": "2026-10-19T10:00:00Z",
        "versions": [
            {"version_id": old, "percentage": percent_old},
            {"version_id": NEW, "percentage": percent_new},
        ],
    }]}}


class CanaryGateTests(unittest.TestCase):
    def test_exact_95_5_and_all_bindings(self):
        with patch.object(gate, "_get_api", side_effect=[VERSION, record()]):
            self.assertEqual(gate.deployment(), (OLD, "slot1"))

    def test_reject_100_0_100_only_wrong_or_unknown(self):
        unknown = "bbbbbbbb-1111-4111-8111-111111111111"
        for deployment in (record(100, 0), record(94, 6),
                           record(95, 5, old=unknown), record(95, 5, ident="")):
            with self.subTest(deployment=deployment):
                with patch.object(gate, "_get_api", side_effect=[VERSION, deployment]):
                    with self.assertRaises(gate.Stop):
                        gate.deployment()

    def test_reject_missing_binding(self):
        bad = {"success": True, "result": {"id": NEW, "resources": {
            "bindings": BINDINGS[:1]}}}
        with patch.object(gate, "_get_api", side_effect=[bad, record()]):
            with self.assertRaises(gate.Stop):
                gate.deployment()

    def test_exact_fingerprint_requires_old_404_and_candidate_200_46(self):
        with patch.object(gate, "old_route_status", return_value=404):
            with patch.object(gate._source, "request_api",
                              return_value=(200, {"providers": [{"id": str(i)} for i in range(46)]})):
                gate.exact_version_fingerprint(OLD)
        with patch.object(gate, "old_route_status", return_value=200):
            with patch.object(gate._source, "request_api") as new:
                with self.assertRaises(gate.Stop):
                    gate.exact_version_fingerprint(OLD)
                new.assert_not_called()
        with patch.object(gate, "old_route_status", return_value=404):
            with patch.object(gate._source, "request_api",
                              return_value=(404, None)):
                with self.assertRaises(gate.Stop):
                    gate.exact_version_fingerprint(OLD)

    def test_refuse_changed_deployment_after_e2e(self):
        with patch.object(gate, "_get_api", return_value=record(94, 6)):
            with self.assertRaises(gate.Stop):
                gate.verify_not_changed("slot1", OLD)
        with patch.object(gate, "_get_api", return_value=record(95, 5, ident="other")):
            with self.assertRaises(gate.Stop):
                gate.verify_not_changed("slot1", OLD)

    def test_no_approval_makes_zero_cloudflare_or_source_calls(self):
        with patch.dict(os.environ, {"MAGNETRA_CANARY_E2E_CHOICE": "CANCEL"}):
            with patch.object(gate, "_get_api") as cloudflare:
                with patch.object(gate._source, "validate_search") as search:
                    with self.assertRaisesRegex(gate.Stop, "EXPLICIT_READONLY"):
                        gate.execute()
                    cloudflare.assert_not_called()
                    search.assert_not_called()

    def test_html_scope_checks_only_original_two_and_never_btdigg(self):
        with patch.dict(os.environ, {"MAGNETRA_CANARY_E2E_CHOICE": gate.RUN_HTML}):
            with patch.object(gate, "deployment", return_value=(OLD, "slot1")), \
                 patch.object(gate, "exact_version_fingerprint"), \
                 patch.object(gate._source, "check_catalog"), \
                 patch.object(gate._source, "validate_search", return_value=[{"details": "test"}]) as search, \
                 patch.object(gate._source, "check_resolve") as resolve, \
                 patch.object(gate._source, "check_eztv_positive") as eztv, \
                 patch.object(gate._source, "check_btdigg_observational") as btdigg, \
                 patch.object(gate, "verify_not_changed"):
                self.assertEqual(gate.execute(), 0)
                self.assertEqual(search.call_args_list, [
                    call("oxtorrent", "ubuntu"), call("torrent9", "ubuntu")])
                self.assertEqual(resolve.call_count, 2)
                eztv.assert_not_called()
                btdigg.assert_not_called()

    def test_eztv_scope_calls_one_bounded_positive_check(self):
        with patch.dict(os.environ, {"MAGNETRA_CANARY_E2E_CHOICE": gate.RUN_HTML_EZTV}):
            with patch.object(gate, "deployment", return_value=(OLD, "slot1")), \
                 patch.object(gate, "exact_version_fingerprint"), \
                 patch.object(gate._source, "check_catalog"), \
                 patch.object(gate._source, "validate_search", return_value=[]) as search, \
                 patch.object(gate._source, "check_resolve"), \
                 patch.object(gate._source, "check_eztv_positive", return_value=True) as eztv, \
                 patch.object(gate._source, "check_btdigg_observational") as btdigg, \
                 patch.object(gate, "verify_not_changed"):
                self.assertEqual(gate.execute(), 0)
                eztv.assert_called_once()
                btdigg.assert_not_called()
                self.assertEqual(search.call_count, 2)


if __name__ == "__main__":
    unittest.main()
