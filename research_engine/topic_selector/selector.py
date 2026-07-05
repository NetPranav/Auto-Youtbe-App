from typing import List, Optional, Any
from common import logger
from ..models import RankedTopic

class TopicSelector:
    """
    Selects the single best topic from a ranked list using AI reasoning.
    """
    def __init__(self, ai_provider: Any = None):
        self.ai = ai_provider
        self.minimum_score = 3.0 # Example threshold

    def select(self, ranked_topics: List[RankedTopic]) -> Optional[RankedTopic]:
        """
        Choose the best topic.
        """
        if not ranked_topics:
            logger.info("No topics available for selection.")
            return None

        # Filter by minimum score
        viable = [t for t in ranked_topics if t.score.total_score >= self.minimum_score]
        
        if not viable:
            logger.warning("No topics met the minimum score threshold.")
            return None

        # Sort by score descending
        viable.sort(key=lambda t: t.score.total_score, reverse=True)
        
        logger.info(f"Selecting from {len(viable)} viable topics.")

        # In production, we pass the top 5 to the LLM (Executive Producer agent) 
        # to make the final subjective call.
        # Here we mock it by just picking the highest mathematically ranked one.
        best_topic = viable[0]
        
        logger.info(f"Topic Selected: {best_topic.candidate.title} (Score: {best_topic.score.total_score:.2f})")
        return best_topic
