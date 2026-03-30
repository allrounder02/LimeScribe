"""Application configuration as an injectable dataclass."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from language_tools import normalize_stt_language, normalize_tts_language


def _getenv(*names: str, default: str = "") -> str:
    for name in names:
        if name in os.environ:
            return os.environ[name]
    return default


def _openai_mode_enabled() -> bool:
    return bool(str(os.environ.get("OPENAI_API_KEY", "")).strip())


@dataclass
class AppConfig:
    """Application configuration loaded from environment variables."""

    # API
    api_key: str = ""
    api_url: str = "https://api.openai.com/v1/audio/transcriptions"
    api_fallback_url: str = ""

    # STT
    stt_model: str = "gpt-4o-mini-transcribe"
    stt_language: str = "english"
    stt_response_format: str = "json"

    # TTS
    tts_url: str = "https://api.openai.com/v1/audio/speech"
    tts_fallback_url: str = ""
    tts_model: str = "gpt-4o-mini-tts"
    tts_voice: str = "coral"
    tts_language: str = "en-us"
    tts_response_format: str = "wav"
    tts_speed: float = 1.0
    tts_instructions: str = ""

    # Dialogue (OpenAI-compatible chat)
    chat_url: str = "https://api.openai.com/v1/chat/completions"
    chat_fallback_url: str = ""
    chat_model: str = "gpt-4o-mini"
    chat_system_prompt: str = "You are a helpful assistant."

    # VAD
    vad_pause_threshold: float = 1.5
    vad_aggressiveness: int = 3
    vad_min_speech_seconds: float = 0.5

    # Logging
    log_level: str = "INFO"
    log_file: str = ""

    @staticmethod
    def from_env() -> "AppConfig":
        """Load config from .env file and environment variables."""
        load_dotenv()
        if _openai_mode_enabled():
            api_url = _getenv("OPENAI_STT_URL", default="https://api.openai.com/v1/audio/transcriptions")
            api_fallback_url = _getenv("OPENAI_STT_FALLBACK_URL", default="")
            stt_model = _getenv("OPENAI_STT_MODEL", default="gpt-4o-mini-transcribe")
            stt_language = normalize_stt_language(_getenv("OPENAI_STT_LANGUAGE", default="english"))
            stt_response_format = _getenv("OPENAI_STT_RESPONSE_FORMAT", default="json")
            tts_url = _getenv("OPENAI_TTS_URL", default="https://api.openai.com/v1/audio/speech")
            tts_fallback_url = _getenv("OPENAI_TTS_FALLBACK_URL", default="")
            tts_model = _getenv("OPENAI_TTS_MODEL", default="gpt-4o-mini-tts")
            tts_voice = _getenv("OPENAI_TTS_VOICE", default="coral")
            tts_language = normalize_tts_language(_getenv("OPENAI_TTS_LANGUAGE", default="en-us"))
            tts_response_format = _getenv("OPENAI_TTS_RESPONSE_FORMAT", default="wav")
            tts_speed = float(_getenv("OPENAI_TTS_SPEED", default="1.0"))
            chat_url = _getenv("OPENAI_CHAT_URL", default="https://api.openai.com/v1/chat/completions")
            chat_fallback_url = _getenv("OPENAI_CHAT_FALLBACK_URL", default="")
            chat_model = _getenv("OPENAI_CHAT_MODEL", default="gpt-4o-mini")
            chat_system_prompt = _getenv(
                "OPENAI_CHAT_SYSTEM_PROMPT",
                default="You are a helpful assistant.",
            )
        else:
            api_url = _getenv("LEMONFOX_API_URL", default="https://api.openai.com/v1/audio/transcriptions")
            api_fallback_url = _getenv("LEMONFOX_API_FALLBACK_URL", default="")
            stt_model = _getenv("LEMONFOX_STT_MODEL", default="gpt-4o-mini-transcribe")
            stt_language = normalize_stt_language(_getenv("LEMONFOX_LANGUAGE", default="english"))
            stt_response_format = _getenv("LEMONFOX_RESPONSE_FORMAT", default="json")
            tts_url = _getenv("LEMONFOX_TTS_URL", default="https://api.openai.com/v1/audio/speech")
            tts_fallback_url = _getenv("LEMONFOX_TTS_FALLBACK_URL", default="")
            tts_model = _getenv("LEMONFOX_TTS_MODEL", default="gpt-4o-mini-tts")
            tts_voice = _getenv("LEMONFOX_TTS_VOICE", default="coral")
            tts_language = normalize_tts_language(_getenv("LEMONFOX_TTS_LANGUAGE", default="en-us"))
            tts_response_format = _getenv("LEMONFOX_TTS_RESPONSE_FORMAT", default="wav")
            tts_speed = float(_getenv("LEMONFOX_TTS_SPEED", default="1.0"))
            chat_url = _getenv("LEMONFOX_CHAT_URL", default="https://api.openai.com/v1/chat/completions")
            chat_fallback_url = _getenv("LEMONFOX_CHAT_FALLBACK_URL", default="")
            chat_model = _getenv("LEMONFOX_CHAT_MODEL", default="gpt-4o-mini")
            chat_system_prompt = _getenv(
                "LEMONFOX_CHAT_SYSTEM_PROMPT",
                default="You are a helpful assistant.",
            )
        return AppConfig(
            api_key=_getenv("OPENAI_API_KEY", "LEMONFOX_API_KEY", default=""),
            api_url=api_url,
            api_fallback_url=api_fallback_url,
            stt_model=stt_model,
            stt_language=stt_language,
            stt_response_format=stt_response_format,
            tts_url=tts_url,
            tts_fallback_url=tts_fallback_url,
            tts_model=tts_model,
            tts_voice=tts_voice,
            tts_language=tts_language,
            tts_response_format=tts_response_format,
            tts_speed=tts_speed,
            tts_instructions=_getenv("OPENAI_TTS_INSTRUCTIONS", default=""),
            chat_url=chat_url,
            chat_fallback_url=chat_fallback_url,
            chat_model=chat_model,
            chat_system_prompt=chat_system_prompt,
            vad_pause_threshold=float(os.getenv("VAD_PAUSE_THRESHOLD", "1.5")),
            vad_aggressiveness=int(os.getenv("VAD_AGGRESSIVENESS", "3")),
            vad_min_speech_seconds=float(os.getenv("VAD_MIN_SPEECH_SECONDS", "0.5")),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            log_file=os.getenv("LOG_FILE", "").strip(),
        )
