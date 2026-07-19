import os
import uuid
import time
from typing import Optional
from google import genai
from common import logger
from common.retry_helpers import with_retry
from config import config
from .base import BaseImageProvider
from providers.models import TaskCategory
from providers.statistics import ProviderStatistics

class GeminiImageProvider(BaseImageProvider):
    def __init__(self):
        api_key = config.gemini_api_key
        if not api_key:
            logger.warning("[Gemini Image] GEMINI_API_KEY is not set. Generation will fail.")
            
        self.client = genai.Client(api_key=api_key)
        
    def generate_image(self, prompt: str, output_dir: str, task_category: TaskCategory = TaskCategory.DEFAULT_IMAGE) -> Optional[str]:
        """Generates an image using Gemini Imagen 3, with DuckDuckGo web search as fallback."""
        if not config.gemini_api_key:
            logger.error("[Gemini Image] API key missing. Falling back to web search.")
            return self._web_image_fallback(prompt, output_dir, task_category)
            
        start_time = time.time()
        success = False
        
        try:
            file_path = self._try_gemini_with_retry(prompt, output_dir)
            if file_path:
                success = True
                return file_path
            else:
                logger.warning("[Gemini Image] Gemini returned no images. Falling back to web search.")
                return self._web_image_fallback(prompt, output_dir, task_category)
        except Exception as e:
            logger.error(f"[Gemini Image] All Gemini retries exhausted: {e}. Falling back to web search.")
            return self._web_image_fallback(prompt, output_dir, task_category)
        finally:
            execution_time = (time.time() - start_time) * 1000
            ProviderStatistics.log_request(
                provider_name="Gemini Imagen 3",
                model_used="imagen-3.0-generate-001",
                request_type="generate_image",
                task_category=task_category,
                execution_time_ms=execution_time,
                success=success
            )
    
    @with_retry(max_retries=3, delay=5, backoff=2)
    def _try_gemini_with_retry(self, prompt: str, output_dir: str) -> Optional[str]:
        """Inner method that raises exceptions so @with_retry can catch them."""
        enhanced_prompt = f"Cinematic, high quality, highly detailed, visually stunning, YouTube documentary style. {prompt}"
        logger.info(f"[Gemini Image] Requesting image via Imagen 3 for prompt: {prompt[:50]}...")
        
        result = self.client.models.generate_images(
            model='imagen-3.0-generate-001',
            prompt=enhanced_prompt,
            config=dict(
                number_of_images=1,
                output_mime_type="image/jpeg",
                aspect_ratio="16:9"  # Standard YouTube landscape
            )
        )
        
        if result.generated_images:
            generated_image = result.generated_images[0]
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, f"gemini_image_{uuid.uuid4().hex[:8]}.jpg")
            generated_image.image.save(file_path)
            return file_path
        
        return None
    
    def _web_image_fallback(self, prompt: str, output_dir: str, task_category: TaskCategory = TaskCategory.DEFAULT_IMAGE) -> Optional[str]:
        """Falls back to DuckDuckGo image search if Gemini fails."""
        try:
            import requests
            from duckduckgo_search import DDGS
            import re
            
            # Clean prompt for better search results
            clean = re.sub(r'[^a-zA-Z0-9 ]', '', prompt)
            query = " ".join(clean.split()[:6])
            if not query:
                query = "technology"
                
            logger.info(f"[Gemini Image] Web image search for: '{query}'")
            results = DDGS().images(query, max_results=3)
            
            for img_result in (results or []):
                try:
                    image_url = img_result.get("image")
                    if not image_url:
                        continue
                    logger.info(f"[Gemini Image] Downloading web image: {image_url[:60]}...")
                    img_res = requests.get(image_url, timeout=15)
                    img_res.raise_for_status()
                    
                    os.makedirs(output_dir, exist_ok=True)
                    file_path = os.path.join(output_dir, f"web_image_{uuid.uuid4().hex[:8]}.jpg")
                    with open(file_path, "wb") as f:
                        f.write(img_res.content)
                    
                    logger.info(f"[Gemini Image] Web fallback image saved: {file_path}")
                    return file_path
                except Exception as dl_err:
                    logger.warning(f"[Gemini Image] Failed to download web image: {dl_err}")
                    continue
                    
            logger.error(f"[Gemini Image] Web image search found no usable results for '{query}'.")
            return None
        except Exception as e:
            logger.error(f"[Gemini Image] Web image search failed completely: {e}")
            return None
