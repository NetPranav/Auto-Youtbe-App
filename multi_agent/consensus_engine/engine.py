from typing import List
from sqlalchemy.orm import Session
from common import logger
from database.models import AgentRun, JudgeDecision, ConsensusResult
from providers.manager import ProviderManager
from multi_agent.prompt_variants.prompts import CONSENSUS_PROMPT



class ConsensusEngine:
    """
    Merges the best elements of multiple drafts into one superior output,
    guided by the Judge's decision.
    """
    def __init__(self, db_session: Session, provider_manager: ProviderManager):
        self.db = db_session
        self.provider = provider_manager.get_provider("content")
        
    def merge(self, runs: List[AgentRun], judge_decision: JudgeDecision, task_context: str) -> ConsensusResult:
        logger.info(f"[ConsensusEngine] Merging {len(runs)} drafts into final consensus...")
        
        drafts_section = ""
        for i, run in enumerate(runs):
            drafts_section += f"\n--- Draft {i+1} (by {run.agent.name}) ---\n{run.output_text}\n"
            
        prompt = CONSENSUS_PROMPT.format(
            task_context=task_context,
            drafts_section=drafts_section,
            judge_reasoning=judge_decision.reasoning
        )
        
        try:
            merged_output = self.provider.generate_text(prompt)
        except Exception as e:
            logger.error(f"[ConsensusEngine] Merge failed: {e}. Defaulting to winner draft.")
            winner_run = self.db.query(AgentRun).filter(AgentRun.id == judge_decision.winner_run_id).first()
            merged_output = winner_run.output_text if winner_run else "Error generating output."
            
        result = ConsensusResult(
            task_context=task_context,
            merged_output=merged_output,
            source_run_ids_json=[r.id for r in runs]
        )
        self.db.add(result)
        self.db.commit()
        
        logger.info("[ConsensusEngine] Consensus reached successfully.")
        return result
