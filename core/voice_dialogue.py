"""Voice dialogue orchestrator — speak -> STT -> chat -> TTS -> play -> loop.

Pure Python, no PyQt6 imports. Designed to be driven from the UI layer via
callbacks for state changes, transcripts, and audio.
"""

from __future__ import annotations

import logging
import re
import threading
from enum import Enum, auto
from typing import TYPE_CHECKING, Callable, Optional

import sounddevice as sd

from core.audio_playback import play_wav_bytes, stop_playback
from core.dialogue_service import DialogueService
from core.lemonfox_client import LemonFoxClient
from core.lemonfox_tts_client import LemonFoxTTSClient
from core.vad_listener import VADListener

if TYPE_CHECKING:
    from core.app_config import AppConfig

logger = logging.getLogger(__name__)

# Regex for detecting sentence boundaries (period, question, exclamation, etc.)
_SENTENCE_END = re.compile(r'[.!?;]\s')


class VoiceDialogueState(Enum):
    IDLE = auto()
    LISTENING = auto()
    TRANSCRIBING = auto()
    THINKING = auto()
    SPEAKING = auto()
    CANCELLING = auto()


class VoiceDialogueOrchestrator:
    """Coordinates the voice dialogue loop: VAD -> STT -> Chat -> TTS -> playback."""

    def __init__(
        self,
        config: "AppConfig",
        dialogue_service: DialogueService,
        on_state_changed: Optional[Callable[[str], None]] = None,
        on_user_transcript: Optional[Callable[[str], None]] = None,
        on_assistant_text: Optional[Callable[[str], None]] = None,
        on_assistant_audio: Optional[Callable[[bytes], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
        on_turn_complete: Optional[Callable[[], None]] = None,
    ):
        self._config = config
        self._dialogue_service = dialogue_service
        self._on_state_changed = on_state_changed
        self._on_user_transcript = on_user_transcript
        self._on_assistant_text = on_assistant_text
        self._on_assistant_audio = on_assistant_audio
        self._on_error = on_error
        self._on_turn_complete = on_turn_complete

        self._state = VoiceDialogueState.IDLE
        self._cancel = threading.Event()
        self._auto_listen = True
        self._vad: Optional[VADListener] = None

        # Own STT/TTS clients to avoid conflicts with Capture tab
        self._stt_client = LemonFoxClient(config=config)
        self._tts_client = LemonFoxTTSClient(config=config)

    @property
    def state(self) -> VoiceDialogueState:
        return self._state

    @property
    def auto_listen(self) -> bool:
        return self._auto_listen

    @auto_listen.setter
    def auto_listen(self, value: bool):
        self._auto_listen = bool(value)

    def start(self):
        """Begin the voice dialogue loop (start listening)."""
        if self._state != VoiceDialogueState.IDLE:
            return
        self._cancel.clear()
        self._start_listening()

    def stop(self):
        """Stop the voice dialogue loop from any state."""
        self._cancel.set()
        self._stop_vad()
        stop_playback()
        self._set_state(VoiceDialogueState.IDLE)

    def _set_state(self, new_state: VoiceDialogueState):
        self._state = new_state
        if self._on_state_changed:
            self._on_state_changed(new_state.name)

    def _start_listening(self):
        if self._cancel.is_set():
            self._set_state(VoiceDialogueState.IDLE)
            return
        self._vad = VADListener(
            on_speech_chunk=self._on_speech_chunk,
            pause_threshold=self._config.vad_pause_threshold,
            vad_aggressiveness=self._config.vad_aggressiveness,
            min_speech_seconds=self._config.vad_min_speech_seconds,
        )
        self._vad.start()
        self._set_state(VoiceDialogueState.LISTENING)

    def _stop_vad(self):
        if self._vad:
            self._vad.stop()
            self._vad = None

    def _on_speech_chunk(self, wav_bytes: bytes):
        """Called by VAD when a speech chunk is ready (background thread)."""
        if self._cancel.is_set():
            return
        self._stop_vad()
        self._set_state(VoiceDialogueState.TRANSCRIBING)
        threading.Thread(target=self._process_turn, args=(wav_bytes,), daemon=True).start()

    def _process_turn(self, wav_bytes: bytes):
        """Run one full turn: transcribe -> chat (streaming) -> TTS -> play."""
        try:
            # 1. Transcribe
            if self._cancel.is_set():
                return
            user_text = self._stt_client.transcribe_bytes(wav_bytes)
            if not user_text or not user_text.strip():
                logger.debug("Empty transcription, restarting listener")
                self._maybe_auto_listen()
                return
            user_text = user_text.strip()

            if self._cancel.is_set():
                return
            if self._on_user_transcript:
                self._on_user_transcript(user_text)

            # 2. Chat with streaming + sentence-pipelined TTS
            self._set_state(VoiceDialogueState.THINKING)
            if self._cancel.is_set():
                return

            accumulated_text = []
            sentence_buffer = []
            first_sentence = True

            def on_delta(delta: str):
                nonlocal first_sentence
                if self._cancel.is_set():
                    return
                accumulated_text.append(delta)
                sentence_buffer.append(delta)
                buffer_str = "".join(sentence_buffer)

                # Check for sentence boundary
                match = _SENTENCE_END.search(buffer_str)
                if match:
                    end_pos = match.end()
                    sentence = buffer_str[:end_pos].strip()
                    remainder = buffer_str[end_pos:]
                    sentence_buffer.clear()
                    if remainder:
                        sentence_buffer.append(remainder)
                    if sentence:
                        self._speak_sentence(sentence)
                        if first_sentence:
                            first_sentence = False

            self._dialogue_service.send_stream(user_text, on_delta=on_delta)

            # Flush remaining text in buffer
            if self._cancel.is_set():
                return
            remainder = "".join(sentence_buffer).strip()
            if remainder:
                self._speak_sentence(remainder)

            full_text = "".join(accumulated_text).strip()
            if self._on_assistant_text and full_text:
                self._on_assistant_text(full_text)

        except Exception as e:
            logger.error("Voice dialogue turn failed: %s", e)
            if self._on_error:
                self._on_error(str(e))
        finally:
            if not self._cancel.is_set():
                if self._on_turn_complete:
                    self._on_turn_complete()
                self._maybe_auto_listen()
            else:
                self._set_state(VoiceDialogueState.IDLE)

    def _speak_sentence(self, sentence: str):
        """Synthesize and play a single sentence."""
        if self._cancel.is_set():
            return
        try:
            self._set_state(VoiceDialogueState.SPEAKING)
            audio_bytes = self._tts_client.synthesize(sentence, response_format="wav")
            if self._cancel.is_set():
                return
            if self._on_assistant_audio:
                self._on_assistant_audio(audio_bytes)
            play_wav_bytes(audio_bytes)
            # Wait for playback to finish
            self._wait_for_playback()
        except Exception as e:
            logger.error("TTS/playback failed for sentence: %s", e)

    def _wait_for_playback(self):
        """Wait for current audio playback to finish, checking cancel."""
        while not self._cancel.is_set():
            try:
                if not sd.get_stream().active:
                    break
            except Exception:
                break
            self._cancel.wait(timeout=0.1)

    def _maybe_auto_listen(self):
        """Restart listening if auto_listen is enabled and not cancelled."""
        if self._cancel.is_set():
            self._set_state(VoiceDialogueState.IDLE)
            return
        if self._auto_listen:
            self._start_listening()
        else:
            self._set_state(VoiceDialogueState.IDLE)
