import json
from typing import Optional, Any
from common import logger
from ..models import ArticleData, TopicCandidate

class TopicExtractor:
    """
    AI-assisted extraction of potential video topics from normalized articles.
    """
    def __init__(self, ai_provider: Any = None):
        self.ai = ai_provider

    def extract(self, article: ArticleData) -> Optional[TopicCandidate]:
        """
        Uses an LLM to extract a topic from the article.
        """
        if self.ai:
            from providers.models import TaskCategory
            prompt = f"Extract a JSON topic from this text: {article.title}\n{article.summary or article.full_text}"
            # In a real scenario we'd pass a JSON schema in the system prompt
            # and call `self.ai.generate_json(...)`.
            resp = self.ai.generate_json(
                prompt=prompt,
                task_category=TaskCategory.RESEARCH_TOPIC_EXTRACTION
            )
        
        logger.debug(f"Extracting topic from: {article.title}")
        
        try:
            # In a real implementation, we would load `prompts/extractor.yaml` 
            # and call `self.ai.generate_json(...)`.
            
            # Mock AI behavior
            mock_json = {
                "title": f"Why {article.title} Changes Everything",
                "main_technology": "Unknown Tech",
                "secondary_technologies": article.tags[:3] if article.tags else [],
                "industry": "Software Engineering",
                "importance": "Major",
                "estimated_audience": "Broad",
                "description": article.summary or "A detailed look into this new technology."
            }
            
            candidate = TopicCandidate(**mock_json)
            return candidate
            
        except Exception as e:
            logger.error(f"Failed to extract topic from {article.url}: {e}")
            return None
