from typing import Any
from common import logger
from ..models import ContentStrategy

class ContentStrategist:
    """
    Determines the overall strategy before writing.
    """
    def __init__(self, ai_provider: Any = None):
        self.ai = ai_provider

    def generate_strategy(self, context_doc: str) -> ContentStrategy:
        """
        Uses AI to generate a content strategy based on the context.
        """
        logger.info("Generating content strategy...")
        
        if self.ai:
            from providers.models import TaskCategory
            prompt = f"Create a strategy for this topic: {context_doc}"
            strategy_text = self.ai.generate_text(
                prompt=prompt, 
                system_prompt="You are a YouTube content strategist.",
                task_category=TaskCategory.CONTENT_STRATEGY
            )
            # We could parse this, but for simplicity we'll just assign some defaults
            # based on whether it succeeds.
        
        # Mock AI generation based on context
        strategy = ContentStrategy(
            target_audience="Beginner to Intermediate Developers",
            objective=f"Why {context_doc[:30]}... changes everything.",
            tone="Educational but energetic",
            video_length_minutes=10,
            key_learning_outcomes=["Concept 1", "Concept 2"],
            curiosity_level="High"
        )
        
        return strategy
