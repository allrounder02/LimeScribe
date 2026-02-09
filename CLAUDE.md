# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

LemonFox Voice Transcriber — a Windows 11 desktop app that transcribes speech to text using the LemonFox.ai API (Whisper large-v3). PyQt6 GUI with system tray icon. Three modes: Listening (VAD), Recording (manual), File transcription.

## Development Environment

- **Developed in WSL2**, runs natively on **Windows 11**
- WSL2 cannot capture mic audio or display GUI — audio/GUI/hotkey testing must happen on Windows
- WSL2 is used for code editing and unit-testable logic only
- Python 3.12 venv at `.venv/`

## Commands

```bash
# Activate venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app (on Windows only — needs mic + display)
python app.py
```

No test framework is configured yet. When tests are added, they should go in a `tests/` directory and use `pytest`.

## Architecture

```
app.py                  # Entry point — QApplication + system tray
ui/
  main_window.py        # Main GUI window with mode tabs (Listening | Recording | File)
  tray_icon.py          # QSystemTrayIcon + context menu
  resources/            # Icons for tray states (idle, listening, recording)
core/
  lemonfox_client.py    # API wrapper — POST to LemonFox transcription endpoint
  audio_recorder.py     # Mic capture via sounddevice, start/pause/stop → WAV bytes
  vad_listener.py       # Continuous listening with webrtcvad + auto-chunking on pause
  text_output.py        # Clipboard (pyperclip) + paste simulation (pyautogui)
config.py               # Settings loader from .env via python-dotenv
hotkeys.py              # Global hotkey registration via pynput
```

### Data flow
1. Audio in (mic via `sounddevice` or file from disk) → WAV bytes
2. WAV bytes → `lemonfox_client.py` → POST to `https://api.lemonfox.ai/v1/audio/transcriptions` with Bearer token auth
3. API response (transcribed text) → displayed in GUI text area + clipboard
4. In Listening mode, `vad_listener.py` auto-detects speech pauses (~1.5s configurable) and sends chunks automatically

### API
- Endpoint: `POST https://api.lemonfox.ai/v1/audio/transcriptions`
- Auth: `Authorization: Bearer <key>` (key stored in `.env` as `LEMONFOX_API_KEY`)
- OpenAI-compatible interface, supports file upload
- Accepted formats: MP3, WAV, FLAC, M4A, OGG

## Build Order

Implementation follows the sequence in `PLAN.md`. Progress is tracked in `REPORTS.md` with timestamps. The build order starts with `lemonfox_client.py`, then `audio_recorder.py`, then a CLI smoke test, then GUI shell, and progressively wires up each mode.

## Key Constraints

- `.env` contains the API key and is gitignored — never commit it
- Audio files (`.wav`, `.mp3`, etc.) are gitignored
- `pyautogui` and `pynput` require a real Windows display — they will fail in WSL2/headless
- `webrtcvad` requires 16-bit PCM audio at 8000, 16000, or 32000 Hz sample rates
