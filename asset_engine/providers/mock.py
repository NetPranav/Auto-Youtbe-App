import os
from typing import Optional
from common import logger
from .base import BaseImageProvider, BaseVoiceProvider, BaseAssetFetcher

class MockImageProvider(BaseImageProvider):
    @property
    def provider_name(self) -> str:
        return "MockImage"

    def generate_image(self, prompt: str, output_path: str) -> Optional[str]:
        logger.info(f"[{self.provider_name}] Mocking image generation for prompt: '{prompt[:30]}...'")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        # Touch a dummy file
        with open(output_path, "w") as f:
            f.write(f"Mock Image Data for prompt: {prompt}")
        return output_path

class MockVoiceProvider(BaseVoiceProvider):
    @property
    def provider_name(self) -> str:
        return "MockVoice"

    def generate_voice(self, text: str, output_path: str) -> Optional[str]:
        logger.info(f"[{self.provider_name}] Mocking voice generation for text: '{text[:30]}...'")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        # Touch a dummy file
        with open(output_path, "w") as f:
            f.write(f"Mock Audio Data for text: {text}")
        return output_path

class MockAssetFetcher(BaseAssetFetcher):
    @property
    def provider_name(self) -> str:
        return "MockFetcher"

    def fetch_asset(self, query: str, output_path: str) -> Optional[str]:
        logger.info(f"[{self.provider_name}] Mocking asset fetch for query: '{query}'")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        # Touch a dummy file
        with open(output_path, "w") as f:
            f.write(f"Mock Fetched Data for query: {query}")
        return output_path
