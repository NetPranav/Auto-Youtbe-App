from typing import Any, List
from common import logger
from ..models import ContentStrategy, HookData

class ScriptGenerator:
    """
    Generates the complete draft script based on the strategy, hook, and outline.
    Now leverages the Multi-Agent Intelligence Platform for collaborative peer-reviewed drafting.
    """
    def __init__(self, provider_manager: Any = None, db_session: Any = None):
        self.provider_manager = provider_manager
        self.db = db_session

    def generate_draft(self, context_doc: str, strategy: ContentStrategy, hook: HookData, outline: List[str]) -> str:
        """
        Drafts the initial script using the AI Editorial Board.
        """
        logger.info("Drafting initial script via AI Editorial Board...")
        
        if self.provider_manager and self.db:
            prompt = f"Write a YouTube script using this hook: {hook.text}. Use the outline: {outline}. Strategy: {strategy.tone}. Make it around {strategy.video_length_minutes * 60} seconds long."
            
            try:
                # This routes through Parallel Generation -> Peer Review -> Debate -> Judge -> Consensus -> Revision
                script = self.provider_manager.collaborative_generate(
                    prompt=prompt,
                    task_context="SCRIPT_GENERATION",
                    db_session=self.db,
                    agent_count=3
                )
            except Exception as e:
                logger.error(f"Multi-agent generation failed: {e}")
                script = None
                
            # Fallback if AI fails or returns empty
            if not script or script.startswith("Error:"):
                script = f"{hook.text}\n\nWelcome back... [AI Generation Failed]"
        else:
            script = f"{hook.text}\n\nWelcome back to the channel. Today we're looking at something brand new."
            
        return script
