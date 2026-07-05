import os
import requests
import uuid
from typing import Optional
from common import logger
from config import config
from asset_engine.providers.base import BaseAssetFetcher

class PexelsAssetFetcher(BaseAssetFetcher):
    @property
    def provider_name(self) -> str:
        return "Pexels"

    def fetch_asset(self, query: str, output_path: str) -> Optional[str]:
        # Defaulting to video for the generic fetch_asset method
        return self.fetch_video(query, output_path)

    def fetch_image(self, query: str, output_dir: str) -> Optional[str]:
        return self._fetch_media(query, output_dir, media_type="photos")
        
    def fetch_video(self, query: str, output_dir: str) -> Optional[str]:
        return self._fetch_media(query, output_dir, media_type="videos")
        
    def _fetch_media(self, query: str, output_dir: str, media_type: str) -> Optional[str]:
        api_key = config.pexels_api_key
        if not api_key:
            logger.error("PEXELS_API_KEY is not set. Cannot fetch from Pexels.")
            return None
            
        url = f"https://api.pexels.com/v1/search" if media_type == "photos" else f"https://api.pexels.com/videos/search"
        headers = {
            "Authorization": api_key
        }
        params = {
            "query": query,
            "per_page": 1,
            "orientation": "landscape" if media_type == "videos" else "square"
        }
        
        try:
            logger.info(f"[Pexels] Searching for {media_type} with query: '{query}'")
            response = requests.get(url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            items = data.get(media_type, [])
            if not items:
                logger.warning(f"[Pexels] No {media_type} found for query: '{query}'")
                return None
                
            item = items[0]
            media_url = ""
            ext = ""
            
            if media_type == "photos":
                media_url = item["src"]["large2x"]
                ext = ".jpg"
            else:
                # Find the highest quality HD video
                hd_files = [f for f in item["video_files"] if f["quality"] == "hd"]
                if hd_files:
                    media_url = hd_files[0]["link"]
                else:
                    media_url = item["video_files"][0]["link"]
                ext = ".mp4"
                
            logger.info(f"[Pexels] Found {media_type}. Downloading from {media_url[:40]}...")
            
            # Download the actual file
            media_res = requests.get(media_url, stream=True, timeout=60)
            media_res.raise_for_status()
            
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, f"pexels_{media_type[:-1]}_{uuid.uuid4().hex[:8]}{ext}")
            
            with open(file_path, "wb") as f:
                for chunk in media_res.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            logger.info(f"[Pexels] Successfully saved to {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"[Pexels] Failed to fetch {media_type}: {e}", exc_info=True)
            return None
