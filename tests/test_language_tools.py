"""Tests for shared English/German language helpers."""

from language_tools import (
    AUTO_LANGUAGE,
    detect_english_or_german,
    normalize_stt_language,
    normalize_tts_language,
    resolve_tts_language,
)


def test_detects_german_text_from_umlauts_and_common_words():
    text = "Guten Morgen, wie geht es dir? Ich möchte heute auf Deutsch sprechen."
    assert detect_english_or_german(text) == "de"


def test_detects_english_text_from_common_words():
    text = "Hello, how are you today? I would like to test the speech output."
    assert detect_english_or_german(text) == "en"


def test_normalizes_auto_and_language_aliases():
    assert normalize_stt_language("AUTO") == AUTO_LANGUAGE
    assert normalize_stt_language("de") == "german"
    assert normalize_tts_language("English") == "en-us"
    assert normalize_tts_language("Deutsch") == "de"


def test_resolve_tts_language_auto_routes_between_english_and_german():
    assert resolve_tts_language("auto", "Please read this sentence aloud.") == "en-us"
    assert resolve_tts_language("auto", "Bitte lies diesen Satz laut vor.") == "de"
