from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ..models import ArticleData

class BaseConnector(ABC):
    """
    Abstract interface for all technology news source connectors.
    """
    
    @property
    @abstractmethod
    def source_name(self) -> str:
        """Name of the source (e.g., 'HackerNews')."""
        pass

    @abstractmethod
    def fetch_articles(self, max_articles: int) -> List[ArticleData]:
        """
        Fetch articles from the source.
        Must gracefully handle network errors and return an empty list if failed.
        """
        pass
