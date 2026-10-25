"""Offline safety of zero-slot diagnostic; never search providers or write Cloudflare."""
import unittest
from unittest.mock import patch
import diagnose_curated_11_zero_readonly_20261025 as d

class Checks(unittest.TestCase):
 def test_exact_version_no_workflow_mutations(self):
  self.assertEqual(d.SPLIT,{d.ACTIVE:100,d.NEW:0})
  self.assertEqual(len(d.ASSETS),5)
  self.assertNotIn("/api/search",[p for p,_ in d.ASSETS])
  self.assertNotIn("/api/resolve",[p for p,_ in d.ASSETS])
 def test_only_good_static_returns_pass(self):
  with patch.object(d,"candidate_http",return_value=(d.ROOT/"web/app.js").read_bytes()):
   self.assertTrue(d.check_asset("/app.js","web/app.js"))
  with patch.object(d,"candidate_http",return_value=b"bad"):
   self.assertFalse(d.check_asset("/app.js","web/app.js"))
 def test_mismatched_split_stops_before_candidate_get(self):
  with patch.object(d,"validated_source"),patch.object(d,"snapshot",return_value=({"id":"other"},{d.ACTIVE:100})),patch.object(d,"candidate_http") as req:
   with self.assertRaises(d.Stop):d.run()
   req.assert_not_called()
if __name__=="__main__":unittest.main()
