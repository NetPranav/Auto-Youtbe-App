from typing import Any, Dict, List
from common import logger

class ScriptOptimizer:
    """
    Revises the script using feedback from reviewers.
    """
    def __init__(self, ai_provider: Any = None):
        self.ai = ai_provider

    def optimize(self, current_script: str, feedback: Dict[str, Any]) -> str:
        """
        Uses AI to rewrite the script incorporating the feedback notes.
        """
        logger.info("Optimizing script based on feedback...")
        
        if self.ai:
            from providers.models import TaskCategory
            prompt = f"Improve this script based on feedback: {feedback}\n\nScript: {current_script}"
            optimized = self.ai.generate_text(
                prompt=prompt, 
                system_prompt="You are a script editor.",
                task_category=TaskCategory.DEFAULT_REASONING
            )
            if optimized and not optimized.startswith("Error"):
                return optimized
        
        # Mock optimization
        optimized_script = current_script + "\n\n[Optimized: Improved pacing and clarified facts.]"
        
        return optimized_script
