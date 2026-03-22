import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def _getenv(*names: str, default: str = "") -> str:
    for name in names:
        if name in os.environ:
            return os.environ[name]
    return default


def _getenv_int(*names: str, default: int) -> int:
    raw = _getenv(*names, default=str(default))
    try:
        return int(raw)
    except (TypeError, ValueError):
        return int(default)


def _getenv_float(*names: str, default: float) -> float:
    raw = _getenv(*names, default=str(default))
    try:
        return float(raw)
    except (TypeError, ValueError):
        return float(default)


def _openai_mode_enabled() -> bool:
    return bool(str(os.environ.get("OPENAI_API_KEY", "")).strip())


OPENAI_TTS_MODELS = ("gpt-4o-mini-tts", "tts-1", "tts-1-hd")
OPENAI_TTS_VOICES = (
    "alloy",
    "ash",
    "ballad",
    "cedar",
    "coral",
    "echo",
    "fable",
    "marin",
    "nova",
    "onyx",
    "sage",
    "shimmer",
    "verse",
)
OPENAI_TTS_RESPONSE_FORMATS = ("wav", "mp3", "opus", "aac", "flac", "pcm")
OPENAI_STT_RESPONSE_FORMATS = ("json", "text", "srt", "vtt", "verbose_json")


def _normalize_chat_model(value, default: str = "gpt-4o-mini") -> str:
    candidate = str(value or "").strip()
    if not candidate:
        return default
    if candidate.startswith("llama-"):
        return default
    return candidate


def _normalize_tts_model(value, default: str = "gpt-4o-mini-tts") -> str:
    candidate = str(value or "").strip()
    return candidate or default


def _normalize_tts_voice(value, default: str = "coral") -> str:
    candidate = str(value or "").strip()
    if not candidate:
        return default
    if candidate in OPENAI_TTS_VOICES or candidate.startswith("voice_"):
        return candidate
    legacy_map = {
        "heart": "coral",
        "bella": "shimmer",
        "michael": "onyx",
        "aoede": "ash",
        "kore": "echo",
        "jessica": "shimmer",
        "nicole": "nova",
        "river": "sage",
        "sky": "alloy",
        "fenrir": "echo",
        "liam": "onyx",
        "puck": "fable",
        "adam": "alloy",
        "santa": "verse",
        "alice": "marin",
        "emma": "marin",
        "isabella": "cedar",
        "lily": "shimmer",
        "daniel": "onyx",
        "george": "alloy",
        "lewis": "echo",
    }
    return legacy_map.get(candidate.lower(), default)

# Hotkey defaults defined here to avoid circular import with hotkeys.py
DEFAULT_HOTKEY_LISTEN = "Ctrl+Alt+L"
DEFAULT_HOTKEY_RECORD = "Ctrl+Alt+R"
DEFAULT_HOTKEY_DIALOGUE = "Ctrl+Alt+D"

OPENAI_API_KEY = _getenv("OPENAI_API_KEY", "LEMONFOX_API_KEY", default="")
if _openai_mode_enabled():
    OPENAI_STT_MODEL = _getenv("OPENAI_STT_MODEL", default="gpt-4o-mini-transcribe")
    OPENAI_STT_LANGUAGE = _getenv("OPENAI_STT_LANGUAGE", default="english")
    OPENAI_STT_RESPONSE_FORMAT = _getenv("OPENAI_STT_RESPONSE_FORMAT", default="json")
    OPENAI_STT_URL = _getenv("OPENAI_STT_URL", default="https://api.openai.com/v1/audio/transcriptions")
    OPENAI_STT_FALLBACK_URL = _getenv("OPENAI_STT_FALLBACK_URL", default="")
    OPENAI_TTS_URL = _getenv("OPENAI_TTS_URL", default="https://api.openai.com/v1/audio/speech")
    OPENAI_TTS_FALLBACK_URL = _getenv("OPENAI_TTS_FALLBACK_URL", default="")
    OPENAI_TTS_MODEL = _normalize_tts_model(_getenv("OPENAI_TTS_MODEL", default="gpt-4o-mini-tts"))
    OPENAI_TTS_VOICE = _normalize_tts_voice(_getenv("OPENAI_TTS_VOICE", default="coral"))
    OPENAI_TTS_LANGUAGE = _getenv("OPENAI_TTS_LANGUAGE", default="en-us")
    OPENAI_TTS_RESPONSE_FORMAT = _getenv("OPENAI_TTS_RESPONSE_FORMAT", default="wav")
    OPENAI_TTS_SPEED = _getenv_float("OPENAI_TTS_SPEED", default=1.0)
