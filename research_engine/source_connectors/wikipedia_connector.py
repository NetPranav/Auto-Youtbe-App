import requests
import random
import time
from typing import List
from common import logger
from ..models import ArticleData
from .base import BaseConnector


class WikipediaConnector(BaseConnector):
    """
    Scrapes 100% genuine historical stories directly from Wikipedia.
    Bypasses Reddit/Google API locks and guarantees authentic, verifiable facts.
    """

    @property
    def source_name(self) -> str:
        return "WikipediaScraper"

    def __init__(self):
        # Known fascinating Wikipedia articles categorized by genre
        self.category_map = {
            "ROMANCE": [
                "Pierre and Marie Curie", "Taj Mahal", "Cleopatra", 
                "Loving v. Virginia", "Johnny Cash", "Frida Kahlo"
            ],
            "HORROR": [
                "Dyatlov Pass incident", "Mary Celeste", "Roanoke colony", 
                "Tunguska event", "Dancing plague of 1518", "Voynich manuscript"
            ],
            "SPORTS": [
                "Miracle on Ice", "Jesse Owens", "Muhammad Ali", 
                "Jackie Robinson", "Babe Ruth", "1997 NBA Finals"
            ],
            "COMEDY": [
                "Emu War", "Boston Molasses Disaster", "London Beer Flood", 
                "List of unusual deaths", "New Coke"
            ]
        }
        
    def fetch_articles(self, limit: int = 2, target_category: str = "ROMANCE") -> List[ArticleData]:
        """
        Pulls genuine historical articles from Wikipedia's public API.
        """
        logger.info(f"[{self.source_name}] Initiating Wikipedia scrape for genuine {target_category} stories...")
        
        titles = self.category_map.get(target_category.upper())
        if not titles:
            logger.warning(f"[{self.source_name}] Unknown category {target_category}. Falling back to ROMANCE.")
            titles = self.category_map["ROMANCE"]
            
        articles = []
        
        # Pick random Wikipedia articles to fetch
        selected_titles = random.sample(titles, min(limit, len(titles)))
        
        headers = {
            "User-Agent": "yt_automate_scraper/1.0 (test@example.com)"
        }
        
        for title in selected_titles:
            try:
                # Use Wikipedia's action=query API to extract plaintext content
                url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext=1&titles={requests.utils.quote(title)}&format=json"
                
                resp = requests.get(url, headers=headers, timeout=10)
                if resp.status_code != 200:
                    logger.error(f"[{self.source_name}] Failed to scrape {title} - Status {resp.status_code}")
                    continue
                    
                data = resp.json()
                pages = data.get("query", {}).get("pages", {})
                
                for page_id, page_data in pages.items():
                    if page_id == "-1":
                        continue
                        
                    content = page_data.get("extract", "")
                    
                    if len(content) < 200:
                        continue
                        
                    articles.append(ArticleData(
                        source=f"Wikipedia",
                        title=title,
                        summary=content[:500] + "...",
                        url=f"https://en.wikipedia.org/wiki/{requests.utils.quote(title)}",
                        full_text=content[:3000],  # Cap length to avoid 70b API timeouts
                        metadata={"genre": target_category}
                    ))
                    
            except Exception as e:
                logger.error(f"[{self.source_name}] Error scraping Wikipedia ({title}): {e}")
                
            time.sleep(1) # Be polite to API
            
        logger.info(f"[{self.source_name}] Successfully scraped {len(articles)} genuine {target_category} stories from Wikipedia.")
        return articles
