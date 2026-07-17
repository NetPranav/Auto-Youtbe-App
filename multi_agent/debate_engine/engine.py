import json
from typing import List
from sqlalchemy.orm import Session
from common import logger
from database.models import AgentRun, PeerReview, DebateRound
from providers.manager import ProviderManager
from multi_agent.prompt_variants.prompts import PEER_REVIEW_PROMPT, DEBATE_PROMPT



class DebateEngine:
    """
    Enables agents to critique each other's work and argue for improvements.
    """
    def __init__(self, db_session: Session, provider_manager: ProviderManager):
        self.db = db_session
        self.provider = provider_manager.get_provider("content")
        
    def peer_review(self, runs: List[AgentRun], task_context: str) -> List[PeerReview]:
        """Each agent reviews every other agent's draft."""
        logger.info(f"[DebateEngine] Starting peer review across {len(runs)} drafts...")
        reviews = []
        
        for reviewer_run in runs:
            for target_run in runs:
                if reviewer_run.id == target_run.id:
                    continue
                    
                prompt = PEER_REVIEW_PROMPT.format(
                    task_context=task_context,
                    draft=target_run.output_text[:2000]
                )
                
                full_prompt = f"{reviewer_run.agent.personality_prefix}\n\n{prompt}"
                
                try:
                    response = self.provider.generate_text(full_prompt, max_tokens=500)
                    if "```json" in response:
                        response = response.split("```json")[1].split("```")[0].strip()
                    elif "```" in response:
                        response = response.split("```")[1].strip()
                    feedback = json.loads(response)
                except Exception as e:
                    logger.warning(f"[DebateEngine] Peer review parse failed: {e}")
                    feedback = {"strengths": [], "weaknesses": ["Parse error"], "score": 5}
                    
                review = PeerReview(
                    reviewer_agent_id=reviewer_run.agent_id,
                    reviewed_run_id=target_run.id,
                    feedback_json=feedback
                )
                self.db.add(review)
                reviews.append(review)
                
        self.db.commit()
        logger.info(f"[DebateEngine] Completed {len(reviews)} peer reviews.")
        return reviews
        
    def debate(self, runs: List[AgentRun], rounds: int = 1) -> List[DebateRound]:
        """Agents argue about each other's work."""
        logger.info(f"[DebateEngine] Starting debate ({rounds} rounds)...")
        all_rounds = []
        previous_args = ""
        
        for round_num in range(1, rounds + 1):
            for run in runs:
                prompt = DEBATE_PROMPT.format(
                    expertise=run.agent.expertise,
                    draft=run.output_text[:1500],
                    previous_arguments=previous_args[-1000:] if previous_args else "None yet."
                )
                
                try:
                    argument = self.provider.generate_text(prompt, max_tokens=200)
                except Exception:
                    argument = "No argument generated."
                    
                dr = DebateRound(
                    round_number=round_num,
                    agent_id=run.agent_id,
                    argument=argument,
                    target_run_id=run.id
                )
                self.db.add(dr)
                all_rounds.append(dr)
                previous_args += f"\n{run.agent.name}: {argument}"
                
        self.db.commit()
        logger.info(f"[DebateEngine] Debate completed with {len(all_rounds)} arguments.")
        return all_rounds
