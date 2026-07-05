from config import config
from common import logger
from research_engine.models.topic import TopicCandidate, TopicScoreData
from typing import Any

class TopicRanker:
    """
    Scores and ranks extracted topics to determine which one is best.
    """
    def __init__(self, ai_provider: Any = None):
        if not ai_provider:
            from providers.manager import ProviderManager
            ai_provider = ProviderManager().get_llm_provider()
        self.ai = ai_provider
        # Load weights from central config
        self.weights = {
            "novelty": config.weight_novelty,
            "audience": config.weight_audience,
            "educational": config.weight_educational,
            "recency": config.weight_recency,
            "competition": config.weight_competition,
            "search_interest": config.weight_search_interest
        }

    def rank(self, candidate: TopicCandidate, novelty_score: float) -> TopicScoreData:
        """
        Calculates the total score based on weights and heuristics.
        Returns a TopicScoreData object.
        """
        if self.ai:
            from providers.models import TaskCategory
            prompt = f"Score this topic out of 10: {candidate.title}"
            response = self.ai.generate_text(
                prompt=prompt, 
                system_prompt="You are an analyst.",
                task_category=TaskCategory.RESEARCH_TOPIC_RANKING
            )
            
        logger.debug(f"Ranking topic: {candidate.title}")
        
        # Audience heuristic
        aud = candidate.estimated_audience.lower()
        audience_score = 1.0 if aud == "mass" else (0.7 if aud == "broad" else 0.3)
        
        # Dummy values for external factors (Search interest, competition)
        # In production, these might query Google Trends APIs
        educational_value = 0.8
        search_interest = 0.6
        competition = 0.4 # Lower is better? We'll invert it in math or assume 0.4 is "low competition" (good). Let's assume 1.0 is best.
        recency = 0.9
        
        total_score = (
            (novelty_score * self.weights["novelty"]) +
            (audience_score * self.weights["audience"]) +
            (educational_value * self.weights["educational"]) +
            (recency * self.weights["recency"]) +
            (competition * self.weights["competition"]) +
            (search_interest * self.weights["search_interest"])
        )
        
        return TopicScoreData(
            novelty=novelty_score,
            audience_size=audience_score,
            educational_value=educational_value,
            search_interest=search_interest,
            competition=competition,
            recency=recency,
            total_score=total_score
        )
