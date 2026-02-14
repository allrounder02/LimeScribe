import os
import json
from pathlib import Path
from dotenv import load_dotenv
from hotkeys import DEFAULT_HOTKEY_LISTEN, DEFAULT_HOTKEY_RECORD

load_dotenv()

LEMONFOX_API_KEY = os.getenv("LEMONFOX_API_KEY", "")
LEMONFOX_LANGUAGE = os.getenv("LEMONFOX_LANGUAGE", "english")
LEMONFOX_RESPONSE_FORMAT = os.getenv("LEMONFOX_RESPONSE_FORMAT", "json")
VAD_PAUSE_THRESHOLD = float(os.getenv("VAD_PAUSE_THRESHOLD", "1.5"))
VAD_AGGRESSIVENESS = int(os.getenv("VAD_AGGRESSIVENESS", "3"))
VAD_MIN_SPEECH_SECONDS = float(os.getenv("VAD_MIN_SPEECH_SECONDS", "0.5"))
LEMONFOX_API_URL = os.getenv(
    "LEMONFOX_API_URL",
    "https://api.lemonfox.ai/v1/audio/transcriptions",
)
LEMONFOX_API_FALLBACK_URL = os.getenv(
    "LEMONFOX_API_FALLBACK_URL",
    "https://transcribe.whisperapi.com",
)
LEMONFOX_TTS_URL = os.getenv(
    "LEMONFOX_TTS_URL",
    "https://api.lemonfox.ai/v1/audio/speech",
)
LEMONFOX_TTS_FALLBACK_URL = os.getenv(
    "LEMONFOX_TTS_FALLBACK_URL",
    "",
)
LEMONFOX_TTS_MODEL = os.getenv("LEMONFOX_TTS_MODEL", "tts-1")
LEMONFOX_TTS_VOICE = os.getenv("LEMONFOX_TTS_VOICE", "heart")
LEMONFOX_TTS_LANGUAGE = os.getenv("LEMONFOX_TTS_LANGUAGE", "en-us")
LEMONFOX_TTS_RESPONSE_FORMAT = os.getenv("LEMONFOX_TTS_RESPONSE_FORMAT", "wav")
LEMONFOX_TTS_SPEED = float(os.getenv("LEMONFOX_TTS_SPEED", "1.0"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("LOG_FILE", "").strip()

_SETTINGS_PATH = Path(__file__).with_name("settings.json")
DEFAULT_SETTINGS = {
    "hotkey_listen": DEFAULT_HOTKEY_LISTEN,
    "hotkey_record": DEFAULT_HOTKEY_RECORD,
    "stt_language": LEMONFOX_LANGUAGE,
    "stt_response_format": LEMONFOX_RESPONSE_FORMAT,
    "auto_copy_transcription": True,
    "tts_model": LEMONFOX_TTS_MODEL,
    "tts_voice": LEMONFOX_TTS_VOICE,
    "tts_language": LEMONFOX_TTS_LANGUAGE,
    "tts_response_format": LEMONFOX_TTS_RESPONSE_FORMAT,
    "tts_speed": str(LEMONFOX_TTS_SPEED),
    "ui_splitter_sizes": "560,340",
    "active_profile": "Default",
    "profiles": [
        {
            "name": "Default",
            "stt_language": LEMONFOX_LANGUAGE,
            "stt_response_format": LEMONFOX_RESPONSE_FORMAT,
            "tts_model": LEMONFOX_TTS_MODEL,
            "tts_voice": LEMONFOX_TTS_VOICE,
            "tts_language": LEMONFOX_TTS_LANGUAGE,
            "tts_response_format": LEMONFOX_TTS_RESPONSE_FORMAT,
            "tts_speed": str(LEMONFOX_TTS_SPEED),
        }
    ],
}


def load_app_settings() -> dict:
    settings = DEFAULT_SETTINGS.copy()
    settings["profiles"] = [dict(p) for p in DEFAULT_SETTINGS["profiles"]]
    if not _SETTINGS_PATH.exists():
        return settings
    try:
        loaded = json.loads(_SETTINGS_PATH.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            for key in DEFAULT_SETTINGS:
                value = loaded.get(key)
                if key == "profiles" and isinstance(value, list):
                    profiles = []
                    for item in value:
                        if isinstance(item, dict) and isinstance(item.get("name"), str) and item["name"].strip():
                            profiles.append(
                                {
                                    "name": item["name"].strip(),
                                    "stt_language": str(item.get("stt_language", settings["stt_language"])).strip(),
                                    "stt_response_format": str(
                                        item.get("stt_response_format", settings["stt_response_format"])
                                    ).strip(),
                                    "tts_model": str(item.get("tts_model", settings["tts_model"])).strip(),
                                    "tts_voice": str(item.get("tts_voice", settings["tts_voice"])).strip(),
                                    "tts_language": str(item.get("tts_language", settings["tts_language"])).strip(),
                                    "tts_response_format": str(
                                        item.get("tts_response_format", settings["tts_response_format"])
                                    ).strip(),
                                    "tts_speed": str(item.get("tts_speed", settings["tts_speed"])).strip(),
                                }
                            )
                    if profiles:
                        settings["profiles"] = profiles
                elif isinstance(DEFAULT_SETTINGS.get(key), bool) and isinstance(value, bool):
                    settings[key] = value
                elif isinstance(value, str) and value.strip():
                    settings[key] = value.strip()
    except (json.JSONDecodeError, OSError):
        pass
    if settings["active_profile"] not in [p["name"] for p in settings["profiles"]]:
        settings["active_profile"] = settings["profiles"][0]["name"]
    return settings


def save_app_settings(settings: dict):
    payload = load_app_settings()
    for key in DEFAULT_SETTINGS:
        value = settings.get(key)
        if key == "profiles" and isinstance(value, list) and value:
            payload[key] = value
        elif isinstance(DEFAULT_SETTINGS.get(key), bool) and isinstance(value, bool):
            payload[key] = value
        elif isinstance(value, str) and value.strip():
            payload[key] = value.strip()
    _SETTINGS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
