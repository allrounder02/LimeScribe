"""Tests for VoiceDialogueOrchestrator state machine and cancellation."""

from __future__ import annotations

import sys
import threading
import time
from unittest.mock import MagicMock, patch

import pytest

# Mock audio/native dependencies not available in WSL2
for _mod in ("sounddevice", "webrtcvad"):
    if _mod not in sys.modules:
        sys.modules[_mod] = MagicMock()

from core.app_config import AppConfig
from core.dialogue_service import DialogueService
from core.voice_dialogue import VoiceDialogueOrchestrator, VoiceDialogueState


def _make_config() -> AppConfig:
    return AppConfig(
        api_key="test-key",
        chat_model="test-model",
    )


def _make_service(config: AppConfig) -> DialogueService:
    return DialogueService(config=config)


class TestVoiceDialogueState:
    def test_initial_state_is_idle(self):
        config = _make_config()
        service = _make_service(config)
        orch = VoiceDialogueOrchestrator(config=config, dialogue_service=service)
        assert orch.state == VoiceDialogueState.IDLE

    def test_auto_listen_default_true(self):
        config = _make_config()
        service = _make_service(config)
        orch = VoiceDialogueOrchestrator(config=config, dialogue_service=service)
        assert orch.auto_listen is True

    def test_auto_listen_toggle(self):
        config = _make_config()
        service = _make_service(config)
        orch = VoiceDialogueOrchestrator(config=config, dialogue_service=service)
        orch.auto_listen = False
        assert orch.auto_listen is False
        orch.auto_listen = True
        assert orch.auto_listen is True

    def test_response_word_limits_are_configurable(self):
        config = _make_config()
        service = _make_service(config)
        orch = VoiceDialogueOrchestrator(config=config, dialogue_service=service)

        orch.set_response_word_limits(max_words_auto_listen=120, max_words_manual=60)

        assert orch.max_words_auto_listen == 120
        assert orch.max_words_manual == 60


class TestStartStop:
    @patch("core.voice_dialogue.VADListener")
    def test_start_transitions_to_listening(self, MockVAD):
        config = _make_config()
        service = _make_service(config)
        states = []
        orch = VoiceDialogueOrchestrator(
            config=config,
            dialogue_service=service,
            on_state_changed=lambda s: states.append(s),
        )
        orch.start()
        assert orch.state == VoiceDialogueState.LISTENING
        assert "LISTENING" in states
        MockVAD.return_value.start.assert_called_once()

    @patch("core.voice_dialogue.VADListener")
    def test_start_ignored_if_not_idle(self, MockVAD):
        config = _make_config()
        service = _make_service(config)
        orch = VoiceDialogueOrchestrator(config=config, dialogue_service=service)
        orch.start()
        MockVAD.return_value.start.assert_called_once()
        orch.start()  # should be ignored
        MockVAD.return_value.start.assert_called_once()

    @patch("core.voice_dialogue.stop_playback")
    @patch("core.voice_dialogue.VADListener")
    def test_stop_returns_to_idle(self, MockVAD, mock_stop_play):
        config = _make_config()
        service = _make_service(config)
        states = []
        orch = VoiceDialogueOrchestrator(
            config=config,
            dialogue_service=service,
            on_state_changed=lambda s: states.append(s),
        )
        orch.start()
        orch.stop()
        assert orch.state == VoiceDialogueState.IDLE
        assert "IDLE" in states
        MockVAD.return_value.stop.assert_called()
        mock_stop_play.assert_called_once()


