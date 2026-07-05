import time
import schedule
import threading
from common.logger import get_logger

logger = get_logger(__name__)

class Scheduler:
    """
    Wraps the 'schedule' library to run periodic CEO polling and Health checks.
    """
    def __init__(self):
        self.running = False
        self.thread = None
        
    def start(self):
        logger.info("[Scheduler] Starting background thread...")
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
            
    def _loop(self):
        while self.running:
            schedule.run_pending()
            time.sleep(1)
            
    def add_job(self, interval_minutes: int, func):
        logger.info(f"[Scheduler] Registered job every {interval_minutes} minutes: {func.__name__}")
        schedule.every(interval_minutes).minutes.do(func)
