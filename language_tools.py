"""Shared language helpers for STT/TTS settings and request shaping."""

from __future__ import annotations

import re

AUTO_LANGUAGE = "auto"

_AUTO_ALIASES = {"auto", "automatic", "detect", "autodetect", "auto-detect"}
_ENGLISH_ALIASES = {"en", "en-us", "en-gb", "english"}
_GERMAN_ALIASES = {"de", "de-de", "german", "deutsch"}
_WORD_RE = re.compile(r"[A-Za-zÄÖÜäöüß']+")
_GERMAN_HINTS = {
    "aber",
    "auch",
    "bitte",
    "danke",
    "das",
    "dass",
    "dein",
    "deine",
    "dem",
    "den",
    "der",
    "die",
    "du",
    "ein",
    "eine",
    "es",
    "für",
    "guten",
    "hallo",
    "hast",
    "habe",
    "haben",
    "heute",
    "ich",
    "ist",
    "jetzt",
    "kann",
    "mit",
    "nicht",
    "noch",
    "oder",
    "schon",
    "sie",
    "und",
    "wie",
    "wir",
    "zu",
}
_ENGLISH_HINTS = {
    "a",
    "an",
    "and",
    "are",
    "can",
    "for",
    "good",
    "hello",
    "hi",
    "how",
    "i",
    "in",
    "is",
    "it",
    "my",
    "now",
    "of",
    "on",
    "please",
    "thanks",
    "thank",
    "that",
    "the",
    "this",
    "to",
    "today",
    "we",
    "with",
    "would",
    "you",
    "your",
}


def is_auto_language(value: str | None) -> bool:
    candidate = str(value or "").strip().lower()
    return candidate in _AUTO_ALIASES


def normalize_stt_language(value: str | None, default: str = "english") -> str:
    candidate = str(value or "").strip().lower()
    if not candidate:
        return default
    if candidate in _AUTO_ALIASES:
        return AUTO_LANGUAGE
    if candidate in _ENGLISH_ALIASES:
        return "english"
    if candidate in _GERMAN_ALIASES:
        return "german"
    return candidate


def normalize_tts_language(value: str | None, default: str = "en-us") -> str:
    candidate = str(value or "").strip().lower()
    if not candidate:
        return default
    if candidate in _AUTO_ALIASES:
        return AUTO_LANGUAGE
    if candidate == "english" or candidate == "en":
        return "en-us"
    if candidate in {"german", "deutsch"}:
        return "de"
    return candidate


def map_openai_stt_language(value: str | None) -> str:
    normalized = normalize_stt_language(value, default="")
    if not normalized or normalized == AUTO_LANGUAGE:
        return ""
    return {
        "english": "en",
        "german": "de",
        "spanish": "es",
        "italian": "it",
        "french": "fr",
        "portuguese": "pt",
        "japanese": "ja",
        "chinese": "zh",
        "hindi": "hi",
    }.get(normalized, normalized)


def detect_english_or_german(text: str, default: str = "en") -> str:
    body = str(text or "").strip()
    if not body:
        return default

    tokens = [token.lower() for token in _WORD_RE.findall(body)]
    if not tokens:
        return default

    joined = " ".join(tokens)
    german_score = 0.0
    english_score = 0.0

    if any(ch in joined for ch in "äöüß"):
        german_score += 4.0
    if re.search(r"\b(i'm|you're|we're|don't|can't|it's|that's|i'll|we'll)\b", joined):
        english_score += 3.0
    if re.search(r"\b(ich|nicht|danke|bitte|guten|möchte|könnte|über)\b", joined):
        german_score += 3.0

    for token in tokens:
        if token in _GERMAN_HINTS:
            german_score += 1.0
        if token in _ENGLISH_HINTS:
            english_score += 1.0

    for fragment in ("sch", "ch", "ei", "ie", "ung"):
        if fragment in joined:
            german_score += 0.25
    for fragment in ("th", "ing", "tion", "ough", "wh"):
        if fragment in joined:
            english_score += 0.25

    if german_score > english_score:
        return "de"
    return "en"


def resolve_tts_language(value: str | None, text: str, default: str = "en-us") -> str:
    normalized = normalize_tts_language(value, default=default)
    if normalized != AUTO_LANGUAGE:
        return normalized
    detected = detect_english_or_german(text, default="en")
    return "de" if detected == "de" else "en-us"


def tts_language_label(value: str | None) -> str:
    normalized = normalize_tts_language(value, default="")
    if normalized == "de":
        return "German"
    if normalized.startswith("en"):
        return "English"
    return (normalized or "Speech").upper()


def build_tts_language_instruction(resolved_language: str, base_instructions: str | None = None) -> str:
    hint = f"Speak naturally in {tts_language_label(resolved_language)}."
    base = str(base_instructions or "").strip()
    if not base:
        return hint
    lowered = base.lower()
    if hint.lower() in lowered:
        return base
    return f"{hint} {base}"
