import time
from .base import BaseLLMProvider
from providers.models import TaskCategory
from providers.statistics import ProviderStatistics
from common import logger

class MockLLMProvider(BaseLLMProvider):
    def generate_text(self, prompt: str, system_prompt: str = "", task_category: TaskCategory = TaskCategory.DEFAULT_REASONING) -> str:
        start_time = time.time()
        # Simulate network latency
        time.sleep(0.01)
        response = f"Mocked AI response for prompt: {prompt[:30]}..."
        
        execution_time = (time.time() - start_time) * 1000
        
        ProviderStatistics.log_request(
            provider_name="MockLLM",
            model_used="mock-model",
            request_type="generate_text",
            task_category=task_category,
            execution_time_ms=execution_time,
            success=True,
            tokens_used=len(response.split())
        )
        return response
        
    def generate_json(self, prompt: str, system_prompt: str = "", task_category: TaskCategory = TaskCategory.DEFAULT_REASONING) -> str:
        start_time = time.time()
        time.sleep(0.01)
        response = '{"status": "mocked", "result": "success"}'
        
        execution_time = (time.time() - start_time) * 1000
        
        ProviderStatistics.log_request(
            provider_name="MockLLM",
            model_used="mock-json-model",
            request_type="generate_json",
            task_category=task_category,
            execution_time_ms=execution_time,
            success=True
        )
        return response
