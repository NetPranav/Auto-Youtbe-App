import os
from typing import List, Dict, Any
from common import logger
from ..models import ArticleData
from ..source_connectors.base import BaseConnector
from ..source_connectors.wikipedia_connector import WikipediaConnector

class ArticleCollector:
    def __init__(self):
        self.max_articles = int(os.getenv("RESEARCH_MAX_ARTICLES_PER_SOURCE", 10))
        self.connectors = self._initialize_connectors()
        
    def _initialize_connectors(self) -> List[BaseConnector]:
        """Initialize the Wikipedia connector for multi-genre scraping."""
        connectors = [WikipediaConnector()]
        logger.info(f"Initialized {len(connectors)} connectors: {[c.source_name for c in connectors]}")
        return connectors
        
    def collect(self, target_category: str = "LOVE_STORY") -> Dict[str, Any]:
        """Collect stories from all configured connectors."""
        logger.info(f"Starting Idea Collection Phase for category: {target_category}")
        
        all_articles: List[ArticleData] = []
        source_stats = []
        
        for connector in self.connectors:
            try:
                # Pass both limit and target_category
                articles = connector.fetch_articles(limit=self.max_articles, target_category=target_category)
                # Convert list of dicts to list of ArticleData if necessary, or let normalizer handle it
                all_articles.extend(articles)
                source_stats.append({
                    "source_name": connector.source_name,
                    "articles_found": len(articles),
                    "errors": None
                })
            except Exception as e:
                logger.error(f"Failed to fetch from {connector.source_name}: {e}")
                
        logger.info(f"Idea Collection complete. Total raw concepts: {len(all_articles)}")
        
        return {
            "articles": all_articles,
            "stats": source_stats
        }
