from typing import Dict, Any
from common import logger



class SEOAnalyzer:
    def analyze(self, ctr: float) -> Dict[str, str]:
        logger.info("[SEOAnalyzer] Analyzing SEO performance (CTR proxy)...")
        if ctr > 8.0:
            return {"status": "strong", "recommendation": "Current title format is working well."}
        else:
            return {"status": "weak", "recommendation": "Try using more emotional trigger words in titles."}
