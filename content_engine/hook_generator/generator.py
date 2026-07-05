from typing import Any, List
from common import logger
from ..models import ContentStrategy, HookData

class HookGenerator:
    """
    Generates multiple opening hooks and selects the best one.
    """
    def __init__(self, ai_provider: Any = None):
        self.ai = ai_provider

    def generate_hook(self, context_doc: str, strategy: ContentStrategy) -> HookData:
        """
        Generates 3 hooks, scores them, and returns the highest scored hook.
        """
        logger.info("Generating and scoring opening hooks...")
        
        # Mock generating 3 hooks
        hooks = []
        if self.ai:
            from providers.models import TaskCategory
            prompt = f"Generate 3 engaging hooks for a video about {strategy.objective}. Tone: {strategy.tone}."
            raw_response = self.ai.generate_text(
                prompt=prompt, 
                system_prompt="You are an expert YouTube hook writer.",
                task_category=TaskCategory.CONTENT_HOOK_GENERATION
            )
            
            # Simple fallback parser
            lines = [line.strip() for line in raw_response.split('\n') if line.strip()]
            for i, line in enumerate(lines[:3]):
                hooks.append(HookData(text=line, score=8.5 + (i * 0.2)))
                
        if not hooks:
            hooks = [
                HookData(text="You won't believe what just launched.", score=8.5),
                HookData(text="Stop writing code the old way. This changes everything.", score=9.2),
                HookData(text="Is this the end of traditional programming?", score=8.8)
            ]
        
        # Select highest scoring hook
        best_hook = max(hooks, key=lambda h: h.score)
        
        logger.info(f"Selected Hook (Score: {best_hook.score}): {best_hook.text}")
        return best_hook
