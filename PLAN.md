# LemonFox Voice Transcriber — Project Plan

## Overview

A Windows 11 desktop application that transcribes speech to text using the [LemonFox.ai](https://lemonfox.ai) API (Whisper large-v3). The app runs in the background with a system tray icon and provides multiple transcription modes. Text-to-Speech will be added in a future phase.

## Target Platform

- **Runs on**: Windows 11 (natively)
- **Developed in**: WSL2 (code editing + unit testing)
- **Tested on**: WSL2 for logic, Windows for GUI/audio/hotkeys
- **Deployment**: GitHub repo → clone on Windows → `pip install -r requirements.txt` → `python app.py`

## Phase 1 — Speech-to-Text

### Mode 1: Listening Mode
- Continuous mic capture with Voice Activity Detection (VAD)
- Auto-detects pauses (~1.5s, configurable) and sends buffered speech to LemonFox API
- Transcribed text is pasted into the active window (Ctrl+V simulation) or saved to clipboard
- Toggle via global hotkey `Ctrl+Alt+L` or GUI button
- Tray icon changes color/state to indicate "listening"

### Mode 2: Record Mode
- Manual Start / Pause / Stop controls in the GUI
- On Stop, full recording is sent to LemonFox API
- Result displayed in GUI text area + copied to clipboard
- Also triggerable via global hotkey `Ctrl+Alt+R`

### Mode 3: File Transcription
- "Select File" button opens Windows file dialog
- Accepts: `.mp3`, `.wav`, `.flac`, `.m4a`, `.ogg`
- Sends file to LemonFox API, shows result in GUI text area
- User can copy result manually

### GUI & System Tray
- **Framework**: PyQt6
- **System Tray**: `QSystemTrayIcon` — icon reflects state (idle / listening / recording)
- **Tray right-click menu**: Show Window, Start Listening, Start Recording, Quit
- **Main Window** (compact):
  - Mode tabs: Listening | Recording | File
  - Recording tab: Start/Pause/Stop buttons
  - File tab: Select file + Transcribe button
  - Shared: text output area, Copy button
  - Settings: API key, language, VAD sensitivity

### Text Output Strategy
1. Copy text to clipboard via `pyperclip`
2. Simulate `Ctrl+V` via `pyautogui` to paste into focused window
3. Optional "typing" mode via `pyautogui.typewrite()` (slower, but visible)

## Phase 2 — Text-to-Speech (Future)
- Select/highlight text in any window
- Global hotkey triggers TTS via LemonFox TTS API
- Audio played through speakers using a pleasant voice
- Voice selection in settings
- *Not in scope for Phase 1*

## Architecture

```
leelo_txt_voice_whispr/
├── app.py                  # Entry point — launches QApplication + system tray
├── ui/
│   ├── main_window.py      # Main GUI window (tabs/modes)
│   ├── tray_icon.py        # System tray icon + context menu
│   └── resources/          # Icons for tray states (idle, listening, recording)
├── core/
│   ├── lemonfox_client.py  # API wrapper (transcribe file, transcribe bytes/URL)
│   ├── audio_recorder.py   # Mic capture, start/pause/stop, returns WAV bytes
│   ├── vad_listener.py     # Continuous listening with VAD + auto-chunking
│   └── text_output.py      # Clipboard + simulate-typing logic
├── config.py               # Settings loader (.env / settings.json)
├── hotkeys.py              # Global hotkey registration (Windows-native)
├── .env                    # API key (gitignored)
├── .gitignore
├── requirements.txt
├── PLAN.md                 # This file
├── REPORTS.md              # Development log with timestamps
└── README.md               # User-facing documentation
```

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `PyQt6` | latest | GUI + system tray |
| `requests` | latest | LemonFox API calls |
| `sounddevice` | latest | Mic capture |
| `numpy` | latest | Audio buffer handling |
| `webrtcvad` | latest | Voice activity detection |
| `pyperclip` | latest | Clipboard read/write |
| `pyautogui` | latest | Simulate keystrokes / paste |
| `pynput` | latest | Global hotkeys (system-wide) |
| `python-dotenv` | latest | Load .env config |

## Build Order

| Step | Component | Description | Status |
|---|---|---|---|
| 1 | `lemonfox_client.py` | API wrapper — file + bytes + URL transcription | done |
| 2 | `audio_recorder.py` | Mic record/stop → WAV bytes | done |
| 3 | CLI smoke test | Record → transcribe → print (prove pipeline) | done |
| 4 | GUI shell | PyQt6 window + system tray with tabs | done |
| 5 | Record mode (GUI) | Wire Start/Pause/Stop to recorder + API | done |
| 6 | File mode (GUI) | File picker → API → display result | done |
| 7 | `vad_listener.py` | Continuous listening with auto-chunking | done |
| 8 | Listening mode (GUI) | Wire VAD to API + text output | done |
| 9 | `text_output.py` | Clipboard + paste-into-active-window | done |
| 10 | `hotkeys.py` | Global hotkeys Ctrl+Alt+L / Ctrl+Alt+R | done |
| 11 | Polish | Tray states, settings panel, error handling | pending |
| 12 | GitHub + Windows test | Push to GitHub, clone on Windows, full test | pending |

## API Reference

- **Endpoint**: `POST https://api.lemonfox.ai/v1/audio/transcriptions`
- **Auth**: `Authorization: Bearer <API_KEY>`
- **Params**: `file`, `language`, `response_format` (json/text/srt/vtt), `diarize`, `translate`, `prompt`
- **Formats**: MP3, WAV, FLAC, M4A, OGG
- **Docs**: https://www.lemonfox.ai/apis/speech-to-text
