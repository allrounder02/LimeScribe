"""Unit tests for cross-platform clipboard shortcut selection."""

import unittest
from unittest.mock import patch

from core import text_output


class TextOutputShortcutTests(unittest.TestCase):
    def test_paste_shortcut_uses_command_on_macos(self):
        with patch.object(text_output.sys, "platform", "darwin"):
            self.assertEqual(text_output._paste_hotkey_keys(), ("command", "v"))

    def test_paste_shortcut_uses_ctrl_elsewhere(self):
        with patch.object(text_output.sys, "platform", "linux"):
            self.assertEqual(text_output._paste_hotkey_keys(), ("ctrl", "v"))


if __name__ == "__main__":
    unittest.main()
