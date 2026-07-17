import os
import sys
from loguru import logger

# Ensure the root directory is in the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.session import get_db_session
from database.models import AssetPackage
from video_engine.engine import VideoEngine

def main():
    logger.info("Starting Video Engine Test...")
    
    with get_db_session() as db:
        # Find the latest finalized asset package
        pkg = db.query(AssetPackage).filter(AssetPackage.status == "FINALIZED").order_by(AssetPackage.created_at.desc()).first()
        
        if not pkg:
            logger.error("No FINALIZED AssetPackage found. Run the Asset Engine first!")
            return
            
        pkg_id = pkg.id
        logger.info(f"Found AssetPackage ID: {pkg_id}")

        logger.info("Initializing Video Engine...")
        engine = VideoEngine(db)
        
        try:
            final_video_path = engine.run(pkg_id)
            logger.success(f"Video Engine finished successfully! Your final video is ready at:")
            logger.success(f"--> {final_video_path}")
        except Exception as e:
            logger.error(f"Video Engine failed: {e}", exc_info=True)

if __name__ == "__main__":
    main()
