# ZestVoice

ZestVoice is a speech-to-text and text-to-speech application powered by the **LemonFox.ai** API (Whisper large-v3). It runs as a **desktop app on Windows/macOS** (PyQt6 GUI with system tray) or as a **headless CLI** for servers, Docker containers, and automation pipelines.

## Features

- **Listening mode** -- always-on microphone with VAD, auto-chunks speech on pause
- **Recording mode** -- manual start/pause/stop recording
- **File mode** -- transcribe audio files from disk
- **Text-to-Speech** -- synthesize speech from text via LemonFox-compatible TTS API
- **Dialogue mode** -- OpenAI-compatible chat with LemonFox Llama models
- **Headless CLI** -- transcribe files and generate TTS without a GUI (`cli.py`)
- **Docker support** -- containerized headless transcription and TTS

### Desktop (Windows / macOS)

- PyQt6 tabbed UI: Capture / Text to Speech / Dialogue / Settings
- System tray icon with state colors (idle=logo, listening=green badge, recording=red badge)
- Global hotkeys: `Ctrl+Alt+L` (listen), `Ctrl+Alt+R` (record), configurable in Settings
- Voice Activity Detection (`webrtcvad`) for pause-based chunking
- Clipboard output and optional paste simulation
- Profile system for saving/loading STT and TTS presets

### Headless / Docker

- `cli.py` with `listen`, `transcribe`, and `tts` subcommands
- Zero GUI dependencies -- imports only from `core/`
- See [TUTORIAL.md](TUTORIAL.md) for setup instructions

## Requirements

| Mode | OS / Runtime | Required |
|---|---|---|
| Desktop | Windows 11+ | Python 3.12+, LemonFox API key, microphone access |
| Desktop | macOS (Apple Silicon or Intel) | Python 3.12+, LemonFox API key, microphone access, `portaudio` (`brew install portaudio`) |
| Headless / Docker | Linux / Docker | Python 3.12+ or Docker, LemonFox API key, PortAudio (`libportaudio2`) for mic-based modes |

## Installation

### Desktop (Windows)

```bash
git clone <repo-url> && cd <repo-folder>
python -m venv .venv

# PowerShell
.\.venv\Scripts\Activate.ps1
# or CMD
.venv\Scripts\activate.bat

pip install -r requirements.txt
```

### Desktop (macOS native)

Use this if you want your friend to run the full GUI natively on a Mac.

| Step | Windows | macOS |
|---|---|---|
| Clone repo | `git clone <repo-url> && cd <repo-folder>` | `git clone <repo-url> && cd <repo-folder>` |
| Create venv | `python -m venv .venv` | `python3 -m venv .venv` |
| Activate venv | `.\.venv\Scripts\Activate.ps1` (PowerShell) | `source .venv/bin/activate` |
| Install system audio lib | *(usually not needed)* | `brew install portaudio` |
| Install Python deps | `pip install -r requirements.txt` | `pip install -r requirements_mac.txt` |
| Run GUI | `python app.py` | `python app.py` |

macOS permissions required:
- Allow **Microphone** access when prompted.
- Allow **Accessibility** access for global hotkeys (`pynput`) and optional key simulation (`pyautogui`).

### Windows one-click launcher (`.bat`)

For daily use on Windows, you can skip manual virtualenv activation:

```bat
run_zestvoice.bat
```

- First run: creates `.venv` and installs dependencies automatically
- Later runs: launches GUI directly (uses `pythonw` so no console window)
- Force dependency refresh:

```bat
run_zestvoice.bat --update
```

Note: `.bat` is a launcher, not a compiled executable. If you want a standalone `.exe`, package with PyInstaller.

If you only want to run setup/update without launching the app:

```bat
install_windows.bat
```

### Headless (Linux / Docker)

```bash
# Linux
pip install httpx[http2] sounddevice numpy webrtcvad python-dotenv

# Docker
docker build -t limescribe .
```

## Configuration

Copy `.env.example` to `.env` and set your API key:

```env
LEMONFOX_API_KEY=your_api_key_here
```

All configuration options:

