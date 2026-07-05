import psutil
from sqlalchemy.orm import Session
from common.logger import get_logger
from database.models import Alert, QueueItem

logger = get_logger(__name__)

class AlertEngine:
    """
    Watches system thresholds and fires alerts into the database.
    Future: Discord/Slack webhook integration.
    """
    def __init__(self, db_session: Session):
        self.db = db_session
        
    def check_all(self):
        logger.info("[AlertEngine] Running alert checks...")
        self._check_disk()
        self._check_memory()
        self._check_queue_growth()
        
    def _check_disk(self):
        disk = psutil.disk_usage('/')
        if disk.percent > 90:
            self._fire("DISK_FULL", "CRITICAL", f"Disk usage at {disk.percent}%. Immediate action required.")
        elif disk.percent > 80:
            self._fire("DISK_WARNING", "WARNING", f"Disk usage at {disk.percent}%.")
            
    def _check_memory(self):
        ram = psutil.virtual_memory()
        if ram.percent > 95:
            self._fire("MEMORY_CRITICAL", "CRITICAL", f"RAM usage at {ram.percent}%.")
            
    def _check_queue_growth(self):
        pending = self.db.query(QueueItem).filter(QueueItem.status == "PENDING").count()
        failed = self.db.query(QueueItem).filter(QueueItem.status == "FAILED").count()
        if pending > 20:
            self._fire("QUEUE_GROWTH", "WARNING", f"Task queue has {pending} pending items.")
        if failed > 5:
            self._fire("REPEATED_FAILURES", "CRITICAL", f"{failed} tasks have failed in the queue.")
            
    def _fire(self, alert_type: str, severity: str, message: str):
        logger.warning(f"[ALERT] [{severity}] {alert_type}: {message}")
        alert = Alert(
            alert_type=alert_type,
            severity=severity,
            message=message
        )
        self.db.add(alert)
        self.db.commit()
