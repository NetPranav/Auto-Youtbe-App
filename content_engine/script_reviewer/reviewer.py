from typing import Any, Dict
from common import logger

class ScriptReviewer:
    """
    Reviews the script for grammar, flow, clarity, and redundancy.
    """
    def __init__(self, ai_provider: Any = None):
        self.ai = ai_provider

    def review(self, script: str) -> Dict[str, Any]:
        """
        Returns a quality score and a list of feedback notes.
        """
        logger.info("Reviewing script quality...")
        
        # Mock review logic
        score = 0.88
        notes = ["Flow is generally good, but the transition in paragraph 3 is a bit abrupt."]
        
        if self.ai:
            from providers.models import TaskCategory
            prompt = f"Review this script: {script}"
            review = self.ai.generate_text(
                prompt=prompt, 
                system_prompt="You are a senior YouTube script reviewer.",
                task_category=TaskCategory.CONTENT_SCRIPT_REVIEW
            )
            if "Error" not in review and len(review) > 10:
                notes.append(review[:100])
            
        return {
            "script_quality_score": score,
            "feedback_notes": notes
        }
