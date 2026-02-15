import sys
import os
import tempfile
import threading
try:
    import winsound
except ImportError:  # Non-Windows environments
    winsound = None

_playback_lock = threading.Lock()
_current_temp_path = None


def _cleanup_temp_file(path: str | None):
    if not path:
        return
    try:
        os.remove(path)
    except OSError:
        pass


def play_wav_bytes(audio_bytes: bytes):
    """Play WAV audio bytes asynchronously on Windows."""
    global _current_temp_path
    if sys.platform != "win32" or winsound is None:
        raise RuntimeError("Audio playback is supported only on Windows in this build.")
    if not audio_bytes:
        raise ValueError("No audio bytes to play.")

    # winsound does not support SND_ASYNC with SND_MEMORY; use a temp WAV file.
    with _playback_lock:
        previous = _current_temp_path
        fd, path = tempfile.mkstemp(prefix="limescribe_tts_", suffix=".wav")
        with os.fdopen(fd, "wb") as f:
            f.write(audio_bytes)

        winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        _current_temp_path = path
        _cleanup_temp_file(previous)


def stop_playback():
    """Stop any active winsound playback."""
    global _current_temp_path
    if sys.platform == "win32" and winsound is not None:
        with _playback_lock:
            winsound.PlaySound(None, winsound.SND_PURGE)
            previous = _current_temp_path
            _current_temp_path = None
            _cleanup_temp_file(previous)
