from typing import Any
from common import logger
from ..models import TopicCandidate

class NoveltyAnalyzer:
    """
    Estimates whether a topic represents brand new tech, major updates, or old news.
    """
    def __init__(self, ai_provider: Any = None):
        self.ai = ai_provider

    def analyze(self, candidate: TopicCandidate) -> float:
        """
        Assigns a novelty score between 0.0 and 1.0.
        """
        logger.debug(f"Analyzing novelty for: {candidate.title}")
        
        if self.ai:
            from providers.models import TaskCategory
            prompt = f"Rate the novelty of this topic from 1 to 10. Topic: {candidate.title}"
            response = self.ai.generate_text(
                prompt=prompt, 
                system_prompt="You are an AI trend analyzer.",
                task_category=TaskCategory.RESEARCH_NOVELTY_ANALYSIS
            )
            # In reality we'd parse the score from response.
            score = 0.5 if "Error" not in response else 0.0
        else:
            score = 0.5  # default
            
        importance = candidate.importance.lower()
        
        if importance == "breaking":
            score = 0.95
        elif importance == "major":
            score = 0.8
        elif importance == "minor":
            score = 0.4
            
        return score
