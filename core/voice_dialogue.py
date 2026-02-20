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

from core.audio_playback import is_playback_active, play_wav_bytes, stop_playback
from core.dialogue_service import DialogueService
from core.lemonfox_client import LemonFoxClient
from core.lemonfox_tts_client import LemonFoxTTSClient
from core.vad_listener import VADListener

if TYPE_CHECKING:
    from core.app_config import AppConfig

logger = logging.getLogger(__name__)

# Regex for detecting sentence boundaries (period, question, exclamation, etc.)
_SENTENCE_END = re.compile(r'[.!?;]\s')
_MAX_WORDS_AUTO_LISTEN = 100
_MAX_WORDS_MANUAL = 50
_MIN_WORD_LIMIT = 10
_MAX_WORD_LIMIT = 500


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
        self._max_words_auto_listen = self._clamp_word_limit(_MAX_WORDS_AUTO_LISTEN, _MAX_WORDS_AUTO_LISTEN)
        self._max_words_manual = self._clamp_word_limit(_MAX_WORDS_MANUAL, _MAX_WORDS_MANUAL)
        self._turn_lock = threading.Lock()
        self._active_turn_id = 0
        self._active_turn_cancel: Optional[threading.Event] = None

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

    @property
    def max_words_auto_listen(self) -> int:
        return self._max_words_auto_listen

    @property
    def max_words_manual(self) -> int:
        return self._max_words_manual

    @staticmethod
    def _clamp_word_limit(value: int | None, default: int) -> int:
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            parsed = int(default)
        return max(_MIN_WORD_LIMIT, min(_MAX_WORD_LIMIT, parsed))

    def set_response_word_limits(
        self,
        max_words_auto_listen: int | None = None,
        max_words_manual: int | None = None,
    ):
        if max_words_auto_listen is not None:
            self._max_words_auto_listen = self._clamp_word_limit(
                max_words_auto_listen,
                self._max_words_auto_listen,
            )
        if max_words_manual is not None:
            self._max_words_manual = self._clamp_word_limit(
                max_words_manual,
                self._max_words_manual,
            )

    def start(self):
        """Begin the voice dialogue loop (start listening)."""
        if self._state != VoiceDialogueState.IDLE:
            return
        self._cancel.clear()
        self._start_listening()

    def stop(self):
        """Stop the voice dialogue loop from any state."""
        self._cancel.set()
        self._cancel_active_turn()
        self._stop_vad()
        stop_playback()
        self._set_state(VoiceDialogueState.IDLE)

    def _set_state(self, new_state: VoiceDialogueState):
        self._state = new_state
        if self._on_state_changed:
            self._on_state_changed(new_state.name)

    def _start_listening(self, set_state: bool = True):
        if self._cancel.is_set():
            if set_state:
                self._set_state(VoiceDialogueState.IDLE)
            return
        if self._vad:
            return
        self._vad = VADListener(
            on_speech_chunk=self._on_speech_chunk,
            pause_threshold=self._config.vad_pause_threshold,
            vad_aggressiveness=self._config.vad_aggressiveness,
            min_speech_seconds=self._config.vad_min_speech_seconds,
        )
        self._vad.start()
        if set_state:
            self._set_state(VoiceDialogueState.LISTENING)

    def _stop_vad(self):
        if self._vad:
            self._vad.stop()
            self._vad = None

    def _response_word_limit(self) -> int:
        return self._max_words_auto_listen if self._auto_listen else self._max_words_manual

    def _cancel_active_turn(self):
        with self._turn_lock:
            if self._active_turn_cancel:
                self._active_turn_cancel.set()

    def _start_turn(self) -> tuple[int, threading.Event]:
        with self._turn_lock:
            if self._active_turn_cancel:
                self._active_turn_cancel.set()
            self._active_turn_id += 1
            turn_id = self._active_turn_id
            turn_cancel = threading.Event()
            self._active_turn_cancel = turn_cancel
        return turn_id, turn_cancel

    def _is_turn_active(self, turn_id: int, turn_cancel: threading.Event) -> bool:
        with self._turn_lock:
            return self._active_turn_id == turn_id and self._active_turn_cancel is turn_cancel

    def _clear_turn_if_active(self, turn_id: int, turn_cancel: threading.Event):
        with self._turn_lock:
            if self._active_turn_id == turn_id and self._active_turn_cancel is turn_cancel:
                self._active_turn_cancel = None

    def _turn_should_stop(self, turn_id: int, turn_cancel: threading.Event) -> bool:
        if self._cancel.is_set():
            return True
        if turn_cancel.is_set():
            return True
        return not self._is_turn_active(turn_id, turn_cancel)

    def _arm_interrupt_listener(self):
        # Barge-in mode: while assistant is thinking/speaking, still listen so
        # the user can interrupt with a new utterance.
        if not self._auto_listen or self._cancel.is_set():
            return
        self._start_listening(set_state=False)

    def _on_speech_chunk(self, wav_bytes: bytes):
        """Called by VAD when a speech chunk is ready (background thread)."""
        if self._cancel.is_set():
            return
        current_state = self._state
        allow_barge_in = self._auto_listen and current_state in (
            VoiceDialogueState.TRANSCRIBING,
            VoiceDialogueState.THINKING,
            VoiceDialogueState.SPEAKING,
        )
        if current_state != VoiceDialogueState.LISTENING and not allow_barge_in:
            return

        self._stop_vad()
        if allow_barge_in:
            logger.debug("Voice barge-in detected; interrupting current turn.")
            self._cancel_active_turn()
            stop_playback()

        turn_id, turn_cancel = self._start_turn()
        self._set_state(VoiceDialogueState.TRANSCRIBING)
        threading.Thread(
            target=self._process_turn,
            args=(wav_bytes, turn_id, turn_cancel),
            daemon=True,
        ).start()

    def _process_turn(self, wav_bytes: bytes, turn_id: int, turn_cancel: threading.Event):
        """Run one full turn: transcribe -> chat (streaming) -> TTS -> play."""
        try:
            # 1. Transcribe
            if self._turn_should_stop(turn_id, turn_cancel):
                return
            user_text = self._stt_client.transcribe_bytes(wav_bytes)
            if not user_text or not user_text.strip():
                logger.debug("Empty transcription, restarting listener")
                return
            user_text = user_text.strip()

            if self._turn_should_stop(turn_id, turn_cancel):
                return
            if self._on_user_transcript:
                self._on_user_transcript(user_text)

            # 2. Chat with streaming + sentence-pipelined TTS
            self._set_state(VoiceDialogueState.THINKING)
            if self._turn_should_stop(turn_id, turn_cancel):
                return

            self._arm_interrupt_listener()
            accumulated_text = []
            sentence_buffer = []

            def on_delta(delta: str):
                if self._turn_should_stop(turn_id, turn_cancel):
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
                        self._speak_sentence(sentence, turn_id, turn_cancel)

            self._dialogue_service.send_stream(
                user_text,
                on_delta=on_delta,
                cancel_event=turn_cancel,
                max_words=self._response_word_limit(),
            )

            # Flush remaining text in buffer
            if self._turn_should_stop(turn_id, turn_cancel):
                return
            remainder = "".join(sentence_buffer).strip()
            if remainder:
                self._speak_sentence(remainder, turn_id, turn_cancel)

            full_text = "".join(accumulated_text).strip()
            if self._on_assistant_text and full_text and not self._turn_should_stop(turn_id, turn_cancel):
                self._on_assistant_text(full_text)

        except Exception as e:
            logger.error("Voice dialogue turn failed: %s", e)
            if self._on_error:
                self._on_error(str(e))
        finally:
            if not self._is_turn_active(turn_id, turn_cancel):
                return
            self._clear_turn_if_active(turn_id, turn_cancel)
            self._stop_vad()
            if self._cancel.is_set():
                self._set_state(VoiceDialogueState.IDLE)
                return
            if not turn_cancel.is_set():
                if self._on_turn_complete:
                    self._on_turn_complete()
                self._maybe_auto_listen()

    def _speak_sentence(self, sentence: str, turn_id: int, turn_cancel: threading.Event):
        """Synthesize and play a single sentence."""
        if self._turn_should_stop(turn_id, turn_cancel):
            return
        try:
            self._set_state(VoiceDialogueState.SPEAKING)
            audio_bytes = self._tts_client.synthesize(sentence, response_format="wav")
            if self._turn_should_stop(turn_id, turn_cancel):
                return
            if self._on_assistant_audio:
                self._on_assistant_audio(audio_bytes)
            play_wav_bytes(audio_bytes)
            # Wait for playback to finish
            self._wait_for_playback(turn_id, turn_cancel)
        except Exception as e:
            logger.error("TTS/playback failed for sentence: %s", e)

    def _wait_for_playback(self, turn_id: int, turn_cancel: threading.Event):
        """Wait for current audio playback to finish, checking cancel."""
        while is_playback_active():
            if self._turn_should_stop(turn_id, turn_cancel):
                stop_playback()
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
