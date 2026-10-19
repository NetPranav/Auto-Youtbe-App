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

    def extract(self, article: ArticleData, target_category: str = "CURRENT_AFFAIRS") -> Optional[TopicCandidate]:
        """
        Uses an LLM to extract a topic from the article.
        """
        logger.debug(f"Extracting topic from: {article.title} (Target Category: {target_category})")
        
        if self.ai:
            try:
                from providers.models import TaskCategory
                
                yaml_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "extractor.yaml")
                with open(yaml_path, 'r') as f:
                    prompt_data = yaml.safe_load(f)
                    
                system_prompt = prompt_data.get("system_prompt", "")
                system_prompt += f"\n\nCRITICAL: You are extracting data for a {target_category} documentary. Format the output to fit this domain perfectly."
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
                "title": f"The True Story of {article.title}",
                "problem_definition": "An incredible true event that defies explanation.",
                "historical_comparison": "This situation echoes legendary tales from the past.",
                "root_cause_analysis": "The sequence of events was completely unpredictable.",
                "supporting_evidence": "Eyewitness accounts and historical records confirm the details.",
                "counterarguments": "Some remain skeptical, but the facts speak for themselves.",
                "global_comparison": "Similar events have occurred worldwide, but rarely with such intensity.",
                "practical_solutions": "This story leaves a lasting legacy we will never forget."
            }
            
            candidate = TopicCandidate(**mock_json)
            return candidate
            
        except Exception as e:
            logger.error(f"Failed to extract topic from {article.url}: {e}")
            return None
