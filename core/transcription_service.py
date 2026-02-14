"""Transcription service — orchestrates STT pipeline without PyQt6 dependency."""

import json
import logging
import shutil
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional
from uuid import uuid4

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
        self._recovery_root = Path(__file__).resolve().parent.parent / "data" / "failed_stt"
        self._recovery_lock = threading.Lock()
        self._last_failed_lock = threading.Lock()
        self._last_failed_kind = ""
        self._last_failed_audio: bytes = b""
        self._last_failed_file_path = ""
        self._last_failed_source = ""

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
        try:
            self._vad = VADListener(
                on_speech_chunk=self._on_vad_chunk,
                pause_threshold=self.config.vad_pause_threshold,
                vad_aggressiveness=self.config.vad_aggressiveness,
                min_speech_seconds=self.config.vad_min_speech_seconds,
            )
            self._vad.start()
            logger.info("VAD listening started")
        except Exception as e:
            self._vad = None
            logger.error("Failed to start VAD listening: %s", e)
            if self._on_error:
                self._on_error(f"Failed to start listening: {e}")

    def stop_listening(self):
        """Stop VAD listening."""
        if self._vad:
            try:
                self._vad.stop()
            except Exception as e:
                logger.error("Failed to stop VAD listening cleanly: %s", e)
            self._vad = None
            logger.info("VAD listening stopped")

    def is_listening(self) -> bool:
        return self._vad is not None

    def _on_vad_chunk(self, wav_bytes: bytes):
        """VAD callback — transcribe chunk in a background thread."""
        threading.Thread(
            target=self._transcribe_bytes,
            args=(wav_bytes, "vad_chunk"),
            daemon=True,
        ).start()

    # -- Manual Recording Mode --

    @property
    def is_recording(self) -> bool:
        return bool(self.recorder and self.recorder.recording)

    def start_recording(self):
        """Start manual mic recording."""
        try:
            self._ensure_recorder()
            self.recorder.start()
            logger.info("Recording started")
        except Exception as e:
            logger.error("Failed to start recording: %s", e)
            if self._on_error:
                self._on_error(f"Failed to start recording: {e}")

    def pause_recording(self):
        if not self.recorder:
            return
        try:
            self.recorder.pause()
        except Exception as e:
            logger.error("Failed to pause recording: %s", e)
            if self._on_error:
                self._on_error(f"Failed to pause recording: {e}")

    def resume_recording(self):
        if not self.recorder:
            return
        try:
            self.recorder.resume()
        except Exception as e:
            logger.error("Failed to resume recording: %s", e)
            if self._on_error:
                self._on_error(f"Failed to resume recording: {e}")

    def stop_recording_and_transcribe(self):
        """Stop recording and transcribe the result in background."""
        if not self.recorder:
            if self._on_error:
                self._on_error("No active recording session")
            return
        try:
            wav_bytes = self.recorder.stop()
        except Exception as e:
            logger.error("Failed to stop recording: %s", e)
            if self._on_error:
                self._on_error(f"Failed to stop recording: {e}")
            return
        logger.info("Recording stopped (%d bytes)", len(wav_bytes))
        if not wav_bytes:
            if self._on_error:
                self._on_error("No audio captured")
            return
        threading.Thread(
            target=self._transcribe_bytes,
            args=(wav_bytes, "manual_recording"),
            daemon=True,
        ).start()

    # -- File Transcription --

    def transcribe_file(self, file_path: str):
        """Transcribe an audio file in background."""
        def worker():
            try:
                text = self.client.transcribe_file(file_path)
                self._clear_last_failed()
                if self._on_transcription:
                    self._on_transcription(text)
            except Exception as e:
                logger.error("File transcription failed: %s", e)
                self._remember_failed_file(file_path=file_path, source="file_upload")
                backup = self._persist_failed_file(file_path, source="file_upload", error=str(e))
                if self._on_error:
                    if backup:
                        self._on_error(
                            f"{e}. Source audio was saved to '{backup}'. You can retry when the server is back."
                        )
                    else:
                        self._on_error(str(e))

        threading.Thread(target=worker, daemon=True).start()

    # -- Shared --

    def _transcribe_bytes(self, wav_bytes: bytes, source: str = "audio_capture"):
        """Transcribe audio bytes (used by both VAD and recording modes)."""
        try:
            text = self.client.transcribe_bytes(wav_bytes)
            self._clear_last_failed()
            if self._on_transcription:
                self._on_transcription(text)
        except Exception as e:
            logger.error("Transcription failed: %s", e)
            self._remember_failed_audio(wav_bytes=wav_bytes, source=source)
            backup = self._persist_failed_audio(wav_bytes, source=source, error=str(e))
            if self._on_error:
                if backup:
                    self._on_error(
                        f"{e}. Captured audio was saved to '{backup}'. You can retry when the server is back."
                    )
                else:
                    self._on_error(str(e))

    def update_settings(
        self,
        language: str = None,
        response_format: str = None,
        vad_aggressiveness: int = None,
        vad_min_speech_seconds: float = None,
        vad_pause_threshold: float = None,
    ):
        """Update STT/VAD settings and apply them live when possible."""
        if language:
            self.client.language = language
        if response_format:
            self.client.response_format = response_format
        restart_vad = False
        if vad_aggressiveness is not None:
            level = max(0, min(3, int(vad_aggressiveness)))
            if self.config.vad_aggressiveness != level:
                self.config.vad_aggressiveness = level
                restart_vad = True
        if vad_min_speech_seconds is not None:
            min_speech = max(0.0, float(vad_min_speech_seconds))
            if self.config.vad_min_speech_seconds != min_speech:
                self.config.vad_min_speech_seconds = min_speech
                restart_vad = True
        if vad_pause_threshold is not None:
            pause = max(0.2, float(vad_pause_threshold))
            if self.config.vad_pause_threshold != pause:
                self.config.vad_pause_threshold = pause
                restart_vad = True

        if restart_vad and self.is_listening():
            try:
                self.stop_listening()
                self.start_listening()
                logger.info("VAD listener restarted to apply updated settings")
            except Exception as e:
                logger.error("Failed to restart VAD listener: %s", e)
                if self._on_error:
                    self._on_error(f"Failed to apply listening settings: {e}")

    def _build_recovery_id(self, source: str) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        safe_source = "".join(ch if ch.isalnum() else "_" for ch in str(source or "").lower()).strip("_")
        safe_source = safe_source or "audio"
        return f"{timestamp}_{safe_source}_{uuid4().hex[:8]}"

    def _write_recovery_metadata(
        self,
        record_id: str,
        source: str,
        error: str,
        saved_path: Path | None = None,
        original_path: str | None = None,
    ):
        try:
            self._recovery_root.mkdir(parents=True, exist_ok=True)
            payload = {
                "id": record_id,
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "source": source,
                "error": str(error or "").strip(),
                "saved_path": str(saved_path) if saved_path else "",
                "original_path": str(original_path or "").strip(),
                "language": getattr(self.client, "language", ""),
                "response_format": getattr(self.client, "response_format", ""),
            }
            meta_path = self._recovery_root / f"{record_id}.json"
            meta_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except OSError as meta_error:
            logger.error("Failed to write STT recovery metadata: %s", meta_error)

    def _persist_failed_audio(self, wav_bytes: bytes, source: str, error: str) -> str | None:
        if not wav_bytes:
            return None
        with self._recovery_lock:
            record_id = self._build_recovery_id(source)
            try:
                self._recovery_root.mkdir(parents=True, exist_ok=True)
                wav_path = self._recovery_root / f"{record_id}.wav"
                wav_path.write_bytes(wav_bytes)
                self._write_recovery_metadata(record_id, source=source, error=error, saved_path=wav_path)
                logger.warning("Saved failed STT audio to %s", wav_path)
                return str(wav_path)
            except OSError as persist_error:
                logger.error("Failed to persist STT recovery audio: %s", persist_error)
                return None

    def _persist_failed_file(self, file_path: str, source: str, error: str) -> str | None:
        with self._recovery_lock:
            record_id = self._build_recovery_id(source)
            source_path = Path(file_path)
            copied_path = None
            try:
                if source_path.exists() and source_path.is_file():
                    self._recovery_root.mkdir(parents=True, exist_ok=True)
                    suffix = source_path.suffix if source_path.suffix else ".bin"
                    copied_path = self._recovery_root / f"{record_id}{suffix}"
                    shutil.copy2(source_path, copied_path)
                    logger.warning("Saved failed STT source file to %s", copied_path)
            except (OSError, shutil.Error) as persist_error:
                logger.error("Failed to copy source file for STT recovery: %s", persist_error)
                copied_path = None
            self._write_recovery_metadata(
                record_id,
                source=source,
                error=error,
                saved_path=copied_path,
                original_path=file_path,
            )
            return str(copied_path) if copied_path else None

    def _remember_failed_audio(self, wav_bytes: bytes, source: str):
        with self._last_failed_lock:
            self._last_failed_kind = "audio"
            self._last_failed_audio = bytes(wav_bytes or b"")
            self._last_failed_file_path = ""
            self._last_failed_source = str(source or "audio_capture")

    def _remember_failed_file(self, file_path: str, source: str):
        with self._last_failed_lock:
            self._last_failed_kind = "file"
            self._last_failed_audio = b""
            self._last_failed_file_path = str(file_path or "").strip()
            self._last_failed_source = str(source or "file_upload")

    def _clear_last_failed(self):
        with self._last_failed_lock:
            self._last_failed_kind = ""
            self._last_failed_audio = b""
            self._last_failed_file_path = ""
            self._last_failed_source = ""

    def has_last_failed_capture(self) -> bool:
        with self._last_failed_lock:
            if self._last_failed_kind == "audio":
                return bool(self._last_failed_audio)
            if self._last_failed_kind == "file":
                return bool(self._last_failed_file_path)
            return False

    def retry_last_failed(self) -> bool:
        with self._last_failed_lock:
            kind = self._last_failed_kind
            audio = bytes(self._last_failed_audio)
            file_path = self._last_failed_file_path
            source = self._last_failed_source or "retry"
        if kind == "audio" and audio:
            threading.Thread(
                target=self._transcribe_bytes,
                args=(audio, f"{source}_retry"),
                daemon=True,
            ).start()
            return True
        if kind == "file" and file_path:
            self.transcribe_file(file_path)
            return True
        return False
