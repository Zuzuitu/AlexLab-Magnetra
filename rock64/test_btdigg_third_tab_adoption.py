#!/usr/bin/env python3
"""Offline: owner manually verifies a third BTDigg tab after two refusals."""
import unittest

from rock64 import btdigg_browser_backend as backend
from rock64.test_btdigg_browser_backend import FakePage, HTML


def three_tabs(*, selected=1):
    first = FakePage(valid=False)
    first.rate_limited = True
    second = first.context.new_page()
    second.rate_limited = True
    second.url = backend.query_url("The Dog Stars 2026")
    third = first.context.new_page()
    third.url = backend.query_url("The Dog Stars 2026")
    third.valid = True
    pages = [first, second, third]
    fetcher = backend.VisibleBrowserFetcher(pages[selected])
    fetcher._recovery_attempts = 2
    fetcher._record_recovery("visible_refusal", 200)
    return fetcher, pages


class ThirdTabAdoptionTests(unittest.TestCase):
    def test_live_owner_shape_is_readonly_until_one_owner_search(self):
        gateway, (first, second, third) = three_tabs()
        state = gateway.browser_state()
        self.assertEqual((state["open_tabs"], state["verified_tabs"]), (3, 1))
        self.assertEqual(state["selected_tab_index"], 1)
        self.assertFalse(state["selected_tab_verified"])
        self.assertTrue(state["visible_source_rate_limited"])
        self.assertFalse(state["visible_captcha_required"])
        self.assertTrue(state["new_searches_paused"])
        self.assertEqual(state["pwa_tab_recovery_attempts"], 2)
        self.assertEqual([x["paired_rows"] for x in state["tab_diagnostics"]],
                         [0, 0, 1])
        self.assertFalse(any(p.closed for p in (first, second, third)))
        self.assertEqual([p.goto_calls for p in (first, second, third)],
                         [[], [], []])

    def test_same_query_adopts_third_and_closes_both_refusals_no_source_request(self):
        fetcher, (first, second, third) = three_tabs()
        self.assertEqual(fetcher.fetch("THE dog STARS 2026"),
                         (200, HTML.encode("utf-8")))
        self.assertTrue(first.closed)
        self.assertTrue(second.closed)
        self.assertFalse(third.closed)
        self.assertIs(fetcher.page, third)
        self.assertIs(fetcher.reference_page, third)
        self.assertEqual([p.goto_calls for p in (first, second, third)],
                         [[], [], []])
        self.assertEqual([p.submit_calls for p in (first, second, third)],
                         [0, 0, 0])
        state = fetcher.browser_state()
        self.assertEqual((state["open_tabs"], state["verified_tabs"]), (1, 1))
        self.assertTrue(state["selected_tab_verified"])
        self.assertFalse(state["visible_source_rate_limited"])
        self.assertFalse(state["new_searches_paused"])
        self.assertEqual(state["pwa_tab_recovery_last_outcome"],
                         "manual_verified_tab_adopted")
        self.assertEqual(state["pwa_tab_recovery_attempts"], 2)
        # Repeating the identical query reuses source HTML without navigation.
        self.assertEqual(fetcher.fetch("The Dog Stars 2026")[0], 200)
        self.assertEqual(third.submit_calls, 0)

    def test_selected_first_refusal_also_adopts_exact_third(self):
        fetcher, pages = three_tabs(selected=0)
        self.assertEqual(fetcher.fetch("The Dog Stars 2026")[0], 200)
        self.assertTrue(all(p.closed for p in pages[:2]))
        self.assertFalse(pages[2].closed)

    def test_mismatch_does_not_trigger_second_request_or_close_tabs(self):
        fetcher, pages = three_tabs()
        self.assertEqual(fetcher.fetch("Entirely Different Movie 2026"),
                         (425, b""))
        self.assertTrue(all(not p.closed for p in pages))
        self.assertEqual(sum(p.submit_calls for p in pages), 0)
        self.assertEqual(sum(len(p.goto_calls) for p in pages), 0)
        self.assertEqual(fetcher.browser_state()["open_tabs"], 3)

    def test_ambiguous_manual_third_tab_fails_closed(self):
        cases = ("blank", "challenge", "foreign", "two_verified",
                 "selected_valid", "real_http429")
        for variant in cases:
            with self.subTest(variant=variant):
                fetcher, pages = three_tabs()
                if variant == "blank":
                    pages[0].rate_limited = False
                    pages[0].url = "about:blank"
                elif variant == "challenge":
                    pages[2].valid = False
                    pages[2].body_text = "Please verify you are human"
                elif variant == "foreign":
                    pages[2].url = "https://example.invalid/test"
                elif variant == "two_verified":
                    pages[0].valid = True
                    pages[0].rate_limited = False
                elif variant == "selected_valid":
                    pages[1].valid = True
                    pages[1].rate_limited = False
                elif variant == "real_http429":
                    fetcher._source_stopped = 429
                    fetcher._last_upstream_http_status = 429
                self.assertFalse(fetcher._adopt_owner_verified_tab(
                    "The Dog Stars 2026"))
                self.assertNotEqual(fetcher.fetch("The Dog Stars 2026")[0], 200)
                self.assertTrue(all(not p.closed for p in pages))
                self.assertEqual(sum(p.submit_calls for p in pages), 0)
                self.assertEqual(sum(len(p.goto_calls) for p in pages), 0)

    def test_four_tabs_cannot_adopt_or_navigate(self):
        fetcher, pages = three_tabs()
        extra = pages[0].context.new_page()
        extra.rate_limited = True
        extra.valid = False
        self.assertEqual(fetcher.fetch("The Dog Stars 2026"), (425, b""))
        self.assertTrue(all(not p.closed for p in [*pages, extra]))
        self.assertEqual(extra.goto_calls, [])


if __name__ == "__main__":
    unittest.main()
