from datetime import datetime, timezone
from sqlalchemy.orm import Session
from common import logger
from database.models import JudgeDecision, ModelPerformance, AgentRun



class Scorer:
    """
    Updates historical model performance based on Judge scores.
    """
    def __init__(self, db_session: Session):
        self.db = db_session
        
    def record_scores(self, judge_decision: JudgeDecision):
        logger.info("[Scorer] Recording evaluation scores...")
        
        scores_json = judge_decision.scores_json or {}
        
        for run_id_str, criteria in scores_json.items():
            # Run id in the JSON is usually "Draft X", but ideally we map it back.
            # Since the Judge just says "Draft 1", we have to map it if we can.
            pass
            
        # For simplicity in this implementation, we will just record that the winner model got a win.
        winner_run = self.db.query(AgentRun).filter(AgentRun.id == judge_decision.winner_run_id).first()
        if not winner_run:
            return
            
        # We don't have the explicit model ID stored on the run in the DB yet, but we can assume
        # the provider used (e.g. from env). For now, we will store performance by Agent Profile ID
        # to track which persona performs best.
        
        perf = self.db.query(ModelPerformance).filter(
            ModelPerformance.model_id == winner_run.agent_id,
            ModelPerformance.task_context == judge_decision.task_context
        ).first()
        
        if not perf:
            perf = ModelPerformance(
                model_id=winner_run.agent_id,
                task_context=judge_decision.task_context
            )
            self.db.add(perf)
            
        perf.total_runs += 1
        perf.avg_score = ((perf.avg_score * (perf.total_runs - 1)) + 10.0) / perf.total_runs # Assume win = 10 for now
        perf.updated_at = datetime.now(timezone.utc)
        
        self.db.commit()
        logger.info(f"[Scorer] Updated performance history for {winner_run.agent.name}.")
