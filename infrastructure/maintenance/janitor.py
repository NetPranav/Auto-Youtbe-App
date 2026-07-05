import os
import glob
import time
from sqlalchemy.orm import Session
from common.logger import get_logger
from database.models import MaintenanceTask

logger = get_logger(__name__)

class Janitor:
    """
    Scheduled maintenance: cleans old logs, temp files, and stale assets.
    """
    def __init__(self, db_session: Session, max_log_age_days: int = 30, max_asset_age_days: int = 60):
        self.db = db_session
        self.max_log_age_sec = max_log_age_days * 86400
        self.max_asset_age_sec = max_asset_age_days * 86400
        
    def run_all(self):
        logger.info("[Janitor] Running scheduled maintenance...")
        cleaned_logs = self._clean_old_files("logs", "*.jsonl")
        cleaned_tmp = self._clean_old_files("data/tmp", "*")
        
        task = MaintenanceTask(
            task_type="FULL_CLEANUP",
            items_processed=cleaned_logs + cleaned_tmp
        )
        self.db.add(task)
        self.db.commit()
        logger.info(f"[Janitor] Maintenance complete. Cleaned {cleaned_logs + cleaned_tmp} items.")
        
    def _clean_old_files(self, directory: str, pattern: str) -> int:
        if not os.path.exists(directory):
            return 0
        count = 0
        now = time.time()
        for filepath in glob.glob(os.path.join(directory, pattern)):
            if os.path.isfile(filepath):
                age = now - os.path.getmtime(filepath)
                if age > self.max_log_age_sec:
                    os.remove(filepath)
                    count += 1
                    logger.debug(f"[Janitor] Removed stale file: {filepath}")
        return count
