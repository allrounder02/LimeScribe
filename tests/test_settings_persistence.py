"""Tests for settings.json persistence of TTS optimization options."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import config


class SettingsPersistenceTests(unittest.TestCase):
    def test_defaults_include_tts_optimization_fields(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            settings_path = Path(tmp_dir) / "settings.json"
            with patch.object(config, "_SETTINGS_PATH", settings_path):
                loaded = config.load_app_settings()

            self.assertTrue(loaded["tts_optimize_long_text"])
            self.assertEqual(loaded["tts_optimize_threshold_chars"], 240)
            self.assertEqual(loaded["chat_model"], config.LEMONFOX_CHAT_MODEL)
            self.assertEqual(loaded["chat_system_prompt"], config.LEMONFOX_CHAT_SYSTEM_PROMPT)
            self.assertTrue(loaded["chat_include_history"])
            self.assertEqual(loaded["voice_max_words_auto_listen"], config.VOICE_MAX_WORDS_AUTO_LISTEN)
            self.assertEqual(loaded["voice_max_words_manual"], config.VOICE_MAX_WORDS_MANUAL)
            self.assertEqual(loaded["output_history"], [])

    def test_save_and_reload_tts_optimization_fields(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            settings_path = Path(tmp_dir) / "settings.json"
            with patch.object(config, "_SETTINGS_PATH", settings_path):
                config.save_app_settings(
                    {
                        "tts_optimize_long_text": False,
                        "tts_optimize_threshold_chars": "360",
                    }
                )
                loaded = config.load_app_settings()

            self.assertFalse(loaded["tts_optimize_long_text"])
            self.assertEqual(loaded["tts_optimize_threshold_chars"], 360)

    def test_invalid_loaded_values_fall_back_to_defaults(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            settings_path = Path(tmp_dir) / "settings.json"
            settings_path.write_text(
                json.dumps(
                    {
                        "tts_optimize_long_text": "not-a-bool",
                        "tts_optimize_threshold_chars": "not-an-int",
                    }
                ),
                encoding="utf-8",
            )
            with patch.object(config, "_SETTINGS_PATH", settings_path):
                loaded = config.load_app_settings()

            self.assertTrue(loaded["tts_optimize_long_text"])
            self.assertEqual(loaded["tts_optimize_threshold_chars"], 240)

    def test_save_and_reload_dialogue_fields(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            settings_path = Path(tmp_dir) / "settings.json"
            with patch.object(config, "_SETTINGS_PATH", settings_path):
                config.save_app_settings(
                    {
                        "chat_model": "llama-70b-chat",
                        "chat_system_prompt": "You are concise.",
                        "chat_include_history": False,
                        "voice_max_words_auto_listen": 120,
                        "voice_max_words_manual": 60,
                    }
                )
                loaded = config.load_app_settings()

            self.assertEqual(loaded["chat_model"], "llama-70b-chat")
            self.assertEqual(loaded["chat_system_prompt"], "You are concise.")
            self.assertFalse(loaded["chat_include_history"])
            self.assertEqual(loaded["voice_max_words_auto_listen"], 120)
            self.assertEqual(loaded["voice_max_words_manual"], 60)

    def test_output_history_roundtrip_is_sanitized_and_limited(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            settings_path = Path(tmp_dir) / "settings.json"
            history = [
                {"name": "One", "text": "alpha", "created_at": "2026-02-18T11:00:00"},
                {"name": "Two", "text": "beta", "created_at": "2026-02-18T11:01:00"},
                {"name": "Three", "text": "gamma", "created_at": "2026-02-18T11:02:00"},
                {"name": "Four", "text": "delta", "created_at": "2026-02-18T11:03:00"},
            ]
            with patch.object(config, "_SETTINGS_PATH", settings_path):
                config.save_app_settings({"output_history": history})
                loaded = config.load_app_settings()

            self.assertEqual(len(loaded["output_history"]), 3)
            self.assertEqual(loaded["output_history"][0]["name"], "One")
            self.assertEqual(loaded["output_history"][2]["text"], "gamma")

    def test_output_history_invalid_items_are_ignored(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            settings_path = Path(tmp_dir) / "settings.json"
            settings_path.write_text(
                json.dumps(
                    {
                        "output_history": [
                            {"name": "Valid", "text": "ok", "created_at": "2026-02-18T11:00:00"},
                            {"name": "MissingText"},
                            "not-a-dict",
                        ]
                    }
                ),
                encoding="utf-8",
            )
            with patch.object(config, "_SETTINGS_PATH", settings_path):
                loaded = config.load_app_settings()

            self.assertEqual(len(loaded["output_history"]), 1)
            self.assertEqual(loaded["output_history"][0]["text"], "ok")


if __name__ == "__main__":
    unittest.main()
