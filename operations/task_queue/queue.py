from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from common.logger import get_logger
from database.models import QueueItem

logger = get_logger(__name__)

class TaskQueue:
    def __init__(self, db_session: Session):
        self.db = db_session
        
    def enqueue(self, workflow_id: str, task_type: str, payload: Dict[str, Any], priority: int = 50) -> QueueItem:
        logger.info(f"[TaskQueue] Enqueueing {task_type} (Priority: {priority}) for Workflow {workflow_id}")
        item = QueueItem(
            workflow_id=workflow_id,
            task_type=task_type,
            payload_json=payload,
            priority=priority,
            status="PENDING"
        )
        self.db.add(item)
        self.db.commit()
        return item
        
    def dequeue(self) -> Optional[QueueItem]:
        # Get highest priority pending task
        item = self.db.query(QueueItem)\
            .filter(QueueItem.status == "PENDING")\
            .order_by(QueueItem.priority.desc(), QueueItem.created_at.asc())\
            .first()
            
        if item:
            item.status = "IN_PROGRESS"
            item.started_at = datetime.now(timezone.utc)
            self.db.commit()
            return item
        return None
        
    def complete(self, item_id: str):
        item = self.db.query(QueueItem).filter(QueueItem.id == item_id).first()
        if item:
            item.status = "COMPLETED"
            item.completed_at = datetime.now(timezone.utc)
            self.db.commit()
            
    def fail(self, item_id: str, error_msg: str):
        item = self.db.query(QueueItem).filter(QueueItem.id == item_id).first()
        if item:
            item.status = "FAILED"
            item.error_message = error_msg
            item.completed_at = datetime.now(timezone.utc)
            self.db.commit()
            
    def retry(self, item_id: str, max_retries: int = 3) -> bool:
        item = self.db.query(QueueItem).filter(QueueItem.id == item_id).first()
        if item and item.retries < max_retries:
            item.retries += 1
            item.status = "PENDING"
            self.db.commit()
            return True
        return False
