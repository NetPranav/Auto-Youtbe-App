import psutil
from sqlalchemy.orm import Session
from common import logger
from database.models import QueueItem



class InfraMonitor:
    """
    Continuous monitoring aggregation point.
    Collects health from all subsystems into a single dashboard payload.
    """
    def __init__(self, db_session: Session):
        self.db = db_session
        
    def get_status(self) -> dict:
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        pending = self.db.query(QueueItem).filter(QueueItem.status == "PENDING").count()
        running = self.db.query(QueueItem).filter(QueueItem.status == "IN_PROGRESS").count()
        
        status = "HEALTHY"
        if cpu > 90 or ram.percent > 90 or disk.percent > 90:
            status = "DEGRADED"
        if cpu > 95 or ram.percent > 95 or disk.percent > 95:
            status = "CRITICAL"
            
        return {
            "overall": status,
            "cpu_percent": cpu,
            "ram_percent": ram.percent,
            "disk_percent": disk.percent,
            "queue_pending": pending,
            "queue_running": running
        }
