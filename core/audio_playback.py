"""Cross-platform audio playback using sounddevice."""

import io
import wave
import logging
import threading

import numpy as np
import sounddevice as sd

logger = logging.getLogger(__name__)

_playback_lock = threading.Lock()
_stop_event = threading.Event()
_playback_thread: threading.Thread | None = None


def play_wav_bytes(audio_bytes: bytes):
    """Play WAV audio bytes asynchronously (cross-platform via sounddevice).

    Raises ValueError if audio_bytes is empty.
    Raises RuntimeError if no audio output device is available.
    """
    if not audio_bytes:
        raise ValueError("No audio bytes to play.")

    # Parse WAV header to get audio data and parameters
    with io.BytesIO(audio_bytes) as buf:
        with wave.open(buf, "rb") as wf:
            channels = wf.getnchannels()
            sample_rate = wf.getframerate()
            sample_width = wf.getsampwidth()
            raw_frames = wf.readframes(wf.getnframes())

    dtype = f"int{sample_width * 8}"
    audio_data = np.frombuffer(raw_frames, dtype=dtype)
    if channels > 1:
        audio_data = audio_data.reshape(-1, channels)

    # Stop any current playback first
    stop_playback()

    def worker():
        try:
            _stop_event.clear()
            sd.play(audio_data, samplerate=sample_rate)
            sd.wait()
        except Exception as e:
            logger.error("Audio playback failed: %s", e)

    global _playback_thread
    with _playback_lock:
        _playback_thread = threading.Thread(target=worker, daemon=True)
        _playback_thread.start()


def stop_playback():
    """Stop any active playback."""
    global _playback_thread
    _stop_event.set()
    try:
        sd.stop()
    except Exception:
        pass
    with _playback_lock:
        if _playback_thread and _playback_thread.is_alive():
            _playback_thread.join(timeout=0.5)
        _playback_thread = None
