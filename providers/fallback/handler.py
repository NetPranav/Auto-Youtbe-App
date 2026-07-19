import time
from typing import Callable, Any
from common import logger
from providers.registry.registry import ModelRegistry
from providers.selector.selector import ModelSelector
from providers.models import TaskCategory

class ProviderFallbackHandler:
    """
    Intercepts calls to the provider, detects failures (timeouts, 500s), 
    marks models as unhealthy, and retries with the next best model.
    """
    def __init__(self):
        self.registry = ModelRegistry()
        self.selector = ModelSelector()
        
    def execute_with_fallback(self, task_category: TaskCategory, func: Callable[[str], Any]) -> Any:
        fallback_chain = self.selector.get_fallback_chain(task_category)
        
        for attempt, model_id in enumerate(fallback_chain):
            try:
                if attempt > 0:
                    logger.warning(f"[FallbackHandler] Fallback triggered! Attempt {attempt+1}/{len(fallback_chain)} using model: {model_id}")
                else:
                    logger.debug(f"[FallbackHandler] Executing with primary model: {model_id}")
                result = func(model_id)
                # If success, return result
                return result
            except Exception as e:
                logger.error(f"[FallbackHandler] Model {model_id} failed: {e}")
                # Mark as unhealthy
                model = self.registry.get_model(model_id)
                if model:
                    model.is_available = False
                    model.timeout_rate += 0.1
                
                if attempt == len(fallback_chain) - 1:
                    logger.critical("[FallbackHandler] All fallback models exhausted. Raising exception.")
                    # Error handling logic as requested: produce diagnostic
                    self._generate_diagnostic_report(fallback_chain)
                    raise e
                    
    def _generate_diagnostic_report(self, chain):
        logger.critical(f"=== NVIDIA NIM DIAGNOSTIC REPORT ===")
        logger.critical(f"Attempted models: {chain}")
        logger.critical(f"All models failed due to timeouts or API errors.")
        logger.critical(f"Please check API Key and network connectivity.")
