import uuid
from typing import Optional, Dict
from common import logger
from providers.manager import ProviderManager
from providers.models import TaskCategory

class ImageGenerator:
    def __init__(self):
        self.provider = ProviderManager().get_image_provider()
        
    def generate(self, provider_type: str, prompt: str, output_dir: str) -> str:
        # We ignore provider_type and let the ProviderManager handle it
        logger.info(f"Generating AI image via ProviderManager...")
        
        return self.provider.generate_image(
            prompt=prompt, 
            output_dir=output_dir, 
            task_category=TaskCategory.DEFAULT_IMAGE
        )
