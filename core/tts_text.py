"""Text cleanup utilities to improve sentence structure before TTS."""

from __future__ import annotations

import re

SENTENCE_PUNCT_RE = re.compile(r"[.!?;:]")
WHITESPACE_RE = re.compile(r"[ \t]+")
PARAGRAPH_SPLIT_RE = re.compile(r"\n{2,}")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def normalize_tts_text(text: str) -> str:
    """Normalize text and add basic sentence boundaries when missing."""
    value = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    value = value.replace("…", "...").replace("—", " - ").replace("–", " - ")
    value = WHITESPACE_RE.sub(" ", value)
    value = re.sub(r" *\n *", "\n", value).strip()
    if not value:
        return ""

    paragraphs = [p.strip() for p in PARAGRAPH_SPLIT_RE.split(value) if p.strip()]
    normalized = [_normalize_paragraph(paragraph) for paragraph in paragraphs]
    return "\n\n".join(part for part in normalized if part).strip()


def split_tts_chunks(text: str, max_chars: int = 1200) -> list[str]:
    """Split text into sentence-aware chunks for multi-request synthesis."""
    value = (text or "").strip()
    if not value:
        return []
    if len(value) <= max_chars:
        return [value]

    pieces = _sentence_pieces(value)
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for piece in pieces:
        segment = piece.strip()
        if not segment:
            continue
        if len(segment) > max_chars:
            for sub in _split_long_segment(segment, max_chars):
                if current:
                    chunks.append(" ".join(current).strip())
                    current = []
                    current_len = 0
                chunks.append(sub)
            continue

        additional = len(segment) if not current else len(segment) + 1
        if current and current_len + additional > max_chars:
            chunks.append(" ".join(current).strip())
            current = [segment]
            current_len = len(segment)
            continue
        current.append(segment)
        current_len += additional

    if current:
        chunks.append(" ".join(current).strip())

    return [chunk for chunk in chunks if chunk]


def _normalize_paragraph(paragraph: str) -> str:
    text = WHITESPACE_RE.sub(" ", paragraph).strip()
    if not text:
        return ""

    words = text.split()
    punct_count = len(SENTENCE_PUNCT_RE.findall(text))
    if punct_count == 0 and len(words) >= 18:
        return _inject_periods(words, target_words=18)
    if punct_count <= 1 and len(words) >= 30:
        return _inject_periods(words, target_words=18)

    if text[-1] not in ".!?":
        text = f"{text}."
    return text


def _inject_periods(words: list[str], target_words: int) -> str:
    segments: list[str] = []
    buffer: list[str] = []
    for word in words:
        buffer.append(word)
        if len(buffer) >= target_words:
            piece = " ".join(buffer).strip()
            if piece and piece[-1] not in ".!?":
                piece += "."
            segments.append(piece)
            buffer = []

    if buffer:
        piece = " ".join(buffer).strip()
        if piece and piece[-1] not in ".!?":
            piece += "."
        segments.append(piece)

    return " ".join(segment for segment in segments if segment)


def _sentence_pieces(value: str) -> list[str]:
    sentence_like = [part.strip() for part in SENTENCE_SPLIT_RE.split(value) if part.strip()]
    if len(sentence_like) == 1:
        # No reliable punctuation boundaries found.
        return _split_long_segment(sentence_like[0], 320)
    return sentence_like


def _split_long_segment(segment: str, max_chars: int) -> list[str]:
    words = segment.split()
    if not words:
        return []

    parts: list[str] = []
    current: list[str] = []
    current_len = 0

    for word in words:
        if not current:
            current = [word]
            current_len = len(word)
            continue
        addition = len(word) + 1
        if current_len + addition > max_chars:
            part = " ".join(current).strip()
            if part and part[-1] not in ".!?":
                part += "."
            parts.append(part)
            current = [word]
            current_len = len(word)
            continue
        current.append(word)
        current_len += addition

    if current:
        part = " ".join(current).strip()
        if part and part[-1] not in ".!?":
            part += "."
        parts.append(part)

    return [part for part in parts if part]
