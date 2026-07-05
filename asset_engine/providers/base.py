from abc import ABC, abstractmethod
from typing import Optional

class BaseImageProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    def generate_image(self, prompt: str, output_path: str) -> Optional[str]:
        """Generates an image and saves it to output_path. Returns the path if successful."""
        pass

class BaseVoiceProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    def generate_voice(self, text: str, output_path: str) -> Optional[str]:
        """Generates audio and saves it to output_path. Returns the path if successful."""
        pass

class BaseAssetFetcher(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    def fetch_asset(self, query: str, output_path: str) -> Optional[str]:
        """Fetches a stock asset/logo/screenshot and saves it to output_path. Returns path if successful."""
        pass
