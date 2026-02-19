"""Unit tests for audio format sniffing helpers."""

import unittest

from core.audio_format import detect_audio_format


class DetectAudioFormatTests(unittest.TestCase):
    def test_detect_wav(self):
        payload = b"RIFF\x00\x00\x00\x00WAVEfmt "
        self.assertEqual(detect_audio_format(payload), "wav")

    def test_detect_flac(self):
        self.assertEqual(detect_audio_format(b"fLaC\x00\x00\x00"), "flac")

    def test_detect_ogg(self):
        self.assertEqual(detect_audio_format(b"OggS\x00\x02"), "ogg")

    def test_detect_mp3_id3(self):
        self.assertEqual(detect_audio_format(b"ID3\x04\x00\x00"), "mp3")

    def test_detect_mp3_frame_sync(self):
        self.assertEqual(detect_audio_format(bytes([0xFF, 0xFB, 0x90, 0x64])), "mp3")

    def test_unknown_or_empty(self):
        self.assertEqual(detect_audio_format(b""), "unknown")
        self.assertEqual(detect_audio_format(b"\x00\x11\x22\x33"), "unknown")


if __name__ == "__main__":
    unittest.main()
