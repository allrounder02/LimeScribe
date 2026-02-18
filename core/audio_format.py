"""Helpers for lightweight audio format detection from raw bytes."""

from __future__ import annotations


def detect_audio_format(audio_bytes: bytes) -> str:
    """Return best-effort format label from container/file signatures."""
    if not audio_bytes:
        return "unknown"

    head = bytes(audio_bytes[:16])

    # RIFF/WAVE
    if len(head) >= 12 and head[:4] == b"RIFF" and head[8:12] == b"WAVE":
        return "wav"
    # FLAC
    if head.startswith(b"fLaC"):
        return "flac"
    # OGG / Opus-in-Ogg / Vorbis-in-Ogg
    if head.startswith(b"OggS"):
        return "ogg"
    # MP3 with ID3 tag
    if head.startswith(b"ID3"):
        return "mp3"
    # MP3 frame sync (common fallback)
    if len(head) >= 2 and head[0] == 0xFF and (head[1] & 0xE0) == 0xE0:
        return "mp3"

    return "unknown"
