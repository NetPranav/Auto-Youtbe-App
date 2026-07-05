from typing import List, Dict, Any
from common import logger
from ..models import TopicCandidate
from database.models import Topic

class DuplicateDetector:
    """
    Detects if a TopicCandidate is a duplicate of a previously approved Topic.
    Uses semantic embedding comparison.
    """
    
    def __init__(self, ai_provider: Any = None):
        self.ai = ai_provider
        # Threshold for cosine similarity (e.g., 0.85 means highly similar)
        self.similarity_threshold = 0.85

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        # Simple implementation for architectural purposes
        # In production, use numpy or scipy
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        return dot_product / (magnitude1 * magnitude2)

    def is_duplicate(self, candidate: TopicCandidate, past_topics: List[Topic]) -> bool:
        """
        Check if the candidate exists in the database.
        """
        if not past_topics:
            return False
            
        logger.debug(f"Checking duplicate for: {candidate.title}")
        
        # 1. Exact match check (cheap)
        for past in past_topics:
            if past.title.lower() == candidate.title.lower():
                logger.info(f"Duplicate found (Exact Match): {candidate.title}")
                return True

        # 2. Semantic check (expensive)
        # In a real app, self.ai.get_embedding(candidate.title + candidate.description)
        # Mock embedding for demonstration
        candidate_embedding = [0.1, 0.2, 0.3] 
        
        for past in past_topics:
            if past.embedding:
                score = self._cosine_similarity(candidate_embedding, past.embedding)
                if score >= self.similarity_threshold:
                    logger.info(f"Duplicate found (Semantic {score:.2f}): {candidate.title} ~= {past.title}")
                    return True
                    
        return False
