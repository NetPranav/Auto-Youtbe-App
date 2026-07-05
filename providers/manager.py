from typing import Optional
from common import logger
from config import config

# We will import the actual provider instances locally to avoid circular dependencies
class ProviderManager:
    """
    Singleton manager for loading, initializing, and distributing provider instances.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProviderManager, cls).__new__(cls)
            cls._instance._initialize()
            cls._instance._bootstrap_models()
        return cls._instance

    def _initialize(self):
        self._llm_provider = None
        self._image_provider = None
        self._voice_provider = None
        self._stock_provider = None
        
    def _bootstrap_models(self):
        from providers.cache.cache import ProviderCache
        from providers.discovery.discoverer import ModelDiscoverer
        from providers.benchmark.benchmarker import ModelBenchmarker
        
        cache = ProviderCache()
        if not cache.load():
            logger.info("[ProviderManager] No cached models found. Running discovery and benchmark...")
            discoverer = ModelDiscoverer()
            discoverer.discover()
            benchmarker = ModelBenchmarker()
            benchmarker.run_benchmarks()
        
    def get_llm_provider(self):
        if not self._llm_provider:
            provider_type = config.ai_text_provider.lower()
            if provider_type == "nim":
                from .llm.nim import NimLLMProvider
                self._llm_provider = NimLLMProvider()
            else:
                from .llm.mock import MockLLMProvider
                self._llm_provider = MockLLMProvider()
        return self._llm_provider
        
    def get_image_provider(self):
        if not self._image_provider:
            provider_type = config.image_provider.lower()
            if provider_type == "nim":
                from .image.nim import NimImageProvider
                self._image_provider = NimImageProvider()
            else:
                from .image.mock import MockImageProvider
                self._image_provider = MockImageProvider()
        return self._image_provider
        
    def get_voice_provider(self):
        if not self._voice_provider:
            provider_type = config.voice_provider.lower()
            if provider_type == "edge_tts":
                from .voice.edge_tts import EdgeTTSProvider
                self._voice_provider = EdgeTTSProvider()
            else:
                from asset_engine.providers.mock import MockVoiceProvider
                self._voice_provider = MockVoiceProvider()
        return self._voice_provider
        
    def get_stock_provider(self):
        if not self._stock_provider:
            provider_type = config.stock_provider.lower()
            if provider_type == "pexels":
                from .stock.pexels import PexelsAssetFetcher
                self._stock_provider = PexelsAssetFetcher()
            else:
                from asset_engine.providers.mock import MockAssetFetcher
                self._stock_provider = MockAssetFetcher()
        return self._stock_provider
