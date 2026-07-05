from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime

class BasePublisher(ABC):
    
    @abstractmethod
    def upload_video(self, video_path: str, title: str, description: str, tags: list, category_id: str, visibility: str, scheduled_time: Optional[datetime] = None) -> Optional[str]:
        """
        Uploads the video and returns the Platform Video ID.
        """
        pass
        
    @abstractmethod
    def upload_thumbnail(self, video_id: str, thumbnail_path: str) -> bool:
        """
        Uploads and attaches a thumbnail to the video ID.
        """
        pass
