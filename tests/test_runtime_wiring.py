"""Smoke tests for entrypoint wiring without GUI/audio/network side effects."""

import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import mock_open, patch

from core import cli_runtime


class RuntimeWiringSmokeTests(unittest.TestCase):
    def test_app_main_delegates_to_gui_runtime(self):
        try:
            import app
        except ModuleNotFoundError as e:
            if e.name == "PyQt6":
                self.skipTest("PyQt6 not installed in this environment")
            raise

        with patch("app.run_gui_app", return_value=7) as run_gui_app:
            code = app.main()
        self.assertEqual(code, 7)
        run_gui_app.assert_called_once_with()

    def test_cli_transcribe_command_wiring_and_cleanup(self):
        class FakeTranscriptionService:
            def __init__(self, _config, on_transcription=None, on_error=None):
                self._on_transcription = on_transcription
                self._on_error = on_error

            def transcribe_file(self, _file_path: str):
                if self._on_transcription:
                    self._on_transcription("transcribed text")

        out = io.StringIO()
        err = io.StringIO()
        with (
            patch.object(cli_runtime.AppConfig, "from_env", return_value=object()),
            patch.object(cli_runtime, "TranscriptionService", FakeTranscriptionService),
            patch.object(cli_runtime, "close_shared_client") as close_shared_client,
            redirect_stdout(out),
            redirect_stderr(err),
        ):
            code = cli_runtime.run_cli(["transcribe", "fake.wav"])

        self.assertEqual(code, 0)
        self.assertEqual(err.getvalue(), "")
        self.assertIn("transcribed text", out.getvalue())
        close_shared_client.assert_called_once_with()

    def test_cli_tts_command_wiring_and_cleanup(self):
        class FakeTTSService:
            def __init__(self, _config, on_audio_ready=None, on_error=None):
                self._on_audio_ready = on_audio_ready
                self._on_error = on_error

            def synthesize(self, _text: str):
                if self._on_audio_ready:
                    self._on_audio_ready(b"RIFF....WAVE")

        out = io.StringIO()
        err = io.StringIO()
        with (
            patch.object(cli_runtime.AppConfig, "from_env", return_value=object()),
            patch.object(cli_runtime, "TTSService", FakeTTSService),
            patch.object(cli_runtime, "close_shared_client") as close_shared_client,
            patch("builtins.open", mock_open()) as mocked_open,
            redirect_stdout(out),
            redirect_stderr(err),
        ):
            code = cli_runtime.run_cli(["tts", "hello", "-o", "fake.wav"])

        self.assertEqual(code, 0)
        self.assertEqual(out.getvalue(), "")
        self.assertIn("Audio saved to fake.wav", err.getvalue())
        mocked_open.assert_called_once_with("fake.wav", "wb")
        close_shared_client.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
