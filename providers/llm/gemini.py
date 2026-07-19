import time
from typing import Optional
from google import genai
from common import logger
from common.retry_helpers import with_retry
from config import config
from .base import BaseLLMProvider
from providers.models import TaskCategory
from providers.statistics import ProviderStatistics

class GeminiLLMProvider(BaseLLMProvider):
    def __init__(self):
        api_key = config.gemini_api_key
        if not api_key:
            logger.warning("[Gemini LLM] GEMINI_API_KEY is not set. Text generation will fail.")
            
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash"
        
    @with_retry(max_retries=3, delay=5, backoff=2)
    def generate_text(self, prompt: str, system_prompt: str = "", task_category: TaskCategory = TaskCategory.DEFAULT_REASONING) -> str:
        if not config.gemini_api_key:
            logger.error("[Gemini LLM] API key missing.")
            return f"Error: API Key missing for Gemini"
            
        start_time = time.time()
        success = False
        response_text = ""
        
        try:
            logger.info(f"[Gemini LLM] Routing task {task_category.value} to model: {self.model_name}")
            
            full_prompt = f"System Instruction: {system_prompt}\n\nUser Request: {prompt}" if system_prompt else prompt
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=dict(temperature=0.7)
            )
            
            response_text = response.text or ""
            success = True
            return response_text
        except Exception as e:
            logger.error(f"[Gemini LLM] Text Generation Error: {e}", exc_info=True)
            return f"Error: {e}"
        finally:
            execution_time = (time.time() - start_time) * 1000
            ProviderStatistics.log_request(
                provider_name="Gemini LLM",
                model_used=self.model_name,
                request_type="generate_text",
                task_category=task_category,
                execution_time_ms=execution_time,
                success=success,
                tokens_used=0
            )
            
    @with_retry(max_retries=3, delay=5, backoff=2)
    def generate_json(self, prompt: str, system_prompt: str = "", task_category: TaskCategory = TaskCategory.DEFAULT_REASONING) -> str:
        if not config.gemini_api_key:
            return "{}"
            
        start_time = time.time()
        success = False
        response_text = "{}"
        
        try:
            logger.info(f"[Gemini LLM] Routing JSON task {task_category.value} to model: {self.model_name}")
            
            sys_prompt = system_prompt + "\nIMPORTANT: Return ONLY valid JSON."
            full_prompt = f"System Instruction: {sys_prompt}\n\nUser Request: {prompt}"
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=dict(temperature=0.1)
            )
            
            content = response.text or "{}"
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
                
            response_text = content
            success = True
            return response_text
        except Exception as e:
            logger.error(f"[Gemini LLM] JSON Generation Error: {e}")
            return "{}"
        finally:
            execution_time = (time.time() - start_time) * 1000
            ProviderStatistics.log_request(
                provider_name="Gemini LLM",
                model_used=self.model_name,
                request_type="generate_json",
                task_category=task_category,
                execution_time_ms=execution_time,
                success=success,
                tokens_used=0
            )
