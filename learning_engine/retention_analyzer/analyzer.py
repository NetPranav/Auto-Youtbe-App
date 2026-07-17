import json
from typing import Dict, Any
from common import logger
from providers.manager import ProviderManager
from learning_engine.prompts.analyzer_prompts import RETENTION_ANALYSIS_PROMPT



class RetentionAnalyzer:
    def __init__(self, provider_manager: ProviderManager):
        self.provider = provider_manager.get_provider("seo")
        
    def analyze(self, graph: Dict[str, int]) -> Dict[str, str]:
        logger.info("[RetentionAnalyzer] Analyzing audience drop-offs...")
        
        prompt = RETENTION_ANALYSIS_PROMPT.format(graph=json.dumps(graph))
        
        try:
            response = self.provider.generate_text(prompt, max_tokens=300)
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].strip()
                
            return json.loads(response)
        except Exception as e:
            logger.error(f"[RetentionAnalyzer] Failed: {e}")
            return {"hook_quality": "unknown", "recommendation": "Unable to analyze retention."}
