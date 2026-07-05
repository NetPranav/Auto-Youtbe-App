import json
from typing import List, Dict
from sqlalchemy.orm import Session
from common.logger import get_logger
from database.models import AgentRun, JudgeDecision
from providers.manager import ProviderManager
from multi_agent.prompt_variants.prompts import JUDGE_PROMPT

logger = get_logger(__name__)

class JudgeEngine:
    """
    The Chief Editor. Scores all drafts and selects the strongest candidate.
    """
    def __init__(self, db_session: Session, provider_manager: ProviderManager):
        self.db = db_session
        self.provider = provider_manager.get_provider("content")
        
    def judge(self, runs: List[AgentRun], task_context: str) -> JudgeDecision:
        logger.info(f"[JudgeEngine] Judging {len(runs)} drafts for {task_context}...")
        
        drafts_section = ""
        for i, run in enumerate(runs):
            drafts_section += f"\n--- Draft {i+1} (by {run.agent.name}) ---\n{run.output_text[:1500]}\n"
            
        prompt = JUDGE_PROMPT.format(
            num_drafts=len(runs),
            task_context=task_context,
            drafts_section=drafts_section
        )
        
        try:
            response = self.provider.generate_text(prompt, max_tokens=800)
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].strip()
            result = json.loads(response)
        except Exception as e:
            logger.error(f"[JudgeEngine] Parse failed: {e}. Defaulting to first draft.")
            result = {
                "scores": {},
                "winner": "Draft 1",
                "reasoning": "Judge parse failed. Defaulting to first draft."
            }
            
        # Find the winning run
        winner_label = result.get("winner", "Draft 1")
        winner_idx = 0
        try:
            winner_idx = int(winner_label.split(" ")[1]) - 1
        except (ValueError, IndexError):
            winner_idx = 0
        winner_idx = min(winner_idx, len(runs) - 1)
        
        decision = JudgeDecision(
            task_context=task_context,
            scores_json=result.get("scores", {}),
            winner_run_id=runs[winner_idx].id,
            reasoning=result.get("reasoning", "")
        )
        self.db.add(decision)
        self.db.commit()
        
        logger.info(f"[JudgeEngine] Winner: {runs[winner_idx].agent.name} — {result.get('reasoning', '')[:100]}")
        return decision
