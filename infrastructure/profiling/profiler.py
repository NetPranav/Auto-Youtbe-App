import psutil
import os
from common import logger



class Profiler:
    """
    Snapshots CPU, memory, and disk performance for diagnostic reports.
    """
    @staticmethod
    def snapshot() -> dict:
        logger.info("[Profiler] Taking system performance snapshot...")
        
        cpu_freq = psutil.cpu_freq()
        
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.5),
            "cpu_freq_mhz": cpu_freq.current if cpu_freq else 0,
            "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "ram_used_percent": psutil.virtual_memory().percent,
            "disk_total_gb": round(psutil.disk_usage('/').total / (1024**3), 2),
            "disk_used_percent": psutil.disk_usage('/').percent,
            "pid_count": len(psutil.pids()),
            "db_size_mb": round(os.path.getsize("youtube_automation.db") / (1024**2), 2) if os.path.exists("youtube_automation.db") else 0
        }
