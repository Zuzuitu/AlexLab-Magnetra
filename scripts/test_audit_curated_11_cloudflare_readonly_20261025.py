"""Offline tests for the curated 11-indexer Cloudflare GET-only preflight."""
import hashlib
import json
import unittest
from unittest.mock import patch
import audit_curated_11_cloudflare_readonly_20261025 as a

ACTIVE=a.EXPECTED_ACTIVE
ZERO="24642346-9db0-4cea-a56e-12e30f35569f"

class TestReadOnly(unittest.TestCase):
    def test_source_guards(self):
        a.source_check()

    def test_public_allowlist_never_allows_magnets_or_writes(self):
        for path in ("/api/search","/api/resolve","/api/companion/magnet","https://example.com/"):
            with self.assertRaises(a.Stop):a.get_public(path)

    def test_single_active_and_rollback_slot(self):
        payload={"id":"deployment-a"}
        with patch.object(a,"_get_api",side_effect=[{"result":{"deployments":[{"id":"deployment-a","created_on":"2026-10-25T00:00:00Z","versions":[{"version_id":ACTIVE,"percentage":100},{"version_id":ZERO,"percentage":0}]}],"success":True}},{"success":True},{"success":True},{"result":{"deployments":[{"id":"deployment-a","created_on":"2026-10-25T00:00:00Z","versions":[{"version_id":ACTIVE,"percentage":100},{"version_id":ZERO,"percentage":0}]}],"success":True}}]),patch.object(a,"verify_binding_payload") as bindings:
            active,zero=a.observe_split()
            self.assertEqual(active,ACTIVE)
            self.assertEqual(zero,[ZERO])
            self.assertEqual(bindings.call_count,2)

    def test_public_proven_catalog_and_hash(self):
        response={
            "/app.js":b"test",
            "/api/health":json.dumps({"ok":True,"total":46,"ported":46}).encode(),
            "/api/providers":json.dumps({"providers":[{"id":x} for x in ["subsplease"]+["p"+str(i) for i in range(45)]]}).encode()
        }
        with patch.object(a,"get_public",side_effect=lambda path:response[path]),patch.object(a,"EXPECTED_PUBLIC_JS_PREFIX",hashlib.sha256(b"test").hexdigest()[:16]):
            self.assertEqual(a.live_public_check(),"old45")

    def test_race_stops_before_reporting_success(self):
        first={"success":True,"result":{"deployments":[{"id":"dep1","created_on":"2026-10-25T00:00:00Z","versions":[{"version_id":ACTIVE,"percentage":100}]}]}}
        other={"success":True,"result":{"deployments":[{"id":"dep2","created_on":"2026-10-25T00:01:00Z","versions":[{"version_id":ACTIVE,"percentage":100}]}]}}
        with patch.object(a,"_get_api",side_effect=[first,{"success":True},other]),patch.object(a,"verify_binding_payload"):
            with self.assertRaises(a.Stop):a.observe_split()

if __name__=="__main__":unittest.main()
