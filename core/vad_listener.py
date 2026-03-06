import io
import time
import wave
import threading
import numpy as np
import sounddevice as sd
import webrtcvad

_VAD_DEFAULTS = {"pause": 1.5, "aggressiveness": 3, "min_speech": 0.5}
_ENERGY_FLOOR_BY_AGGR = {0: 90.0, 1: 130.0, 2: 185.0, 3: 250.0}
_NOISE_MULTIPLIER_BY_AGGR = {0: 1.20, 1: 1.35, 2: 1.50, 3: 1.70}
_TRIGGER_FRAMES_BY_AGGR = {0: 1, 1: 2, 2: 3, 3: 4}
_NOISE_ADAPT_ALPHA = 0.05
_HOLDOFF_NOISE_ADAPT_ALPHA = 0.25


SAMPLE_RATE = 16000  # webrtcvad requires 8000, 16000, or 32000
CHANNELS = 1
FRAME_DURATION_MS = 30  # 10, 20, or 30 ms per webrtcvad spec
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)  # samples per frame


class VADListener:
    """Continuous mic listener with voice activity detection.

    Detects speech, buffers it, and when a pause of `pause_threshold` seconds
    is detected, emits the buffered speech as WAV bytes via the callback.
    """

    def __init__(
        self,
        on_speech_chunk,
        on_speech_start=None,
        speech_start_min_frames=None,
        speech_start_rms_multiplier=1.0,
        pause_threshold=None,
        vad_aggressiveness=None,
        min_speech_seconds=None,
    ):
        """
        Args:
            on_speech_chunk: callable(wav_bytes: bytes) — called from a background
                thread when a speech chunk is ready for transcription.
            on_speech_start: callable() — called from a background thread as soon
                as speech is confidently detected with the stricter speech-start gate.
            speech_start_min_frames: minimum voiced frames before `on_speech_start`
                can fire. Defaults to the normal speech trigger frame count.
            speech_start_rms_multiplier: extra RMS multiple over the normal VAD
                energy gate required before `on_speech_start` fires.
            pause_threshold: seconds of silence after speech to trigger a chunk.
            vad_aggressiveness: 0-3 (0 = least aggressive, 3 = most aggressive filtering).
            min_speech_seconds: minimum detected voiced duration required before emit.
        """
        self.on_speech_chunk = on_speech_chunk
        self.on_speech_start = on_speech_start
        self.pause_threshold = pause_threshold if pause_threshold is not None else _VAD_DEFAULTS["pause"]
        vad_level = _VAD_DEFAULTS["aggressiveness"] if vad_aggressiveness is None else vad_aggressiveness
        min_seconds = _VAD_DEFAULTS["min_speech"] if min_speech_seconds is None else min_speech_seconds
        vad_level = max(0, min(3, int(vad_level)))
        min_seconds = max(0.0, float(min_seconds))
        self.vad = webrtcvad.Vad(vad_level)
        self._energy_floor = _ENERGY_FLOOR_BY_AGGR[vad_level]
        self._noise_multiplier = _NOISE_MULTIPLIER_BY_AGGR[vad_level]
        self._trigger_speech_frames = _TRIGGER_FRAMES_BY_AGGR[vad_level]
        self._speech_start_min_frames = max(
            self._trigger_speech_frames,
            int(speech_start_min_frames or self._trigger_speech_frames),
        )
        self._speech_start_rms_multiplier = max(1.0, float(speech_start_rms_multiplier or 1.0))

        self._stream = None
        self._running = False
        self._thread = None
        self._speech_holdoff_until = 0.0

        # Ring buffer for VAD frames
        self._frames_per_pause = int(self.pause_threshold * 1000 / FRAME_DURATION_MS)
        self._min_speech_frames = max(1, int(min_seconds * 1000 / FRAME_DURATION_MS))

    def start(self):
        """Start listening on the default mic."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop listening."""
        self._running = False
        thread = self._thread
        if not thread:
            return

        # stop() can be invoked from inside the listener callback thread.
        # Joining the current thread raises RuntimeError, so skip join here.
        if thread is threading.current_thread():
            return

        thread.join(timeout=3)
        if not thread.is_alive():
            self._thread = None

    def set_speech_detection_holdoff(self, seconds: float):
        holdoff_seconds = max(0.0, float(seconds or 0.0))
        if holdoff_seconds <= 0.0:
            return
        target = time.monotonic() + holdoff_seconds
        self._speech_holdoff_until = max(self._speech_holdoff_until, target)

    @staticmethod
    def _frame_rms(frame: np.ndarray) -> float:
        if frame.size == 0:
            return 0.0
        mono = frame[:, 0] if frame.ndim == 2 else frame
        samples = mono.astype(np.float32)
        return float(np.sqrt(np.mean(np.square(samples), dtype=np.float64)))

    def _energy_gate(self, noise_rms: float) -> float:
        return max(self._energy_floor, float(noise_rms) * self._noise_multiplier)

    def _is_speech_frame(self, pcm_bytes: bytes, frame_rms: float, noise_rms: float) -> bool:
        if frame_rms < self._energy_gate(noise_rms):
            return False
        return bool(self.vad.is_speech(pcm_bytes, SAMPLE_RATE))

    def _should_emit_speech_start(self, speech_frame_count: int, frame_rms: float, noise_rms: float) -> bool:
        if speech_frame_count < self._speech_start_min_frames:
            return False
        speech_start_gate = self._energy_gate(noise_rms) * self._speech_start_rms_multiplier
        return frame_rms >= speech_start_gate

    def _in_speech_detection_holdoff(self, now: float | None = None) -> bool:
        current = time.monotonic() if now is None else float(now)
        return current < self._speech_holdoff_until

    def _listen_loop(self):
        speech_frames = []
        speech_frame_count = 0
        silent_frame_count = 0
        in_speech = False
        speech_start_emitted = False
        candidate_frames = []
        candidate_speech_count = 0
        noise_rms = self._energy_floor / max(1.0, self._noise_multiplier)

        # Use a blocking stream read instead of callback for simplicity with VAD
        stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            blocksize=FRAME_SIZE,
        )
        stream.start()

        try:
            while self._running:
                data, overflowed = stream.read(FRAME_SIZE)
                pcm = data[:, 0].tobytes()
                frame_rms = self._frame_rms(data)
                now = time.monotonic()

                if self._in_speech_detection_holdoff(now):
                    speech_frames.clear()
                    speech_frame_count = 0
                    silent_frame_count = 0
                    in_speech = False
                    speech_start_emitted = False
                    candidate_frames.clear()
                    candidate_speech_count = 0
                    noise_rms = ((1.0 - _HOLDOFF_NOISE_ADAPT_ALPHA) * noise_rms) + (
                        _HOLDOFF_NOISE_ADAPT_ALPHA * frame_rms
                    )
                    continue

                is_speech = self._is_speech_frame(pcm, frame_rms=frame_rms, noise_rms=noise_rms)

                if is_speech:
                    silent_frame_count = 0
                    if not in_speech:
                        candidate_speech_count += 1
                        candidate_frames.append(data.copy())
                        if candidate_speech_count >= self._trigger_speech_frames:
                            in_speech = True
                            speech_frames.extend(candidate_frames)
                            speech_frame_count += candidate_speech_count
                            candidate_frames.clear()
                            candidate_speech_count = 0
                            if (
                                self.on_speech_start
                                and not speech_start_emitted
                                and self._should_emit_speech_start(
                                    speech_frame_count=speech_frame_count,
                                    frame_rms=frame_rms,
                                    noise_rms=noise_rms,
                                )
                            ):
                                self.on_speech_start()
                                speech_start_emitted = True
                    else:
                        speech_frame_count += 1
                        speech_frames.append(data.copy())
                        if (
                            self.on_speech_start
                            and not speech_start_emitted
                            and self._should_emit_speech_start(
                                speech_frame_count=speech_frame_count,
                                frame_rms=frame_rms,
                                noise_rms=noise_rms,
                            )
                        ):
                            self.on_speech_start()
                            speech_start_emitted = True
                else:
                    if in_speech:
                        # Still buffering during short silence within speech
                        silent_frame_count += 1
                        speech_frames.append(data.copy())

                        if silent_frame_count >= self._frames_per_pause:
                            # Pause detected — emit the chunk
                            wav_bytes = self._to_wav(speech_frames) if speech_frame_count >= self._min_speech_frames else b""
                            speech_frames.clear()
                            speech_frame_count = 0
                            in_speech = False
                            speech_start_emitted = False
                            silent_frame_count = 0
                            if wav_bytes:
                                self.on_speech_chunk(wav_bytes)
                    else:
                        candidate_frames.clear()
                        candidate_speech_count = 0
                        noise_rms = ((1.0 - _NOISE_ADAPT_ALPHA) * noise_rms) + (_NOISE_ADAPT_ALPHA * frame_rms)
        finally:
            stream.stop()
            stream.close()

            # Flush any remaining speech
            if speech_frames:
                wav_bytes = self._to_wav(speech_frames) if speech_frame_count >= self._min_speech_frames else b""
                if wav_bytes:
                    self.on_speech_chunk(wav_bytes)

    @staticmethod
    def _to_wav(frames: list[np.ndarray]) -> bytes:
        if not frames:
            return b""
        audio = np.concatenate(frames, axis=0)
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio.tobytes())
        return buf.getvalue()
