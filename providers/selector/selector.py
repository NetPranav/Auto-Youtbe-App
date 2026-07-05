from typing import Optional, List
from common import logger
from config import config
from providers.registry.registry import ModelRegistry, ModelInfo
from providers.models import TaskCategory

class ModelSelector:
    """
    Selects the best available model for a given task based on benchmark scores and health.
    """
    def __init__(self):
        self.registry = ModelRegistry()
        
    def _get_preferred_model_id(self, category: TaskCategory) -> Optional[str]:
        # Map TaskCategory to the config variables
        mapping = {
            TaskCategory.RESEARCH_NOVELTY_ANALYSIS: config.research_model,
            TaskCategory.RESEARCH_TOPIC_EXTRACTION: config.topic_extraction_model,
            TaskCategory.RESEARCH_TOPIC_RANKING: config.topic_ranking_model,
            TaskCategory.CONTENT_STRATEGY: config.script_strategy_model,
            TaskCategory.CONTENT_HOOK_GENERATION: config.hook_generation_model,
            TaskCategory.CONTENT_OUTLINE_GENERATION: config.outline_model,
            TaskCategory.CONTENT_SCRIPT_WRITING: config.script_model,
            TaskCategory.CONTENT_FACT_CHECKING: config.fact_check_model,
            TaskCategory.CONTENT_SCRIPT_REVIEW: config.script_review_model,
            TaskCategory.CONTENT_RETENTION_ANALYSIS: config.retention_model,
            TaskCategory.CONTENT_SCENE_PLANNING: config.scene_planner_model,
            TaskCategory.CONTENT_SEO_GENERATION: config.seo_model,
        }
        return mapping.get(category)
        
    def get_best_model_for_task(self, category: TaskCategory) -> str:
        chain = self.get_fallback_chain(category)
        return chain[0]
        
    def get_fallback_chain(self, category: TaskCategory) -> list[str]:
        models = self.registry.get_healthy_models()
        if not models:
            return ["meta/llama-3.1-8b-instruct"]
            
        if category in [TaskCategory.CONTENT_HOOK_GENERATION, TaskCategory.CONTENT_SCRIPT_WRITING]:
            models.sort(key=lambda x: (x.creativity_score, -x.avg_latency_ms), reverse=True)
        else:
            models.sort(key=lambda x: (x.reasoning_score, -x.avg_latency_ms), reverse=True)
            
        chain = [m.model_id for m in models]
        
        # Insert preferred model at the front if it's healthy
        preferred_id = self._get_preferred_model_id(category)
        if preferred_id:
            preferred_model = self.registry.get_model(preferred_id)
            if preferred_model and preferred_model.is_available:
                if preferred_id in chain:
                    chain.remove(preferred_id)
                chain.insert(0, preferred_id)
                logger.debug(f"[ModelSelector] Prioritizing preferred model '{preferred_id}' for {category.value}")
            else:
                logger.warning(f"[ModelSelector] Preferred model '{preferred_id}' is unhealthy or missing. Falling back to dynamic selection.")
                
        # Limit to top 5 for the retry chain
        return chain[:5]
