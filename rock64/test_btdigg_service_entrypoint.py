#!/usr/bin/env python3
"""Offline source-only regression: never replace CFFI-backed gateway in place."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parent
CHECKER=ROOT/"check-btdigg-service-entrypoint.py"
spec=spec_from_file_location("btdigg_entrypoint_checker", CHECKER)
checker=module_from_spec(spec)
spec.loader.exec_module(checker)


class EffectiveEntryPointTests(unittest.TestCase):
    def test_cffi_is_not_base_updater_or_chromium(self):
        raw=(
            "ExecStart={ path=/opt/magnetra-btdigg/.venv-cffi-0.17.0/bin/python "
            "; argv[]=/opt/magnetra-btdigg/.venv-cffi-0.17.0/bin/python -I "
            "/opt/magnetra-btdigg/btdigg_cffi_gateway.py ; ignore_errors=no }\n"
            "DropInPaths=/etc/systemd/system/magnetra-btdigg.service.d/50-magnetra-cffi.conf\n"
            "ActiveState=active\n"
        )
        state=checker.classify(raw)
        self.assertEqual(state["effective_entrypoint"],"cffi_override")
        self.assertEqual(state["override_types"],["cffi"])
        self.assertFalse(state["base_updater_eligible"])
        self.assertFalse(state["chromium_bridge_enabled"])
        self.assertEqual(state["source_requests"],0)

    def test_base_service_no_override_eligible(self):
        raw=(
            "ExecStart={ path=/usr/bin/python3 ; argv[]=/usr/bin/python3 -I "
            "/opt/magnetra-btdigg/btdigg_gateway.py ; ignore_errors=no }\n"
            "DropInPaths=\nActiveState=active\n"
        )
        state=checker.classify(raw)
        self.assertTrue(state["base_updater_eligible"])
        self.assertFalse(state["chromium_bridge_enabled"])

    def test_stacked_cffi_then_chromium_is_never_a_success(self):
        raw=(
            "ExecStart={ path=/opt/magnetra-btdigg/.venv-cffi-0.17.0/bin/python "
            "; argv[]=/opt/magnetra-btdigg/btdigg_cffi_gateway.py }\n"
            "DropInPaths=/etc/systemd/system/magnetra-btdigg.service.d/20-owner-chromium-bridge.conf "
            "/etc/systemd/system/magnetra-btdigg.service.d/50-magnetra-cffi.conf\n"
            "ActiveState=active\n"
        )
        state=checker.classify(raw)
        self.assertEqual(state["effective_entrypoint"],"cffi_override")
        self.assertFalse(state["chromium_bridge_enabled"])
        self.assertFalse(state["base_updater_eligible"])

    def test_unknown_override_fails_closed_and_no_paths_echoed(self):
        state=checker.classify(
            "ExecStart=/opt/unverified/script.py\n"
            "DropInPaths=/private/secret/99-override.conf\n"
            "ActiveState=failed\n"
        )
        self.assertEqual(state["effective_entrypoint"],"unknown")
        self.assertEqual(state["override_types"],["other"])
        self.assertFalse(state["service_active"])
        self.assertFalse(state["base_updater_eligible"])

    def test_updaters_block_live_cffi_before_mutation(self):
        update=(ROOT/"update-btdigg.sh").read_text()
        activation=(ROOT/"activate-btdigg-chromium-bridge.sh").read_text()
        for text in (update,activation):
            self.assertIn("ACTIVE_DROPINS=",text)
            self.assertIn("50-magnetra-cffi.conf",text)
            self.assertIn("systemctl show",text)
        self.assertLess(update.index("ACTIVE_DROPINS="),update.index('STAGE="$(mktemp'))
        self.assertLess(activation.index("ACTIVE_DROPINS="),
                        activation.index('STAGE_TOKEN="$(mktemp'))
        self.assertIn("READ_ONLY_NEXT:",update)
        self.assertNotIn("/v1/search?",CHECKER.read_text())
        self.assertNotIn("urllib",CHECKER.read_text())


if __name__=="__main__":
    unittest.main()
