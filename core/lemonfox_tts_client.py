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
    """Wrapper for OpenAI-compatible text-to-speech APIs."""

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
        instructions=None,
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
            self.instructions = instructions if instructions is not None else config.tts_instructions
        else:
            from config import (
                OPENAI_API_KEY,
                OPENAI_TTS_FALLBACK_URL,
                OPENAI_TTS_INSTRUCTIONS,
                OPENAI_TTS_LANGUAGE,
                OPENAI_TTS_MODEL,
                OPENAI_TTS_RESPONSE_FORMAT,
                OPENAI_TTS_SPEED,
                OPENAI_TTS_URL,
                OPENAI_TTS_VOICE,
            )
            self.api_key = api_key or OPENAI_API_KEY
            self.tts_url = tts_url or OPENAI_TTS_URL
            self.fallback_url = fallback_url if fallback_url is not None else OPENAI_TTS_FALLBACK_URL
            self.model = model or OPENAI_TTS_MODEL
            self.voice = voice or OPENAI_TTS_VOICE
            self.language = language or OPENAI_TTS_LANGUAGE
            self.response_format = response_format or OPENAI_TTS_RESPONSE_FORMAT
            self.speed = OPENAI_TTS_SPEED if speed is None else speed
            self.instructions = instructions if instructions is not None else OPENAI_TTS_INSTRUCTIONS

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

    @staticmethod
    def _supports_openai_native_payload(endpoint: str) -> bool:
        return "api.openai.com" in str(endpoint or "")

    def synthesize(
        self,
        text: str,
        model=None,
        voice=None,
        language=None,
        response_format=None,
        speed=None,
        instructions=None,
    ) -> bytes:
        if not text or not text.strip():
            raise ValueError("Text-to-speech input cannot be empty.")

        payload = {
            "model": model or self.model,
            "voice": voice or self.voice,
            "input": text,
            "response_format": response_format or self.response_format,
            "speed": self.speed if speed is None else speed,
        }
        resolved_instructions = instructions if instructions is not None else self.instructions
        if resolved_instructions:
            payload["instructions"] = resolved_instructions

        endpoints = [self.tts_url]
        if self.fallback_url and self.fallback_url != self.tts_url:
            endpoints.append(self.fallback_url)

        client = get_shared_client()
        last_error = None
        for endpoint in endpoints:
            try:
                logger.debug(
                    "TTS request -> %s | model=%s voice=%s response_format=%s speed=%s",
                    endpoint,
                    payload["model"],
                    payload["voice"],
                    payload["response_format"],
                    payload["speed"],
                )
                request_payload = dict(payload)
                # OpenAI's speech API examples do not send `language` for built-in voices.
                # Keep the field only for non-OpenAI backends where callers may rely on it.
                if not self._supports_openai_native_payload(endpoint) and (language or self.language):
                    request_payload["language"] = language or self.language
                resp = client.post(
                    endpoint,
                    headers=self._headers(),
                    json=request_payload,
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
