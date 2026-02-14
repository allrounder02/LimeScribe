#!/usr/bin/env python3
"""Headless LimeScribe — no GUI required.

Usage:
    python cli.py listen                     # VAD listening, prints to stdout
    python cli.py transcribe <file>          # Transcribe audio file
    python cli.py tts <text> -o output.wav   # Text-to-speech
"""

import sys
import os
import time
import logging
import argparse
import threading

sys.path.insert(0, os.path.dirname(__file__))

from core.app_config import AppConfig
from core.transcription_service import TranscriptionService
from core.tts_service import TTSService
from core.http_client import close_shared_client


def cmd_listen(config: AppConfig):
    """VAD listening mode — prints transcriptions to stdout."""
    def on_text(text: str):
        print(text)
        sys.stdout.flush()

    def on_error(error: str):
        print(f"[ERROR] {error}", file=sys.stderr)

    service = TranscriptionService(config, on_transcription=on_text, on_error=on_error)
    service.start_listening()

    print("[INFO] Listening... Press Ctrl+C to stop.", file=sys.stderr)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Stopping...", file=sys.stderr)
        service.stop_listening()


def cmd_transcribe(config: AppConfig, file_path: str):
    """Transcribe an audio file."""
    done = threading.Event()
    result = {}

    def on_text(text: str):
        result["text"] = text
        done.set()

    def on_error(error: str):
        result["error"] = error
        done.set()

    service = TranscriptionService(config, on_transcription=on_text, on_error=on_error)
    service.transcribe_file(file_path)
    done.wait(timeout=120)

    if "error" in result:
        print(f"[ERROR] {result['error']}", file=sys.stderr)
        sys.exit(1)
    elif "text" in result:
        print(result["text"])
    else:
        print("[ERROR] Transcription timed out", file=sys.stderr)
        sys.exit(1)


def cmd_tts(config: AppConfig, text: str, output_path: str):
    """Text-to-speech — save audio to file."""
    done = threading.Event()
    result = {}

    def on_audio(audio_bytes: bytes):
        result["audio"] = audio_bytes
        done.set()

    def on_error(error: str):
        result["error"] = error
        done.set()

    service = TTSService(config, on_audio_ready=on_audio, on_error=on_error)
    service.synthesize(text)
    done.wait(timeout=120)

    if "error" in result:
        print(f"[ERROR] {result['error']}", file=sys.stderr)
        sys.exit(1)
    elif "audio" in result:
        with open(output_path, "wb") as f:
            f.write(result["audio"])
        print(f"Audio saved to {output_path}", file=sys.stderr)
    else:
        print("[ERROR] TTS timed out", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="LimeScribe Headless Transcriber")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("listen", help="Start VAD listening mode")

    p_transcribe = sub.add_parser("transcribe", help="Transcribe an audio file")
    p_transcribe.add_argument("file", help="Path to audio file")

    p_tts = sub.add_parser("tts", help="Text-to-speech synthesis")
    p_tts.add_argument("text", help="Text to synthesize")
    p_tts.add_argument("-o", "--output", default="output.wav", help="Output audio file")

    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

    config = AppConfig.from_env()

    try:
        if args.command == "listen":
            cmd_listen(config)
        elif args.command == "transcribe":
            cmd_transcribe(config, args.file)
        elif args.command == "tts":
            cmd_tts(config, args.text, args.output)
    finally:
        close_shared_client()


if __name__ == "__main__":
    main()
