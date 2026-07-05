from typing import List
from datetime import datetime
from common import logger
from ..models import ArticleData
from .base import BaseConnector

class HackerNewsConnector(BaseConnector):
    """
    Fetches top stories from Hacker News using their Firebase API.
    """
    
    @property
    def source_name(self) -> str:
        return "HackerNews"

    def fetch_articles(self, max_articles: int) -> List[ArticleData]:
        articles = []
        try:
            logger.info(f"[{self.source_name}] Fetching up to {max_articles} top stories.")
            
            # NOTE: Full implementation uses `requests` to hit HN API.
            # import requests
            # top_ids = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json").json()
            # for item_id in top_ids[:max_articles]:
            #     item = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json").json()
            #     articles.append(ArticleData(...))
            
            # Returning mock
            articles.append(ArticleData(
                title="Show HN: A new framework for building agentic workflows",
                url="https://example.com/agents",
                source=self.source_name,
                publication_date=datetime.utcnow(),
                summary="An open source framework for agents.",
                full_text="HN comments and post text..."
            ))
            
            logger.info(f"[{self.source_name}] Successfully fetched {len(articles)} articles.")
        except Exception as e:
            logger.error(f"[{self.source_name}] Failed to fetch articles: {e}")
        
        return articles[:max_articles]
