"""Unit tests for TTSService long-text optimization options."""

import io
import threading
import unittest
import wave

from core.app_config import AppConfig
from core.tts_service import TTSService


def _make_wav_bytes(sample_rate: int = 16000, duration_ms: int = 60) -> bytes:
    frame_count = int(sample_rate * duration_ms / 1000.0)
    silence = b"\x00\x00" * frame_count
    out = io.BytesIO()
    with wave.open(out, "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(sample_rate)
        writer.writeframes(silence)
    return out.getvalue()


class _FakeTTSClient:
    def __init__(self):
        self.calls: list[str] = []
        self.response_format = "wav"

    def synthesize(self, text: str) -> bytes:
        self.calls.append(text)
        return _make_wav_bytes()


class TTSServiceOptionsTests(unittest.TestCase):
    def _run_service(self, service: TTSService, text: str, **kwargs) -> dict:
        done = threading.Event()
        result: dict = {}

        def on_audio(_audio: bytes):
            result["ok"] = True
            done.set()

        def on_error(error: str):
            result["error"] = error
            done.set()

        service._on_audio_ready = on_audio
        service._on_error = on_error
        service.synthesize(text, **kwargs)
        self.assertTrue(done.wait(2.0), "Timed out waiting for background TTS worker.")
        return result

    def test_optimize_disabled_keeps_raw_text(self):
        config = AppConfig()
        service = TTSService(config)
        fake_client = _FakeTTSClient()
        service.client = fake_client

        raw_text = "this long text has no punctuation and should be sent exactly as entered by the user"
        result = self._run_service(
            service,
            raw_text,
            optimize_long_text=False,
            long_text_threshold_chars=1,
        )

        self.assertNotIn("error", result)
        self.assertEqual(fake_client.calls, [raw_text])

    def test_optimize_enabled_rewrites_long_text(self):
        config = AppConfig()
        service = TTSService(config)
        fake_client = _FakeTTSClient()
        service.client = fake_client

        raw_text = (
            "this is a long paragraph without punctuation and it keeps going "
            "so the model has no clear boundary to follow while reading aloud "
            "and the resulting cadence can sound rushed or monotone"
        )
        result = self._run_service(
            service,
            raw_text,
            optimize_long_text=True,
            long_text_threshold_chars=20,
        )

        self.assertNotIn("error", result)
        self.assertEqual(len(fake_client.calls), 1)
        self.assertNotEqual(fake_client.calls[0], raw_text)
        self.assertIn(".", fake_client.calls[0])

    def test_optimize_enabled_but_below_threshold_keeps_raw_text(self):
        config = AppConfig()
        service = TTSService(config)
        fake_client = _FakeTTSClient()
        service.client = fake_client

        raw_text = "short text without punctuation"
        result = self._run_service(
            service,
            raw_text,
            optimize_long_text=True,
            long_text_threshold_chars=999,
        )

        self.assertNotIn("error", result)
        self.assertEqual(fake_client.calls, [raw_text])


if __name__ == "__main__":
    unittest.main()
