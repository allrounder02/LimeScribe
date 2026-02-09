import io
import wave
import threading
import collections
import numpy as np
import sounddevice as sd
import webrtcvad

from config import VAD_PAUSE_THRESHOLD


SAMPLE_RATE = 16000  # webrtcvad requires 8000, 16000, or 32000
CHANNELS = 1
FRAME_DURATION_MS = 30  # 10, 20, or 30 ms per webrtcvad spec
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)  # samples per frame


class VADListener:
    """Continuous mic listener with voice activity detection.

    Detects speech, buffers it, and when a pause of `pause_threshold` seconds
    is detected, emits the buffered speech as WAV bytes via the callback.
    """

    def __init__(self, on_speech_chunk, pause_threshold=None, vad_aggressiveness=2):
        """
        Args:
            on_speech_chunk: callable(wav_bytes: bytes) — called from a background
                thread when a speech chunk is ready for transcription.
            pause_threshold: seconds of silence after speech to trigger a chunk.
            vad_aggressiveness: 0-3 (0 = least aggressive, 3 = most aggressive filtering).
        """
        self.on_speech_chunk = on_speech_chunk
        self.pause_threshold = pause_threshold or VAD_PAUSE_THRESHOLD
        self.vad = webrtcvad.Vad(vad_aggressiveness)

        self._stream = None
        self._running = False
        self._thread = None

        # Ring buffer for VAD frames
        self._frames_per_pause = int(self.pause_threshold * 1000 / FRAME_DURATION_MS)

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
        if self._thread:
            self._thread.join(timeout=3)
            self._thread = None

    def _listen_loop(self):
        speech_frames = []
        silent_frame_count = 0
        in_speech = False

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

                is_speech = self.vad.is_speech(pcm, SAMPLE_RATE)

                if is_speech:
                    in_speech = True
                    silent_frame_count = 0
                    speech_frames.append(data.copy())
                elif in_speech:
                    # Still buffering during short silence within speech
                    silent_frame_count += 1
                    speech_frames.append(data.copy())

                    if silent_frame_count >= self._frames_per_pause:
                        # Pause detected — emit the chunk
                        wav_bytes = self._to_wav(speech_frames)
                        speech_frames.clear()
                        in_speech = False
                        silent_frame_count = 0
                        if wav_bytes:
                            self.on_speech_chunk(wav_bytes)
        finally:
            stream.stop()
            stream.close()

            # Flush any remaining speech
            if speech_frames:
                wav_bytes = self._to_wav(speech_frames)
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
