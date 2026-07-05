from typing import Any, Dict, List
from common import logger

class FactChecker:
    """
    Reviews the script for factual accuracy and hallucinations.
    """
    def __init__(self, ai_provider: Any = None):
        self.ai = ai_provider

    def check(self, script: str) -> Dict[str, Any]:
        """
        Returns a score and a list of feedback notes.
        """
        logger.info("Running fact checker on script...")
        
        # Mock fact checking logic
        # If the script is very short, give it a pass, else maybe it has hallucinations
        score = 0.95
        notes = []
        if self.ai:
            from providers.models import TaskCategory
            prompt = f"Fact check this script: {script}"
            issues = self.ai.generate_text(
                prompt=prompt, 
                system_prompt="You are a strict fact checker.",
                task_category=TaskCategory.CONTENT_FACT_CHECKING
            )
            if "Error" not in issues and len(issues) > 10:
                notes.append(issues[:100])
        elif len(script) < 50:
            score = 0.5
            notes.append("Script is too short to be factually dense.")
            
        return {
            "fact_score": score,
            "feedback_notes": notes
        }
