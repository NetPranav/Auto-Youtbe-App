import time
import requests
from datetime import datetime
from common import logger
from config import config
from providers.registry.registry import ModelRegistry

class ModelValidator:
    """
    Validates that a model is operational by performing a small chat request.
    """
    def __init__(self):
        self.api_key = config.nvidia_nim_api_key
        self.base_url = config.nvidia_base_url
        self.registry = ModelRegistry()
        
    def validate_model(self, model_id: str, timeout: int = 15) -> bool:
        model = self.registry.get_model(model_id)
        if not model:
            logger.warning(f"[ModelValidator] Model {model_id} not in registry.")
            return False
            
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 5
        }
        
        start_time = time.time()
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
            latency = (time.time() - start_time) * 1000
            
            if resp.status_code == 200:
                model.is_available = True
                model.avg_latency_ms = latency
                model.last_checked = datetime.utcnow()
                logger.debug(f"[ModelValidator] {model_id} is healthy (Latency: {latency:.2f}ms)")
                return True
            else:
                model.is_available = False
                model.last_checked = datetime.utcnow()
                logger.warning(f"[ModelValidator] {model_id} failed validation: {resp.status_code} - {resp.text}")
                return False
        except Exception as e:
            model.is_available = False
            model.last_checked = datetime.utcnow()
            logger.warning(f"[ModelValidator] {model_id} exception during validation: {e}")
            return False
