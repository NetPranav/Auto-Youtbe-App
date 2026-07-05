from typing import Any, List
from common import logger
from ..models import ContentStrategy, HookData

class ScriptGenerator:
    """
    Generates the complete draft script based on the strategy, hook, and outline.
    """
    def __init__(self, ai_provider: Any = None):
        self.ai = ai_provider

    def generate_draft(self, context_doc: str, strategy: ContentStrategy, hook: HookData, outline: List[str]) -> str:
        """
        Drafts the initial script.
        """
        logger.info("Drafting initial script...")
        if self.ai:
            from providers.models import TaskCategory
            prompt = f"Write a YouTube script using this hook: {hook.text}. Use the outline: {outline}. Strategy: {strategy.tone}. Make it around {strategy.video_length_minutes * 60} seconds long."
            script = self.ai.generate_text(
                prompt=prompt, 
                system_prompt="You are an expert YouTube scriptwriter.",
                task_category=TaskCategory.CONTENT_SCRIPT_WRITING
            )
            # Fallback if AI fails or returns empty
            if not script or script.startswith("Error:"):
                script = f"{hook.text}\n\nWelcome back... [AI Generation Failed]"
        else:
            script = f"{hook.text}\n\nWelcome back to the channel. Today we're looking at something brand new."
            
        return script
