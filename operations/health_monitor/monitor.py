from sqlalchemy.orm import Session
from common.logger import get_logger
from operations.resource_manager.manager import ResourceManager

logger = get_logger(__name__)

class HealthMonitor:
    def __init__(self, db_session: Session, resource_manager: ResourceManager):
        self.db = db_session
        self.resource_manager = resource_manager
        
    def check_health(self) -> dict:
        logger.info("[HealthMonitor] Running system health checks...")
        
        # 1. Check DB connectivity
        db_ok = False
        try:
            self.db.execute("SELECT 1")
            db_ok = True
        except Exception as e:
            logger.error(f"[HealthMonitor] Database unreachable: {e}")
            
        # 2. Resource levels
        res_ok = self.resource_manager.can_accept_task()
        
        status = "HEALTHY" if (db_ok and res_ok) else "DEGRADED"
        
        return {
            "status": status,
            "database": db_ok,
            "resources_available": res_ok
        }