class TestProcessTurn:
    @patch("core.voice_dialogue.VADListener")
    @patch("core.voice_dialogue.play_wav_bytes")
    def test_full_turn_flow(self, mock_play, MockVAD):
        config = _make_config()
        service = _make_service(config)

        user_transcripts = []
        assistant_texts = []
        states = []
        turn_done = threading.Event()

        orch = VoiceDialogueOrchestrator(
            config=config,
            dialogue_service=service,
            on_state_changed=lambda s: states.append(s),
            on_user_transcript=lambda t: user_transcripts.append(t),
            on_assistant_text=lambda t: assistant_texts.append(t),
            on_turn_complete=lambda: turn_done.set(),
        )

        # Mock STT
        orch._stt_client = MagicMock()
        orch._stt_client.transcribe_bytes.return_value = "Hello there"

        # Mock TTS
        orch._tts_client = MagicMock()
        orch._tts_client.synthesize.return_value = b"fake-wav-data"

        # Mock dialogue service send_stream to yield one complete response
        def mock_send_stream(text, on_delta=None, **_kwargs):
            if on_delta:
                on_delta("Hi! ")
                on_delta("How are you?")
            service._on_reply = None  # prevent callback

        service.send_stream = mock_send_stream

        # Mock playback activity to avoid waiting
        with patch("core.voice_dialogue.is_playback_active", return_value=False):

            # Simulate VAD firing
            orch.auto_listen = False
            orch.start()
            assert orch.state == VoiceDialogueState.LISTENING

            # Trigger speech chunk
            orch._on_speech_chunk(b"fake-wav")

            # Wait for turn to complete
            assert turn_done.wait(timeout=5)

        assert user_transcripts == ["Hello there"]
        assert "TRANSCRIBING" in states
        assert "THINKING" in states

    @patch("core.voice_dialogue.VADListener")
    @patch("core.voice_dialogue.play_wav_bytes")
    def test_speech_chunk_callback_from_background_thread(self, mock_play, MockVAD):
        config = _make_config()
        service = _make_service(config)

        states = []
        turn_done = threading.Event()

        orch = VoiceDialogueOrchestrator(
            config=config,
            dialogue_service=service,
            on_state_changed=lambda s: states.append(s),
            on_turn_complete=lambda: turn_done.set(),
        )

        orch._stt_client = MagicMock()
        orch._stt_client.transcribe_bytes.return_value = "Hello"

        orch._tts_client = MagicMock()
        orch._tts_client.synthesize.return_value = b"fake-wav-data"

        def mock_send_stream(text, on_delta=None, **_kwargs):
            if on_delta:
                on_delta("Hi.")

        service.send_stream = mock_send_stream

        with patch("core.voice_dialogue.is_playback_active", return_value=False):

            orch.auto_listen = False
            orch.start()

            callback_thread = threading.Thread(
                target=orch._on_speech_chunk,
                args=(b"fake-wav",),
                daemon=True,
            )
            callback_thread.start()
            callback_thread.join(timeout=2)

            assert turn_done.wait(timeout=5)

        assert "TRANSCRIBING" in states
        assert "THINKING" in states

    @patch("core.voice_dialogue.VADListener")
    @patch("core.voice_dialogue.stop_playback")
    def test_cancel_during_turn(self, mock_stop_play, MockVAD):
        config = _make_config()
        service = _make_service(config)
        states = []

        orch = VoiceDialogueOrchestrator(
            config=config,
            dialogue_service=service,
            on_state_changed=lambda s: states.append(s),
        )

        # Mock STT to block until cancelled
        stt_entered = threading.Event()

        def slow_transcribe(wav_bytes):
            stt_entered.set()
            time.sleep(5)  # will be interrupted
            return "text"

        orch._stt_client = MagicMock()
        orch._stt_client.transcribe_bytes.side_effect = slow_transcribe

        orch.start()
        orch._on_speech_chunk(b"fake-wav")

        # Wait for transcription to start, then cancel
        stt_entered.wait(timeout=2)
        orch.stop()

        assert orch.state == VoiceDialogueState.IDLE


class TestAutoListen:
    @patch("core.voice_dialogue.VADListener")
    @patch("core.voice_dialogue.play_wav_bytes")
    def test_auto_listen_restarts_after_turn(self, mock_play, MockVAD):
        config = _make_config()
        service = _make_service(config)
        turn_done = threading.Event()

        orch = VoiceDialogueOrchestrator(
            config=config,
            dialogue_service=service,
            on_turn_complete=lambda: turn_done.set(),
        )

        orch._stt_client = MagicMock()
        orch._stt_client.transcribe_bytes.return_value = "test"

        orch._tts_client = MagicMock()
        orch._tts_client.synthesize.return_value = b"audio"

        def mock_send_stream(text, on_delta=None, **_kwargs):
            if on_delta:
                on_delta("Reply.")

        service.send_stream = mock_send_stream

        with patch("core.voice_dialogue.is_playback_active", return_value=False):

            orch.auto_listen = True
            orch.start()
            orch._on_speech_chunk(b"wav")
            turn_done.wait(timeout=5)

        # After turn, should be back to LISTENING
        assert orch.state == VoiceDialogueState.LISTENING

    @patch("core.voice_dialogue.VADListener")
    @patch("core.voice_dialogue.play_wav_bytes")
    def test_no_auto_listen_stays_idle(self, mock_play, MockVAD):
        config = _make_config()
        service = _make_service(config)
        turn_done = threading.Event()

        orch = VoiceDialogueOrchestrator(
            config=config,
            dialogue_service=service,
            on_turn_complete=lambda: turn_done.set(),
        )

        orch._stt_client = MagicMock()
        orch._stt_client.transcribe_bytes.return_value = "test"

        orch._tts_client = MagicMock()
        orch._tts_client.synthesize.return_value = b"audio"

        def mock_send_stream(text, on_delta=None, **_kwargs):
            if on_delta:
                on_delta("Reply.")

        service.send_stream = mock_send_stream

        with patch("core.voice_dialogue.is_playback_active", return_value=False):

            orch.auto_listen = False
            orch.start()
            orch._on_speech_chunk(b"wav")
            turn_done.wait(timeout=5)

        assert orch.state == VoiceDialogueState.IDLE


