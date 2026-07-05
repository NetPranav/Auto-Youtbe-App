import random
from typing import Dict, Any
from common.logger import get_logger

logger = get_logger(__name__)

class AnalyticsCollector:
    def collect(self, platform_video_id: str) -> Dict[str, Any]:
        """
        In a real application, this connects to the YouTube Analytics API.
        Because we lack a verified OAuth client to query advanced retention metrics,
        we mock robust analytics to prove the AI parsing logic works.
        """
        logger.info(f"[AnalyticsCollector] Fetching metrics for video {platform_video_id}...")
        
        # Simulating random performance (Good vs Bad hook)
        is_good = random.choice([True, False])
        
        if is_good:
            return {
                "views": random.randint(10000, 50000),
                "ctr_percent": round(random.uniform(7.5, 12.0), 1),
                "avg_view_duration_sec": 45.0,
                "retention_graph": {
                    "0:00": 100,
                    "0:05": 85,
                    "0:30": 60,
                    "1:00": 55
                }
            }
        else:
            return {
                "views": random.randint(100, 1000),
                "ctr_percent": round(random.uniform(2.0, 4.5), 1),
                "avg_view_duration_sec": 12.0,
                "retention_graph": {
                    "0:00": 100,
                    "0:05": 40, # Massive dropoff = bad hook
                    "0:30": 15,
                    "1:00": 5
                }
            }
