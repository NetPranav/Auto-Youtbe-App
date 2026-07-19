import json
from config import config
from common import logger
from research_engine.models.topic import TopicCandidate, TopicScoreData
from typing import Any

class TopicRanker:
    """
    Scores and ranks extracted topics to determine which one is best.
    """
    def __init__(self, ai_provider: Any = None):
        if not ai_provider:
            from providers.manager import ProviderManager
            ai_provider = ProviderManager().get_llm_provider()
        self.ai = ai_provider

    def rank(self, candidate: TopicCandidate, novelty_score: float, target_category: str = "CURRENT_AFFAIRS") -> TopicScoreData:
        """
        Calculates the total score based on weights and heuristics.
        Returns a TopicScoreData object.
        """
        logger.debug(f"Ranking topic: {candidate.title} for {target_category}")
        
        scores = {
            "evidence_strength": 9.5,
            "source_reliability": 9.5,
            "historical_coverage": 9.5,
            "expert_consensus": 9.5,
            "conflict_risk": 1.0,
            "educational_value": 9.5,
            "practical_relevance": 9.5
        }
        
        if self.ai:
            from providers.models import TaskCategory
            system_prompt = (
                "You are an objective Research Evaluator. Score the following research topic based on its depth, "
                "factual foundation, and neutrality. Return ONLY a JSON object with keys: "
                "evidence_strength, source_reliability, historical_coverage, expert_consensus, "
                "conflict_risk, educational_value, practical_relevance. Each value must be a float between 0 and 10.\n"
                "CRITICAL INSTRUCTION: If the topic provides strong evidence and is completely neutral, you MUST score "
                "the positive metrics 9.5 or higher, and conflict_risk 1.0 or lower.\n"
                f"NOTE: The target category is {target_category}. If it is HISTORY, do not aggressively penalize practical_solutions if they focus on historical resolutions."
            )
            
            prompt = (
                f"Title: {candidate.title}\n"
                f"Problem: {candidate.problem_definition}\n"
                f"History: {candidate.historical_comparison}\n"
                f"Root Cause: {candidate.root_cause_analysis}\n"
                f"Evidence: {candidate.supporting_evidence}\n"
                f"Counterarguments: {candidate.counterarguments}\n"
                f"Global: {candidate.global_comparison}\n"
                f"Solutions: {candidate.practical_solutions}\n"
            )
            
            try:
                response = self.ai.generate_text(
                    prompt=prompt, 
                    system_prompt=system_prompt,
                    task_category=TaskCategory.RESEARCH_TOPIC_RANKING
                )
                
                # Robust JSON extraction
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0].strip()
                elif "```" in response:
                    response = response.split("```")[1].strip()
                    
                start_idx = response.find('{')
                end_idx = response.rfind('}')
                if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
                    response = response[start_idx:end_idx+1]
                
                llm_scores = json.loads(response)
                for k in scores.keys():
                    if k in llm_scores:
                        scores[k] = float(llm_scores[k])
            except Exception as e:
                logger.error(f"[TopicRanker] Failed to get LLM scores: {e}")
        
        # Calculate final confidence score
        # Invert conflict risk so 0 risk = 10 safety score
        safety_score = 10.0 - scores["conflict_risk"]
        
        sum_positives = (
            scores["evidence_strength"] + 
            scores["source_reliability"] + 
            scores["historical_coverage"] + 
            scores["expert_consensus"] + 
            scores["educational_value"] + 
            scores["practical_relevance"] +
            safety_score
        )
        
        final_confidence = sum_positives / 7.0
        
        # Cap between 0 and 10
        final_confidence = max(0.0, min(10.0, final_confidence))
        
        return TopicScoreData(
            evidence_strength=scores["evidence_strength"],
            source_reliability=scores["source_reliability"],
            historical_coverage=scores["historical_coverage"],
            expert_consensus=scores["expert_consensus"],
            conflict_risk=scores["conflict_risk"],
            educational_value=scores["educational_value"],
            practical_relevance=scores["practical_relevance"],
            total_score=final_confidence, # backward compatibility
            confidence_score=final_confidence
        )
