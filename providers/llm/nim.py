import time
from typing import Any
from openai import OpenAI
from config import config
from .base import BaseLLMProvider
from providers.models import TaskCategory
from providers.statistics import ProviderStatistics
from providers.fallback.handler import ProviderFallbackHandler
from common import logger
from common.retry_helpers import with_retry

class NimLLMProvider(BaseLLMProvider):
    def __init__(self):
        api_key = config.nvidia_nim_api_key or "NO_KEY"
        if api_key == "NO_KEY":
            logger.warning("NVIDIA_NIM_API_KEY is not set. NIM LLM Provider will likely fail.")
            
        self.client = OpenAI(
            base_url=config.nvidia_base_url,
            api_key=api_key,
            timeout=config.request_timeout,
            max_retries=config.max_retries
        )
        self.fallback_handler = ProviderFallbackHandler()
        
    def generate_text(self, prompt: str, system_prompt: str = "", task_category: TaskCategory = TaskCategory.DEFAULT_REASONING) -> str:
        @with_retry(max_retries=3, delay=5, backoff=2)
        def _execute(model: str) -> str:
            logger.info(f"[NIM LLM] Routing task {task_category.value} to model: {model}")
            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1024,
            )
            response_text = completion.choices[0].message.content or ""
            return response_text

        start_time = time.time()
        success = False
        tokens = 0
        response_text = ""
        model_used = "unknown"
        
        try:
            response_text = self.fallback_handler.execute_with_fallback(task_category, _execute)
            success = True
            return response_text
        except Exception as e:
            logger.error(f"[NIM LLM] Text Generation Error after fallback exhausted: {e}")
            response_text = f"Error: {e}"
            return response_text
        finally:
            execution_time = (time.time() - start_time) * 1000
            ProviderStatistics.log_request(
                provider_name="NVIDIA NIM",
                model_used=model_used,
                request_type="generate_text",
                task_category=task_category,
                execution_time_ms=execution_time,
                success=success,
                tokens_used=tokens
            )
            
    def generate_json(self, prompt: str, system_prompt: str = "", task_category: TaskCategory = TaskCategory.DEFAULT_REASONING) -> str:
        @with_retry(max_retries=3, delay=5, backoff=2)
        def _execute(model: str) -> str:
            logger.info(f"[NIM LLM] Routing JSON task {task_category.value} to model: {model}")
            sys_prompt = system_prompt + "\nIMPORTANT: Return ONLY valid JSON."
            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1024,
            )
            content = completion.choices[0].message.content or "{}"
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            return content

        start_time = time.time()
        success = False
        tokens = 0
        response_text = "{}"
        model_used = "unknown"
        
        try:
            response_text = self.fallback_handler.execute_with_fallback(task_category, _execute)
            success = True
            return response_text
        except Exception as e:
            logger.error(f"[NIM LLM] JSON Generation Error after fallback exhausted: {e}")
            return "{}"
        finally:
            execution_time = (time.time() - start_time) * 1000
            ProviderStatistics.log_request(
                provider_name="NVIDIA NIM",
                model_used=model_used,
                request_type="generate_json",
                task_category=task_category,
                execution_time_ms=execution_time,
                success=success,
                tokens_used=tokens
            )
