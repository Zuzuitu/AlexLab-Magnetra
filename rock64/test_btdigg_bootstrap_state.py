#!/usr/bin/env python3
"""Offline tests for private last-query and one-attempt-per-boot state."""
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from rock64.btdigg_bootstrap_state import BootstrapState, BOOT_MARKER, LAST_QUERY


class BootstrapStateTests(unittest.TestCase):
    def test_private_seed_and_single_boot_attempt(self):
        with TemporaryDirectory() as base:
            d = Path(base)
            state = BootstrapState(d)
            self.assertIsNone(state.last_query())
            state.remember_verified("  The Dog Stars 2026 720p  ")
            self.assertEqual(state.last_query(), "The Dog Stars 2026 720p")
            self.assertEqual((d / LAST_QUERY).stat().st_mode & 0o777, 0o600)
            first_stat=(d / LAST_QUERY).stat().st_mtime_ns
            state.remember_verified("The Dog Stars 2026 720p")
            self.assertEqual((d / LAST_QUERY).stat().st_mtime_ns,first_stat)
            first = "2e0b2420-e8a8-4984-8b4a-84f049a4935b"
            second = "eafee280-0f42-497c-a29b-297f908ab026"
            self.assertTrue(state.claim_boot_attempt(first))
            self.assertFalse(state.claim_boot_attempt(first))
            self.assertEqual((d / BOOT_MARKER).stat().st_mode & 0o777, 0o600)
            self.assertTrue(state.claim_boot_attempt(second))
            self.assertFalse(state.claim_boot_attempt(second))

    def test_bad_query_never_saved(self):
        with TemporaryDirectory() as base:
            state = BootstrapState(base)
            for bad in ["", "a", "x" * 181, "bad\nquery", None]:
                with self.subTest(bad=repr(bad)[:20]):
                    with self.assertRaises(ValueError):
                        state.remember_verified(bad)
            self.assertIsNone(state.last_query())

    def test_rejects_symlinks_permissive_dirs_and_bad_markers(self):
        with TemporaryDirectory() as base:
            d = Path(base)
            state = BootstrapState(d)
            state.remember_verified("Test search 2026")
            (d / LAST_QUERY).unlink()
            (d / LAST_QUERY).symlink_to(d / "other")
            self.assertIsNone(state.last_query())
            with self.assertRaises(ValueError):
                state.remember_verified("Safe query")
            (d / LAST_QUERY).unlink()
            (d / BOOT_MARKER).symlink_to(d / "other")
            with self.assertRaises(ValueError):
                state.claim_boot_attempt("2e0b2420-e8a8-4984-8b4a-84f049a4935b")
            (d / BOOT_MARKER).unlink()
            os.chmod(d, 0o755)
            with self.assertRaises(ValueError):
                BootstrapState(d)

    def test_error_does_not_reset_existing_marker(self):
        with TemporaryDirectory() as base:
            d = Path(base)
            state = BootstrapState(d)
            first = "2e0b2420-e8a8-4984-8b4a-84f049a4935b"
            self.assertTrue(state.claim_boot_attempt(first))
            with self.assertRaises(ValueError):
                state.claim_boot_attempt("INVALID")
            self.assertFalse(state.claim_boot_attempt(first))


if __name__ == "__main__":
    unittest.main()
