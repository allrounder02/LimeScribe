"""Wrapper for LemonFox OpenAI-compatible chat-completions API."""

from __future__ import annotations

import json
import logging
from collections.abc import Iterator
from typing import TYPE_CHECKING

import httpx

from core.http_client import get_shared_client

if TYPE_CHECKING:
    from core.app_config import AppConfig

logger = logging.getLogger(__name__)


class LemonFoxChatClient:
    """Simple chat-completions client for the Dialogue feature."""

    def __init__(
        self,
        config: "AppConfig | None" = None,
        api_key=None,
        chat_url=None,
        fallback_url=None,
        model=None,
    ):
        if config:
            self.api_key = api_key or config.api_key
            self.chat_url = chat_url or config.chat_url
            self.fallback_url = fallback_url if fallback_url is not None else config.chat_fallback_url
            self.model = model or config.chat_model
        else:
            from config import (
                LEMONFOX_API_KEY,
                LEMONFOX_CHAT_FALLBACK_URL,
                LEMONFOX_CHAT_MODEL,
                LEMONFOX_CHAT_URL,
            )

            self.api_key = api_key or LEMONFOX_API_KEY
            self.chat_url = chat_url or LEMONFOX_CHAT_URL
            self.fallback_url = fallback_url if fallback_url is not None else LEMONFOX_CHAT_FALLBACK_URL
            self.model = model or LEMONFOX_CHAT_MODEL

    def _headers(self):
        return {"Authorization": f"Bearer {self.api_key}"}

    def complete_stream(self, messages: list[dict], model: str | None = None) -> Iterator[str]:
        """Stream chat completions via SSE, yielding content deltas."""
        if not isinstance(messages, list) or not messages:
            raise ValueError("Chat messages must be a non-empty list.")

        payload = {
            "model": (model or self.model or "").strip(),
            "messages": messages,
            "stream": True,
        }
        if not payload["model"]:
            raise ValueError("Chat model cannot be empty.")

        endpoints = [self.chat_url]
        if self.fallback_url and self.fallback_url != self.chat_url:
            endpoints.append(self.fallback_url)

        last_error = None
        for endpoint in endpoints:
            try:
                logger.debug(
                    "Chat stream request -> %s | model=%s messages=%d",
                    endpoint,
                    payload["model"],
                    len(payload["messages"]),
                )
                yield from self._stream_sse(endpoint, payload)
                return
            except httpx.HTTPError as e:
                logger.warning("Chat stream failed on %s: %s", endpoint, e)
                last_error = e
                continue

        if last_error:
            raise last_error
        raise RuntimeError("Chat stream request failed without an explicit error.")

    def _stream_sse(self, endpoint: str, payload: dict) -> Iterator[str]:
        """Open an SSE stream and yield content deltas until [DONE]."""
        client = get_shared_client()
        with client.stream("POST", endpoint, headers=self._headers(), json=payload) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line.startswith("data:"):
                    continue
                data = line[len("data:"):].strip()
                if data == "[DONE]":
                    return
                try:
                    chunk = json.loads(data)
                except (json.JSONDecodeError, ValueError):
                    continue
                choices = chunk.get("choices")
                if not isinstance(choices, list) or not choices:
                    continue
                delta = choices[0].get("delta", {})
                content = delta.get("content")
                if content:
                    yield content

    def complete(self, messages: list[dict], model: str | None = None) -> str:
        if not isinstance(messages, list) or not messages:
            raise ValueError("Chat messages must be a non-empty list.")

        payload = {
            "model": (model or self.model or "").strip(),
            "messages": messages,
        }
        if not payload["model"]:
            raise ValueError("Chat model cannot be empty.")

        endpoints = [self.chat_url]
        if self.fallback_url and self.fallback_url != self.chat_url:
            endpoints.append(self.fallback_url)

        client = get_shared_client()
        last_error = None
        for endpoint in endpoints:
            try:
                logger.debug(
                    "Chat request -> %s | model=%s messages=%d",
                    endpoint,
                    payload["model"],
                    len(payload["messages"]),
                )
                resp = client.post(endpoint, headers=self._headers(), json=payload)
                resp.raise_for_status()
                return self._extract_assistant_content(resp.json())
            except httpx.HTTPError as e:
                logger.warning("Chat request failed on %s: %s", endpoint, e)
                last_error = e
                continue
            except ValueError as e:
                raise RuntimeError(f"Chat response was not valid JSON: {e}") from e

        if last_error:
            raise last_error
        raise RuntimeError("Chat request failed without an explicit error.")

    @staticmethod
    def _extract_assistant_content(payload) -> str:
        if not isinstance(payload, dict):
            raise RuntimeError("Chat response payload is not a JSON object.")
        choices = payload.get("choices")
        if not isinstance(choices, list) or not choices:
            raise RuntimeError("Chat response is missing a valid 'choices' list.")

        first = choices[0]
        if not isinstance(first, dict):
            raise RuntimeError("Chat response choice is malformed.")
        message = first.get("message")
        if not isinstance(message, dict):
            raise RuntimeError("Chat response choice is missing 'message'.")
        content = LemonFoxChatClient._coerce_content(message.get("content"))
        if content:
            return content
        raise RuntimeError("Chat response did not include assistant content.")

    @staticmethod
    def _coerce_content(content) -> str:
        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            parts = []
            for item in content:
                if isinstance(item, dict):
                    text = str(item.get("text", "")).strip()
                    if text:
                        parts.append(text)
            return "\n".join(parts).strip()
        return str(content or "").strip()
