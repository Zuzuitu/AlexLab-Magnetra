#!/usr/bin/env python3
"""No-network tests for BTDigg production-vs-candidate differential."""
import importlib.util
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import call, patch

PATH = Path(__file__).with_name("diagnose-btdigg-production-vs-candidate.py")
spec = importlib.util.spec_from_file_location("magnetra_btdigg_compare", PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


def success(n=2):
    magnet = "magnet:?xt=urn:btih:" + "c" * 40
    results = [{"provider": "btdigg", "name": "Sample", "magnet": magnet}] * n
    return 200, {"results": results, "total": n,
                 "stats": [{"provider": "btdigg", "count": n, "ok": True}],
                 "errors": []}


class DifferentialTests(unittest.TestCase):
    def test_fixed_canonical_query(self):
        self.assertEqual(mod.PATH, "/api/search?q=ubuntu&providers=btdigg&category=all")

    def test_old_and_candidate_are_only_called_after_old_pass(self):
        with patch.dict(os.environ, {"MAGNETRA_BTDIGG_COMPARE_APPROVAL": "COMPARE_OLD_THEN_CANDIDATE"}), \
             patch.object(mod.e2e, "check_deployment"), patch.object(mod.e2e, "check_routing_fingerprint"), \
             patch.object(mod, "check_one_version", side_effect=[("PASS", 3), ("PASS", 3)]) as check:
            self.assertEqual(mod.run(), 0)
            self.assertEqual(check.call_args_list,
                             [call(candidate=False), call(candidate=True)])

    def test_source_504_stops_without_candidate_probe_or_retry(self):
        with patch.dict(os.environ, {"MAGNETRA_BTDIGG_COMPARE_APPROVAL": "COMPARE_OLD_THEN_CANDIDATE"}), \
             patch.object(mod.e2e, "check_deployment"), patch.object(mod.e2e, "check_routing_fingerprint"), \
             patch.object(mod, "check_one_version", return_value=("ERROR_BTDIGG_SOURCE_TIMEOUT_HTTP_504", 0)) as check:
            self.assertEqual(mod.run(), 1)
            check.assert_called_once_with(candidate=False)

    def test_source_rate_limit_stops_without_retry(self):
        with patch.dict(os.environ, {"MAGNETRA_BTDIGG_COMPARE_APPROVAL": "COMPARE_OLD_THEN_CANDIDATE"}), \
             patch.object(mod.e2e, "check_deployment"), patch.object(mod.e2e, "check_routing_fingerprint"), \
             patch.object(mod, "check_one_version", return_value=("ERROR_RATE_LIMIT_HTTP_429", 0)) as check:
            self.assertEqual(mod.run(), 1)
            check.assert_called_once_with(candidate=False)

    def test_manual_approval_is_fail_closed(self):
        with patch.dict(os.environ, {"MAGNETRA_BTDIGG_COMPARE_APPROVAL": "CANCEL"}), \
             patch.object(mod.e2e, "check_deployment") as gate:
            self.assertEqual(mod.run(), 2)
            gate.assert_not_called()

    def test_not_positive_from_only_http_200(self):
        with patch.object(mod.e2e, "request_api", return_value=(200, {"results": [], "errors": [],
                         "stats": [{"provider": "btdigg", "ok": True, "count": 0}]})):
            self.assertEqual(mod.check_one_version(candidate=False)[0], "SOURCE_EMPTY_UNVERIFIED")

    def test_genuine_source_owned_magnet_validation(self):
        with patch.object(mod.e2e, "request_api", return_value=success(2)) as req:
            self.assertEqual(mod.check_one_version(candidate=True), ("PASS", 2))
            req.assert_called_once_with(mod.PATH, candidate=True)

    def test_wrong_source_fails(self):
        status, body = success(1)
        body["results"][0] = dict(body["results"][0], provider="oxtorrent")
        with patch.object(mod.e2e, "request_api", return_value=(status, body)):
            self.assertEqual(mod.check_one_version(candidate=True)[0],
                             "INVALID_OR_FOREIGN_MAGNET_ROWS")

    def test_schema_error_cannot_pass(self):
        status, body = success(1)
        body["stats"][0]["count"] = 999
        with patch.object(mod.e2e, "request_api", return_value=(status, body)):
            self.assertEqual(mod.check_one_version(candidate=False)[0], "RESULT_COUNTER_MISMATCH")

    def test_provider_error_logged_as_safe_code_only(self):
        payload = {"results": [], "stats": [], "errors": [{
            "code": "BTDIGG_SOURCE_TIMEOUT",
            "error": "BTDigg Rock64 source timed out (HTTP 504) CONFIDENTIAL_TOKEN"
        }]}
        with patch.object(mod.e2e, "request_api", return_value=(200, payload)):
            self.assertEqual(mod.check_one_version(candidate=False),
                             ("ERROR_BTDIGG_SOURCE_TIMEOUT_HTTP_504", 0))

    def test_old_pass_candidate_fail_classified(self):
        with patch.dict(os.environ, {"MAGNETRA_BTDIGG_COMPARE_APPROVAL": "COMPARE_OLD_THEN_CANDIDATE"}), \
             patch.object(mod.e2e, "check_deployment"), patch.object(mod.e2e, "check_routing_fingerprint"), \
             patch.object(mod, "check_one_version", side_effect=[
                 ("PASS", 10), ("ERROR_BTDIGG_TUNNEL_TIMEOUT", 0)]) as check:
            self.assertEqual(mod.run(), 1)
            self.assertEqual(check.call_count, 2)


if __name__ == "__main__":
    unittest.main()
