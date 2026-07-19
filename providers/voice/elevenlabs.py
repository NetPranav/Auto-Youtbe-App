import os
import uuid
import time
from typing import Optional
from elevenlabs.client import ElevenLabs
from common import logger
from common.retry_helpers import with_retry
from config import config
from asset_engine.providers.base import BaseVoiceProvider

class ElevenLabsVoiceProvider(BaseVoiceProvider):
    @property
    def provider_name(self) -> str:
        return "ElevenLabs"

    def __init__(self):
        api_key = config.elevenlabs_api_key
        if not api_key:
            logger.warning("[ElevenLabs] ELEVENLABS_API_KEY is not set. Generation will fail.")
            
        self.client = ElevenLabs(api_key=api_key)
        
        # We can pick a highly expressive conversational voice
        # E.g. "Rachel" or "Drew"
        self.voice_id = "EXAVITQu4vr4xnSDxMaL" # Rachel

    @with_retry(max_retries=3, delay=5, backoff=2)
    def generate_voice(self, text: str, output_dir: str) -> Optional[str]:
        if not config.elevenlabs_api_key:
            logger.error("[ElevenLabs] API key missing.")
            return None
            
        try:
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, f"voice_{uuid.uuid4().hex[:8]}.mp3")
            
            logger.info(f"[ElevenLabs] Generating voice for text: '{text[:30]}...'")
            
            # Using the v2 audio generation API
            audio_generator = self.client.text_to_speech.convert(
                text=text,
                voice_id=self.voice_id,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
            )
            
            with open(file_path, "wb") as f:
                for chunk in audio_generator:
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"[ElevenLabs] Successfully saved voice to {file_path}")
            return file_path
                
        except Exception as e:
            logger.error(f"[ElevenLabs] Failed to generate voice: {e}", exc_info=True)
            return None