else:
    OPENAI_STT_MODEL = _getenv("LEMONFOX_STT_MODEL", default="gpt-4o-mini-transcribe")
    OPENAI_STT_LANGUAGE = _getenv("LEMONFOX_LANGUAGE", default="english")
    OPENAI_STT_RESPONSE_FORMAT = _getenv("LEMONFOX_RESPONSE_FORMAT", default="json")
    OPENAI_STT_URL = _getenv("LEMONFOX_API_URL", default="https://api.openai.com/v1/audio/transcriptions")
    OPENAI_STT_FALLBACK_URL = _getenv("LEMONFOX_API_FALLBACK_URL", default="")
    OPENAI_TTS_URL = _getenv("LEMONFOX_TTS_URL", default="https://api.openai.com/v1/audio/speech")
    OPENAI_TTS_FALLBACK_URL = _getenv("LEMONFOX_TTS_FALLBACK_URL", default="")
    OPENAI_TTS_MODEL = _normalize_tts_model(_getenv("LEMONFOX_TTS_MODEL", default="gpt-4o-mini-tts"))
    OPENAI_TTS_VOICE = _normalize_tts_voice(_getenv("LEMONFOX_TTS_VOICE", default="coral"))
    OPENAI_TTS_LANGUAGE = _getenv("LEMONFOX_TTS_LANGUAGE", default="en-us")
    OPENAI_TTS_RESPONSE_FORMAT = _getenv("LEMONFOX_TTS_RESPONSE_FORMAT", default="wav")
    OPENAI_TTS_SPEED = _getenv_float("LEMONFOX_TTS_SPEED", default=1.0)
OPENAI_TTS_INSTRUCTIONS = _getenv("OPENAI_TTS_INSTRUCTIONS", default="")
if _openai_mode_enabled():
    OPENAI_CHAT_URL = _getenv("OPENAI_CHAT_URL", default="https://api.openai.com/v1/chat/completions")
    OPENAI_CHAT_FALLBACK_URL = _getenv("OPENAI_CHAT_FALLBACK_URL", default="")
    OPENAI_CHAT_MODEL = _normalize_chat_model(_getenv("OPENAI_CHAT_MODEL", default="gpt-4o-mini"))
    OPENAI_CHAT_SYSTEM_PROMPT = _getenv(
        "OPENAI_CHAT_SYSTEM_PROMPT",
        default="You are a helpful assistant.",
    )
else:
    OPENAI_CHAT_URL = _getenv("LEMONFOX_CHAT_URL", default="https://api.openai.com/v1/chat/completions")
    OPENAI_CHAT_FALLBACK_URL = _getenv("LEMONFOX_CHAT_FALLBACK_URL", default="")
    OPENAI_CHAT_MODEL = _normalize_chat_model(_getenv("LEMONFOX_CHAT_MODEL", default="gpt-4o-mini"))
    OPENAI_CHAT_SYSTEM_PROMPT = _getenv(
        "LEMONFOX_CHAT_SYSTEM_PROMPT",
        default="You are a helpful assistant.",
    )
