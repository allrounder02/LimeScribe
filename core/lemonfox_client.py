import io
import requests
from config import API_URL, LEMONFOX_API_KEY, LEMONFOX_LANGUAGE, LEMONFOX_RESPONSE_FORMAT


class LemonFoxClient:
    """Wrapper for the LemonFox.ai speech-to-text API."""

    def __init__(self, api_key=None, language=None, response_format=None):
        self.api_key = api_key or LEMONFOX_API_KEY
        self.language = language or LEMONFOX_LANGUAGE
        self.response_format = response_format or LEMONFOX_RESPONSE_FORMAT

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
        files = {"file": (filename, file_obj)}
        resp = requests.post(
            API_URL,
            headers=self._headers(),
            data=data,
            files=files,
            timeout=120,
        )
        resp.raise_for_status()

        if self.response_format == "json":
            return resp.json().get("text", "")
        return resp.text
