"""Application configuration as an injectable dataclass."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class AppConfig:
    """Application configuration loaded from environment variables."""

    # API
    api_key: str = ""
    api_url: str = "https://api.lemonfox.ai/v1/audio/transcriptions"
    api_fallback_url: str = "https://transcribe.whisperapi.com"

    # STT
    stt_language: str = "english"
    stt_response_format: str = "json"

    # TTS
    tts_url: str = "https://api.lemonfox.ai/v1/audio/speech"
    tts_fallback_url: str = ""
    tts_model: str = "tts-1"
    tts_voice: str = "heart"
    tts_language: str = "en-us"
    tts_response_format: str = "wav"
    tts_speed: float = 1.0

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
        return AppConfig(
            api_key=os.getenv("LEMONFOX_API_KEY", ""),
            api_url=os.getenv("LEMONFOX_API_URL", "https://api.lemonfox.ai/v1/audio/transcriptions"),
            api_fallback_url=os.getenv("LEMONFOX_API_FALLBACK_URL", "https://transcribe.whisperapi.com"),
            stt_language=os.getenv("LEMONFOX_LANGUAGE", "english"),
            stt_response_format=os.getenv("LEMONFOX_RESPONSE_FORMAT", "json"),
            tts_url=os.getenv("LEMONFOX_TTS_URL", "https://api.lemonfox.ai/v1/audio/speech"),
            tts_fallback_url=os.getenv("LEMONFOX_TTS_FALLBACK_URL", ""),
            tts_model=os.getenv("LEMONFOX_TTS_MODEL", "tts-1"),
            tts_voice=os.getenv("LEMONFOX_TTS_VOICE", "heart"),
            tts_language=os.getenv("LEMONFOX_TTS_LANGUAGE", "en-us"),
            tts_response_format=os.getenv("LEMONFOX_TTS_RESPONSE_FORMAT", "wav"),
            tts_speed=float(os.getenv("LEMONFOX_TTS_SPEED", "1.0")),
            vad_pause_threshold=float(os.getenv("VAD_PAUSE_THRESHOLD", "1.5")),
            vad_aggressiveness=int(os.getenv("VAD_AGGRESSIVENESS", "3")),
            vad_min_speech_seconds=float(os.getenv("VAD_MIN_SPEECH_SECONDS", "0.5")),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            log_file=os.getenv("LOG_FILE", "").strip(),
        )
