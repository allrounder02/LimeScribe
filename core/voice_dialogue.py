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

# Regex for detecting sentence boundaries and shorter speaker-mode chunks.
_SENTENCE_END = re.compile(r'[.!?;]\s')
_SPEECH_BREAK = re.compile(r'[.!?;:,]\s')
_WORD_RE = re.compile(r"\S+")
_MAX_WORDS_AUTO_LISTEN = 100
_MAX_WORDS_MANUAL = 50
_MIN_WORD_LIMIT = 10
_MAX_WORD_LIMIT = 500
_BARGE_IN_PLAYBACK_HOLDOFF_SECONDS = 0.30
_BARGE_IN_SPEECH_START_FRAMES = 5
_BARGE_IN_SPEECH_START_RMS_MULTIPLIER = 1.25
_SPEECH_MAX_WORDS_PER_CHUNK = 12


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
        self._speaker_mode = True
        self._vad: Optional[VADListener] = None
        self._max_words_auto_listen = self._clamp_word_limit(_MAX_WORDS_AUTO_LISTEN, _MAX_WORDS_AUTO_LISTEN)
        self._max_words_manual = self._clamp_word_limit(_MAX_WORDS_MANUAL, _MAX_WORDS_MANUAL)
        self._turn_lock = threading.Lock()
        self._active_turn_id = 0
        self._active_turn_cancel: Optional[threading.Event] = None
        self._barge_in_active = threading.Event()

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
    def speaker_mode(self) -> bool:
        return self._speaker_mode

    @speaker_mode.setter
    def speaker_mode(self, value: bool):
        self._speaker_mode = bool(value)

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

    def update_tts_settings(self, **kwargs):
        """Update TTS settings for voice dialogue playback only."""
        for key in ("model", "voice", "language", "response_format", "speed"):
            if key in kwargs and kwargs[key] is not None:
                setattr(self._tts_client, key, kwargs[key])

    def start(self):
        """Begin the voice dialogue loop (start listening)."""
        if self._state != VoiceDialogueState.IDLE:
            return
        self._cancel.clear()
        self._start_listening()

    def stop(self):
        """Stop the voice dialogue loop from any state."""
        self._cancel.set()
        self._barge_in_active.clear()
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
            on_speech_start=self._on_speech_start,
            speech_start_min_frames=_BARGE_IN_SPEECH_START_FRAMES,
            speech_start_rms_multiplier=_BARGE_IN_SPEECH_START_RMS_MULTIPLIER,
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
            self._barge_in_active.clear()
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
        # Speaker mode listens between short playback chunks. Headphone mode
        # keeps the interrupt listener active even while audio is playing.
        if not self._auto_listen or self._cancel.is_set():
            return
        self._start_listening(set_state=False)

    def _on_speech_start(self):
        """Handle interrupt detection based on the current audio mode."""
        if self._cancel.is_set() or not self._auto_listen:
            return
        if self._speaker_mode:
            if self._state != VoiceDialogueState.THINKING:
                return
            logger.debug("Voice interruption detected while assistant is thinking; canceling current turn.")
            self._cancel_active_turn()
            self._set_state(VoiceDialogueState.LISTENING)
            return

        if self._barge_in_active.is_set():
            return
        if self._state not in (VoiceDialogueState.THINKING, VoiceDialogueState.SPEAKING):
            return

        logger.debug("Voice barge-in speech start detected; stopping assistant immediately.")
        self._barge_in_active.set()
        self._cancel_active_turn()
        stop_playback()
        self._set_state(VoiceDialogueState.LISTENING)

    def _on_speech_chunk(self, wav_bytes: bytes):
        """Called by VAD when a speech chunk is ready (background thread)."""
        if self._cancel.is_set():
            return
        current_state = self._state
        if self._speaker_mode:
            allow_barge_in = self._auto_listen and current_state == VoiceDialogueState.THINKING
        else:
            allow_barge_in = self._auto_listen and (
                self._barge_in_active.is_set()
                or current_state in (
                    VoiceDialogueState.TRANSCRIBING,
                    VoiceDialogueState.THINKING,
                    VoiceDialogueState.SPEAKING,
                )
            )
        if current_state != VoiceDialogueState.LISTENING and not allow_barge_in:
            return

        self._stop_vad()
        if not self._speaker_mode and allow_barge_in and not self._barge_in_active.is_set():
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
                if self._speaker_mode:
                    self._flush_ready_speech_chunks(sentence_buffer, turn_id, turn_cancel)
                else:
                    self._flush_ready_sentence_chunks(sentence_buffer, turn_id, turn_cancel)

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
            if not self._speaker_mode and turn_cancel.is_set() and self._barge_in_active.is_set():
                self._clear_turn_if_active(turn_id, turn_cancel)
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
        """Synthesize and play one assistant speech chunk."""
        if self._turn_should_stop(turn_id, turn_cancel):
            return
        try:
            if self._speaker_mode:
                self._stop_vad()
            self._set_state(VoiceDialogueState.SPEAKING)
            audio_bytes = self._tts_client.synthesize(sentence, response_format="wav")
            if self._turn_should_stop(turn_id, turn_cancel):
                return
            if self._on_assistant_audio:
                self._on_assistant_audio(audio_bytes)
            if not self._speaker_mode and self._vad:
                self._vad.set_speech_detection_holdoff(_BARGE_IN_PLAYBACK_HOLDOFF_SECONDS)
            play_wav_bytes(audio_bytes)
            # Wait for playback to finish
            self._wait_for_playback(turn_id, turn_cancel)
            if not self._turn_should_stop(turn_id, turn_cancel):
                self._set_state(VoiceDialogueState.THINKING)
                if self._speaker_mode:
                    self._arm_interrupt_listener()
        except Exception as e:
            logger.error("TTS/playback failed for sentence: %s", e)

    def _flush_ready_sentence_chunks(self, sentence_buffer: list[str], turn_id: int, turn_cancel: threading.Event):
        while not self._turn_should_stop(turn_id, turn_cancel):
            chunk, remainder = self._extract_sentence_chunk("".join(sentence_buffer))
            if not chunk:
                return
            sentence_buffer.clear()
            if remainder:
                sentence_buffer.append(remainder)
            self._speak_sentence(chunk, turn_id, turn_cancel)

    def _flush_ready_speech_chunks(self, sentence_buffer: list[str], turn_id: int, turn_cancel: threading.Event):
        while not self._turn_should_stop(turn_id, turn_cancel):
            chunk, remainder = self._extract_speech_chunk("".join(sentence_buffer))
            if not chunk:
                return
            sentence_buffer.clear()
            if remainder:
                sentence_buffer.append(remainder)
            self._speak_sentence(chunk, turn_id, turn_cancel)

    @staticmethod
    def _extract_sentence_chunk(buffer: str) -> tuple[str, str]:
        text = str(buffer or "")
        if not text.strip():
            return "", ""

        match = _SENTENCE_END.search(text)
        if not match:
            return "", text

        split_at = match.end()
        return text[:split_at].strip(), text[split_at:]

    @staticmethod
    def _extract_speech_chunk(buffer: str) -> tuple[str, str]:
        text = str(buffer or "")
        if not text.strip():
            return "", ""

        match = _SPEECH_BREAK.search(text)
        if match:
            split_at = match.end()
            return text[:split_at].strip(), text[split_at:]

        word_matches = list(_WORD_RE.finditer(text))
        if len(word_matches) >= _SPEECH_MAX_WORDS_PER_CHUNK:
            split_at = word_matches[_SPEECH_MAX_WORDS_PER_CHUNK - 1].end()
            return text[:split_at].strip(), text[split_at:]

        return "", text

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
