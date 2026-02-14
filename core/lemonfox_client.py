import io
import logging
from typing import TYPE_CHECKING

import httpx

from core.http_client import get_shared_client

if TYPE_CHECKING:
    from core.app_config import AppConfig

logger = logging.getLogger(__name__)


class LemonFoxClient:
    """Wrapper for the LemonFox.ai speech-to-text API."""

    def __init__(self, config: "AppConfig | None" = None, api_key=None, language=None, response_format=None):
        if config:
            self.api_key = api_key or config.api_key
            self.language = language or config.stt_language
            self.response_format = response_format or config.stt_response_format
            self.api_url = config.api_url
            self.fallback_api_url = config.api_fallback_url
        else:
            from config import (
                LEMONFOX_API_KEY, LEMONFOX_LANGUAGE, LEMONFOX_RESPONSE_FORMAT,
                LEMONFOX_API_URL, LEMONFOX_API_FALLBACK_URL,
            )
            self.api_key = api_key or LEMONFOX_API_KEY
            self.language = language or LEMONFOX_LANGUAGE
            self.response_format = response_format or LEMONFOX_RESPONSE_FORMAT
            self.api_url = LEMONFOX_API_URL
            self.fallback_api_url = LEMONFOX_API_FALLBACK_URL

    def _headers(self):
        return {"Authorization": f"Bearer {self.api_key}"}

    def transcribe_file(self, file_path: str) -> str:
        """Transcribe an audio file from disk."""
        with open(file_path, "rb") as f:
            return self._send(f, file_path.rsplit("/", 1)[-1])

    def transcribe_bytes(self, audio_bytes: bytes, filename: str = "audio.wav") -> str:
        """Transcribe raw audio bytes (e.g. from mic recording)."""
        buf = io.BytesIO(audio_bytes)
        buf.name = filename
        return self._send(buf, filename)

    def _send(self, file_obj, filename: str) -> str:
        """Send audio to the LemonFox API and return transcribed text."""
        data = {
            "language": self.language,
            "response_format": self.response_format,
        }
        endpoints = [self.api_url]
        if self.fallback_api_url and self.fallback_api_url != self.api_url:
            endpoints.append(self.fallback_api_url)

        client = get_shared_client()
        last_error = None
        for endpoint in endpoints:
            try:
                logger.debug("STT request -> %s", endpoint)
                if hasattr(file_obj, "seek"):
                    file_obj.seek(0)
                files = {"file": (filename, file_obj)}
                resp = client.post(
                    endpoint,
                    headers=self._headers(),
                    data=data,
                    files=files,
                )
                resp.raise_for_status()
                if self.response_format == "json":
                    return resp.json().get("text", "")
                return resp.text
            except httpx.HTTPError as e:
                logger.warning("STT request failed on %s: %s", endpoint, e)
                last_error = e
                continue

        if last_error:
            raise last_error
        raise RuntimeError("Transcription request failed without an explicit error.")
