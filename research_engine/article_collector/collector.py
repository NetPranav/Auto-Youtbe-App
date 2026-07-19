from typing import List, Dict, Any
from common import logger
from ..models import ArticleData
from ..source_connectors.base import BaseConnector
from ..source_connectors.rss import RSSConnector
from ..source_connectors.hackernews import HackerNewsConnector

class ArticleCollector:
    """
    Coordinates enabled source connectors and aggregates raw articles.
    """
    
    def __init__(self, enabled_sources: List[str], max_articles_per_source: int):
        self.enabled_sources = enabled_sources
        self.max_articles = max_articles_per_source
        self.connectors: List[BaseConnector] = self._initialize_connectors()

    def _initialize_connectors(self) -> List[BaseConnector]:
        """Load connectors based on configuration."""
        loaded = []
        # Normalizing to lowercase for comparison
        sources = [s.strip().lower() for s in self.enabled_sources]
        
        if "rss" in sources:
            loaded.append(RSSConnector())
        if "hackernews" in sources:
            loaded.append(HackerNewsConnector())
            
        logger.info(f"Initialized {len(loaded)} connectors: {[c.source_name for c in loaded]}")
        return loaded

    def collect(self, target_category: str = "CURRENT_AFFAIRS") -> Dict[str, Any]:
        """
        Runs enabled connectors based on the target category.
        Returns a dict containing the articles and metadata about the process.
        """
        all_articles: List[ArticleData] = []
        source_stats = []

        logger.info(f"Starting Article Collection Phase for category: {target_category}")
        
        # Simple routing for our mock feeds: RSS -> Current Affairs, HackerNews -> History
        active_connectors = []
        for connector in self.connectors:
            if target_category == "CURRENT_AFFAIRS" and connector.source_name == "RSS":
                active_connectors.append(connector)
            elif target_category == "HISTORY" and connector.source_name == "HackerNews":
                active_connectors.append(connector)
                
        if not active_connectors:
            logger.warning(f"No active connectors matched the target category: {target_category}")

        for connector in active_connectors:
            articles = connector.fetch_articles(self.max_articles)
            all_articles.extend(articles)
            
            source_stats.append({
                "source_name": connector.source_name,
                "articles_found": len(articles),
                "errors": None # Handled inside connector
            })

        logger.info(f"Article Collection complete. Total raw articles: {len(all_articles)}")
        
        return {
            "articles": all_articles,
            "stats": source_stats
        }
