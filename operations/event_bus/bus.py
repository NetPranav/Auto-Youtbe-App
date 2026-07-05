from typing import Callable, Dict, List, Any
from common.logger import get_logger

logger = get_logger(__name__)

class EventBus:
    """
    A simple Pub/Sub memory bus.
    In a distributed system, this would be Redis PubSub or RabbitMQ.
    """
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        logger.debug(f"[EventBus] Subscribed to {event_type}")

    def publish(self, event_type: str, payload: Dict[str, Any] = None):
        logger.info(f"[EventBus] Publishing Event: {event_type}")
        if payload is None:
            payload = {}
            
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    callback(payload)
                except Exception as e:
                    logger.error(f"[EventBus] Subscriber failed on event {event_type}: {e}")
