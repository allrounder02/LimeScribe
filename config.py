import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Hotkey defaults defined here to avoid circular import with hotkeys.py
DEFAULT_HOTKEY_LISTEN = "Ctrl+Alt+L"
DEFAULT_HOTKEY_RECORD = "Ctrl+Alt+R"

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
LEMONFOX_CHAT_URL = os.getenv(
    "LEMONFOX_CHAT_URL",
    "https://api.lemonfox.ai/v1/chat/completions",
)
LEMONFOX_CHAT_FALLBACK_URL = os.getenv(
    "LEMONFOX_CHAT_FALLBACK_URL",
    "",
)
LEMONFOX_CHAT_MODEL = os.getenv("LEMONFOX_CHAT_MODEL", "llama-8b-chat")
LEMONFOX_CHAT_SYSTEM_PROMPT = os.getenv("LEMONFOX_CHAT_SYSTEM_PROMPT", "You are a helpful assistant.")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("LOG_FILE", "").strip()

_SETTINGS_PATH = Path(__file__).with_name("settings.json")


def _estimate_vad_noise_level(vad_aggressiveness: int, vad_min_speech_seconds: float) -> int:
    aggr_ratio = max(0.0, min(1.0, float(vad_aggressiveness) / 3.0))
    min_ratio = (float(vad_min_speech_seconds) - 0.30) / (1.20 - 0.30)
    min_ratio = max(0.0, min(1.0, min_ratio))
    return int(round(((aggr_ratio * 0.7) + (min_ratio * 0.3)) * 100))


_DEFAULT_VAD_NOISE_LEVEL = _estimate_vad_noise_level(VAD_AGGRESSIVENESS, VAD_MIN_SPEECH_SECONDS)
_DEFAULT_TTS_PROFILE_NAME = "Default Voice"
_OUTPUT_HISTORY_LIMIT = 3

DEFAULT_SETTINGS = {
    "hotkey_listen": DEFAULT_HOTKEY_LISTEN,
    "hotkey_record": DEFAULT_HOTKEY_RECORD,
    "stt_language": LEMONFOX_LANGUAGE,
    "stt_response_format": LEMONFOX_RESPONSE_FORMAT,
    "auto_copy_transcription": True,
    "clear_output_after_copy": False,
    "stop_listening_after_copy": False,
    "keep_wrapping_parentheses": False,
    "vad_noise_level": _DEFAULT_VAD_NOISE_LEVEL,
    "vad_aggressiveness": VAD_AGGRESSIVENESS,
    "vad_min_speech_seconds": VAD_MIN_SPEECH_SECONDS,
    "tts_model": LEMONFOX_TTS_MODEL,
    "tts_voice": LEMONFOX_TTS_VOICE,
    "tts_language": LEMONFOX_TTS_LANGUAGE,
    "tts_response_format": LEMONFOX_TTS_RESPONSE_FORMAT,
    "tts_speed": str(LEMONFOX_TTS_SPEED),
    "tts_optimize_long_text": True,
    "tts_optimize_threshold_chars": 240,
    "chat_model": LEMONFOX_CHAT_MODEL,
    "chat_system_prompt": LEMONFOX_CHAT_SYSTEM_PROMPT,
    "chat_include_history": True,
    "active_tts_profile": _DEFAULT_TTS_PROFILE_NAME,
    "tts_profiles": [
        {
            "name": _DEFAULT_TTS_PROFILE_NAME,
            "voice_filter_language": "any",
            "voice_filter_gender": "any",
            "tts_model": LEMONFOX_TTS_MODEL,
            "tts_voice": LEMONFOX_TTS_VOICE,
            "tts_language": LEMONFOX_TTS_LANGUAGE,
            "tts_response_format": LEMONFOX_TTS_RESPONSE_FORMAT,
            "tts_speed": str(LEMONFOX_TTS_SPEED),
        }
    ],
    "output_history": [],
    "dark_mode": False,
    "ui_splitter_sizes": "560,340",
    "active_profile": "Default",
    "profiles": [
        {
            "name": "Default",
            "stt_language": LEMONFOX_LANGUAGE,
            "stt_response_format": LEMONFOX_RESPONSE_FORMAT,
            "vad_noise_level": _DEFAULT_VAD_NOISE_LEVEL,
            "vad_aggressiveness": VAD_AGGRESSIVENESS,
            "vad_min_speech_seconds": VAD_MIN_SPEECH_SECONDS,
            "tts_model": LEMONFOX_TTS_MODEL,
            "tts_voice": LEMONFOX_TTS_VOICE,
            "tts_language": LEMONFOX_TTS_LANGUAGE,
            "tts_response_format": LEMONFOX_TTS_RESPONSE_FORMAT,
            "tts_speed": str(LEMONFOX_TTS_SPEED),
        }
    ],
}


