import io
import wave
import threading
import numpy as np
import sounddevice as sd


SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = "int16"


class AudioRecorder:
    """Records audio from the microphone, supports start/pause/resume/stop."""

    def __init__(self, sample_rate=SAMPLE_RATE):
        self.sample_rate = sample_rate
        self._frames: list[np.ndarray] = []
        self._stream = None
        self._lock = threading.Lock()
        self._paused = False
        self.recording = False

    def start(self):
        """Start recording from the default mic."""
        with self._lock:
            self._frames.clear()
            self._paused = False
            self.recording = True
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=CHANNELS,
            dtype=DTYPE,
            callback=self._audio_callback,
        )
        self._stream.start()

    def pause(self):
        """Pause recording (keeps stream open)."""
        with self._lock:
            self._paused = True

    def resume(self):
        """Resume recording after pause."""
        with self._lock:
            self._paused = False

    def stop(self) -> bytes:
        """Stop recording and return WAV bytes."""
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        with self._lock:
            self.recording = False
            self._paused = False
            frames = list(self._frames)
            self._frames.clear()
        return self._to_wav(frames)

    def _audio_callback(self, indata, frames, time_info, status):
        with self._lock:
            if not self._paused:
                self._frames.append(indata.copy())

    def _to_wav(self, frames: list[np.ndarray]) -> bytes:
        """Convert captured frames to WAV bytes."""
        if not frames:
            return b""
        audio = np.concatenate(frames, axis=0)
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio.tobytes())
        return buf.getvalue()
