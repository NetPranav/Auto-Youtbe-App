import requests
import time
from common import logger
from config import config

class ProviderHealthMonitor:
    """
    Periodically checks the health of providers.
    """
    @staticmethod
    def check_nim_health() -> bool:
        """
        Pings NVIDIA NIM models endpoint to verify API key and availability.
        """
        api_key = config.nvidia_nim_api_key
        if not api_key:
            logger.warning("[Health] NVIDIA_NIM_API_KEY not configured.")
            return False
            
        url = f"{config.nvidia_base_url}/models"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        try:
            start = time.time()
            res = requests.get(url, headers=headers, timeout=10)
            latency = (time.time() - start) * 1000
            
            if res.status_code == 200:
                logger.info(f"[Health] NVIDIA NIM is healthy. Latency: {latency:.2f}ms")
                return True
            elif res.status_code == 401:
                logger.error("[Health] NVIDIA NIM Auth Failed (401). Invalid API Key.")
                return False
            elif res.status_code == 429:
                logger.warning("[Health] NVIDIA NIM Rate Limited (429).")
                return False
            else:
                logger.error(f"[Health] NVIDIA NIM returned {res.status_code}: {res.text[:100]}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"[Health] NVIDIA NIM Unreachable: {e}")
            return False
