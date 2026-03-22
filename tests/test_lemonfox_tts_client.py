"""Unit tests for LemonFoxTTSClient error extraction and payload handling."""

import unittest
from unittest.mock import MagicMock, patch

import httpx

from core.lemonfox_tts_client import LemonFoxTTSClient


class LemonFoxTTSClientErrorTests(unittest.TestCase):
    def test_http_error_message_extracts_nested_json_error(self):
        response = httpx.Response(
            400,
            headers={"content-type": "application/json"},
            content=b'{"error":{"message":"Input text is too long."}}',
        )
        message = LemonFoxTTSClient._http_error_message(response)
        self.assertIn("HTTP 400", message)
        self.assertIn("Input text is too long.", message)

    def test_http_error_message_falls_back_when_body_is_not_text(self):
        response = httpx.Response(502, content=b"\x00\x01\x02\x03")
        message = LemonFoxTTSClient._http_error_message(response)
        self.assertEqual(message, "TTS request failed with HTTP 502")

    def test_unexpected_non_audio_message_handles_json_payload(self):
        response = httpx.Response(
            200,
            headers={"content-type": "application/json"},
            content=b'{"error":"quota exceeded"}',
        )
        message = LemonFoxTTSClient._unexpected_non_audio_message(response)
        self.assertIn("application/json", message)
        self.assertIn("quota exceeded", message)

    def test_unexpected_non_audio_message_handles_bracket_text(self):
        response = httpx.Response(
            200,
            headers={"content-type": "text/plain"},
            content=b"[TTS] generation failed due to invalid voice id",
        )
        message = LemonFoxTTSClient._unexpected_non_audio_message(response)
        self.assertIn("text/plain", message)
        self.assertIn("invalid voice id", message)

    def test_unexpected_non_audio_message_is_empty_for_binary(self):
        response = httpx.Response(
            200,
            headers={"content-type": "application/octet-stream"},
            content=b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR",
        )
        self.assertEqual(LemonFoxTTSClient._unexpected_non_audio_message(response), "")

    def test_openai_payload_omits_language_and_includes_instructions(self):
        client = LemonFoxTTSClient(
            api_key="test-key",
            tts_url="https://api.openai.com/v1/audio/speech",
            model="gpt-4o-mini-tts",
            voice="coral",
            language="en-us",
            response_format="wav",
            instructions="Speak warmly.",
        )
        response = httpx.Response(
            200,
            headers={"content-type": "audio/wav"},
            content=b"RIFF....WAVE",
        )

        with patch("core.lemonfox_tts_client.get_shared_client") as mock_get:
            mock_http = MagicMock()
            mock_http.post.return_value = response
            mock_get.return_value = mock_http

            audio = client.synthesize("Hello world")

        self.assertEqual(audio, b"RIFF....WAVE")
        kwargs = mock_http.post.call_args.kwargs
        self.assertNotIn("language", kwargs["json"])
        self.assertEqual(kwargs["json"]["instructions"], "Speak warmly.")


if __name__ == "__main__":
    unittest.main()
