"""Fail-closed, offline checks for the Home logo + TPB serializer guarded release."""
import inspect
import os
import unittest
from unittest.mock import patch
import release_home_tpb_serial_guarded_20261027 as release

ACTIVE="fdffdc78-0bd3-4721-a5b1-11f515c52bd1"
ROLLBACK="40bfd647-2b8a-4643-94f2-577e723aba97"

class HomeTPBGuardTests(unittest.TestCase):
    def test_expected_previous_release_versions_and_web_v11_hash(self):
        self.assertEqual(release.BASELINE,{ACTIVE:100,ROLLBACK:0})
        self.assertEqual(release.OLD_PUBLIC_GIT_BLOB,"b77e000acd3dba27961b37167139337b53a42aef")
        self.assertEqual(release.PINNED_BLOBS["web/sw.js"],"07476f8637667f5ec72b07d628421267b69f9feb")
        self.assertEqual(release.PINNED_BLOBS["worker/src/verified-source-cache.mjs"],"0a3b5de0234edbb16df931ab7073e3240983be95")

    def test_manual_dispatch_is_explicitly_required(self):
        with patch.dict(os.environ,{"MAGNETRA_HOME_TPB_RELEASE_ACTION":""}):
            with patch.object(release,"release") as do_release:
                self.assertEqual(release.main(),2)
                do_release.assert_not_called()
        self.assertEqual(release.ACTION,"CONFIRM_MAGNETRA_HOME_TPB_SERIAL_20261027")

    def test_execute_actual_reviewed_source_hashes_and_iOS_home_guard(self):
        cfg=release.source_guard()
        self.assertEqual(cfg["name"],"alexlab-magnetra")

    def test_no_provider_quota_consuming_positive_queries(self):
        code=inspect.getsource(release.release)
        self.assertNotIn("prove_original_positive_searches",code)
        self.assertNotIn("thepiratebay",code)
        self.assertIn("verify_candidate(NEW)",code)
        self.assertIn("public_postflight(NEW)",code)

    def test_live_asset_guard_checks_previous_service_worker_not_unchanged_app(self):
        code=inspect.getsource(release.release)
        self.assertIn('old_bytes=candidate_http("/sw.js",None)',code)
        self.assertNotIn('live_http("/sw.js")',code)
        self.assertIn('"/sw.js":"javascript"',inspect.getsource(release.candidate_http))
        self.assertIn("OLD_PUBLIC_GIT_BLOB",code)
        self.assertIn("stable(first,BASELINE)",code)

    def test_previous_real_v11_service_worker_passes_prewrite_guard(self):
        # Simulate the exact previously deployed immutable SW from the v12
        # reviewed source by reversing only the approved version bump.
        current=(release.ROOT/"web/sw.js").read_bytes()
        self.assertEqual(current.count(b'alexlab-magnetra-v12'),1)
        previous=current.replace(b'alexlab-magnetra-v12',b'alexlab-magnetra-v11')
        import hashlib
        blob=hashlib.sha1(b"blob "+str(len(previous)).encode()+b"\\x00"+previous).hexdigest()
        self.assertEqual(blob,release.OLD_PUBLIC_GIT_BLOB)
        self.assertNotEqual(current,previous)
        requests=[]
        def public_asset(path,version):
            requests.append((path,version))
            return previous
        with patch.object(release,"source_guard",return_value={"name":"alexlab-magnetra"}), \\
             patch.object(release,"split_guard",return_value=object()), \\
             patch.object(release,"candidate_http",side_effect=public_asset), \\
             patch.object(release,"stable"), \\
             patch.object(release,"upload",side_effect=release.Stop("EXPECTED_BEFORE_UPLOAD")) as upload:
            with self.assertRaisesRegex(release.Stop,"EXPECTED_BEFORE_UPLOAD"):
                release.release()
            upload.assert_called_once()
        self.assertEqual(requests,[("/sw.js",None)],"same-origin asset, no legacy HTTP helper")

    def test_unknown_baseline_must_stop_before_immutable_upload(self):
        with patch.object(release,"source_guard",return_value={}), \
             patch.object(release,"split_guard",side_effect=release.Stop("UNKNOWN_LIVE_SPLIT")), \
             patch.object(release,"upload") as upload:
            with self.assertRaises(release.Stop):release.release()
            upload.assert_not_called()

    def test_unknown_traffic_split_is_not_rolled_back_blindly(self):
        with patch.object(release,"snapshot",return_value=(object(),{ACTIVE:84,ROLLBACK:16})), \
             patch.object(release,"_wrangler_deploy") as change:
            release.rollback_if_safe("11111111-1111-4111-8111-111111111111")
            change.assert_not_called()

    def test_no_unapproved_remote_paths_or_credential_dump(self):
        with self.assertRaises(release.Stop):
            release.candidate_http("/api/search?q=linux&providers=thepiratebay",
                                   "11111111-1111-4111-8111-111111111111")
        text=inspect.getsource(release)
        self.assertIn("verify_binding_payload(NEW,_get_api",text)
        self.assertIn("verify_reviewed_html",text)
        self.assertNotIn("print(os.environ",text)

if __name__=="__main__":
    unittest.main()
