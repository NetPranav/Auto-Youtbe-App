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
        # 1. Initialize Database Schema (Creates SQLite file locally by default)
        init_db()

        # 2. Instantiate Orchestrator (Dependency Injection happens here)
        # For Phase 1, we pass None as engines have not been built yet.
        app = Orchestrator(
            research_engine=None,
            content_engine=None,
            asset_engine=None,
            video_engine=None,
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
