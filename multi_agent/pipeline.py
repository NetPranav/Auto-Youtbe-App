from sqlalchemy.orm import Session
from common import logger
from providers.manager import ProviderManager

from multi_agent.agent_registry.registry import AgentRegistry
from multi_agent.agent_manager.manager import AgentManager
from multi_agent.debate_engine.engine import DebateEngine
from multi_agent.judge_engine.engine import JudgeEngine
from multi_agent.consensus_engine.engine import ConsensusEngine
from multi_agent.revision_engine.engine import RevisionEngine
from multi_agent.evaluation.scorer import Scorer



class MultiAgentPipeline:
    """
    Orchestrates the entire AI Editorial Board workflow:
    Parallel Generation -> Peer Review -> Debate -> Judge -> Consensus -> Revision
    """
    def __init__(self, db_session: Session, provider_manager: ProviderManager):
        self.db = db_session
        self.provider_manager = provider_manager
        
        self.registry = AgentRegistry()
        self.manager = AgentManager(db_session, provider_manager)
        self.debate = DebateEngine(db_session, provider_manager)
        self.judge = JudgeEngine(db_session, provider_manager)
        self.consensus = ConsensusEngine(db_session, provider_manager)
        self.revision = RevisionEngine(provider_manager)
        self.scorer = Scorer(db_session)
        
    def run_collaborative(self, prompt: str, task_context: str, agent_count: int = 3) -> str:
        logger.info(f"=== [MultiAgentPipeline] Starting AI Editorial Board for {task_context} ===")
        
        # 1. Assignment
        agents = self.registry.get_agents_for_task(task_context, count=agent_count)
        
        # 2. Parallel Generation
        runs = self.manager.run_parallel(agents, prompt, task_context)
        if not runs:
            logger.error("[MultiAgentPipeline] All agents failed to generate drafts. Aborting.")
            raise Exception("Multi-agent generation failed entirely.")
            
        # 3. Peer Review
        self.debate.peer_review(runs, task_context)
        
        # 4. Debate
        self.debate.debate(runs, rounds=1)
        
        # 5. Judge
        decision = self.judge.judge(runs, task_context)
        
        # 6. Consensus
        consensus_result = self.consensus.merge(runs, decision, task_context)
        
        # 7. Revision
        final_output = self.revision.polish(consensus_result.merged_output)
        
        # 8. Evaluation / Scoring
        self.scorer.record_scores(decision)
        
        logger.info(f"=== [MultiAgentPipeline] Editorial Board Consensus Reached ===")
        return final_output
