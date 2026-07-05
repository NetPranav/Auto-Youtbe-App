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
        Will be expanded in future phases to manage the state machine.
        """
        if not self._is_running:
            self.initialize()
            
        logger.info("Orchestrator execution started.")
        # Future: Execute Research -> Content -> Asset -> Video -> Publisher -> Learning
        logger.info("Orchestrator execution finished.")

    def shutdown(self) -> None:
        """Graceful shutdown hook."""
        logger.info("Orchestrator shutting down...")
        self._is_running = False