VAD_PAUSE_THRESHOLD = _getenv_float("VAD_PAUSE_THRESHOLD", default=1.5)
VAD_AGGRESSIVENESS = _getenv_int("VAD_AGGRESSIVENESS", default=3)
VAD_MIN_SPEECH_SECONDS = _getenv_float("VAD_MIN_SPEECH_SECONDS", default=0.5)
VOICE_MAX_WORDS_AUTO_LISTEN = _getenv_int("VOICE_MAX_WORDS_AUTO_LISTEN", default=100)
VOICE_MAX_WORDS_MANUAL = _getenv_int("VOICE_MAX_WORDS_MANUAL", default=50)
LOG_LEVEL = _getenv("LOG_LEVEL", default="INFO").upper()
LOG_FILE = _getenv("LOG_FILE", default="").strip()

# Legacy aliases kept so the rest of the app can migrate incrementally.
LEMONFOX_API_KEY = OPENAI_API_KEY
LEMONFOX_LANGUAGE = OPENAI_STT_LANGUAGE
LEMONFOX_RESPONSE_FORMAT = OPENAI_STT_RESPONSE_FORMAT
LEMONFOX_API_URL = OPENAI_STT_URL
LEMONFOX_API_FALLBACK_URL = OPENAI_STT_FALLBACK_URL
LEMONFOX_TTS_URL = OPENAI_TTS_URL
LEMONFOX_TTS_FALLBACK_URL = OPENAI_TTS_FALLBACK_URL
LEMONFOX_TTS_MODEL = OPENAI_TTS_MODEL
LEMONFOX_TTS_VOICE = OPENAI_TTS_VOICE
LEMONFOX_TTS_LANGUAGE = OPENAI_TTS_LANGUAGE
LEMONFOX_TTS_RESPONSE_FORMAT = OPENAI_TTS_RESPONSE_FORMAT
LEMONFOX_TTS_SPEED = OPENAI_TTS_SPEED
LEMONFOX_CHAT_URL = OPENAI_CHAT_URL
LEMONFOX_CHAT_FALLBACK_URL = OPENAI_CHAT_FALLBACK_URL
LEMONFOX_CHAT_MODEL = OPENAI_CHAT_MODEL
LEMONFOX_CHAT_SYSTEM_PROMPT = OPENAI_CHAT_SYSTEM_PROMPT

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
    "hotkey_dialogue": DEFAULT_HOTKEY_DIALOGUE,
    "stt_language": OPENAI_STT_LANGUAGE,
    "stt_response_format": OPENAI_STT_RESPONSE_FORMAT,
    "auto_copy_transcription": True,
    "clear_output_after_copy": False,
    "stop_listening_after_copy": False,
    "keep_wrapping_parentheses": False,
    "vad_noise_level": _DEFAULT_VAD_NOISE_LEVEL,
    "vad_aggressiveness": VAD_AGGRESSIVENESS,
    "vad_min_speech_seconds": VAD_MIN_SPEECH_SECONDS,
    "tts_model": OPENAI_TTS_MODEL,
    "tts_voice": OPENAI_TTS_VOICE,
    "tts_language": OPENAI_TTS_LANGUAGE,
    "tts_response_format": OPENAI_TTS_RESPONSE_FORMAT,
    "tts_speed": str(OPENAI_TTS_SPEED),
    "tts_optimize_long_text": True,
    "tts_optimize_threshold_chars": 240,
    "chat_model": OPENAI_CHAT_MODEL,
    "chat_system_prompt": OPENAI_CHAT_SYSTEM_PROMPT,
    "chat_include_history": True,
    "voice_max_words_auto_listen": VOICE_MAX_WORDS_AUTO_LISTEN,
    "voice_max_words_manual": VOICE_MAX_WORDS_MANUAL,
    "voice_speaker_mode": True,
    "active_tts_profile": _DEFAULT_TTS_PROFILE_NAME,
    "active_dialogue_tts_profile": _DEFAULT_TTS_PROFILE_NAME,
    "tts_profiles": [
        {
            "name": _DEFAULT_TTS_PROFILE_NAME,
            "voice_filter_language": "any",
            "voice_filter_gender": "any",
            "tts_model": OPENAI_TTS_MODEL,
            "tts_voice": OPENAI_TTS_VOICE,
            "tts_language": OPENAI_TTS_LANGUAGE,
            "tts_response_format": OPENAI_TTS_RESPONSE_FORMAT,
            "tts_speed": str(OPENAI_TTS_SPEED),
        }
    ],
    "output_history": [],
    "dark_mode": False,
    "ui_splitter_sizes": "560,340",
    "active_profile": "Default",
    "profiles": [
        {
            "name": "Default",
            "stt_language": OPENAI_STT_LANGUAGE,
            "stt_response_format": OPENAI_STT_RESPONSE_FORMAT,
            "vad_noise_level": _DEFAULT_VAD_NOISE_LEVEL,
            "vad_aggressiveness": VAD_AGGRESSIVENESS,
            "vad_min_speech_seconds": VAD_MIN_SPEECH_SECONDS,
            "tts_model": OPENAI_TTS_MODEL,
            "tts_voice": OPENAI_TTS_VOICE,
            "tts_language": OPENAI_TTS_LANGUAGE,
            "tts_response_format": OPENAI_TTS_RESPONSE_FORMAT,
            "tts_speed": str(OPENAI_TTS_SPEED),
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
                                    "tts_model": _normalize_tts_model(
                                        item.get("tts_model", settings["tts_model"]),
                                        default=settings["tts_model"],
                                    ),
                                    "tts_voice": _normalize_tts_voice(
                                        item.get("tts_voice", settings["tts_voice"]),
                                        default=settings["tts_voice"],
                                    ),
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
                                    "tts_model": _normalize_tts_model(
                                        item.get("tts_model", settings["tts_model"]),
                                        default=settings["tts_model"],
                                    ),
                                    "tts_voice": _normalize_tts_voice(
                                        item.get("tts_voice", settings["tts_voice"]),
                                        default=settings["tts_voice"],
                                    ),
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
                    cleaned = value.strip()
                    if key == "chat_model":
                        settings[key] = _normalize_chat_model(cleaned, default=DEFAULT_SETTINGS[key])
                    elif key == "tts_model":
                        settings[key] = _normalize_tts_model(cleaned, default=DEFAULT_SETTINGS[key])
                    elif key == "tts_voice":
                        settings[key] = _normalize_tts_voice(cleaned, default=DEFAULT_SETTINGS[key])
                    else:
                        settings[key] = cleaned
    except (json.JSONDecodeError, OSError):
        pass
    settings["chat_model"] = _normalize_chat_model(settings.get("chat_model"), default=DEFAULT_SETTINGS["chat_model"])
    settings["tts_model"] = _normalize_tts_model(settings.get("tts_model"), default=DEFAULT_SETTINGS["tts_model"])
    settings["tts_voice"] = _normalize_tts_voice(settings.get("tts_voice"), default=DEFAULT_SETTINGS["tts_voice"])
    if settings["active_profile"] not in [p["name"] for p in settings["profiles"]]:
        settings["active_profile"] = settings["profiles"][0]["name"]
    if settings["active_tts_profile"] not in [p["name"] for p in settings["tts_profiles"]]:
        settings["active_tts_profile"] = settings["tts_profiles"][0]["name"]
    if settings["active_dialogue_tts_profile"] not in [p["name"] for p in settings["tts_profiles"]]:
        settings["active_dialogue_tts_profile"] = settings["active_tts_profile"]
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
            cleaned = value.strip()
            if key == "chat_model":
                payload[key] = _normalize_chat_model(cleaned, default=DEFAULT_SETTINGS[key])
            elif key == "tts_model":
                payload[key] = _normalize_tts_model(cleaned, default=DEFAULT_SETTINGS[key])
            elif key == "tts_voice":
                payload[key] = _normalize_tts_voice(cleaned, default=DEFAULT_SETTINGS[key])
            else:
                payload[key] = cleaned
    _SETTINGS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
