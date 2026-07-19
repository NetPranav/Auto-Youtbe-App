import os
import yaml
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
        logger.debug(f"Extracting topic from: {article.title}")
        
        if self.ai:
            try:
                from providers.models import TaskCategory
                
                yaml_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "extractor.yaml")
                with open(yaml_path, 'r') as f:
                    prompt_data = yaml.safe_load(f)
                    
                system_prompt = prompt_data.get("system_prompt", "")
                user_prompt = prompt_data.get("user_prompt", "").format(
                    title=article.title,
                    summary=article.summary,
                    text_snippet=article.full_text[:2000] if article.full_text else ""
                )
                
                resp = self.ai.generate_json(
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    task_category=TaskCategory.RESEARCH_TOPIC_EXTRACTION
                )
                
                if resp:
                    import json
                    parsed_resp = json.loads(resp)
                    return TopicCandidate(**parsed_resp)
            except Exception as e:
                logger.error(f"AI extraction failed, falling back to mock: {e}")

        try:
            # Fallback Mock AI behavior
            mock_json = {
                "title": f"The hidden impact of {article.title}",
                "problem_definition": "A major crisis unfolding unnoticed.",
                "historical_comparison": "Things have gotten significantly worse over the last 10 years.",
                "root_cause_analysis": "Systemic failures and outdated infrastructure.",
                "supporting_evidence": "Data from multiple international organizations confirms a 30% drop in key metrics.",
                "counterarguments": "Some claim it's a cyclical trend rather than a permanent decline.",
                "global_comparison": "Countries like Singapore have implemented robust policies with success.",
                "practical_solutions": "Immediate investment in modernizing infrastructure is required."
            }
            
            candidate = TopicCandidate(**mock_json)
            return candidate
            
        except Exception as e:
            logger.error(f"Failed to extract topic from {article.url}: {e}")
            return None
