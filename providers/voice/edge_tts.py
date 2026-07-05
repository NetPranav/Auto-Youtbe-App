import os
import uuid
import asyncio
from typing import Optional
import edge_tts
from common import logger
from config import config
from asset_engine.providers.base import BaseVoiceProvider

class EdgeTTSProvider(BaseVoiceProvider):
    @property
    def provider_name(self) -> str:
        return "EdgeTTS"

    def __init__(self):
        # Default high-quality English voice
        self.voice = "en-US-ChristopherNeural"
        
    async def _generate_async(self, text: str, output_path: str) -> None:
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_path)

    def generate_voice(self, text: str, output_dir: str) -> Optional[str]:
        try:
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, f"voice_{uuid.uuid4().hex[:8]}.mp3")
            
            logger.info(f"[EdgeTTS] Generating voice for text: '{text[:30]}...'")
            
            # edge-tts is async, but this is a sync interface, so we run the event loop
            asyncio.run(self._generate_async(text, file_path))
            
            if os.path.exists(file_path):
                logger.info(f"[EdgeTTS] Successfully saved voice to {file_path}")
                return file_path
            else:
                logger.error("[EdgeTTS] Failed to generate audio file.")
                return None
                
        except Exception as e:
            logger.error(f"[EdgeTTS] Failed to generate voice: {e}", exc_info=True)
            return None
