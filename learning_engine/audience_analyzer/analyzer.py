from typing import Dict, Any
from common.logger import get_logger

logger = get_logger(__name__)

class AudienceAnalyzer:
    def analyze(self, views: int) -> Dict[str, str]:
        logger.info("[AudienceAnalyzer] Analyzing Audience reach...")
        if views > 10000:
            return {"reach": "high", "recommendation": "Double down on this topic."}
        else:
            return {"reach": "low", "recommendation": "Topic may be too niche or saturated."}
