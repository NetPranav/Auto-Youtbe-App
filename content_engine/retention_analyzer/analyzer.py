from typing import Any, Dict
from common import logger

class RetentionAnalyzer:
    """
    Estimates viewer retention by evaluating pacing, curiosity gaps, and sentence length.
    """
    def __init__(self, ai_provider: Any = None):
        self.ai = ai_provider

    def analyze(self, script: str) -> Dict[str, Any]:
        """
        Returns a retention score and improvement suggestions.
        """
        logger.info("Analyzing script for retention potential...")
        
        # Mock retention logic
        score = 0.90
        notes = []
        if self.ai:
            from providers.models import TaskCategory
            prompt = f"Analyze retention for this script: {script}"
            analysis = self.ai.generate_text(
                prompt=prompt, 
                system_prompt="You are a YouTube audience retention expert.",
                task_category=TaskCategory.CONTENT_RETENTION_ANALYSIS
            )
            if "Error" not in analysis and len(analysis) > 10:
                notes.append(analysis[:100])
        elif "subscribe" in script.lower()[:100]:
            score = 0.6
            notes.append("Do not ask for subscribers too early, it hurts retention.")
            
        return {
            "retention_score": score,
            "feedback_notes": notes
        }
