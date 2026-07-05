import os
import json
from dataclasses import asdict
from datetime import datetime
from common import logger
from providers.registry.registry import ModelRegistry, ModelInfo

class ProviderCache:
    """
    Caches model discovery and benchmark results to avoid re-benchmarking every run.
    """
    def __init__(self, cache_file: str = "reports/model_benchmark/cache.json"):
        self.cache_file = cache_file
        self.registry = ModelRegistry()
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        
    def save(self):
        models = self.registry.get_all_models()
        data = []
        for m in models:
            d = asdict(m)
            d["last_checked"] = d["last_checked"].isoformat() if d["last_checked"] else None
            data.append(d)
            
        with open(self.cache_file, "w") as f:
            json.dump(data, f, indent=4)
        logger.info(f"[ProviderCache] Saved {len(data)} models to cache.")
        
    def load(self) -> bool:
        if not os.path.exists(self.cache_file):
            return False
            
        try:
            with open(self.cache_file, "r") as f:
                data = json.load(f)
                
            self.registry.clear()
            for d in data:
                if d.get("last_checked"):
                    d["last_checked"] = datetime.fromisoformat(d["last_checked"])
                model = ModelInfo(**d)
                self.registry.add_model(model)
                
            logger.info(f"[ProviderCache] Loaded {len(data)} models from cache.")
            return True
        except Exception as e:
            logger.error(f"[ProviderCache] Failed to load cache: {e}")
            return False
