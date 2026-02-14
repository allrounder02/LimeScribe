"""TTS service — orchestrates text-to-speech pipeline without PyQt6 dependency."""

import logging
import threading
from typing import Callable, Optional

from core.app_config import AppConfig
from core.lemonfox_tts_client import LemonFoxTTSClient

logger = logging.getLogger(__name__)


class TTSService:
    """Orchestrates text-to-speech synthesis.

    Callbacks are invoked from background threads. UI code must handle
    thread-safety (e.g., via Qt signals or other mechanisms).
    """

    def __init__(
        self,
        config: AppConfig,
        on_audio_ready: Optional[Callable[[bytes], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ):
        self.config = config
        self.client = LemonFoxTTSClient(config=config)
        self._on_audio_ready = on_audio_ready
        self._on_error = on_error
        self._last_audio: bytes = b""

    def synthesize(self, text: str):
        """Synthesize text to audio in a background thread."""
        if not text or not text.strip():
            if self._on_error:
                self._on_error("Text cannot be empty")
            return

        def worker():
            try:
                audio_bytes = self.client.synthesize(text)
                self._last_audio = audio_bytes
                if self._on_audio_ready:
                    self._on_audio_ready(audio_bytes)
            except Exception as e:
                logger.error("TTS synthesis failed: %s", e)
                if self._on_error:
                    self._on_error(str(e))

        threading.Thread(target=worker, daemon=True).start()

    def get_last_audio(self) -> bytes:
        return self._last_audio

    def update_settings(self, **kwargs):
        """Update TTS settings on the live client."""
        for key in ("model", "voice", "language", "response_format", "speed"):
            if key in kwargs and kwargs[key] is not None:
                setattr(self.client, key, kwargs[key])
