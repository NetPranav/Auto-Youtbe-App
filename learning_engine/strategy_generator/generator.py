from typing import Dict, Any, List
from common import logger



class StrategyGenerator:
    def generate(self, perf: Dict[str, Any], ret: Dict[str, str], seo: Dict[str, str], thumb: Dict[str, str], aud: Dict[str, str]) -> List[Dict[str, str]]:
        logger.info("[StrategyGenerator] Synthesizing engine recommendations...")
        
        recs = []
        
        if ret.get("hook_quality") == "bad":
            recs.append({
                "target_engine": "CONTENT",
                "recommendation_text": ret.get("recommendation", "Improve hook pacing.")
            })
            
        if seo.get("status") == "weak":
            recs.append({
                "target_engine": "PUBLISHER",
                "recommendation_text": seo.get("recommendation", "Improve title CTR.")
            })
            
        if thumb.get("status") == "weak":
            recs.append({
                "target_engine": "ASSET",
                "recommendation_text": thumb.get("recommendation", "Improve thumbnail contrast.")
            })
            
        if aud.get("reach") == "high":
            recs.append({
                "target_engine": "RESEARCH",
                "recommendation_text": "Prioritize this topic format in future searches."
            })
            
        return recs
