import unittest
from contextlib import ExitStack
from unittest.mock import patch

import release_magnetra_one_tap_309 as release


class GuardedRelease(unittest.TestCase):
    old = "11111111-2222-4333-8444-555555555555"

    def setUp(self):
        ctx = self.enterContext(ExitStack())
        self.m = {key:ctx.enter_context(patch.object(release,key)) for key in (
            "source_guard", "snapshot", "critical_binding_guard", "catalog_guard",
            "stable", "_wrangler_deploy", "wait_for", "verify_all_assets",
            "verify_public_with_html_settle", "rollback_if_safe"
        )}
        self.m["snapshot"].return_value = ("baseline", {self.old:100})
        self.m["wait_for"].side_effect = ["zero", "canary", "full"]

    def test_read_only_never_writes(self):
        release.run("READ_ONLY", "")
        self.m["_wrangler_deploy"].assert_not_called()

    def test_missing_or_stale_baseline_never_writes(self):
        for expected in ("", release.NEW):
            with self.assertRaises(release.Stop):
                release.run(release.ACTION, expected)
        self.m["_wrangler_deploy"].assert_not_called()

    def test_promotes_only_after_each_verified_stage(self):
        release.run(release.ACTION, self.old)
        new = release.NEW
        writes = [a.args[0] for a in self.m["_wrangler_deploy"].call_args_list]
        self.assertEqual(writes, [[self.old+"@100%",new+"@0%"],
                                  [self.old+"@95%",new+"@5%"],
                                  [self.old+"@0%",new+"@100%"]])
        self.m["verify_public_with_html_settle"].assert_called_once_with(
            "full", {self.old:0,new:100}
        )

    def test_asset_mismatch_before_canary_leaves_old_live(self):
        self.m["verify_all_assets"].side_effect = release.Stop("asset mismatch")
        with self.assertRaises(release.Stop):
            release.run(release.ACTION, self.old)
        self.m["_wrangler_deploy"].assert_called_once()
        self.m["rollback_if_safe"].assert_not_called()

    def test_failed_canary_does_not_promote_and_requests_bounded_rollback(self):
        self.m["verify_all_assets"].side_effect = [None,release.Stop("failed canary")]
        with self.assertRaises(release.Stop):
            release.run(release.ACTION, self.old)
        self.assertEqual(self.m["_wrangler_deploy"].call_count,2)
        self.m["rollback_if_safe"].assert_called_once_with(self.old,release.NEW)
