FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libportaudio2 \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install core dependencies only (no GUI)
RUN pip install --no-cache-dir \
    httpx[http2]>=0.27 \
    sounddevice>=0.4 \
    numpy>=1.24 \
    webrtcvad>=2.0.10 \
    python-dotenv>=1.0

COPY core/ core/
COPY config.py .
COPY cli.py .

# .env must be provided at runtime (mount or env vars)
# docker run -v /path/to/.env:/app/.env limescribe transcribe /data/audio.wav

ENTRYPOINT ["python", "cli.py"]
CMD ["--help"]
