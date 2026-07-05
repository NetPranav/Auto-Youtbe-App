from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime

class ArticleData(BaseModel):
    """
    Normalized internal representation of an Article.
    Used for transferring data between Collector, Normalizer, and Extractor.
    """
    title: str
    url: str
    source: str
    publication_date: Optional[datetime] = None
    author: Optional[str] = None
    summary: Optional[str] = None
    full_text: Optional[str] = None
    categories: List[str] = []
    tags: List[str] = []
