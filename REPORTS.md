# Development Reports — LemonFox Voice Transcriber

This file tracks key milestones, decisions, errors, and progress throughout development.
Each entry includes a timestamp and category tag.

---

## [2026-02-19 — FEATURE] Voice Dialogue: speak → STT → chat → TTS → play → auto-listen loop

### What was built

A full voice conversation loop in the Dialogue tab. The user clicks **Talk** (or presses `Ctrl+Alt+D`), speaks, and the app transcribes their speech, sends it to the chat API, synthesizes the response as audio, plays it, and automatically listens for the next turn — like talking to a voice assistant.

### Architecture

**State machine** (in `core/voice_dialogue.py`):
```
IDLE → LISTENING → TRANSCRIBING → THINKING → SPEAKING → LISTENING (loop)
  ↑                                                          │
  └──────────────── stop() ←─────────────────────────────────┘
```

**Key latency optimization**: Streaming chat + sentence-pipelined TTS. Instead of waiting for the full chat response before starting TTS, the chat API is called with `stream: true` (SSE). As text streams in, sentence boundaries are detected, and TTS is triggered on the **first complete sentence** while the rest still streams. This cuts perceived response latency significantly.

### Files created

| File | Lines | Purpose |
|------|-------|---------|
| `core/voice_dialogue.py` | ~185 | `VoiceDialogueOrchestrator` — pure Python state machine. Creates own STT/TTS clients (avoids conflicts with Capture tab). Shares `DialogueService` for conversation history. Uses `threading.Event` for clean cancellation. |
| `tests/test_chat_streaming.py` | ~140 | 6 tests: SSE delta yielding, `[DONE]` sentinel handling, empty content skipping, non-data line filtering, input validation |
| `tests/test_voice_dialogue.py` | ~170 | 10 tests: state transitions, start/stop, full turn flow with mocked STT/TTS/chat, cancellation mid-turn, auto-listen on/off |

### Files modified

| File | What changed |
|------|-------------|
| `core/lemonfox_chat_client.py` | Added `complete_stream()` + `_stream_sse()` — SSE streaming via `httpx.Client.stream()`, parses `data:` lines, yields content deltas, handles `[DONE]` sentinel, endpoint failover |
| `core/dialogue_service.py` | Added `send_stream(text, on_delta)` — wraps `client.complete_stream()` with history management, calls `on_delta(chunk)` for each piece, appends full response to history when done |
| `ui/dialogue_panel.py` | Added voice controls row: Talk/Stop toggle button, Auto-listen checkbox, state label. New signals: `voice_start_requested`, `voice_stop_requested`, `auto_listen_changed`. Text input disabled while voice is active |
| `ui/main_window.py` | Instantiates `VoiceDialogueOrchestrator`, adds 5 Qt signals for thread-safe callbacks, connects panel voice signals → orchestrator, adds `toggle_voice_dialogue_from_external()` for hotkey, cleans up on close |
| `hotkeys.py` | Added `on_dialogue_toggle` callback, `dialogue_hotkey` param (default `Ctrl+Alt+D`), `_trigger_dialogue()`. `get_hotkeys()` now returns 3-tuple |
| `ui/hotkey_bridge.py` | Added `dialogue_requested` signal + `emit_dialogue_requested()` |
| `ui/app_runtime.py` | Wires dialogue hotkey through bridge to `toggle_voice_dialogue_from_external()` |
| `config.py` | Added `DEFAULT_HOTKEY_DIALOGUE = "Ctrl+Alt+D"` and `"hotkey_dialogue"` to `DEFAULT_SETTINGS` |
| `ui/settings_panel.py` | Updated `get_hotkeys()` unpacking to handle new 3-tuple return |

### How the orchestrator turn works (step by step)

1. VAD (`core/vad_listener.py`) fires `on_speech_chunk(wav_bytes)` → state = TRANSCRIBING
2. Worker thread: `LemonFoxClient.transcribe_bytes(wav_bytes)` → fires `on_user_transcript` callback
3. State = THINKING → `dialogue_service.send_stream(text, on_delta=...)`
4. `on_delta` accumulates text, detects sentence boundaries (`[.!?;]\s` regex)
5. Each complete sentence → `_speak_sentence()`: TTS synthesize → `play_wav_bytes()` → wait for playback
6. State = SPEAKING during playback
7. After all sentences done → `on_turn_complete` → state = LISTENING (if auto_listen) or IDLE
8. `stop()` at any point → sets cancel event, stops VAD, stops audio playback, resets to IDLE

### Design decisions

- **Own STT/TTS client instances**: The orchestrator creates its own `LemonFoxClient` and `LemonFoxTTSClient` to avoid conflicts with the Capture tab's shared services (e.g., if the user is also doing file transcription)
- **Shared DialogueService**: Voice and text turns go into the same conversation history, so the chat context is preserved regardless of input method
- **Cancel event checked at every stage**: `_cancel.is_set()` is checked before STT, before chat, before TTS, and during playback wait — ensures clean interruption from any state
- **TTS forced to WAV**: `_speak_sentence` always requests `response_format="wav"` for in-app playback compatibility
- **No PyQt6 in orchestrator**: `core/voice_dialogue.py` is pure Python — callbacks fire on background threads, Qt signals in `main_window.py` marshal them to the UI thread

### Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| "Talk" button does nothing | VAD can't open mic (WSL2, no audio device) | Must run on Windows with mic access |
| Transcription returns empty | Speech too short / below `min_speech_seconds` | Lower VAD sensitivity in Settings |
| TTS playback fails | PortAudio not installed, or non-WAV format | Ensure `libportaudio2` installed; TTS forced to WAV internally |
| Chat response never arrives | Wrong model name or API key | Check `chat_model` in Dialogue panel, verify `.env` API key |
| Auto-listen doesn't restart | `chk_auto_listen` unchecked, or error during turn | Check auto-listen checkbox; check logs for errors |
| Hotkey `Ctrl+Alt+D` doesn't work | Hotkey conflict with another app | Change in Settings → hotkey_dialogue |
| State stuck on "Thinking..." | Chat API timeout (120s default) | Check network; the httpx client has 120s timeout |
| Tests fail with PortAudio error | Running tests in WSL2 without PortAudio | `test_voice_dialogue.py` mocks `sounddevice`/`webrtcvad`; other test files may need similar mocking |

### Test results

```
48 passed, 5 skipped (PyQt6 tests, expected in WSL2)
```

All 16 new tests pass. No regressions in existing 37 tests.

### What's NOT included (future work)

- Settings UI for the dialogue hotkey (currently hardcoded default, persisted in settings.json)
- Visual waveform or audio level indicator during LISTENING state
- Interrupt-by-speaking (currently must click Stop then Talk again)
- Streaming TTS (play audio chunks as they arrive from TTS API — would need API support)

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
