# Development Reports — LemonFox Voice Transcriber

This file tracks key milestones, decisions, errors, and progress throughout development.
Each entry includes a timestamp and category tag.

---

## [2026-02-09 — PLANNING] Project initialized

- Created empty project directory at `/home/joe/leelo_txt_voice_whispr/`
- Researched LemonFox.ai API: `POST https://api.lemonfox.ai/v1/audio/transcriptions`
- Confirmed API is OpenAI-compatible (Whisper large-v3), supports file upload + URL
- Defined 3 modes: Listening (VAD), Recording (manual), File transcription
- Chose PyQt6 for GUI + system tray (QSystemTrayIcon)
- Chose sounddevice + webrtcvad for audio capture + VAD
- Plan finalized and saved to `PLAN.md`
- Development will happen in WSL2, final testing on Windows 11
- Deployment via GitHub → Windows clone

### Decisions made:
- Phase 1: Speech-to-Text only. TTS deferred to Phase 2.
- Native GUI (PyQt6) preferred over Streamlit for system tray support and background operation.
- Text output: clipboard + Ctrl+V paste simulation (pyautogui). Typing mode optional.
- No installer needed — terminal launch via `python app.py`.
- WSL Python env for development/testing logic; Windows Python for audio/GUI/hotkeys.

### Open items:
- [x] User to install Python environment in WSL
- [x] User to provide LemonFox API key (will go in `.env`)
- [ ] Confirm Windows Python is installed with pip available
- [ ] Create GitHub repository when ready for Windows testing

---

## [2026-02-09 — BUILD] Steps 1–10 implemented

All core modules and GUI built in a single session. Every file compiles cleanly under `py_compile`.

### Files created:
| File | Purpose |
|---|---|
| `config.py` | Loads `.env` settings (API key, language, format, VAD threshold) |
| `core/lemonfox_client.py` | LemonFox API wrapper — `transcribe_file()` and `transcribe_bytes()` |
| `core/audio_recorder.py` | Mic capture via `sounddevice` — start/pause/resume/stop → WAV bytes |
| `core/vad_listener.py` | Continuous listening with `webrtcvad` — auto-chunks on speech pauses |
| `core/text_output.py` | Clipboard copy (`pyperclip`) + paste simulation (`pyautogui`) |
| `hotkeys.py` | Global hotkeys via `pynput` — Ctrl+Alt+L (listen), Ctrl+Alt+R (record) |
| `ui/tray_icon.py` | `QSystemTrayIcon` with colored circle icons (idle/listening/recording) |
| `ui/main_window.py` | Tabbed main window — Listening, Recording, File tabs + shared output area |
| `app.py` | Entry point — wires window, tray, and hotkeys together |
| `cli_test.py` | CLI smoke test — record → transcribe → print |

### What's wired:
- **Recording mode**: Start/Pause/Stop → sends WAV to API → displays + copies result
- **File mode**: File picker → sends to API → displays + copies result
- **Listening mode**: VAD auto-detects speech → sends chunks → appends text continuously + copies to clipboard
- **Tray icon**: Changes color for idle (grey), listening (green), recording (red)
- **Tray menu**: Show Window, Start Listening, Start Recording, Quit
- **Global hotkeys**: Ctrl+Alt+L (toggle listen), Ctrl+Alt+R (toggle record)
- **Close to tray**: Window X hides to tray instead of quitting

### Needs Windows testing:
- [ ] Mic capture via `sounddevice`
- [ ] GUI rendering (PyQt6)
- [ ] System tray icon display
- [ ] Global hotkeys (pynput)
- [ ] Clipboard + paste simulation (pyperclip / pyautogui)
- [ ] Full end-to-end: speak → VAD → API → text in active window
