from sqlalchemy.orm import Session
from common import logger
from database.models import QueueItem



class RecoveryManager:
    def __init__(self, db_session: Session):
        self.db = db_session
        
    def recover(self):
        logger.info("=== [RecoveryManager] Running startup crash recovery ===")
        
        # Find any tasks that were IN_PROGRESS when the system shut down
        stuck_tasks = self.db.query(QueueItem).filter(QueueItem.status == "IN_PROGRESS").all()
        
        if not stuck_tasks:
            logger.info("[RecoveryManager] Clean startup. No stuck tasks found.")
            return
            
        for task in stuck_tasks:
            logger.warning(f"[RecoveryManager] Recovering Task {task.task_type} (ID: {task.id})")
            # For simplicity, we just push them back to PENDING.
            # In a real system, we'd check if we need to rollback files/DB changes.
            task.status = "PENDING"
            task.retries += 1
            
        self.db.commit()
        logger.info(f"[RecoveryManager] Successfully recovered {len(stuck_tasks)} tasks.")
