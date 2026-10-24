import unittest
from unittest.mock import patch
import diagnose_therarbag_iphone_exact_size_20261024 as d

class ExactCardTests(unittest.TestCase):
    def test_exact_card_selection_and_fail_closed(self):
        name="[2026.10.20]Cyberpunk: Edgerunners 2 (Original Series Soundtrack)[FLAC]"
        card={"provider":"therarbag","name":name,"size":"352.7 MB","details":"https://therarbg.com/post-detail/95bf8b/item/?src=listing"}
        self.assertTrue(d.exact_title_and_size(card))
        for change in [{"size":"1.2 GB"},{"name":"Totally different title"},{"provider":"oxtorrent"},{"size":"352.8 MB"}]:
            self.assertFalse(d.exact_title_and_size({**card,**change}))
    def test_matching_logs_only_safe_fields(self):
        name="Cyberpunk: Edgerunners 2 (Original Series Soundtrack)"
        url="https://therarbg.com/post-detail/95bf8b/private-title/?tracking=secret"
        with patch("builtins.print") as logger:
            d.inspect({"results":[{"name":name,"size":"352.7 MB","provider":"therarbag","details":url,"magnet":"private magnet data"}]})
        text=" ".join(" ".join(map(str,c.args)) for c in logger.call_args_list)
        self.assertIn("SOURCE_DETAIL_SHAPE: QUERY_PRESENT",text)
        self.assertIn("SAME_FINAL_URL_ID: True",text)
        self.assertNotIn(url,text)
        self.assertNotIn(name,text)
        self.assertNotIn("private",text)
        self.assertNotIn("secret",text)
    def test_normal_card_on_original_url(self):
        with patch("builtins.print") as logger:
            d.inspect({"results":[{"name":"Cyberpunk Edgerunners 2 Original Series Soundtrack","size":"352.7 MB","provider":"therarbag","details":d.PUBLIC_URL}]})
        text=" ".join(" ".join(map(str,c.args)) for c in logger.call_args_list)
        self.assertIn("EXACT_OWNER_FINAL_URL: True",text)
        self.assertIn("SOURCE_DETAIL_SHAPE: JSON_URL_ACCEPTABLE",text)
    def test_zero_match_is_not_claimed_as_successful_fix(self):
        with patch("builtins.print") as logger:
            d.inspect({"results":[]})
        text=" ".join(" ".join(map(str,c.args)) for c in logger.call_args_list)
        self.assertIn("NO_MATCH_DIFFERENT_SEARCH_SNAPSHOT_NO_INFERENCE",text)
    def test_requires_approval_without_egress(self):
        with patch.object(d.sys,"argv",["script"]),patch.object(d,"api_search") as search:
            self.assertEqual(d.main(),2)
            search.assert_not_called()

if __name__=="__main__":unittest.main()
