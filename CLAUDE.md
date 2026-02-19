# CLAUDE.md

## Project

**ZestVoice** — a Windows 11 desktop app (with optional headless/Docker mode) for speech-to-text, text-to-speech, and AI chat using the LemonFox.ai API. PyQt6 GUI with system tray icon. Also ships a CLI entry point for headless use.

## Development Environment

- **Developed in WSL2**, runs natively on **Windows 11**
- WSL2 cannot capture mic audio or display GUI — audio/GUI/hotkey testing must happen on Windows
- WSL2 is fine for code editing, linting, and running `pytest`
- Python 3.12, venv at `.venv/`

## Commands

```bash
source .venv/bin/activate
pip install -r requirements.txt

# GUI (Windows only — needs mic + display)
python app.py

# Headless CLI
python cli.py

# Tests
pytest tests/
```

## Architecture

```
app.py                       # GUI entry point → ui/app_runtime.py
cli.py                       # Headless CLI entry point → core/cli_runtime.py

config.py                    # Settings loader (.env + settings.json), all defaults
hotkeys.py                   # Global hotkey registration via pynput

core/
  app_config.py              # Injectable AppConfig dataclass
  http_client.py             # Shared httpx client (HTTP/2 connection pooling)
  lemonfox_client.py         # STT API wrapper (POST audio → transcription)
  lemonfox_tts_client.py     # TTS API wrapper (POST text → audio)
  lemonfox_chat_client.py    # Chat completions API wrapper
  transcription_service.py   # Pure-Python STT orchestration (no PyQt6)
  tts_service.py             # Pure-Python TTS orchestration (no PyQt6)
  dialogue_service.py        # Chat/dialogue orchestration
  audio_recorder.py          # Mic capture via sounddevice → WAV bytes
  vad_listener.py            # Continuous listening + webrtcvad auto-chunking
  audio_format.py            # Audio format conversion utilities
  audio_playback.py          # Cross-platform audio playback (sounddevice)
  wav_playback.py            # WAV-specific playback helpers
  tts_audio_output.py        # TTS audio output pipeline
  tts_text.py                # Text pre-processing for TTS
  text_output.py             # Clipboard (pyperclip) + paste simulation (pyautogui)
  assets.py                  # Asset path resolution
  cli_runtime.py             # Headless CLI runtime logic

ui/
  app_runtime.py             # QApplication bootstrap + system tray setup
  main_window.py             # Main GUI window with mode tabs
  settings_panel.py          # Settings UI panel
  tts_panel.py               # TTS controls panel
  dialogue_panel.py          # Chat/dialogue UI panel
  tray_icon.py               # QSystemTrayIcon + context menu
  hotkey_bridge.py           # Bridges pynput hotkeys ↔ Qt signals
  icon_library.py            # Icon loading utilities

assets/icons/                # Tray + UI icons

tests/                       # pytest test suite
```

### Data Flow

1. **STT**: Audio in (mic via `sounddevice` or file) → WAV bytes → `lemonfox_client.py` → LemonFox API → transcribed text → GUI + clipboard
2. **VAD/Listening mode**: `vad_listener.py` auto-detects speech pauses and sends chunks automatically
3. **TTS**: Text → `lemonfox_tts_client.py` → LemonFox TTS API → audio bytes → `audio_playback.py` → speakers
4. **Chat**: User message → `lemonfox_chat_client.py` → LemonFox Chat API → response text

### APIs

All endpoints are OpenAI-compatible and configurable via `.env`:

| Service | Default URL | Auth |
|---------|------------|------|
| STT | `https://api.lemonfox.ai/v1/audio/transcriptions` | Bearer `LEMONFOX_API_KEY` |
| TTS | `https://api.lemonfox.ai/v1/audio/speech` | Bearer `LEMONFOX_API_KEY` |
| Chat | `https://api.lemonfox.ai/v1/chat/completions` | Bearer `LEMONFOX_API_KEY` |

Each service has a configurable fallback URL.

## Configuration

- **`.env`** — API keys and defaults (gitignored, see `.env.example`)
- **`settings.json`** — Runtime user preferences, persisted by the app (gitignored)
- **`config.py`** — Loads both sources; provides `load_app_settings()` / `save_app_settings()`
- Supports multiple STT profiles and TTS voice profiles

## Key Constraints

- `.env` and `settings.json` are gitignored — never commit them
- Audio files (`.wav`, `.mp3`, `.flac`, `.m4a`, `.ogg`) are gitignored
- `pyautogui` and `pynput` require a real Windows display — they fail in WSL2/headless
- `webrtcvad` requires 16-bit PCM at 8000, 16000, or 32000 Hz
- `httpx` with HTTP/2 is used instead of `requests` for connection pooling
- `core/` modules are kept free of PyQt6 imports so they work in headless/CLI mode
- UI modules live in `ui/` and may import PyQt6

## Dependencies

Core (all modes): `httpx[http2]`, `sounddevice`, `numpy`, `webrtcvad`/`webrtcvad-wheels`, `python-dotenv`

GUI-only: `PyQt6`, `pyperclip`, `pyautogui`, `pynput`

See `requirements.txt` for exact specifiers. A separate `requirements_mac.txt` exists for macOS.
