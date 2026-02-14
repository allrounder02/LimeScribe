# Headless Setup Tutorial

This guide covers running LimeScribe without a GUI -- on a Linux server, in a Docker container, or in any environment where you need speech-to-text and text-to-speech via the command line.

## Prerequisites

- A LemonFox API key (get one at [lemonfox.ai](https://lemonfox.ai))
- Python 3.12+ **or** Docker
- Audio files to transcribe (for file mode), or a microphone (for listening mode)

## Option A: Direct Python Install

### 1. Clone and enter the project

```bash
git clone <repo-url>
cd ZestVoice
```

### 2. Install core dependencies only

You do not need PyQt6, pyautogui, pynput, or pyperclip for headless mode.

```bash
python -m venv .venv
source .venv/bin/activate

pip install httpx[http2] sounddevice numpy webrtcvad python-dotenv
```

If you plan to use microphone-based modes (listening or recording), install PortAudio:

```bash
# Debian / Ubuntu
sudo apt-get install libportaudio2

# Fedora
sudo dnf install portaudio

# macOS
brew install portaudio
```

File transcription and TTS do **not** require PortAudio -- they only make HTTP calls to the API.

### 3. Configure your API key

```bash
cp .env.example .env
```

Edit `.env` and set your key:

```env
LEMONFOX_API_KEY=your_api_key_here
```

All other settings have sensible defaults. See the [configuration table in README.md](README.md#configuration) for the full list.

### 4. Run the CLI

**Transcribe a file:**

```bash
python cli.py transcribe path/to/audio.wav
```

The transcribed text is printed to stdout. You can pipe it:

```bash
python cli.py transcribe meeting.mp3 > transcript.txt
```

**Text-to-speech:**

```bash
python cli.py tts "Hello, this is a test." -o output.wav
```

The generated audio is saved to the specified file.

**VAD listening mode** (requires microphone + PortAudio):

```bash
python cli.py listen
```

This runs continuously, printing each transcribed chunk to stdout. Press `Ctrl+C` to stop.

**Debug logging:**

```bash
python cli.py --log-level DEBUG transcribe audio.wav
```

## Option B: Docker

### 1. Build the image

```bash
docker build -t limescribe .
```

The Dockerfile installs only core dependencies (no GUI packages). The image is based on `python:3.12-slim` with `libportaudio2` for optional mic support.

### 2. Create your .env file

```bash
cp .env.example .env
# Edit .env and set LEMONFOX_API_KEY
```

### 3. Transcribe a file

```bash
docker run --rm \
    -v $(pwd)/.env:/app/.env \
    -v /path/to/audio:/data \
    limescribe transcribe /data/recording.wav
```

The transcription is printed to stdout. Capture it with:

```bash
docker run --rm \
    -v $(pwd)/.env:/app/.env \
    -v /path/to/audio:/data \
    limescribe transcribe /data/recording.wav > transcript.txt
```

### 4. Text-to-speech

```bash
docker run --rm \
    -v $(pwd)/.env:/app/.env \
    -v $(pwd)/output:/data \
    limescribe tts "Generate this speech" -o /data/output.wav
```

The audio file appears in `./output/output.wav`.

### 5. Environment variables instead of .env

You can pass the API key directly without mounting a file:

```bash
docker run --rm \
    -e LEMONFOX_API_KEY=your_key_here \
    -v /path/to/audio:/data \
    limescribe transcribe /data/audio.wav
```

Override any setting with `-e`:

```bash
docker run --rm \
    -e LEMONFOX_API_KEY=your_key_here \
    -e LEMONFOX_LANGUAGE=german \
    -v /path/to/audio:/data \
    limescribe transcribe /data/interview_de.mp3
```

## Option C: Docker Compose

For repeated use or integration with other services, create a `docker-compose.yml`:

```yaml
services:
  limescribe:
    build: .
    env_file: .env
    volumes:
      - ./audio:/data
    entrypoint: ["python", "cli.py"]
```

Then run:

```bash
# Transcribe
docker compose run --rm limescribe transcribe /data/meeting.wav

# TTS
docker compose run --rm limescribe tts "Hello world" -o /data/hello.wav
```

## Integrating with Other Applications

The `core/` layer is a standalone Python SDK. You can import it directly in your own code without any GUI dependencies:

```python
from core.app_config import AppConfig
from core.transcription_service import TranscriptionService
from core.tts_service import TTSService
from core.http_client import close_shared_client

config = AppConfig.from_env()

# Transcribe a file (synchronous wrapper)
import threading

done = threading.Event()
result = {}

def on_text(text):
    result["text"] = text
    done.set()

stt = TranscriptionService(config, on_transcription=on_text)
stt.transcribe_file("audio.wav")
done.wait(timeout=120)

print(result["text"])

# Text-to-speech
done.clear()
audio_result = {}

def on_audio(audio_bytes):
    audio_result["audio"] = audio_bytes
    done.set()

tts = TTSService(config, on_audio_ready=on_audio)
tts.synthesize("Hello world")
done.wait(timeout=120)

with open("output.wav", "wb") as f:
    f.write(audio_result["audio"])

# Clean up
close_shared_client()
```

### Wrapping in a REST API

You can expose LimeScribe as an HTTP service using FastAPI or Flask:

```python
# Example: FastAPI wrapper (not included in repo)
from fastapi import FastAPI, UploadFile
from core.app_config import AppConfig
from core.lemonfox_client import LemonFoxClient

app = FastAPI()
config = AppConfig.from_env()
client = LemonFoxClient(config=config)

@app.post("/transcribe")
async def transcribe(file: UploadFile):
    audio_bytes = await file.read()
    text = client.transcribe_bytes(audio_bytes, filename=file.filename)
    return {"text": text}
```

## Troubleshooting

**"PortAudio library not found"** -- Install `libportaudio2` (Debian/Ubuntu) or `portaudio` (Fedora/macOS). This is only needed for microphone modes, not file transcription or TTS.

**"No module named 'core'"** -- Make sure you run `cli.py` from the project root directory, not from inside a subdirectory.

**API timeout** -- The default timeout is 120 seconds. For very large files, the API may take longer. Check your network connection and API key validity.

**Empty transcription** -- Verify the audio file is not silent or corrupted. Try a known-good WAV file first. Check `--log-level DEBUG` output for API response details.
