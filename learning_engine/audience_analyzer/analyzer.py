from typing import Dict, Any
from common import logger



class AudienceAnalyzer:
    def analyze(self, views: int) -> Dict[str, str]:
        logger.info("[AudienceAnalyzer] Analyzing Audience reach...")
        if views > 10000:
            return {"reach": "high", "recommendation": "Double down on this topic."}
        else:
            return {"reach": "low", "recommendation": "Topic may be too niche or saturated."}
