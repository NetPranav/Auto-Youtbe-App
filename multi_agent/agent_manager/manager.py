import time
import uuid
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from common import logger
from database.models import AgentProfile, AgentRun
from providers.manager import ProviderManager



class AgentManager:
    """
    Orchestrates agent lifecycle: creates profiles, assigns tasks, collects outputs.
    """
    def __init__(self, db_session: Session, provider_manager: ProviderManager):
        self.db = db_session
        self.provider_manager = provider_manager
        
    def ensure_profile(self, agent_def: Dict) -> AgentProfile:
        """Get or create an AgentProfile in the DB."""
        existing = self.db.query(AgentProfile).filter(AgentProfile.name == agent_def["name"]).first()
        if existing:
            return existing
            
        profile = AgentProfile(
            name=agent_def["name"],
            expertise=agent_def["expertise"],
            personality_prefix=agent_def.get("personality_prefix", "")
        )
        self.db.add(profile)
        self.db.commit()
        return profile
        
    def run_agent(self, profile: AgentProfile, prompt: str, task_context: str) -> AgentRun:
        """Execute a single agent against a prompt and store the result."""
        logger.info(f"[AgentManager] Running agent '{profile.name}' for {task_context}...")
        
        full_prompt = f"{profile.personality_prefix}\n\n{prompt}"
        
        provider = self.provider_manager.get_provider("content")
        
        start = time.perf_counter()
        try:
            output = provider.generate_text(full_prompt, max_tokens=2000)
        except Exception as e:
            logger.error(f"[AgentManager] Agent '{profile.name}' failed: {e}")
            output = None
        elapsed = time.perf_counter() - start
        
        run = AgentRun(
            agent_id=profile.id,
            task_context=task_context,
            prompt_used=full_prompt,
            output_text=output,
            duration_sec=round(elapsed, 2)
        )
        self.db.add(run)
        self.db.commit()
        
        logger.info(f"[AgentManager] Agent '{profile.name}' completed in {elapsed:.2f}s")
        return run
        
    def run_parallel(self, agent_defs: List[Dict], prompt: str, task_context: str) -> List[AgentRun]:
        """Run multiple agents on the same prompt and collect all outputs."""
        runs = []
        for agent_def in agent_defs:
            profile = self.ensure_profile(agent_def)
            run = self.run_agent(profile, prompt, task_context)
            if run.output_text:
                runs.append(run)
        return runs
