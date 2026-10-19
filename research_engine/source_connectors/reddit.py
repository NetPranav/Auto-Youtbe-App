import requests
import random
import time
from typing import List
from common import logger
from ..models import ArticleData
from .base import BaseConnector


class RedditConnector(BaseConnector):
    """
    Scrapes 100% genuine user stories directly from Reddit via their public JSON API.
    Supports dynamic multi-genre scraping (Romance, Horror, Sports, Comedy).
    """

    @property
    def source_name(self) -> str:
        return "RedditScraper"

    def __init__(self):
        # Subreddits categorized by target genres
        self.category_map = {
            "ROMANCE": ["Love", "TrueLoveStories", "relationship_advice", "relationships"],
            "HORROR": ["TrueScaryStories", "LetsNotMeet", "Paranormal", "creepyencounters"],
            "SPORTS": ["sports", "olympics", "nba", "soccer", "nfl"],
            "COMEDY": ["tifu", "funny", "Jokes", "ContagiousLaughter"]
        }
        
    def fetch_articles(self, limit: int = 10, target_category: str = "ROMANCE") -> List[ArticleData]:
        """
        Pulls top weekly/monthly JSON posts from the target subreddits.
        """
        logger.info(f"[{self.source_name}] Initiating web scrape for genuine {target_category} stories...")
        
        # Determine which subreddits to scrape based on category (fallback to Romance if unknown)
        subreddits = self.category_map.get(target_category.upper())
        if not subreddits:
            logger.warning(f"[{self.source_name}] Unknown category {target_category}. Falling back to ROMANCE.")
            subreddits = self.category_map["ROMANCE"]
            
        articles = []
        
        # Pick 2 random subreddits from the category to scrape
        selected_subs = random.sample(subreddits, min(2, len(subreddits)))
        
        # Standard browser User-Agent so Reddit doesn't block the request immediately
        # Reddit requires a highly specific User-Agent for bots/scripts to avoid 403 Forbidden
        headers = {
            "User-Agent": "python:yt_automate_scraper:v1.0 (by /u/Antigravity)"
        }
        
        for sub in selected_subs:
            try:
                # Get the top posts of the month to ensure high quality stories
                url = f"https://www.reddit.com/r/{sub}/top.json?t=month&limit={limit}"
                
                resp = requests.get(url, headers=headers, timeout=10)
                if resp.status_code != 200:
                    logger.error(f"[{self.source_name}] Failed to scrape /r/{sub} - Status {resp.status_code}")
                    continue
                    
                data = resp.json()
                posts = data.get("data", {}).get("children", [])
                
                for post in posts:
                    post_data = post.get("data", {})
                    
                    title = post_data.get("title", "")
                    content = post_data.get("selftext", "")
                    url_path = post_data.get("permalink", "")
                    upvotes = post_data.get("ups", 0)
                    
                    # We only want text-heavy self posts, not just images/videos
                    if len(content) < 200:
                        continue
                        
                    articles.append(ArticleData(
                        source=f"Reddit (/r/{sub})",
                        title=title,
                        summary=content[:500] + "...",
                        url=f"https://www.reddit.com{url_path}",
                        full_text=content,
                        metadata={"upvotes": upvotes, "genre": target_category}
                    ))
                    
                    if len(articles) >= limit:
                        break
                        
            except Exception as e:
                logger.error(f"[{self.source_name}] Error scraping /r/{sub}: {e}")
                
            time.sleep(1) # Be polite to API
            
            if len(articles) >= limit:
                break
                
        logger.info(f"[{self.source_name}] Successfully scraped {len(articles)} genuine {target_category} stories.")
        return articles
