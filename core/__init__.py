"""Public core APIs for composition roots and external integrations."""

from core.app_config import AppConfig
from core.dialogue_service import DialogueService
from core.http_client import close_shared_client, get_shared_client
from core.transcription_service import TranscriptionService
from core.tts_service import TTSService

__all__ = [
    "AppConfig",
    "DialogueService",
    "TranscriptionService",
    "TTSService",
    "get_shared_client",
    "close_shared_client",
]
