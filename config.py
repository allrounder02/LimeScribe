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

_SETTINGS_PATH = Path(__file__).with_name("settings.json")
DEFAULT_SETTINGS = {
    "hotkey_listen": DEFAULT_HOTKEY_LISTEN,
    "hotkey_record": DEFAULT_HOTKEY_RECORD,
}


def load_app_settings() -> dict:
    settings = DEFAULT_SETTINGS.copy()
    if not _SETTINGS_PATH.exists():
        return settings
    try:
        loaded = json.loads(_SETTINGS_PATH.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            for key in DEFAULT_SETTINGS:
                value = loaded.get(key)
                if isinstance(value, str) and value.strip():
                    settings[key] = value.strip()
    except (json.JSONDecodeError, OSError):
        pass
    return settings


def save_app_settings(settings: dict):
    payload = DEFAULT_SETTINGS.copy()
    for key in DEFAULT_SETTINGS:
        value = settings.get(key)
        if isinstance(value, str) and value.strip():
            payload[key] = value.strip()
    _SETTINGS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
