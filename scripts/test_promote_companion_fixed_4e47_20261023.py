"""Offline fail-closed control tests for fixed immutable Companion rollout."""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, call

sys.path.insert(0, str(Path(__file__).resolve().parent))
import promote_companion_fixed_4e47_20261023 as r

class SafeReleaseTests(unittest.TestCase):
    def test_only_exact_owner_action_allows_any_call(self):
        with patch.dict(os.environ, {"MAGNETRA_COMPANION_FIXED_PROMOTION_ACTION": ""}):
            with patch.object(r, "release", side_effect=AssertionError("not authorized")):
                self.assertEqual(r.main(), 2)

    def test_verified_candidate_old_and_new_immutable_ids(self):
        self.assertEqual(r.BASELINE, {r.OLD:100, r.FIXED:0})
        self.assertEqual(r.CANARY, {r.OLD:95, r.FIXED:5})
        self.assertEqual(r.FULL, {r.OLD:0, r.FIXED:100})
        self.assertEqual(r.PROOF_STATUS, 401)
        self.assertEqual(r.PROOF_MARKER, "upstream-http-401")
        self.assertNotEqual(r.OLD, r.FIXED)

    def test_source_review_rejects_drift_and_matches_reviewed_main(self):
        self.assertTrue(r.source_guard())

    def test_exact_promotion_preserves_identities_and_verifies_postflight(self):
        previous={"id":"baseline"}
        next_dep={"id":"canary"}
        with patch.object(r,"stable") as stable, \
             patch.object(r,"_wrangler_deploy",return_value=True) as deploy, \
             patch.object(r,"wait_for",return_value=next_dep) as wait, \
             patch.object(r,"attest_candidate") as candidate:
            result=r.promote(previous,r.BASELINE,r.CANARY,95,5,"CANARY_5")
        self.assertEqual(result,next_dep)
        deploy.assert_called_once()
        args=deploy.call_args.args[0]
        self.assertEqual(args,[r.OLD+"@95%",r.FIXED+"@5%"])
        wait.assert_called_once_with(previous,r.BASELINE,r.CANARY,True)
        stable.assert_has_calls([call(previous,r.BASELINE),call(next_dep,r.CANARY)])
        candidate.assert_called_once()

    def test_release_orders_5_and_100_only_after_success(self):
        with patch.object(r,"preflight",return_value={"id":"old"}), \
             patch.object(r,"promote",side_effect=[{"id":"five"},{"id":"full"}]) as promote, \
             patch.object(r,"restore_if_safe") as restore:
            self.assertEqual(r.release(),0)
        self.assertEqual(promote.call_count,2)
        self.assertEqual(promote.call_args_list[0].args[1:],[r.BASELINE,r.CANARY,95,5,"CANARY_5"])
        self.assertEqual(promote.call_args_list[1].args[1:],[r.CANARY,r.FULL,0,100,"PRODUCTION_100"])
        restore.assert_not_called()

    def test_canary_failure_blocks_full_and_attempts_guarded_rollback(self):
        with patch.object(r,"preflight",return_value={"id":"old"}), \
             patch.object(r,"promote",side_effect=r.Stop("test failure")) as promote, \
             patch.object(r,"restore_if_safe",return_value=True) as restore:
            self.assertEqual(r.release(),1)
        self.assertEqual(promote.call_count,1)
        restore.assert_called_once()

    def test_unrecognized_split_refuses_rollback(self):
        bad={r.OLD:33,r.FIXED:67}
        with patch.object(r,"snapshot",return_value=({"id":"unknown"},bad)), \
             patch.object(r,"_wrangler_deploy",side_effect=AssertionError("forbidden")):
            self.assertFalse(r.restore_if_safe())

    def test_canary_rollback_explicitly_restores_previous_100(self):
        prior={"id":"canary-deployment"}
        after={"id":"restored"}
        with patch.object(r,"snapshot",return_value=(prior,r.CANARY)), \
             patch.object(r,"stable"), \
             patch.object(r,"attest_candidate"), \
             patch.object(r,"_wrangler_deploy",return_value=True) as deploy, \
             patch.object(r,"wait_for",return_value=after) as wait:
            self.assertTrue(r.restore_if_safe())
        self.assertEqual(deploy.call_args.args[0],[r.OLD+"@100%",r.FIXED+"@0%"])
        wait.assert_called_once_with(prior,r.CANARY,r.BASELINE,True)

if __name__=="__main__":
    unittest.main()
