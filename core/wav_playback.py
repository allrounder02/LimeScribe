"""Realtime WAV playback controller with transport and tuning controls."""

from __future__ import annotations

import io
import threading
import wave

import numpy as np
import sounddevice as sd


def _decode_pcm_to_float32(raw_frames: bytes, sample_width: int) -> np.ndarray:
    if sample_width == 1:
        data = np.frombuffer(raw_frames, dtype=np.uint8).astype(np.float32)
        return (data - 128.0) / 128.0
    if sample_width == 2:
        data = np.frombuffer(raw_frames, dtype=np.int16).astype(np.float32)
        return data / 32768.0
    if sample_width == 3:
        raw = np.frombuffer(raw_frames, dtype=np.uint8).reshape(-1, 3)
        data = (
            raw[:, 0].astype(np.int32)
            | (raw[:, 1].astype(np.int32) << 8)
            | (raw[:, 2].astype(np.int32) << 16)
        )
        signed = data - ((data & 0x800000) << 1)
        return signed.astype(np.float32) / 8388608.0
    if sample_width == 4:
        data = np.frombuffer(raw_frames, dtype=np.int32).astype(np.float32)
        return data / 2147483648.0
    raise ValueError(f"Unsupported WAV sample width: {sample_width}")


class WavPlaybackController:
    """Audio transport with play/pause/stop/seek and runtime speed/pitch."""

    def __init__(self):
        self._lock = threading.RLock()
        self._stream: sd.OutputStream | None = None
        self._audio: np.ndarray | None = None  # shape: (frames, channels), float32
        self._sample_rate = 0
        self._position_frames = 0.0
        self._playing = False
        self._speed = 1.0
        self._pitch_semitones = 0.0

    def load_wav_bytes(self, audio_bytes: bytes):
        if not audio_bytes:
            raise ValueError("No audio bytes provided")
        with io.BytesIO(audio_bytes) as buf:
            with wave.open(buf, "rb") as wf:
                channels = wf.getnchannels()
                sample_rate = wf.getframerate()
                sample_width = wf.getsampwidth()
                raw_frames = wf.readframes(wf.getnframes())
        if channels <= 0 or sample_rate <= 0:
            raise ValueError("Invalid WAV format")

        decoded = _decode_pcm_to_float32(raw_frames, sample_width)
        if decoded.size == 0:
            raise ValueError("WAV audio contains no frames")
        audio = decoded.reshape(-1, channels).astype(np.float32, copy=False)

        with self._lock:
            self._close_stream_locked()
            self._audio = audio
            self._sample_rate = int(sample_rate)
            self._position_frames = 0.0
            self._playing = False

    def play(self):
        with self._lock:
            if self._audio is None:
                return
            if self._position_frames >= self._last_frame_index_locked():
                self._position_frames = 0.0
            self._ensure_stream_locked()
            if self._stream is not None and not self._stream.active:
                self._stream.start()
            self._playing = True

    def pause(self):
        with self._lock:
            self._playing = False

    def stop(self):
        with self._lock:
            self._playing = False
            self._position_frames = 0.0

    def close(self):
        with self._lock:
            self._playing = False
            self._close_stream_locked()
            self._audio = None
            self._sample_rate = 0
            self._position_frames = 0.0

    def has_audio(self) -> bool:
        with self._lock:
            return self._audio is not None and self._audio.size > 0

    def is_playing(self) -> bool:
        with self._lock:
            return self._playing

    def set_speed(self, speed: float):
        with self._lock:
            self._speed = max(0.50, min(2.50, float(speed)))

    def set_pitch_semitones(self, semitones: float):
        with self._lock:
            self._pitch_semitones = max(-12.0, min(12.0, float(semitones)))

    def get_speed(self) -> float:
        with self._lock:
            return float(self._speed)

    def get_pitch_semitones(self) -> float:
        with self._lock:
            return float(self._pitch_semitones)

    def seek_seconds(self, seconds: float):
        with self._lock:
            if self._audio is None:
                return
            target = max(0.0, float(seconds)) * float(self._sample_rate)
            self._position_frames = max(0.0, min(self._last_frame_index_locked(), target))

    def get_duration_seconds(self) -> float:
        with self._lock:
            if self._audio is None or self._sample_rate <= 0:
                return 0.0
            return float(self._audio.shape[0]) / float(self._sample_rate)

    def get_position_seconds(self) -> float:
        with self._lock:
            if self._sample_rate <= 0:
                return 0.0
            return float(self._position_frames) / float(self._sample_rate)

    def _last_frame_index_locked(self) -> float:
        if self._audio is None or self._audio.shape[0] <= 1:
            return 0.0
        return float(self._audio.shape[0] - 1)

    def _playback_increment_locked(self) -> float:
        # Simple resampling approach: speed and pitch both affect step size.
        step = self._speed * (2.0 ** (self._pitch_semitones / 12.0))
        return max(0.05, min(5.0, float(step)))

    def _ensure_stream_locked(self):
        if self._stream is not None:
            return
        if self._audio is None or self._sample_rate <= 0:
            return
        channels = int(self._audio.shape[1])
        self._stream = sd.OutputStream(
            samplerate=self._sample_rate,
            channels=channels,
            dtype="float32",
            callback=self._stream_callback,
        )

    def _close_stream_locked(self):
        if self._stream is None:
            return
        try:
            if self._stream.active:
                self._stream.stop()
        finally:
            try:
                self._stream.close()
            finally:
                self._stream = None

    def _stream_callback(self, outdata, frames, _time_info, _status):
        with self._lock:
            audio = self._audio
            if audio is None or audio.size == 0 or not self._playing:
                outdata.fill(0)
                return

            increment = self._playback_increment_locked()
            start = self._position_frames
            indices = start + (increment * np.arange(frames, dtype=np.float64))
            max_index = self._last_frame_index_locked()
            valid_count = int(np.searchsorted(indices, max_index, side="left"))
            valid_count = max(0, min(frames, valid_count))

            if valid_count > 0:
                idx_valid = indices[:valid_count]
                base = np.floor(idx_valid).astype(np.int64)
                frac = (idx_valid - base).astype(np.float32)
                left = audio[base]
                right = audio[np.minimum(base + 1, audio.shape[0] - 1)]
                out = left + ((right - left) * frac[:, None])
                outdata[:valid_count, :] = out

            if valid_count < frames:
                outdata[valid_count:, :].fill(0)
                self._position_frames = max_index
                self._playing = False
                return

            self._position_frames = start + (increment * float(frames))
