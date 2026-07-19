import logging
from typing import Optional

logger = logging.getLogger(__name__)


class VoiceService:
    """Orchestrates wake-word detection, speech-to-text, and text-to-speech rendering pipelines."""

    def __init__(self, tts_voice: str = "default") -> None:
        self.tts_voice = tts_voice

    async def speak(self, text: str) -> None:
        logger.info(f"TTS Synthesizing with voice={self.tts_voice}: '{text}'")

    async def listen(self) -> Optional[str]:
        logger.info("STT listening for user speech")
        return None
