"""Unit tests for TTS text preparation helpers."""

import io
import unittest
import wave

from core.tts_service import TTSService
from core.tts_text import normalize_tts_text, split_tts_chunks


def _make_wav_bytes(sample_rate: int = 16000, duration_ms: int = 100) -> bytes:
    frame_count = int(sample_rate * duration_ms / 1000.0)
    silence = b"\x00\x00" * frame_count
    out = io.BytesIO()
    with wave.open(out, "wb") as writer:
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(sample_rate)
        writer.writeframes(silence)
    return out.getvalue()


class TTSTextTests(unittest.TestCase):
    def test_normalize_tts_text_injects_periods_for_long_unpunctuated_text(self):
        text = (
            "this is a long paragraph without punctuation and it keeps going so the voice model "
            "has no good sentence boundaries to follow and the cadence becomes unnatural quickly"
        )
        normalized = normalize_tts_text(text)
        self.assertIn(".", normalized)
        self.assertTrue(normalized.endswith("."))

    def test_split_tts_chunks_respects_max_chars(self):
        text = (
            "First sentence is short. "
            "Second sentence is also fairly short. "
            "Third sentence remains concise."
        )
        chunks = split_tts_chunks(text, max_chars=45)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk) <= 45 for chunk in chunks))

    def test_merge_wav_chunks_adds_silence_gap(self):
        first = _make_wav_bytes(duration_ms=100)
        second = _make_wav_bytes(duration_ms=100)
        merged = TTSService._merge_wav_chunks([first, second], silence_ms=100)

        with wave.open(io.BytesIO(merged), "rb") as reader:
            total_frames = reader.getnframes()
            frame_rate = reader.getframerate()
            duration_ms = int((total_frames / frame_rate) * 1000)

        # 100ms + 100ms + 100ms silence
        self.assertGreaterEqual(duration_ms, 295)
        self.assertLessEqual(duration_ms, 305)


if __name__ == "__main__":
    unittest.main()
