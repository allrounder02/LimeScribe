import os
from dotenv import load_dotenv

load_dotenv()

LEMONFOX_API_KEY = os.getenv("LEMONFOX_API_KEY", "")
LEMONFOX_LANGUAGE = os.getenv("LEMONFOX_LANGUAGE", "english")
LEMONFOX_RESPONSE_FORMAT = os.getenv("LEMONFOX_RESPONSE_FORMAT", "json")
VAD_PAUSE_THRESHOLD = float(os.getenv("VAD_PAUSE_THRESHOLD", "1.5"))

API_URL = "https://api.lemonfox.ai/v1/audio/transcriptions"
