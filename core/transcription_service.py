"""Transcription service — orchestrates STT pipeline without PyQt6 dependency."""

import logging
import threading
from typing import Callable, Optional

from core.app_config import AppConfig
from core.lemonfox_client import LemonFoxClient

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Orchestrates speech-to-text: recording, VAD listening, file transcription.

    Callbacks are invoked from background threads. UI code must handle
    thread-safety (e.g., via Qt signals or other mechanisms).
    """

    def __init__(
        self,
        config: AppConfig,
        on_transcription: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ):
        self.config = config
        self.client = LemonFoxClient(config=config)
        self.recorder = None  # Lazy-loaded (needs PortAudio)
        self._vad = None
        self._on_transcription = on_transcription
        self._on_error = on_error

    # -- VAD Listening Mode --

    def _ensure_recorder(self):
        if self.recorder is None:
            from core.audio_recorder import AudioRecorder
            self.recorder = AudioRecorder()

    def start_listening(self):
        """Start continuous VAD listening."""
        if self._vad:
            return
        from core.vad_listener import VADListener
        self._vad = VADListener(
            on_speech_chunk=self._on_vad_chunk,
            pause_threshold=self.config.vad_pause_threshold,
            vad_aggressiveness=self.config.vad_aggressiveness,
            min_speech_seconds=self.config.vad_min_speech_seconds,
        )
        self._vad.start()
        logger.info("VAD listening started")

    def stop_listening(self):
        """Stop VAD listening."""
        if self._vad:
            self._vad.stop()
            self._vad = None
            logger.info("VAD listening stopped")

    def is_listening(self) -> bool:
        return self._vad is not None

    def _on_vad_chunk(self, wav_bytes: bytes):
        """VAD callback — transcribe chunk in a background thread."""
        threading.Thread(target=self._transcribe_bytes, args=(wav_bytes,), daemon=True).start()

    # -- Manual Recording Mode --

    @property
    def is_recording(self) -> bool:
        return self.recorder.recording

    def start_recording(self):
        """Start manual mic recording."""
        self._ensure_recorder()
        self.recorder.start()
        logger.info("Recording started")

    def pause_recording(self):
        self.recorder.pause()

    def resume_recording(self):
        self.recorder.resume()

    def stop_recording_and_transcribe(self):
        """Stop recording and transcribe the result in background."""
        wav_bytes = self.recorder.stop()
        logger.info("Recording stopped (%d bytes)", len(wav_bytes))
        if not wav_bytes:
            if self._on_error:
                self._on_error("No audio captured")
            return
        threading.Thread(target=self._transcribe_bytes, args=(wav_bytes,), daemon=True).start()

    # -- File Transcription --

    def transcribe_file(self, file_path: str):
        """Transcribe an audio file in background."""
        def worker():
            try:
                text = self.client.transcribe_file(file_path)
                if self._on_transcription:
                    self._on_transcription(text)
            except Exception as e:
                logger.error("File transcription failed: %s", e)
                if self._on_error:
                    self._on_error(str(e))

        threading.Thread(target=worker, daemon=True).start()

    # -- Shared --

    def _transcribe_bytes(self, wav_bytes: bytes):
        """Transcribe audio bytes (used by both VAD and recording modes)."""
        try:
            text = self.client.transcribe_bytes(wav_bytes)
            if self._on_transcription:
                self._on_transcription(text)
        except Exception as e:
            logger.error("Transcription failed: %s", e)
            if self._on_error:
                self._on_error(str(e))

    def update_settings(self, language: str = None, response_format: str = None):
        """Update STT settings on the live client."""
        if language:
            self.client.language = language
        if response_format:
            self.client.response_format = response_format
