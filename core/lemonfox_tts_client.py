import requests
import logging

from config import (
    LEMONFOX_API_KEY,
    LEMONFOX_TTS_URL,
    LEMONFOX_TTS_FALLBACK_URL,
    LEMONFOX_TTS_MODEL,
    LEMONFOX_TTS_VOICE,
    LEMONFOX_TTS_LANGUAGE,
    LEMONFOX_TTS_RESPONSE_FORMAT,
    LEMONFOX_TTS_SPEED,
)

logger = logging.getLogger(__name__)


class LemonFoxTTSClient:
    """Wrapper for LemonFox/OpenAI-compatible text-to-speech APIs."""

    def __init__(
        self,
        api_key=None,
        tts_url=None,
        fallback_url=None,
        model=None,
        voice=None,
        language=None,
        response_format=None,
        speed=None,
    ):
        self.api_key = api_key or LEMONFOX_API_KEY
        self.tts_url = tts_url or LEMONFOX_TTS_URL
        self.fallback_url = fallback_url if fallback_url is not None else LEMONFOX_TTS_FALLBACK_URL
        self.model = model or LEMONFOX_TTS_MODEL
        self.voice = voice or LEMONFOX_TTS_VOICE
        self.language = language or LEMONFOX_TTS_LANGUAGE
        self.response_format = response_format or LEMONFOX_TTS_RESPONSE_FORMAT
        self.speed = LEMONFOX_TTS_SPEED if speed is None else speed

    def _headers(self):
        return {"Authorization": f"Bearer {self.api_key}"}

    def synthesize(self, text: str, model=None, voice=None, language=None, response_format=None, speed=None) -> bytes:
        if not text or not text.strip():
            raise ValueError("Text-to-speech input cannot be empty.")

        payload = {
            "model": model or self.model,
            "voice": voice or self.voice,
            "input": text,
            "language": language or self.language,
            "response_format": response_format or self.response_format,
            "speed": self.speed if speed is None else speed,
        }

        endpoints = [self.tts_url]
        if self.fallback_url and self.fallback_url != self.tts_url:
            endpoints.append(self.fallback_url)

        last_error = None
        for endpoint in endpoints:
            try:
                logger.debug("TTS request -> %s", endpoint)
                resp = requests.post(
                    endpoint,
                    headers=self._headers(),
                    json=payload,
                    timeout=120,
                )
                resp.raise_for_status()
                return resp.content
            except requests.RequestException as e:
                logger.warning("TTS request failed on %s: %s", endpoint, e)
                last_error = e
                continue

        if last_error:
            raise last_error
        raise RuntimeError("Text-to-speech request failed without an explicit error.")
