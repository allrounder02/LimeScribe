import json
import logging
from typing import TYPE_CHECKING

import httpx

from core.audio_format import detect_audio_format
from core.http_client import get_shared_client

if TYPE_CHECKING:
    from core.app_config import AppConfig

logger = logging.getLogger(__name__)


class LemonFoxTTSClient:
    """Wrapper for LemonFox/OpenAI-compatible text-to-speech APIs."""

    def __init__(
        self,
        config: "AppConfig | None" = None,
        api_key=None,
        tts_url=None,
        fallback_url=None,
        model=None,
        voice=None,
        language=None,
        response_format=None,
        speed=None,
    ):
        if config:
            self.api_key = api_key or config.api_key
            self.tts_url = tts_url or config.tts_url
            self.fallback_url = fallback_url if fallback_url is not None else config.tts_fallback_url
            self.model = model or config.tts_model
            self.voice = voice or config.tts_voice
            self.language = language or config.tts_language
            self.response_format = response_format or config.tts_response_format
            self.speed = config.tts_speed if speed is None else speed
        else:
            from config import (
                LEMONFOX_API_KEY, LEMONFOX_TTS_URL, LEMONFOX_TTS_FALLBACK_URL,
                LEMONFOX_TTS_MODEL, LEMONFOX_TTS_VOICE, LEMONFOX_TTS_LANGUAGE,
                LEMONFOX_TTS_RESPONSE_FORMAT, LEMONFOX_TTS_SPEED,
            )
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

    @staticmethod
    def _extract_message(value) -> str:
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, dict):
            if "error" in value:
                inner = LemonFoxTTSClient._extract_message(value.get("error"))
                if inner:
                    return inner
            for key in ("message", "detail", "description"):
                candidate = LemonFoxTTSClient._extract_message(value.get(key))
                if candidate:
                    return candidate
            return ""
        if isinstance(value, list):
            for item in value:
                candidate = LemonFoxTTSClient._extract_message(item)
                if candidate:
                    return candidate
            return ""
        return str(value or "").strip()

    @staticmethod
    def _decode_text_payload(content: bytes) -> str:
        if not content:
            return ""
        snippet = content[:8192]
        try:
            text = snippet.decode("utf-8")
        except UnicodeDecodeError:
            return ""
        stripped = text.strip()
        if not stripped:
            return ""
        printable = sum(1 for ch in stripped if ch.isprintable() or ch in "\r\n\t")
        ratio = printable / max(1, len(stripped))
        if ratio < 0.9:
            return ""
        return stripped

    @staticmethod
    def _payload_message_from_text(text: str) -> str:
        body = (text or "").strip()
        if not body:
            return ""
        if body.startswith("{") or body.startswith("["):
            try:
                parsed = json.loads(body)
                extracted = LemonFoxTTSClient._extract_message(parsed)
                if extracted:
                    return extracted
            except (json.JSONDecodeError, TypeError, ValueError):
                pass
        return body

    @staticmethod
    def _http_error_message(resp: httpx.Response) -> str:
        status_label = f"TTS request failed with HTTP {resp.status_code}"
        text = LemonFoxTTSClient._decode_text_payload(resp.content)
        detail = LemonFoxTTSClient._payload_message_from_text(text)
        if detail:
            return f"{status_label}: {detail}"
        return status_label

    @staticmethod
    def _unexpected_non_audio_message(resp: httpx.Response) -> str:
        text = LemonFoxTTSClient._decode_text_payload(resp.content)
        detail = LemonFoxTTSClient._payload_message_from_text(text)
        if not detail:
            return ""
        content_type = str(resp.headers.get("content-type", "")).strip() or "unknown content-type"
        return f"TTS API returned {content_type} instead of audio: {detail}"

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

        client = get_shared_client()
        last_error = None
        for endpoint in endpoints:
            try:
                logger.debug(
                    "TTS request -> %s | model=%s voice=%s language=%s response_format=%s speed=%s",
                    endpoint,
                    payload["model"],
                    payload["voice"],
                    payload["language"],
                    payload["response_format"],
                    payload["speed"],
                )
                resp = client.post(
                    endpoint,
                    headers=self._headers(),
                    json=payload,
                )
                if resp.status_code >= 400:
                    raise RuntimeError(self._http_error_message(resp))

                audio_bytes = resp.content
                if detect_audio_format(audio_bytes) != "unknown":
                    return audio_bytes

                unexpected_message = self._unexpected_non_audio_message(resp)
                if unexpected_message:
                    raise RuntimeError(unexpected_message)
                return audio_bytes
            except (httpx.HTTPError, RuntimeError) as e:
                logger.warning("TTS request failed on %s: %s", endpoint, e)
                last_error = e
                continue

        if last_error:
            raise last_error
        raise RuntimeError("Text-to-speech request failed without an explicit error.")
