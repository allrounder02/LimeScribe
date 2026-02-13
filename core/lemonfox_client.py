import io
import logging
import requests
from config import (
    LEMONFOX_API_KEY,
    LEMONFOX_LANGUAGE,
    LEMONFOX_RESPONSE_FORMAT,
    LEMONFOX_API_URL,
    LEMONFOX_API_FALLBACK_URL,
)

logger = logging.getLogger(__name__)


class LemonFoxClient:
    """Wrapper for the LemonFox.ai speech-to-text API."""

    def __init__(self, api_key=None, language=None, response_format=None):
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

        last_error = None
        for endpoint in endpoints:
            try:
                logger.debug("STT request -> %s", endpoint)
                if hasattr(file_obj, "seek"):
                    file_obj.seek(0)
                files = {"file": (filename, file_obj)}
                resp = requests.post(
                    endpoint,
                    headers=self._headers(),
                    data=data,
                    files=files,
                    timeout=120,
                )
                resp.raise_for_status()
                if self.response_format == "json":
                    return resp.json().get("text", "")
                return resp.text
            except requests.RequestException as e:
                logger.warning("STT request failed on %s: %s", endpoint, e)
                last_error = e
                continue

        if last_error:
            raise last_error
        raise RuntimeError("Transcription request failed without an explicit error.")
