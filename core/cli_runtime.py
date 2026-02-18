"""Headless CLI runtime wiring for ZestVoice."""

import argparse
import logging
import sys
import threading
import time
from collections.abc import Sequence

from core.app_config import AppConfig
from core.http_client import close_shared_client
from core.transcription_service import TranscriptionService
from core.tts_service import TTSService


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ZestVoice Headless Transcriber")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("listen", help="Start VAD listening mode")

    p_transcribe = sub.add_parser("transcribe", help="Transcribe an audio file")
    p_transcribe.add_argument("file", help="Path to audio file")

    p_tts = sub.add_parser("tts", help="Text-to-speech synthesis")
    p_tts.add_argument("text", help="Text to synthesize")
    p_tts.add_argument("-o", "--output", default="output.wav", help="Output audio file")
    return parser


def _configure_logging(level_name: str):
    logging.basicConfig(
        level=getattr(logging, str(level_name or "").upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def cmd_listen(config: AppConfig) -> int:
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
        return 0


def cmd_transcribe(config: AppConfig, file_path: str) -> int:
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
        return 1
    if "text" in result:
        print(result["text"])
        return 0
    print("[ERROR] Transcription timed out", file=sys.stderr)
    return 1


def cmd_tts(config: AppConfig, text: str, output_path: str) -> int:
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
        return 1
    if "audio" in result:
        with open(output_path, "wb") as f:
            f.write(result["audio"])
        print(f"Audio saved to {output_path}", file=sys.stderr)
        return 0
    print("[ERROR] TTS timed out", file=sys.stderr)
    return 1


def run_cli(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    _configure_logging(args.log_level)
    config = AppConfig.from_env()

    try:
        if args.command == "listen":
            return cmd_listen(config)
        if args.command == "transcribe":
            return cmd_transcribe(config, args.file)
        if args.command == "tts":
            return cmd_tts(config, args.text, args.output)
        parser.error(f"Unknown command: {args.command}")
        return 2
    finally:
        close_shared_client()

