import sys
import os

# Add parent directory to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from common import logger
from database.database import init_db
from research_engine import ResearchEngine
from content_engine import ContentEngine
from asset_engine import AssetEngine

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
    
    from database.session import get_db_session
    from database.models import ContentPackage
    
    with get_db_session() as db:
        c_pkg = db.query(ContentPackage).filter(ContentPackage.topic_id == topic['topic_id']).order_by(ContentPackage.created_at.desc()).first()
        if not c_pkg:
            logger.error("Could not find ContentPackage in DB. Aborting.")
            return False
        content_pkg_id = c_pkg.id
        
    asset_pkg = asset_engine.run(content_pkg_id)
    
    if not asset_pkg:
        logger.error("Asset Engine failed to produce an asset package. Aborting pipeline.")
        return False
        
    logger.info(f"Asset Engine successfully generated Asset Package for Content Package ID: {asset_pkg.content_package_id}")
    logger.info(f"Generated {len(asset_pkg.assets)} assets.")
    logger.info("=== PIPELINE COMPLETED SUCCESSFULLY ===")
    return True

if __name__ == "__main__":
    success = run_pipeline()
    if not success:
        sys.exit(1)
