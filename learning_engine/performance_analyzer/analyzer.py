import json
from typing import Dict, Any
from common.logger import get_logger
from providers.manager import ProviderManager
from learning_engine.prompts.analyzer_prompts import PERFORMANCE_ANALYSIS_PROMPT

logger = get_logger(__name__)

class PerformanceAnalyzer:
    def __init__(self, provider_manager: ProviderManager):
        self.provider = provider_manager.get_provider("seo")
        
    def analyze(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("[PerformanceAnalyzer] Analyzing overall success metrics...")
        
        prompt = PERFORMANCE_ANALYSIS_PROMPT.format(
            views=metrics.get("views", 0),
            ctr=metrics.get("ctr_percent", 0.0),
            duration=metrics.get("avg_view_duration_sec", 0.0)
        )
        
        try:
            response = self.provider.generate_text(prompt, max_tokens=300)
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].strip()
                
            return json.loads(response)
        except Exception as e:
            logger.error(f"[PerformanceAnalyzer] Failed: {e}")
            return {"overall_score": 50, "conclusion": "Failed to parse."}