| Variable | Default | Description |
|---|---|---|
| `LEMONFOX_API_KEY` | *(required)* | LemonFox API key |
| `LEMONFOX_LANGUAGE` | `english` | Transcription language |
| `LEMONFOX_RESPONSE_FORMAT` | `json` | API response format |
| `VAD_PAUSE_THRESHOLD` | `1.5` | Seconds of silence before chunk submission |
| `VAD_AGGRESSIVENESS` | `3` | VAD strictness 0-3 (higher = stricter) |
| `VAD_MIN_SPEECH_SECONDS` | `0.5` | Minimum voiced duration before sending |
| `LEMONFOX_API_URL` | `https://api.lemonfox.ai/v1/audio/transcriptions` | Primary STT endpoint |
| `LEMONFOX_API_FALLBACK_URL` | `https://transcribe.whisperapi.com` | Fallback STT endpoint |
| `LEMONFOX_TTS_URL` | `https://api.lemonfox.ai/v1/audio/speech` | Primary TTS endpoint |
| `LEMONFOX_TTS_FALLBACK_URL` | *(empty)* | Optional fallback TTS endpoint |
| `LEMONFOX_TTS_MODEL` | `tts-1` | TTS model name |
| `LEMONFOX_TTS_VOICE` | `heart` | TTS voice name |
| `LEMONFOX_TTS_LANGUAGE` | `en-us` | TTS language code |
| `LEMONFOX_TTS_RESPONSE_FORMAT` | `wav` | TTS output format |
| `LEMONFOX_TTS_SPEED` | `1.0` | TTS speed multiplier |
| `LEMONFOX_CHAT_URL` | `https://api.lemonfox.ai/v1/chat/completions` | Primary Dialogue endpoint |
| `LEMONFOX_CHAT_FALLBACK_URL` | *(empty)* | Optional fallback Dialogue endpoint |
| `LEMONFOX_CHAT_MODEL` | `llama-8b-chat` | Dialogue model (`llama-8b-chat` or `llama-70b-chat`) |
| `LEMONFOX_CHAT_SYSTEM_PROMPT` | `You are a helpful assistant.` | Default Dialogue system prompt |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG/INFO/WARNING/ERROR) |
| `LOG_FILE` | *(empty)* | Optional log file path |

## Usage

### Desktop GUI

```bash
python app.py
```

The app starts in the system tray and opens the main window.

**Listening tab** -- Click **Start Listening** (or `Ctrl+Alt+L`). Speak normally; the app detects pauses and sends chunks for transcription. Results are appended to the output area and copied to clipboard.

**Recording tab** -- Click **Start**, then **Pause/Resume** as needed. Click **Stop** to transcribe. Result appears in output and is copied to clipboard.

**File tab** -- Click **Select File**, choose an audio file (`.mp3`, `.wav`, `.flac`, `.m4a`, `.ogg`), then click **Transcribe**.

**Text to Speech tab** -- Enter text or click **Use Transcription Output**. Click **Generate & Play** to synthesize audio and play it in-app when the response format is WAV. Use **Save Last Audio** to export and **Open Saved Audio** to reopen previously saved files.

**Dialogue tab** -- Chat with LemonFox OpenAI-compatible models. Pick `llama-8b-chat` or `llama-70b-chat`, optionally customize the system prompt, and choose whether to include prior conversation history in each request.

**Settings tab** -- Three sub-pages: General (hotkeys), Speech (STT options + profiles), Voice (TTS options + voice presets). Changes apply immediately without restarting.

**Tray menu** -- Show Window, Start Listening, Start Recording, Quit.

**Window behavior** -- Click X to quit the app. Use the system tray icon menu (**Show Window**) to restore the window after it is hidden/minimized by the OS.

### Headless CLI

```bash
# Transcribe a file
python cli.py transcribe recording.wav

# Text-to-speech
python cli.py tts "Hello world" -o hello.wav

# VAD listening (needs microphone)
python cli.py listen
```

### Docker

```bash
# Transcribe a file
docker run -v /path/to/.env:/app/.env -v /path/to/audio:/data \
    limescribe transcribe /data/recording.wav

# Text-to-speech
docker run -v /path/to/.env:/app/.env -v /path/to/output:/data \
    limescribe tts "Hello world" -o /data/hello.wav
```

See [TUTORIAL.md](TUTORIAL.md) for detailed headless/Docker setup instructions.

## Project Structure

