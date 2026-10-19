#!/usr/bin/env python3
"""No-network safety tests for manual 100% candidate release and rollback."""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import call, patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import release_magnetra_candidate_100 as m

OLD = "a9df4429-1111-4111-8111-111111111111"
NEW = m.VERSION
OTHER = "bbbbbbbb-1111-4111-8111-111111111111"
BINDINGS = [{"name": name, "type": kind} for name, kind in (
    ("BTDIGG_GATEWAY_TOKEN", "secret_text"),
    ("MAGNETRA_GATEWAY_TOKEN", "secret_key"),
    ("ASSETS", "assets"),
)]
VERSION = {"success": True, "result": {"id": NEW, "resources": {
    "bindings": BINDINGS,
}}}


def dep(shares, ident="d1"):
    return {"success": True, "result": {"deployments": [{
        "id": ident,
        "created_on": "2026-10-19T13:00:00Z",
        "versions": [{"version_id": k, "percentage": v} for k, v in shares.items()],
    }]}}


CANARY = dep({OLD: 95, NEW: 5})
PROMOTED = dep({OLD: 0, NEW: 100}, ident="d2")
RESTORED = dep({OLD: 100, NEW: 0}, ident="d3")


class ReleaseTests(unittest.TestCase):
    def test_default_cancel_never_queries_cloudflare(self):
        with patch.dict(os.environ, {"MAGNETRA_RELEASE_ACTION": "CANCEL"}):
            with patch.object(m, "_get_api") as api:
                with patch.object(m, "_wrangler_deploy") as write:
                    self.assertEqual(m.execute(), 2)
                    api.assert_not_called()
                    write.assert_not_called()

    def test_100_percent_exact_release_preserves_old_version_at_zero(self):
        with patch.dict(os.environ, {"MAGNETRA_RELEASE_ACTION": m.PROMOTE}):
            with patch.object(m, "_get_api", side_effect=[
                    VERSION, CANARY, CANARY, CANARY, PROMOTED]):
                with patch.object(m, "_wrangler_deploy", return_value=True) as write:
                    self.assertEqual(m.execute(), 0)
                    write.assert_called_once()
                    self.assertEqual(write.call_args.args[0],
                                     [OLD + "@0%", NEW + "@100%"])

    def test_release_does_not_start_from_old_100_candidate_zero(self):
        with patch.object(m, "_get_api", side_effect=[
                VERSION, RESTORED, RESTORED]):
            with patch.object(m, "_wrangler_deploy") as write:
                self.assertEqual(m.promote(), 2)
                write.assert_not_called()

    def test_release_rejects_missing_bindings_before_write(self):
        invalid = {"success": True, "result": {"id": NEW, "resources": {
            "bindings": BINDINGS[:2],
        }}}
        with patch.object(m, "_get_api", side_effect=[invalid, CANARY]):
            with patch.object(m, "_wrangler_deploy") as write:
                with self.assertRaises(ValueError):
                    m.promote()
                write.assert_not_called()

    def test_release_rejects_wrong_split_and_unknown_old(self):
        for state in (dep({OLD: 96, NEW: 4}), dep({OTHER: 95, NEW: 5})):
            with self.subTest(state=state):
                with patch.object(m, "_get_api", side_effect=[
                        VERSION, state, state]):
                    with patch.object(m, "_wrangler_deploy") as write:
                        if state["result"]["deployments"][0]["versions"][0]["version_id"] == OTHER:
                            with self.assertRaises(ValueError):
                                m.promote()
                        else:
                            self.assertEqual(m.promote(), 2)
                        write.assert_not_called()

    def test_race_before_write_stops_promotion(self):
        with patch.object(m, "_get_api", side_effect=[
                VERSION, CANARY, CANARY, dep({OLD: 95, NEW: 5}, ident="new")]):
            with patch.object(m, "_wrangler_deploy") as write:
                self.assertEqual(m.promote(), 2)
                write.assert_not_called()

    def test_bounded_postflight_allows_metadata_propagation(self):
        with patch.object(m, "_get_api", side_effect=[
                VERSION, CANARY, CANARY, CANARY, CANARY, PROMOTED]):
            with patch.object(m, "_wrangler_deploy", return_value=True):
                with patch.object(m.time, "sleep") as pause:
                    self.assertEqual(m.promote(), 0)
                    pause.assert_called_once_with(2)

    def test_stale_postflight_is_not_promotion_success(self):
        with patch.object(m, "_get_api", side_effect=[
                VERSION, CANARY, CANARY, CANARY,
                CANARY, CANARY, CANARY, CANARY]):
            with patch.object(m, "_wrangler_deploy", return_value=True):
                with patch.object(m.time, "sleep") as pause:
                    self.assertEqual(m.promote(), 1)
                    self.assertEqual(pause.call_count, 3)

    def test_wrong_known_postflight_attempts_guarded_rollback(self):
        wrong = dep({OLD: 10, NEW: 90}, ident="d2")
        with patch.object(m, "_get_api", side_effect=[
                VERSION, CANARY, CANARY, CANARY, wrong]):
            with patch.object(m, "_wrangler_deploy", return_value=True):
                with patch.object(m, "guarded_restore", return_value=False) as restore:
                    self.assertEqual(m.promote(), 1)
                    restore.assert_called_once_with(OLD)

    def test_unknown_concurrent_postflight_never_force_rolls_back(self):
        unknown = dep({OTHER: 100}, ident="d2")
        with patch.object(m, "_get_api", side_effect=[
                VERSION, CANARY, CANARY, CANARY, unknown]):
            with patch.object(m, "_wrangler_deploy", return_value=True):
                with patch.object(m, "guarded_restore") as restore:
                    self.assertEqual(m.promote(), 1)
                    restore.assert_not_called()

    def test_guarded_restore_corrects_wrong_known_version_split(self):
        wrong = dep({OLD: 90, NEW: 10}, ident="d2")
        with patch.object(m, "_get_api", side_effect=[
                wrong, wrong, RESTORED]):
            with patch.object(m, "_wrangler_deploy", return_value=True) as writer:
                self.assertTrue(m.guarded_restore(OLD))
                self.assertEqual(writer.call_args.args[0],
                                 [OLD + "@100%", NEW + "@0%"])

    def test_guarded_restore_refuses_unknown_third_party_version(self):
        unknown = dep({OLD: 90, OTHER: 10}, ident="d2")
        with patch.object(m, "_get_api", return_value=unknown):
            with patch.object(m, "_wrangler_deploy") as writer:
                self.assertFalse(m.guarded_restore(OLD))
                writer.assert_not_called()

    def test_manual_rollback_from_exact_promoted_to_old_100(self):
        with patch.dict(os.environ, {"MAGNETRA_RELEASE_ACTION": m.ROLLBACK_ACTION}):
            with patch.object(m, "_get_api", side_effect=[
                    PROMOTED, PROMOTED, PROMOTED, RESTORED]):
                with patch.object(m, "_wrangler_deploy", return_value=True) as write:
                    self.assertEqual(m.execute(), 0)
                    self.assertEqual(write.call_args.args[0],
                                     [OLD + "@100%", NEW + "@0%"])

    def test_manual_rollback_from_canary_to_old_100(self):
        with patch.object(m, "_get_api", side_effect=[
                CANARY, CANARY, CANARY, RESTORED]):
            with patch.object(m, "_wrangler_deploy", return_value=True) as write:
                self.assertEqual(m.rollback(), 0)
                self.assertEqual(write.call_args.args[0],
                                 [OLD + "@100%", NEW + "@0%"])

    def test_manual_rollback_already_restored_is_noop(self):
        with patch.object(m, "_get_api", return_value=RESTORED):
            with patch.object(m, "_wrangler_deploy") as write:
                self.assertEqual(m.rollback(), 0)
                write.assert_not_called()

    def test_rollback_refuses_unknown_or_concurrent_deployment(self):
        unknown = dep({OLD: 70, OTHER: 30})
        with patch.object(m, "_get_api", return_value=unknown):
            with patch.object(m, "_wrangler_deploy") as write:
                self.assertEqual(m.rollback(), 2)
                write.assert_not_called()

    def test_rollback_refuses_post_preflight_deployment_race(self):
        changed = dep({OLD: 0, NEW: 100}, ident="different")
        with patch.object(m, "_get_api", side_effect=[PROMOTED, PROMOTED, changed]):
            with patch.object(m, "_wrangler_deploy") as write:
                self.assertEqual(m.rollback(), 1)
                write.assert_not_called()

    def test_rollback_failure_cannot_be_reported_success(self):
        with patch.object(m, "_get_api", side_effect=[
                PROMOTED, PROMOTED, PROMOTED, PROMOTED]):
            with patch.object(m, "_wrangler_deploy", return_value=False):
                self.assertEqual(m.rollback(), 1)


if __name__ == "__main__":
    unittest.main()
