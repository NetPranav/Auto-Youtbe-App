import re
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
            prompt = (
                f"Rate the novelty of this topic on a scale from 1 to 10, "
                f"where 1 = very old / well-covered news and 10 = breaking / never-before-covered.\n"
                f"Topic: {candidate.title}\n"
                f"Description: {candidate.problem_definition}\n\n"
                f"Respond with ONLY a single number between 1 and 10."
            )
            try:
                response = self.ai.generate_text(
                    prompt=prompt,
                    system_prompt="You are an AI trend analyzer. Respond with ONLY a number.",
                    task_category=TaskCategory.RESEARCH_NOVELTY_ANALYSIS
                )
                # Extract the first number from the response
                numbers = re.findall(r'\b(\d+(?:\.\d+)?)\b', response)
                if numbers:
                    raw_score = float(numbers[0])
                    # Clamp to [1, 10] and normalize to [0, 1]
                    raw_score = max(1.0, min(10.0, raw_score))
                    score = raw_score / 10.0
                    logger.debug(f"[NoveltyAnalyzer] Parsed novelty score: {score:.2f} (raw: {raw_score})")
                    return score
            except Exception as e:
                logger.warning(f"[NoveltyAnalyzer] Failed to parse LLM score: {e}")

        return 0.5  # default if no AI or parsing fails

