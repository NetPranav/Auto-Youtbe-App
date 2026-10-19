from typing import Any, Dict
from common import logger, BaseEngine
from .health import check_health

class Orchestrator:
    """
    The central state machine and coordinator for the Autonomous YouTube System.
    Uses Dependency Injection for all engines.
    """

    def __init__(
        self,
        research_engine: BaseEngine | None = None,
        content_engine: BaseEngine | None = None,
        asset_engine: BaseEngine | None = None,
        video_engine: BaseEngine | None = None,
        publisher_engine: BaseEngine | None = None,
        learning_engine: BaseEngine | None = None,
    ):
        # Inject dependencies
        self.research_engine = research_engine
        self.content_engine = content_engine
        self.asset_engine = asset_engine
        self.video_engine = video_engine
        self.publisher_engine = publisher_engine
        self.learning_engine = learning_engine

        self._is_running = False

    def initialize(self) -> None:
        """Startup hook for the Orchestrator."""
        logger.info("Orchestrator initializing...")
        health_report = check_health()
        
        if health_report["status"] != "Healthy":
            logger.critical("System is unhealthy. Halting initialization.")
            raise SystemExit("Health check failed. Check logs for details.")
        
        self._is_running = True
        logger.info("Orchestrator initialized successfully.")

    def run(self) -> None:
        """
        Main execution loop. 
        """
        if not self._is_running:
            self.initialize()
            
        logger.info("Orchestrator execution started.")
        
        # 1. Research Phase
        if not self.research_engine:
            logger.error("No Research Engine configured.")
            return
        
        research_result = self.research_engine.run()
        if not research_result:
            logger.error("Research phase failed.")
            return
            
        topic_id = research_result['topic_id']
        logger.success(f"Research complete. Topic ID: {topic_id}")
        
        # 2. Content Phase
        if not self.content_engine:
            logger.error("No Content Engine configured.")
            return
            
        content_pkg_data = self.content_engine.run(topic_id)
        if not content_pkg_data:
            logger.error("Content generation failed.")
            return
            
        # Get content_package_id from DB
        from database.session import get_db_session
        from database.models import ContentPackage, AssetPackage
        
        with get_db_session() as db:
            c_pkg = db.query(ContentPackage).filter(ContentPackage.topic_id == topic_id).first()
            if not c_pkg:
                logger.error("Could not find ContentPackage in DB.")
                return
            content_package_id = c_pkg.id
            
        logger.success(f"Content complete. Package ID: {content_package_id}")
        
        # 3. Asset Phase
        if not self.asset_engine:
            logger.error("No Asset Engine configured.")
            return
            
        asset_pkg_data = self.asset_engine.run(content_package_id)
        if not asset_pkg_data:
            logger.error("Asset generation failed.")
            return
            
        with get_db_session() as db:
            a_pkg = db.query(AssetPackage).filter(AssetPackage.content_package_id == content_package_id).first()
            if not a_pkg:
                logger.error("Could not find AssetPackage in DB.")
                return
            asset_package_id = a_pkg.id
            
        logger.success(f"Asset complete. Package ID: {asset_package_id}")
        
        # 4. Video Phase
        if not self.video_engine:
            logger.error("No Video Engine configured.")
            return
            
        final_video_path = self.video_engine.run(asset_package_id)
        if not final_video_path:
            logger.error("Video rendering failed.")
            return
            
        logger.success(f"Orchestrator execution finished. Final Video: {final_video_path}")

    def shutdown(self) -> None:
        """Graceful shutdown hook."""
        logger.info("Orchestrator shutting down...")
        self._is_running = False
