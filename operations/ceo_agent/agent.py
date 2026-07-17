from sqlalchemy.orm import Session
from common import logger
from database.models import OperationDecision, QueueItem
from operations.decision_engine.engine import DecisionEngine
from operations.workflow_planner.planner import WorkflowPlanner



class CEOAgent:
    def __init__(self, db_session: Session, decision_engine: DecisionEngine, workflow_planner: WorkflowPlanner):
        self.db = db_session
        self.decision_engine = decision_engine
        self.workflow_planner = workflow_planner
        
    def execute_strategic_cycle(self):
        logger.info("=== [CEO Agent] Initiating Strategic Evaluation Cycle ===")
        
        # 1. Check if we already have too much in the queue (backpressure)
        pending = self.db.query(QueueItem).filter(QueueItem.status == "PENDING").count()
        if pending > 10:
            logger.info(f"[CEO Agent] Queue is full ({pending} tasks). Skipping generation cycle.")
            return
            
        # 2. Consult Decision Engine
        decision = self.decision_engine.decide()
        
        # 3. Log Decision
        op = OperationDecision(
            decision_type=decision["decision"],
            justification=decision["justification"]
        )
        self.db.add(op)
        self.db.commit()
        
        logger.info(f"[CEO Agent] Decision: {decision['decision']} | Reason: {decision['justification']}")
        
        # 4. Take Action
        if decision["decision"] == "GENERATE":
            self.workflow_planner.start_new_workflow(decision["topic"])
