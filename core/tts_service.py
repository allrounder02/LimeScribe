"""TTS service — orchestrates text-to-speech pipeline without PyQt6 dependency."""

import io
import logging
import threading
import wave
from typing import Callable, Optional

from core.app_config import AppConfig
from core.lemonfox_tts_client import LemonFoxTTSClient
from core.tts_text import normalize_tts_text, split_tts_chunks

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
        self._chunk_target_chars = 1200

    def synthesize(
        self,
        text: str,
        optimize_long_text: bool = True,
        long_text_threshold_chars: int = 240,
    ):
        """Synthesize text to audio in a background thread."""
        if not text or not text.strip():
            if self._on_error:
                self._on_error("Text cannot be empty")
            return

        def worker():
            try:
                raw_text = (text or "").strip()
                if not raw_text:
                    raise ValueError("Text cannot be empty")

                threshold = max(1, int(long_text_threshold_chars or 1))
                use_optimization = bool(optimize_long_text) and len(raw_text) >= threshold
                if use_optimization:
                    prepared_text = normalize_tts_text(raw_text)
                    chunks = split_tts_chunks(prepared_text, max_chars=self._chunk_target_chars)
                    response_format = str(self.client.response_format or "").strip().lower()
                    if len(chunks) > 1 and response_format == "wav":
                        logger.info("TTS input split into %d chunks for synthesis.", len(chunks))
                        chunk_audio = [self.client.synthesize(chunk) for chunk in chunks]
                        audio_bytes = self._merge_wav_chunks(chunk_audio, silence_ms=160)
                    else:
                        if len(chunks) > 1:
                            logger.info(
                                "TTS input exceeds chunk target but response_format=%s; using single request.",
                                response_format or "unknown",
                            )
                        audio_bytes = self.client.synthesize(prepared_text)
                else:
                    audio_bytes = self.client.synthesize(raw_text)
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

    @staticmethod
    def _merge_wav_chunks(parts: list[bytes], silence_ms: int = 160) -> bytes:
        if not parts:
            return b""

        merged_frames: list[bytes] = []
        params = None

        for index, wav_bytes in enumerate(parts):
            with wave.open(io.BytesIO(wav_bytes), "rb") as reader:
                current_params = (
                    reader.getnchannels(),
                    reader.getsampwidth(),
                    reader.getframerate(),
                    reader.getcomptype(),
                    reader.getcompname(),
                )
                if params is None:
                    params = current_params
                elif current_params != params:
                    raise ValueError("Chunked TTS WAV responses use mismatched audio formats.")
                merged_frames.append(reader.readframes(reader.getnframes()))
                if index < len(parts) - 1 and silence_ms > 0:
                    silence_frames = int((reader.getframerate() * silence_ms) / 1000.0)
                    silence_bytes = b"\x00" * silence_frames * reader.getnchannels() * reader.getsampwidth()
                    merged_frames.append(silence_bytes)

        if params is None:
            return b""

        out = io.BytesIO()
        with wave.open(out, "wb") as writer:
            writer.setnchannels(params[0])
            writer.setsampwidth(params[1])
            writer.setframerate(params[2])
            writer.writeframes(b"".join(merged_frames))
        return out.getvalue()
