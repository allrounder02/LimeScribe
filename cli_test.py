"""CLI smoke test: record from mic → transcribe via LemonFox → print result.

Run on Windows only (needs mic access):
    python cli_test.py

Press Enter to stop recording.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from core.audio_recorder import AudioRecorder
from core.lemonfox_client import LemonFoxClient


def main():
    client = LemonFoxClient()
    recorder = AudioRecorder()

    print("Recording... press Enter to stop.")
    recorder.start()
    input()
    wav_bytes = recorder.stop()

    if not wav_bytes:
        print("No audio captured.")
        return

    print(f"Captured {len(wav_bytes)} bytes. Sending to LemonFox API...")
    try:
        text = client.transcribe_bytes(wav_bytes)
        print(f"\nTranscription:\n{text}")
    except Exception as e:
        print(f"API error: {e}")


if __name__ == "__main__":
    main()
