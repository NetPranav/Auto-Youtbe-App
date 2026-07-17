import os
import requests
import base64
import uuid
import time
from typing import Optional
from common import logger
from config import config
from .base import BaseImageProvider
from providers.models import TaskCategory
from providers.statistics import ProviderStatistics

class NimImageProvider(BaseImageProvider):
    def __init__(self):
        self.client = requests.Session()
        
    def generate_image(self, prompt: str, output_dir: str, task_category: TaskCategory = TaskCategory.DEFAULT_IMAGE) -> Optional[str]:
        api_key = config.nvidia_nim_api_key
        if not api_key:
            logger.error("NVIDIA_NIM_API_KEY is not set. Cannot generate image.")
            return None
            
        url = f"{config.nvidia_base_url}/images/generations"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # We just use the default image model instead of dynamic routing since images aren't benchmarked
        model = config.default_image_model
        
        payload = {
            "prompt": prompt,
            "model": model,
            "n": 1,
            "size": "1024x1024",
            "response_format": "b64_json"
        }
        
        start_time = time.time()
        success = False
        
        try:
            logger.info(f"[NIM Image] Requesting image via model {model} for prompt: {prompt[:30]}...")
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            if "data" in data and len(data["data"]) > 0:
                b64_data = data["data"][0]["b64_json"]
                image_bytes = base64.b64decode(b64_data)
                
                os.makedirs(output_dir, exist_ok=True)
                file_path = os.path.join(output_dir, f"nim_image_{uuid.uuid4().hex[:8]}.png")
                
                with open(file_path, "wb") as f:
                    f.write(image_bytes)
                
                success = True
                return file_path
            else:
                logger.error("[NIM Image] API returned no image data.")
                return None
        except Exception as e:
            logger.error(f"[NIM Image] API request failed: {e}. Falling back to free Pollinations API...", exc_info=True)
            try:
                import urllib.parse
                from common.retry_helpers import with_retry
                
                @with_retry(max_retries=3, delay=5, backoff=2)
                def _try_pollinations():
                    encoded_prompt = urllib.parse.quote(prompt)
                    fallback_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
                    res = requests.get(fallback_url, timeout=30)
                    res.raise_for_status()
                    return res.content

                image_bytes = _try_pollinations()
                
                os.makedirs(output_dir, exist_ok=True)
                file_path = os.path.join(output_dir, f"fallback_image_{uuid.uuid4().hex[:8]}.jpg")
                with open(file_path, "wb") as f:
                    f.write(image_bytes)
                
                success = True
                return file_path
                
            except Exception as pollinations_e:
                logger.error(f"[NIM Image] Pollinations also failed: {pollinations_e}. Falling back to Web Image Search...")
                try:
                    from duckduckgo_search import DDGS
                    # Extract a short query from the prompt for better search results
                    words = prompt.split()
                    query = " ".join(words[:5]).replace("A cinematic representation of:", "").strip()
                    if not query:
                        query = "technology"
                        
                    results = DDGS().images(query, max_results=1)
                    if results and len(results) > 0:
                        image_url = results[0].get("image")
                        logger.info(f"[NIM Image] Found web image for '{query}': {image_url}")
                        
                        img_res = requests.get(image_url, timeout=30)
                        img_res.raise_for_status()
                        
                        os.makedirs(output_dir, exist_ok=True)
                        file_path = os.path.join(output_dir, f"web_fallback_image_{uuid.uuid4().hex[:8]}.jpg")
                        with open(file_path, "wb") as f:
                            f.write(img_res.content)
                            
                        success = True
                        return file_path
                    else:
                        logger.error(f"[NIM Image] Web Image Search found no results for '{query}'.")
                        return None
                except Exception as search_e:
                    logger.error(f"[NIM Image] Web Image Search failed completely: {search_e}")
                    return None
        finally:
            execution_time = (time.time() - start_time) * 1000
            ProviderStatistics.log_request(
                provider_name="NVIDIA NIM Image",
                model_used=model,
                request_type="generate_image",
                task_category=task_category,
                execution_time_ms=execution_time,
                success=success
            )
