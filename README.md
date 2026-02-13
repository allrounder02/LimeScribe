# LimeScribe

LimeScribe is a desktop speech-to-text app for **Windows 11** built with **PyQt6** and the **LemonFox.ai** transcription API.

It supports three workflows:
- **Listening mode**: always-on microphone listening with VAD (auto-chunks speech on pause)
- **Recording mode**: manual start/pause/stop recording
- **File mode**: transcribe audio files from disk

The app runs with a system tray icon, global hotkeys, and auto-copies transcription output to clipboard.

## Features

- PyQt6 desktop UI with tabs for Listening / Recording / File
- System tray support with status color:
  - Gray: idle
  - Green: listening
  - Red: recording
- Global hotkeys:
  - `Ctrl+Alt+L` toggle listening
  - `Ctrl+Alt+R` toggle recording
  - Both are configurable in the **Settings** tab
- Voice Activity Detection (`webrtcvad`) for pause-based chunking
- LemonFox API integration for both recorded audio bytes and local files
- Clipboard output (`pyperclip`) and optional paste helpers (`pyautogui`)

## Requirements

- Windows 11 (recommended runtime platform)
- Python 3.10+
- LemonFox API key
- Microphone access

Notes:
- The project can be edited from WSL2, but GUI/audio/hotkeys need native Windows to run correctly.
- `.env` is required for API auth and options.

## Installation

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies.

```bash
python -m venv .venv
# PowerShell
.\.venv\Scripts\Activate.ps1
# or CMD
.venv\Scripts\activate.bat

pip install -r requirements.txt
```

## Configuration

Create a `.env` file from `.env.example` and set your values:

```env
LEMONFOX_API_KEY=your_api_key_here
LEMONFOX_LANGUAGE=english
LEMONFOX_RESPONSE_FORMAT=json
VAD_PAUSE_THRESHOLD=1.5
VAD_AGGRESSIVENESS=3
VAD_MIN_SPEECH_SECONDS=0.5
LEMONFOX_API_URL=https://api.lemonfox.ai/v1/audio/transcriptions
LEMONFOX_API_FALLBACK_URL=https://transcribe.whisperapi.com
```

Environment variables:
- `LEMONFOX_API_KEY`: required API key
- `LEMONFOX_LANGUAGE`: transcription language (default `english`)
- `LEMONFOX_RESPONSE_FORMAT`: API response format (default `json`)
- `VAD_PAUSE_THRESHOLD`: seconds of silence before chunk submission in Listening mode
- `VAD_AGGRESSIVENESS`: VAD strictness `0-3` (higher is stricter, default `3`)
- `VAD_MIN_SPEECH_SECONDS`: minimum voiced speech before sending a chunk (default `0.5`)
- `LEMONFOX_API_URL`: primary transcription endpoint
- `LEMONFOX_API_FALLBACK_URL`: fallback endpoint if primary is unreachable

## Run

```bash
python app.py
```

The app starts in the tray and opens the main window.

## Usage

### Listening tab
- Click **Start Listening** (or press `Ctrl+Alt+L`).
- Speak normally; the app detects pauses and sends chunks for transcription.
- Transcribed chunks are appended to output and copied to clipboard.

### Recording tab
- Click **Start**, then **Pause/Resume** as needed.
- Click **Stop** to transcribe the captured audio.
- Result appears in output and is copied to clipboard.

### File tab
- Click **Select File** and choose an audio file.
- Supported picker filter: `.mp3`, `.wav`, `.flac`, `.m4a`, `.ogg`
- Click **Transcribe** to process and display text.

### Tray menu
- Show Window
- Start Listening
- Start Recording
- Quit

### Window behavior
- Click window `X` to fully quit the app (terminal process ends).
- Use **Minimize to Tray** to keep the app running in the background tray.

### Settings tab
- View and edit global keyboard shortcuts for:
  - Toggle Listening
  - Toggle Recording
- Save changes without restarting the app
- Restore default shortcuts

## Optional CLI Smoke Test

A basic mic-to-API command line test is included:

```bash
python cli_test.py
```

It records until Enter is pressed, then prints transcription.

## Project Structure

```text
app.py                  # App entrypoint (Qt app + tray + hotkeys)
config.py               # .env settings loader
hotkeys.py              # Global hotkey registration
cli_test.py             # CLI smoke test
core/
  audio_recorder.py     # Mic recording to WAV bytes
  vad_listener.py       # Continuous listening + VAD chunking
  lemonfox_client.py    # LemonFox transcription API wrapper
  text_output.py        # Clipboard + paste/type helpers
ui/
  main_window.py        # Main UI and mode logic
  tray_icon.py          # Tray icon states and menu
```

## Troubleshooting

- `401 Unauthorized`: check `LEMONFOX_API_KEY` in `.env`.
- No mic input: verify Windows microphone permissions and default input device.
- Hotkeys not firing: run app in native Windows desktop session (not headless/WSL GUI).
- Clipboard/paste issues: ensure focused target app accepts `Ctrl+V`.
- Repeated idle text (for example repeated "Thank you"):
  - Set `VAD_AGGRESSIVENESS=3` in `.env`.
  - Set `VAD_MIN_SPEECH_SECONDS=0.5` in `.env`.
  - If it still happens, increase `VAD_MIN_SPEECH_SECONDS` to `0.7`.

## Security

- Do not commit `.env`.
- Rotate API keys if they are exposed.

## License

No license file is currently included.
