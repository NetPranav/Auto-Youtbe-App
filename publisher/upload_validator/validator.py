import os
from common.logger import get_logger

logger = get_logger(__name__)

class UploadValidator:
    def validate(self, video_path: str, thumbnail_path: str, metadata: dict) -> bool:
        logger.info("[UploadValidator] Running pre-flight checks on upload package...")
        
        if not video_path or not os.path.exists(video_path):
            logger.error(f"Video file missing at path: {video_path}")
            return False
            
        if not thumbnail_path or not os.path.exists(thumbnail_path):
            logger.error(f"Thumbnail file missing at path: {thumbnail_path}")
            return False
            
        file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        if file_size_mb == 0:
            logger.error("Video file is empty (0 bytes).")
            return False
            
        if not metadata.get("title") or not metadata.get("description"):
            logger.error("Metadata is missing title or description.")
            return False
            
        logger.info(f"[UploadValidator] Validation passed. Video size: {file_size_mb:.2f} MB")
        return True
