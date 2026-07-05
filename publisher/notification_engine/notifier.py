from common.logger import get_logger
from sqlalchemy.orm import Session
from database.models import Notification

logger = get_logger(__name__)

class NotificationEngine:
    def __init__(self, db_session: Session):
        self.db = db_session
        
    def notify(self, event_type: str, message: str, level: str = "INFO"):
        logger.info(f"[NotificationEngine] [{event_type}] {message}")
        
        # Save to DB
        notif = Notification(
            event_type=event_type,
            message=message,
            level=level
        )
        self.db.add(notif)
        self.db.commit()
        
        # Future: Webhook integration (Discord, Slack)
        # if level == "ERROR":
        #    send_discord_webhook(message)
