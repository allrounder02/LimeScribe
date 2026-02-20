"""Dialogue service that orchestrates chat-completions calls in background threads."""

from __future__ import annotations

import logging
import re
import threading
from typing import Callable, Optional

from core.app_config import AppConfig
from core.lemonfox_chat_client import LemonFoxChatClient

logger = logging.getLogger(__name__)
_WORD_RE = re.compile(r"\S+")


class DialogueService:
    """Manages chat settings + history for the Dialogue tab."""

    def __init__(
        self,
        config: AppConfig,
        on_reply: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ):
        self.config = config
        self.client = LemonFoxChatClient(config=config)
        self._on_reply = on_reply
        self._on_error = on_error
        self._lock = threading.RLock()
        self._include_history = True
        self._system_prompt = str(config.chat_system_prompt or "").strip()
        self._history: list[dict] = []
        self._reset_history_locked()

    @property
    def include_history(self) -> bool:
        with self._lock:
            return bool(self._include_history)

    @property
    def system_prompt(self) -> str:
        with self._lock:
            return str(self._system_prompt)

    def update_settings(
        self,
        model: str | None = None,
        system_prompt: str | None = None,
        include_history: bool | None = None,
        reset_history: bool = False,
    ):
        with self._lock:
            if model is not None:
                candidate = str(model).strip()
                if candidate:
                    self.client.model = candidate
            prompt_changed = False
            if system_prompt is not None:
                candidate = str(system_prompt).strip()
                if candidate != self._system_prompt:
                    self._system_prompt = candidate
                    prompt_changed = True
            if include_history is not None:
                self._include_history = bool(include_history)
            if reset_history or prompt_changed:
                self._reset_history_locked()

    def clear_history(self):
        with self._lock:
            self._reset_history_locked()

    def send_stream(
        self,
        text: str,
        on_delta: Callable[[str], None] | None = None,
        cancel_event: threading.Event | None = None,
        max_words: int | None = None,
    ):
        """Send a message and stream the response, calling on_delta for each chunk.

        Runs synchronously (caller should use a background thread).
        Appends the full response to history when done, then fires on_reply.
        """
        message = (text or "").strip()
        if not message:
            if self._on_error:
                self._on_error("Dialogue message cannot be empty.")
            return

        appended_user = False
        try:
            with self._lock:
                if self._include_history:
                    self._history.append({"role": "user", "content": message})
                    appended_user = True
                    request_messages = [dict(msg) for msg in self._history]
                else:
                    request_messages: list[dict] = []
                    if self._system_prompt:
                        request_messages.append({"role": "system", "content": self._system_prompt})
                    request_messages.append({"role": "user", "content": message})

            accumulated = ""
            limit = int(max_words) if max_words is not None else 0
            if limit < 0:
                limit = 0

            stream_cancelled = False
            for delta in self.client.complete_stream(request_messages, cancel_event=cancel_event):
                if cancel_event is not None and cancel_event.is_set():
                    stream_cancelled = True
                    break

                candidate = accumulated + str(delta or "")
                if limit > 0:
                    trimmed = self._truncate_to_words(candidate, limit)
                    emitted = trimmed[len(accumulated):]
                    accumulated = trimmed
                    if emitted and on_delta:
                        on_delta(emitted)
                    if len(trimmed) < len(candidate):
                        # Word limit reached; stop generation for a shorter assistant turn.
                        break
                else:
                    accumulated = candidate
                    if on_delta:
                        on_delta(delta)

            if cancel_event is not None and cancel_event.is_set():
                stream_cancelled = True

            full_text = accumulated.strip()
            with self._lock:
                if self._include_history and full_text and not stream_cancelled:
                    self._history.append({"role": "assistant", "content": full_text})

            if self._on_reply and not stream_cancelled:
                self._on_reply(full_text)
        except Exception as e:
            logger.error("Dialogue stream failed: %s", e)
            with self._lock:
                if appended_user and self._history:
                    last = self._history[-1]
                    if last.get("role") == "user" and last.get("content") == message:
                        self._history.pop()
            if self._on_error:
                self._on_error(str(e))

    def send(self, text: str):
        message = (text or "").strip()
        if not message:
            if self._on_error:
                self._on_error("Dialogue message cannot be empty.")
            return
        threading.Thread(target=self._send_worker, args=(message,), daemon=True).start()

    def _send_worker(self, user_text: str):
        appended_user = False
        try:
            with self._lock:
                if self._include_history:
                    self._history.append({"role": "user", "content": user_text})
                    appended_user = True
                    request_messages = [dict(msg) for msg in self._history]
                else:
                    request_messages: list[dict] = []
                    if self._system_prompt:
                        request_messages.append({"role": "system", "content": self._system_prompt})
                    request_messages.append({"role": "user", "content": user_text})

            assistant_text = self.client.complete(request_messages)

            with self._lock:
                if self._include_history:
                    self._history.append({"role": "assistant", "content": assistant_text})

            if self._on_reply:
                self._on_reply(assistant_text)
        except Exception as e:
            logger.error("Dialogue request failed: %s", e)
            with self._lock:
                if appended_user and self._history:
                    last = self._history[-1]
                    if last.get("role") == "user" and last.get("content") == user_text:
                        self._history.pop()
            if self._on_error:
                self._on_error(str(e))

    def _reset_history_locked(self):
        self._history = []
        if self._system_prompt:
            self._history.append({"role": "system", "content": self._system_prompt})

    @staticmethod
    def _truncate_to_words(text: str, max_words: int) -> str:
        if max_words <= 0:
            return ""
        count = 0
        for match in _WORD_RE.finditer(text or ""):
            count += 1
            if count == max_words:
                return text[:match.end()]
        return str(text or "")
