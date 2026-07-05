import requests
from datetime import datetime
from common import logger
from config import config
from providers.registry.registry import ModelRegistry, ModelInfo

class ModelDiscoverer:
    """
    Fetches the live list of models from NVIDIA NIM and stores them in the registry.
    """
    def __init__(self):
        self.api_key = config.nvidia_nim_api_key
        self.base_url = config.nvidia_base_url
        self.registry = ModelRegistry()
        
    def discover(self):
        if not self.api_key or self.api_key == "NO_KEY":
            logger.warning("[ModelDiscoverer] NVIDIA API Key not set. Cannot discover models.")
            return []
            
        url = f"{self.base_url}/models"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"[ModelDiscoverer] Discovering models from {url}...")
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                data = resp.json().get("data", [])
                models_found = []
                for item in data:
                    model_id = item.get("id")
                    if not model_id:
                        continue
                    
                    capabilities = []
                    # Infer capabilities from name
                    name_lower = model_id.lower()
                    if "vision" in name_lower or "vl" in name_lower:
                        capabilities.append("vision")
                    if "instruct" in name_lower:
                        capabilities.append("instruct")
                    if "chat" in name_lower:
                        capabilities.append("chat")
                    if "embed" in name_lower:
                        capabilities.append("embedding")
                    
                    info = ModelInfo(
                        model_id=model_id,
                        provider="nvidia_nim",
                        capabilities=capabilities,
                        last_checked=datetime.utcnow()
                    )
                    self.registry.add_model(info)
                    models_found.append(info)
                    
                logger.info(f"[ModelDiscoverer] Discovered {len(models_found)} models.")
                return models_found
            else:
                logger.error(f"[ModelDiscoverer] Failed to discover models: {resp.status_code} - {resp.text}")
                return []
        except Exception as e:
            logger.error(f"[ModelDiscoverer] Exception during discovery: {e}")
            return []
