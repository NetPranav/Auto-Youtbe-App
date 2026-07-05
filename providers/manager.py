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

    def get_provider(self, provider_type: str):
        """Generic accessor for engines."""
        if provider_type == "content":
            return self.get_llm_provider()
        elif provider_type == "image":
            return self.get_image_provider()
        elif provider_type == "voice":
            return self.get_voice_provider()
        elif provider_type == "stock":
            return self.get_stock_provider()
        raise ValueError(f"Unknown provider type: {provider_type}")
        
    def collaborative_generate(self, prompt: str, task_context: str, db_session, agent_count: int = 3) -> str:
        """
        Seamless integration point for engines.
        Routes the generation request through the multi-agent AI Editorial Board.
        """
        try:
            # We import locally to avoid circular dependencies at startup
            from multi_agent.pipeline import MultiAgentPipeline
            pipeline = MultiAgentPipeline(db_session, self)
            return pipeline.run_collaborative(prompt, task_context, agent_count)
        except Exception as e:
            logger.error(f"[ProviderManager] Collaborative generation failed: {e}. Falling back to single-model generation.")
            provider = self.get_llm_provider()
            return provider.generate_text(prompt, max_tokens=2500)

