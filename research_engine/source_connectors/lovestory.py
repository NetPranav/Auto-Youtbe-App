import json
import random
from typing import List
from datetime import datetime
from .base import BaseConnector
from common import logger
from providers.manager import ProviderManager

class LoveStoryConnector(BaseConnector):
    @property
    def source_name(self) -> str:
        return "LLM_LoveStories"

    def fetch_articles(self, limit: int = 5) -> List[dict]:
        logger.info(f"[{self.source_name}] Hallucinating {limit} real historical/modern love story pitches...")
        
        prompt = f"""
        You are a YouTube Shorts idea generator specializing in REAL, true-life love stories.
        Generate a JSON list of {limit} unique, fascinating, and true love stories (either historical or modern).
        CRITICAL RULES:
        1. They MUST be 100% genuine, verifiable stories that actually happened.
        2. Do NOT just give generic dramatic epics. Include stories with funny moments, incredible loyalty, unexpected twists, or charming unattended/unknown short anecdotes of couples.
        
        Respond ONLY with a valid JSON array of objects. Do not include markdown formatting or backticks.
        Example format:
        [
            {{
                "title": "The Lovers of Valdaro",
                "link": "https://en.wikipedia.org/wiki/Lovers_of_Valdaro",
                "summary": "A pair of human skeletons dated to 6,000 years ago were discovered locked in an eternal embrace.",
                "published_date": "2023-01-01",
                "source": "Archaeology",
                "author": "History"
            }}
        ]
        """
        
        try:
            from providers.models import TaskCategory
            ai_provider = ProviderManager().get_llm_provider()
            
            response_text = ai_provider.generate_json(
                prompt=prompt,
                task_category=TaskCategory.RESEARCH_IDEA_GENERATION
            )
            
            if not response_text:
                raise ValueError("LLM returned empty response")
                
            # Clean markdown if present
            response_text = response_text.replace("```json", "").replace("```", "").strip()
            articles = json.loads(response_text)
            
            from research_engine.models.article import ArticleData
            
            if not isinstance(articles, list):
                articles = [articles]
                
            formatted_articles = []
            for art in articles[:limit]:
                formatted_articles.append(ArticleData(
                    title=art.get("title", "Unknown Story"),
                    url=art.get("link", f"https://truelove.com/{random.randint(1000,9999)}"),
                    summary=art.get("summary", ""),
                    publication_date=datetime.now(),
                    source="LLM_TrueLove",
                    author=art.get("author", "History")
                ))
                
            logger.info(f"[{self.source_name}] Successfully generated {len(formatted_articles)} true love story pitches.")
            return formatted_articles
            
        except Exception as e:
            logger.error(f"[{self.source_name}] Failed to generate love stories via LLM: {e}")
            return []
