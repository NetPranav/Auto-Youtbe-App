from typing import Dict, Any
from common.logger import get_logger

logger = get_logger(__name__)

class ThumbnailAnalyzer:
    def analyze(self, ctr: float) -> Dict[str, str]:
        logger.info("[ThumbnailAnalyzer] Analyzing Thumbnail CTR...")
        if ctr > 8.0:
            return {"status": "strong", "recommendation": "Current thumbnail style (contrast, text) is effective."}
        else:
            return {"status": "weak", "recommendation": "Increase brightness and use fewer words on thumbnail."}
