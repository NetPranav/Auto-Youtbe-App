from common import logger
from providers.manager import ProviderManager

class AssetFetcherManager:
    def __init__(self):
        self.provider = ProviderManager().get_stock_provider()

    def fetch(self, provider_type: str, query: str, storage_dir: str) -> str:
        logger.info(f"Fetching stock asset via ProviderManager...")
        if provider_type == "STOCK_VIDEO":
            return self.provider.fetch_video(query, storage_dir)
        else:
            return self.provider.fetch_image(query, storage_dir)
