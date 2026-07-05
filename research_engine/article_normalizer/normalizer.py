import re
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from typing import List
from common import logger
from ..models import ArticleData

class ArticleNormalizer:
    """
    Cleans and standardizes raw article data.
    """
    
    @staticmethod
    def _clean_url(url: str) -> str:
        """Removes tracking parameters (utm_*, etc) from URL."""
        if not url:
            return ""
        try:
            parsed = urlparse(url)
            query = parse_qs(parsed.query, keep_blank_values=True)
            # Remove tracking params
            filtered_query = {k: v for k, v in query.items() if not k.startswith('utm_')}
            new_query = urlencode(filtered_query, doseq=True)
            return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))
        except Exception:
            return url

    @staticmethod
    def _strip_html(text: str) -> str:
        """Basic HTML stripping. (In a real app, use beautifulsoup4)"""
        if not text:
            return ""
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text).strip()

    def normalize(self, raw_articles: List[ArticleData]) -> List[ArticleData]:
        """
        Normalizes a list of articles.
        """
        logger.info(f"Normalizing {len(raw_articles)} articles.")
        normalized = []
        
        for article in raw_articles:
            try:
                norm_article = ArticleData(
                    title=article.title.strip(),
                    url=self._clean_url(article.url),
                    source=article.source.strip(),
                    publication_date=article.publication_date,
                    author=article.author.strip() if article.author else None,
                    summary=self._strip_html(article.summary),
                    full_text=self._strip_html(article.full_text) if article.full_text else None,
                    categories=[c.strip().lower() for c in article.categories],
                    tags=[t.strip().lower() for t in article.tags]
                )
                normalized.append(norm_article)
            except Exception as e:
                logger.warning(f"Failed to normalize article '{article.title[:30]}': {e}")
        
        logger.info(f"Successfully normalized {len(normalized)} articles.")
        return normalized