```
app.py                      # Desktop GUI entry point
cli.py                      # Headless CLI entry point
config.py                   # Settings loader (.env + settings.json)
requirements_mac.txt        # macOS install target (currently extends requirements.txt)
hotkeys.py                  # Global hotkey registration (pynput)
Dockerfile                  # Headless container build

core/                       # Pure Python, no PyQt6 dependency
  app_config.py             # Injectable config dataclass
  cli_runtime.py            # CLI command wiring + lifecycle
  dialogue_service.py       # Dialogue orchestration
  http_client.py            # Shared httpx client with connection pooling
  lemonfox_chat_client.py   # LemonFox chat-completions API wrapper
  transcription_service.py  # STT orchestration (VAD, recording, file)
  tts_service.py            # TTS orchestration
  tts_text.py               # Long-text cleanup + chunking helpers for TTS
  lemonfox_client.py        # LemonFox STT API wrapper
  lemonfox_tts_client.py    # LemonFox TTS API wrapper
  audio_recorder.py         # Mic recording to WAV bytes
  vad_listener.py           # Continuous listening + VAD chunking
  audio_format.py           # Audio format signature detection (WAV/FLAC/MP3/OGG)
  wav_playback.py           # WAV-only playback controller for desktop TTS player
  audio_playback.py         # Legacy cross-platform audio playback helper
  text_output.py            # Clipboard + paste helpers (lazy imports)

ui/                         # PyQt6 widgets
  app_runtime.py            # GUI runtime wiring + lifecycle
  dialogue_panel.py         # Dialogue input + transcript widget
  hotkey_bridge.py          # Thread-safe pynput -> Qt signal bridge
  main_window.py            # Main window + tab coordination
  settings_panel.py         # Settings, profiles, voice presets
  tts_panel.py              # TTS input widget
  tray_icon.py              # System tray icon and menu

data/
  voice_presets.json        # Voice actor presets (language/gender/id)

tests/
  test_runtime_wiring.py    # Non-GUI smoke tests for entrypoint wiring
  test_dialogue_service.py  # Dialogue history behavior
  test_lemonfox_chat_client.py # Chat API response parsing
  test_lemonfox_tts_client.py  # TTS API error parsing and non-audio handling
```

### Architecture

The `core/` layer is a standalone Python SDK with no GUI dependencies. It uses `httpx` with HTTP/2 and connection pooling for efficient API calls (important in VAD mode where each speech chunk is a separate request). The `ui/` layer wraps services with PyQt6 signals for thread-safe GUI updates.

### Entry Points and Wiring

- `app.py` is a thin desktop entry point that delegates to `ui/app_runtime.py`.
- `cli.py` is a thin headless entry point that delegates to `core/cli_runtime.py`.
- Runtime wiring modules own startup/shutdown orchestration (logging, hotkeys, tray, settings callbacks, shared HTTP client cleanup).

Import conventions:

- Use explicit module imports inside packages (example: `from core.transcription_service import TranscriptionService`).
- Use package-level exports in `core/__init__.py` and `ui/__init__.py` only for stable public interfaces; avoid wildcard re-exports.

```
               app.py (GUI)          cli.py (headless)
                   |                       |
                   v                       v
              ui/ (PyQt6)         (no GUI needed)
                   |                       |
                   +-------+-------+-------+
                           |
                        core/ (pure Python)
                           |
                    httpx -> LemonFox API
```

## Troubleshooting

- **401 Unauthorized**: check `LEMONFOX_API_KEY` in `.env`
- **No mic input**: verify microphone permissions and default input device
- **Hotkeys not firing**: run in a native desktop session (not WSL/headless). On macOS, grant Accessibility permission.
- **Clipboard/paste issues**: ensure focused target app accepts the platform paste shortcut (`Ctrl+V` on Windows/Linux, `Cmd+V` on macOS)
- **Repeated idle text** (e.g. "Thank you" from silence): set `VAD_AGGRESSIVENESS=3` and `VAD_MIN_SPEECH_SECONDS=0.5` (or higher)
- **TTS playback error mentioning RIFF / non-audio**: set `LEMONFOX_TTS_RESPONSE_FORMAT=wav` for in-app playback. If the API returns text/JSON (for example bracketed error text), the app now surfaces that server message directly.
- **PortAudio not found**: install `libportaudio2` (Linux) or `portaudio` via Homebrew on macOS

### Verbose logging

Set in `.env`:
```env
LOG_LEVEL=DEBUG
LOG_FILE=limescribe.log
```

## Security

- Do not commit `.env` -- it is gitignored
- Rotate API keys if exposed

## License

No license file is currently included.
