import psutil
from common import logger



class ResourceManager:
    def __init__(self, max_cpu_percent: float = 90.0, max_ram_percent: float = 90.0):
        self.max_cpu_percent = max_cpu_percent
        self.max_ram_percent = max_ram_percent
        
    def can_accept_task(self) -> bool:
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        
        if cpu > self.max_cpu_percent:
            logger.warning(f"[ResourceManager] CPU load too high ({cpu}%). Rejecting task.")
            return False
            
        if ram > self.max_ram_percent:
            logger.warning(f"[ResourceManager] RAM load too high ({ram}%). Rejecting task.")
            return False
            
        return True
