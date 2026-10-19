"""
Main entry point for the Autonomous AI YouTube System.
"""

import sys
from common import logger
from database import init_db
from orchestrator import Orchestrator

def main() -> None:
    logger.info("Starting Autonomous AI YouTube System...")
    
    try:
        # Import models so Base.metadata is populated before create_all
        import database.models
        
        # 1. Initialize Database Schema (Creates SQLite file locally by default)
        init_db()

        # Import engines
        from research_engine.engine import ResearchEngine
        from content_engine.engine import ContentEngine
        from asset_engine.engine import AssetEngine
        from video_engine.engine import VideoEngine
        from database.session import SessionLocal

        # 2. Instantiate Orchestrator
        app = Orchestrator(
            research_engine=ResearchEngine(),
            content_engine=ContentEngine(),
            asset_engine=AssetEngine(),
            video_engine=VideoEngine(db_session=SessionLocal()),
            publisher_engine=None,
            learning_engine=None
        )

        # 3. Initialize and run (this triggers the health check)
        app.initialize()
        app.run()
        app.shutdown()

    except Exception as e:
        logger.critical(f"Fatal application error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
