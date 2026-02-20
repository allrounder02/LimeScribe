"""Tests for VADListener thread-stop behavior."""

from __future__ import annotations

import sys
import threading
from unittest.mock import MagicMock

import numpy as np

# Mock audio/native dependencies not available in WSL2
for _mod in ("sounddevice", "webrtcvad"):
    if _mod not in sys.modules:
        sys.modules[_mod] = MagicMock()

from core.vad_listener import VADListener


def test_stop_does_not_join_current_thread():
    listener = VADListener(on_speech_chunk=lambda _wav: None)
    listener._running = True
    listener._thread = threading.current_thread()

    # Regression: this used to raise RuntimeError("cannot join current thread")
    listener.stop()

    assert listener._running is False


def test_stop_joins_when_called_from_other_thread():
    listener = VADListener(on_speech_chunk=lambda _wav: None)
    fake_thread = MagicMock()
    fake_thread.is_alive.return_value = False
    listener._running = True
    listener._thread = fake_thread

    listener.stop()

    fake_thread.join.assert_called_once_with(timeout=3)
    assert listener._thread is None


def test_is_speech_frame_rejects_low_energy_even_if_vad_true():
    listener = VADListener(on_speech_chunk=lambda _wav: None, vad_aggressiveness=3)
    listener.vad.is_speech.return_value = True

    is_speech = listener._is_speech_frame(b"\x00\x00" * 480, frame_rms=40.0, noise_rms=25.0)

    assert is_speech is False


def test_is_speech_frame_accepts_high_energy_when_vad_true():
    listener = VADListener(on_speech_chunk=lambda _wav: None, vad_aggressiveness=3)
    listener.vad.is_speech.return_value = True

    is_speech = listener._is_speech_frame(b"\x00\x00" * 480, frame_rms=1200.0, noise_rms=25.0)

    assert is_speech is True


def test_frame_rms_for_silence_is_zero():
    silent = np.zeros((480, 1), dtype=np.int16)
    assert VADListener._frame_rms(silent) == 0.0