def _coerce_int(value, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def _coerce_float(value, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _sanitize_output_history(value) -> list[dict]:
    entries = []
    if not isinstance(value, list):
        return entries
    for item in value:
        if not isinstance(item, dict):
            continue
        text = str(item.get("text", "")).strip()
        if not text:
            continue
        name = str(item.get("name", "")).strip()
        created_at = str(item.get("created_at", "")).strip()
        if not name:
            preview = " ".join(text.split())
            name = preview[:48].strip()
            if len(preview) > 48:
                name = f"{name}..."
        entries.append(
            {
                "name": name,
                "text": text,
                "created_at": created_at,
            }
        )
        if len(entries) >= _OUTPUT_HISTORY_LIMIT:
            break
    return entries


def load_app_settings() -> dict:
    settings = DEFAULT_SETTINGS.copy()
    settings["profiles"] = [dict(p) for p in DEFAULT_SETTINGS["profiles"]]
    settings["tts_profiles"] = [dict(p) for p in DEFAULT_SETTINGS["tts_profiles"]]
    settings["output_history"] = [dict(item) for item in DEFAULT_SETTINGS["output_history"]]
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
                                    "vad_noise_level": _coerce_int(
                                        item.get("vad_noise_level", settings["vad_noise_level"]),
                                        settings["vad_noise_level"],
                                    ),
                                    "vad_aggressiveness": _coerce_int(
                                        item.get("vad_aggressiveness", settings["vad_aggressiveness"]),
                                        settings["vad_aggressiveness"],
                                    ),
                                    "vad_min_speech_seconds": _coerce_float(
                                        item.get("vad_min_speech_seconds", settings["vad_min_speech_seconds"]),
                                        settings["vad_min_speech_seconds"],
                                    ),
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
                elif key == "tts_profiles" and isinstance(value, list):
                    tts_profiles = []
                    for item in value:
                        if isinstance(item, dict) and isinstance(item.get("name"), str) and item["name"].strip():
                            tts_profiles.append(
                                {
                                    "name": item["name"].strip(),
                                    "voice_filter_language": str(
                                        item.get("voice_filter_language", "any")
                                    ).strip().lower() or "any",
                                    "voice_filter_gender": str(item.get("voice_filter_gender", "any")).strip().lower()
                                    or "any",
                                    "tts_model": str(item.get("tts_model", settings["tts_model"])).strip(),
                                    "tts_voice": str(item.get("tts_voice", settings["tts_voice"])).strip(),
                                    "tts_language": str(item.get("tts_language", settings["tts_language"])).strip(),
                                    "tts_response_format": str(
                                        item.get("tts_response_format", settings["tts_response_format"])
                                    ).strip(),
                                    "tts_speed": str(item.get("tts_speed", settings["tts_speed"])).strip(),
                                }
                            )
                    if tts_profiles:
                        settings["tts_profiles"] = tts_profiles
                elif key == "output_history" and isinstance(value, list):
                    settings["output_history"] = _sanitize_output_history(value)
                elif isinstance(DEFAULT_SETTINGS.get(key), bool) and isinstance(value, bool):
                    settings[key] = value
                elif isinstance(DEFAULT_SETTINGS.get(key), int) and not isinstance(DEFAULT_SETTINGS.get(key), bool):
                    settings[key] = _coerce_int(value, DEFAULT_SETTINGS[key])
                elif isinstance(DEFAULT_SETTINGS.get(key), float):
                    settings[key] = _coerce_float(value, DEFAULT_SETTINGS[key])
                elif isinstance(value, str) and value.strip():
                    settings[key] = value.strip()
    except (json.JSONDecodeError, OSError):
        pass
    if settings["active_profile"] not in [p["name"] for p in settings["profiles"]]:
        settings["active_profile"] = settings["profiles"][0]["name"]
    if settings["active_tts_profile"] not in [p["name"] for p in settings["tts_profiles"]]:
        settings["active_tts_profile"] = settings["tts_profiles"][0]["name"]
    return settings


def save_app_settings(settings: dict):
    payload = load_app_settings()
    for key in DEFAULT_SETTINGS:
        value = settings.get(key)
        if key in {"profiles", "tts_profiles"} and isinstance(value, list) and value:
            payload[key] = value
        elif key == "output_history" and isinstance(value, list):
            payload[key] = _sanitize_output_history(value)
        elif isinstance(DEFAULT_SETTINGS.get(key), bool) and isinstance(value, bool):
            payload[key] = value
        elif isinstance(DEFAULT_SETTINGS.get(key), int) and not isinstance(DEFAULT_SETTINGS.get(key), bool):
            payload[key] = _coerce_int(value, payload.get(key, DEFAULT_SETTINGS[key]))
        elif isinstance(DEFAULT_SETTINGS.get(key), float):
            payload[key] = _coerce_float(value, payload.get(key, DEFAULT_SETTINGS[key]))
        elif isinstance(value, str) and value.strip():
            payload[key] = value.strip()
    _SETTINGS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
