import os
from typing import Optional
from common.logger import get_logger
from database.models import AssetPackage, Asset
from sqlalchemy.orm import Session

logger = get_logger(__name__)

class ThumbnailSelector:
    def __init__(self, db_session: Session):
        self.db = db_session
        
    def select(self, asset_package_id: str) -> Optional[str]:
        logger.info("[ThumbnailSelector] Evaluating thumbnails for best CTR...")
        
        # Look for a specific THUMBNAIL asset first
        thumbnail = self.db.query(Asset).filter(
            Asset.package_id == asset_package_id,
            Asset.asset_type == "THUMBNAIL"
        ).first()
        
        if thumbnail and os.path.exists(thumbnail.file_path):
            logger.info(f"[ThumbnailSelector] Found generated thumbnail: {thumbnail.file_path}")
            return thumbnail.file_path
            
        # Fallback to the first IMAGE
        image = self.db.query(Asset).filter(
            Asset.package_id == asset_package_id,
            Asset.asset_type == "IMAGE"
        ).first()
        
        if image and os.path.exists(image.file_path):
            logger.warning("[ThumbnailSelector] No specific THUMBNAIL found. Using first scene image as fallback.")
            return image.file_path
            
        logger.error("[ThumbnailSelector] No valid images found to use as thumbnail.")
        return None
