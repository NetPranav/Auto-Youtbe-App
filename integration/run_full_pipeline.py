import sys
import os

# Add parent directory to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from common import logger
from database.database import init_db
from research_engine.engine import ResearchEngine
from content_engine.engine import ContentEngine
from asset_engine.engine import AssetEngine
from video_engine.engine import VideoEngine
from publisher.engine import PublishingEngine
from providers.manager import ProviderManager
from database.session import get_db_session
from database.models import ContentPackage

def run_pipeline():
    logger.info("=== STARTING FULL E2E PIPELINE ===")
    
    db_path = "yt_automate.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        logger.info(f"Cleared old database {db_path} for clean integration run.")
    
    init_db()
    
    # 1. Research Engine
    logger.info("Phase 1: Research Engine")
    research_engine = ResearchEngine()
    topic = research_engine.run()
    
    if not topic:
        logger.error("Research Engine failed to produce a topic. Aborting pipeline.")
        return False
        
    logger.info(f"Research Engine generated Topic ID: {topic['topic_id']}")
    
    # 2. Content Engine
    logger.info("Phase 2: Content Engine")
    content_engine = ContentEngine()
    content_pkg = content_engine.run(topic['topic_id'])
    
    if not content_pkg:
        logger.error("Content Engine failed to produce a content package. Aborting pipeline.")
        return False
        
    logger.info(f"Content Engine generated Content Package for Topic ID: {content_pkg.topic_id}")
    
    # 3. Asset Engine
    logger.info("Phase 3: Asset Engine")
    asset_engine = AssetEngine()
    
    with get_db_session() as db:
        c_pkg = db.query(ContentPackage).filter(ContentPackage.topic_id == topic['topic_id']).order_by(ContentPackage.created_at.desc()).first()
        if not c_pkg:
            logger.error("Could not find ContentPackage in DB. Aborting.")
            return False
        content_pkg_id = c_pkg.id
        
        asset_result = asset_engine.run(content_pkg_id)
        
        if not asset_result:
            logger.error("Asset Engine failed to produce an asset package. Aborting pipeline.")
            return False
            
        logger.info(f"Asset Engine successfully generated Asset Package for Content Package ID: {content_pkg_id}")
        
        # Phase 5: Video Engine
        logger.info("Phase 5: Video Engine")
        video_engine = VideoEngine(db)
        
        asset_package_id = asset_result.id
        if not asset_package_id:
            logger.error("Failed to get asset package id from result.")
            return False
            
        final_video_path = video_engine.run(asset_package_id)
        
        logger.info(f"Final Video path: {final_video_path}")
        
        if not final_video_path:
            logger.error("Video engine failed. Aborting pipeline.")
            return False
            
        # Phase 6: Publishing Engine
        logger.info("Phase 6: Publishing & Distribution Engine")
        
        # Publisher engine requires provider manager for AI Metadata generation
        provider_manager = ProviderManager()
        publisher_engine = PublishingEngine(db, provider_manager)
        
        # We need the VideoProject ID. We can derive it by querying the latest VideoProject for this asset package.
        from database.models import VideoProject
        video_project = db.query(VideoProject).filter(VideoProject.asset_package_id == asset_package_id).order_by(VideoProject.created_at.desc()).first()
        
        if not video_project:
            logger.error("Could not find VideoProject in DB.")
            return False
            
        published_url = publisher_engine.run(video_project.id)
        
        logger.info("=== FULL YOUTUBE AUTOMATION PIPELINE COMPLETED SUCCESSFULLY ===")
        logger.info(f"Published URL: {published_url}")
    return True

if __name__ == "__main__":
    success = run_pipeline()
    if not success:
        sys.exit(1)