class TestBargeIn:
    @patch("core.voice_dialogue.stop_playback")
    @patch("core.voice_dialogue.threading.Thread")
    def test_auto_listen_allows_barge_in_while_speaking(self, MockThread, mock_stop_playback):
        config = _make_config()
        service = _make_service(config)
        orch = VoiceDialogueOrchestrator(config=config, dialogue_service=service)

        previous_turn_cancel = threading.Event()
        orch._active_turn_cancel = previous_turn_cancel
        orch._auto_listen = True
        orch._state = VoiceDialogueState.SPEAKING
        orch._vad = MagicMock()

        orch._on_speech_chunk(b"interrupt-wav")

        assert previous_turn_cancel.is_set()
        mock_stop_playback.assert_called_once()
        assert orch._state == VoiceDialogueState.TRANSCRIBING
        assert orch._active_turn_cancel is not previous_turn_cancel
        MockThread.return_value.start.assert_called_once()

    @patch("core.voice_dialogue.threading.Thread")
    @patch("core.voice_dialogue.stop_playback")
    def test_no_barge_in_when_auto_listen_off(self, mock_stop_playback, MockThread):
        config = _make_config()
        service = _make_service(config)
        orch = VoiceDialogueOrchestrator(config=config, dialogue_service=service)

        previous_turn_cancel = threading.Event()
        orch._active_turn_cancel = previous_turn_cancel
        orch._auto_listen = False
        orch._state = VoiceDialogueState.SPEAKING
        orch._vad = MagicMock()

        orch._on_speech_chunk(b"ignored")

        assert previous_turn_cancel.is_set() is False
        mock_stop_playback.assert_not_called()
        MockThread.return_value.start.assert_not_called()


class TestWordLimits:
    @patch("core.voice_dialogue.VADListener")
    @patch("core.voice_dialogue.play_wav_bytes")
    def test_manual_mode_uses_shorter_word_limit(self, mock_play, MockVAD):
        config = _make_config()
        service = _make_service(config)
        turn_done = threading.Event()
        seen_limits: list[int] = []

        orch = VoiceDialogueOrchestrator(
            config=config,
            dialogue_service=service,
            on_turn_complete=lambda: turn_done.set(),
        )
        orch._stt_client = MagicMock()
        orch._stt_client.transcribe_bytes.return_value = "test"
        orch._tts_client = MagicMock()
        orch._tts_client.synthesize.return_value = b"audio"

        def mock_send_stream(text, on_delta=None, **kwargs):
            seen_limits.append(int(kwargs.get("max_words", 0)))
            if on_delta:
                on_delta("Reply.")

        service.send_stream = mock_send_stream

        with patch("core.voice_dialogue.is_playback_active", return_value=False):
            orch.auto_listen = False
            orch.start()
            orch._on_speech_chunk(b"wav")
            turn_done.wait(timeout=5)

        assert seen_limits[-1] == 50

    @patch("core.voice_dialogue.VADListener")
    @patch("core.voice_dialogue.play_wav_bytes")
    def test_auto_listen_mode_uses_100_word_limit(self, mock_play, MockVAD):
        config = _make_config()
        service = _make_service(config)
        turn_done = threading.Event()
        seen_limits: list[int] = []

        orch = VoiceDialogueOrchestrator(
            config=config,
            dialogue_service=service,
            on_turn_complete=lambda: turn_done.set(),
        )
        orch._stt_client = MagicMock()
        orch._stt_client.transcribe_bytes.return_value = "test"
        orch._tts_client = MagicMock()
        orch._tts_client.synthesize.return_value = b"audio"

        def mock_send_stream(text, on_delta=None, **kwargs):
            seen_limits.append(int(kwargs.get("max_words", 0)))
            if on_delta:
                on_delta("Reply.")

        service.send_stream = mock_send_stream

        with patch("core.voice_dialogue.is_playback_active", return_value=False):
            orch.auto_listen = True
            orch.start()
            orch._on_speech_chunk(b"wav")
            turn_done.wait(timeout=5)

        assert seen_limits[-1] == 100
