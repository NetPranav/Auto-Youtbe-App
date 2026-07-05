from common import logger
from providers.manager import ProviderManager

class VoiceGenerator:
    def __init__(self):
        self.provider = ProviderManager().get_voice_provider()
        
    def generate(self, provider_type: str, text: str, storage_dir: str) -> str:
        logger.info(f"Generating voice via ProviderManager...")
        return self.provider.generate_voice(text, storage_dir)
