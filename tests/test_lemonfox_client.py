"""Unit tests for STT request shaping during the OpenAI migration."""

from unittest.mock import MagicMock, patch

from core.lemonfox_client import LemonFoxClient


class TestLemonFoxClientRequestShaping:
    def test_sends_explicit_model_for_standard_json_transcription(self):
        client = LemonFoxClient(
            api_key="test-key",
            model="gpt-4o-mini-transcribe",
            language="english",
            response_format="json",
        )
        client.api_url = "https://api.openai.com/v1/audio/transcriptions"
        response = MagicMock()
        response.raise_for_status = MagicMock()
        response.json.return_value = {"text": "hello world"}
        response.text = '{"text":"hello world"}'

        with patch("core.lemonfox_client.get_shared_client") as mock_get:
            mock_http = MagicMock()
            mock_http.post.return_value = response
            mock_get.return_value = mock_http

            text = client.transcribe_bytes(b"fake-audio")

        assert text == "hello world"
        kwargs = mock_http.post.call_args.kwargs
        assert kwargs["data"]["model"] == "gpt-4o-mini-transcribe"
        assert kwargs["data"]["language"] == "en"
        assert kwargs["data"]["response_format"] == "json"

    def test_subtitle_formats_fall_back_to_whisper_for_compatibility(self):
        client = LemonFoxClient(
            api_key="test-key",
            model="gpt-4o-mini-transcribe",
            language="english",
            response_format="srt",
        )
        client.api_url = "https://api.openai.com/v1/audio/transcriptions"
        response = MagicMock()
        response.raise_for_status = MagicMock()
        response.text = "1\n00:00:00,000 --> 00:00:01,000\nHello\n"

        with patch("core.lemonfox_client.get_shared_client") as mock_get:
            mock_http = MagicMock()
            mock_http.post.return_value = response
            mock_get.return_value = mock_http

            text = client.transcribe_bytes(b"fake-audio")

        assert "Hello" in text
        kwargs = mock_http.post.call_args.kwargs
        assert kwargs["data"]["model"] == "whisper-1"
        assert kwargs["data"]["language"] == "en"
        assert kwargs["data"]["response_format"] == "srt"

    def test_non_openai_backends_keep_human_language_name(self):
        client = LemonFoxClient(
            api_key="test-key",
            model="gpt-4o-mini-transcribe",
            language="english",
            response_format="json",
        )
        client.api_url = "https://example.com/v1/audio/transcriptions"
        response = MagicMock()
        response.raise_for_status = MagicMock()
        response.json.return_value = {"text": "hello world"}
        response.text = '{"text":"hello world"}'

        with patch("core.lemonfox_client.get_shared_client") as mock_get:
            mock_http = MagicMock()
            mock_http.post.return_value = response
            mock_get.return_value = mock_http

            client.transcribe_bytes(b"fake-audio")

        kwargs = mock_http.post.call_args.kwargs
        assert kwargs["data"]["language"] == "english"

    def test_auto_language_omits_language_field_for_openai(self):
        client = LemonFoxClient(
            api_key="test-key",
            model="gpt-4o-mini-transcribe",
            language="auto",
            response_format="json",
        )
        client.api_url = "https://api.openai.com/v1/audio/transcriptions"
        response = MagicMock()
        response.raise_for_status = MagicMock()
        response.json.return_value = {"text": "guten morgen"}
        response.text = '{"text":"guten morgen"}'

        with patch("core.lemonfox_client.get_shared_client") as mock_get:
            mock_http = MagicMock()
            mock_http.post.return_value = response
            mock_get.return_value = mock_http

            text = client.transcribe_bytes(b"fake-audio")

        assert text == "guten morgen"
        kwargs = mock_http.post.call_args.kwargs
        assert "language" not in kwargs["data"]
