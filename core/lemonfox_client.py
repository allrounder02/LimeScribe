import io
import json
import logging
from typing import TYPE_CHECKING

import httpx

from core.http_client import get_shared_client

if TYPE_CHECKING:
    from core.app_config import AppConfig

logger = logging.getLogger(__name__)


class LemonFoxClient:
    """Wrapper for OpenAI-compatible speech-to-text APIs."""

    _OPENAI_LANGUAGE_MAP = {
        "english": "en",
        "german": "de",
        "spanish": "es",
        "italian": "it",
        "french": "fr",
        "portuguese": "pt",
        "japanese": "ja",
        "chinese": "zh",
        "hindi": "hi",
    }

    def __init__(
        self,
        config: "AppConfig | None" = None,
        api_key=None,
        model=None,
        language=None,
        response_format=None,
    ):
        if config:
            self.api_key = api_key or config.api_key
            self.model = model or config.stt_model
            self.language = language or config.stt_language
            self.response_format = response_format or config.stt_response_format
            self.api_url = config.api_url
            self.fallback_api_url = config.api_fallback_url
        else:
            from config import (
                OPENAI_API_KEY,
                OPENAI_STT_FALLBACK_URL,
                OPENAI_STT_LANGUAGE,
                OPENAI_STT_MODEL,
                OPENAI_STT_RESPONSE_FORMAT,
                OPENAI_STT_URL,
            )
            self.api_key = api_key or OPENAI_API_KEY
            self.model = model or OPENAI_STT_MODEL
            self.language = language or OPENAI_STT_LANGUAGE
            self.response_format = response_format or OPENAI_STT_RESPONSE_FORMAT
            self.api_url = OPENAI_STT_URL
            self.fallback_api_url = OPENAI_STT_FALLBACK_URL

    def _headers(self):
        return {"Authorization": f"Bearer {self.api_key}"}

    @staticmethod
    def _resolve_model(model: str, response_format: str) -> str:
        candidate = str(model or "").strip() or "whisper-1"
        normalized_format = str(response_format or "").strip().lower()
        if normalized_format in {"srt", "vtt", "verbose_json"} and candidate.startswith("gpt-4o"):
            return "whisper-1"
        return candidate

    @classmethod
    def _normalize_language(cls, endpoint: str, language: str) -> str:
        candidate = str(language or "").strip()
        if not candidate:
            return ""
        if "api.openai.com" not in str(endpoint or ""):
            return candidate
        return cls._OPENAI_LANGUAGE_MAP.get(candidate.lower(), candidate)

    @staticmethod
    def _looks_like_json(text: str) -> bool:
        value = (text or "").lstrip()
        return bool(value) and value[0] in "{["

    @staticmethod
    def _extract_text_from_payload(payload) -> str:
        if isinstance(payload, dict):
            text_value = payload.get("text")
            if isinstance(text_value, str) and text_value.strip():
                return text_value.strip()
            segments = payload.get("segments")
            if isinstance(segments, list):
                pieces = []
                for item in segments:
                    if not isinstance(item, dict):
                        continue
                    seg_text = str(item.get("text", "")).strip()
                    if seg_text:
                        pieces.append(seg_text)
                if pieces:
                    return " ".join(pieces)
            return ""
        if isinstance(payload, list):
            pieces = []
            for item in payload:
                if not isinstance(item, dict):
                    continue
                seg_text = str(item.get("text", "")).strip()
                if seg_text:
                    pieces.append(seg_text)
            if pieces:
                return " ".join(pieces)
            return ""
        return ""

    def _extract_text_from_json_response(self, resp: httpx.Response) -> str:
        try:
            payload = resp.json()
        except ValueError as e:
            raise RuntimeError(f"STT response was expected to be JSON but could not be parsed: {e}") from e
        text = self._extract_text_from_payload(payload)
        if text:
            return text
        raise RuntimeError("STT response JSON did not contain a usable 'text' field.")

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
        """Send audio to the transcription API and return transcribed text."""
        requested_format = str(self.response_format or "").strip()
        resolved_model = self._resolve_model(self.model, requested_format)
        resolved_language = self._normalize_language(self.api_url, self.language)
        data = {
            "response_format": requested_format or self.response_format,
            "model": resolved_model,
        }
        endpoints = [self.api_url]
        if self.fallback_api_url and self.fallback_api_url != self.api_url:
            endpoints.append(self.fallback_api_url)

        client = get_shared_client()
        last_error = None
        for endpoint in endpoints:
            try:
                logger.debug(
                    "STT request -> %s | model=%s language=%s response_format=%s",
                    endpoint,
                    data.get("model", ""),
                    self._normalize_language(endpoint, resolved_language),
                    data.get("response_format", ""),
                )
                if hasattr(file_obj, "seek"):
                    file_obj.seek(0)
                files = {"file": (filename, file_obj)}
                request_data = dict(data)
                normalized_language = self._normalize_language(endpoint, resolved_language)
                if normalized_language:
                    request_data["language"] = normalized_language
                resp = client.post(
                    endpoint,
                    headers=self._headers(),
                    data=request_data,
                    files=files,
                )
                resp.raise_for_status()
                normalized_format = requested_format.lower()
                if normalized_format in {"json", "verbose_json"}:
                    return self._extract_text_from_json_response(resp)
                body_text = resp.text
                if self._looks_like_json(body_text):
                    try:
                        payload = json.loads(body_text)
                    except ValueError:
                        return body_text
                    extracted = self._extract_text_from_payload(payload)
                    if extracted:
                        logger.warning(
                            "STT returned JSON while response_format=%s; using extracted text field.",
                            requested_format,
                        )
                        return extracted
                return body_text
            except httpx.HTTPError as e:
                logger.warning("STT request failed on %s: %s", endpoint, e)
                last_error = e
                continue

        if last_error:
            raise last_error
        raise RuntimeError("Transcription request failed without an explicit error.")
