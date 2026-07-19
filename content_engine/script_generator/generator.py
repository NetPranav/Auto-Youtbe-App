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
        For Shorts: pure information, no filler, no channel promotion.
        """
        logger.info("Drafting initial script via AI Editorial Board...")
        
        script = None
        
        if self.provider_manager and self.db:
            prompt = (
                f"Write a YouTube Shorts script about: {hook.text}\n"
                f"Outline: {outline}\n"
                f"Tone: {strategy.tone}\n\n"
                f"RULES:\n"
                f"- Pure information only. No filler.\n"
                f"- Do NOT use markdown. Do NOT use headers like 'Hook' or 'Video Title'.\n"
                f"- Do NOT say 'welcome back', 'hey guys', 'subscribe', 'like and share', or any channel promotion.\n"
                f"- Do NOT include stage directions, brackets, or meta-commentary.\n"
                f"- Write in short, punchy sentences. One idea per sentence.\n"
                f"- Target length: EXACTLY 15 to 20 sentences total.\n"
                f"- Output ONLY the spoken words of the script, nothing else.\n"
            )
            
            try:
                script = self.provider_manager.collaborative_generate(
                    prompt=prompt,
                    task_context="SCRIPT_GENERATION",
                    db_session=self.db,
                    agent_count=3
                )
            except Exception as e:
                logger.error(f"Multi-agent generation failed: {e}")
                script = None
                
            # Validate: reject if it contains error markers or is too short
            if script and not script.startswith("Error:") and len(script.strip()) > 50:
                # Clean any accidental meta-text the AI might have added
                script = self._clean_script(script)
                return script
        
        # Fallback: Build a clean, factual script from the outline
        logger.warning("AI script generation unavailable. Building factual fallback script.")
        script = self._build_fallback_script(hook, outline, strategy)
        return script
    
    def _clean_script(self, script: str) -> str:
        """Remove any AI artifacts, brackets, or meta-commentary from the script."""
        import re
        # Remove anything in square brackets like [pause], [AI Generation Failed], etc.
        script = re.sub(r'\[.*?\]', '', script)
        # Remove common AI filler phrases
        filler_phrases = [
            "welcome back to the channel",
            "hey guys",
            "don't forget to subscribe",
            "like and subscribe",
            "smash that like button",
            "hit the bell icon",
            "see you in the next one",
            "make sure to subscribe",
            "let me know in the comments",
        ]
        for phrase in filler_phrases:
            script = re.sub(re.escape(phrase), '', script, flags=re.IGNORECASE)
        # Clean up extra whitespace
        script = re.sub(r'\n{3,}', '\n\n', script)
        script = re.sub(r'  +', ' ', script)
        return script.strip()
    
    def _build_fallback_script(self, hook: HookData, outline: List[str], strategy: ContentStrategy) -> str:
        """Builds a clean, information-dense fallback script from the outline."""
        sentences = []
        
        # Start with the hook (cleaned)
        hook_text = hook.text.strip()
        # Remove any numbering or formatting from hook
        import re
        hook_text = re.sub(r'^\d+\.\s*\**', '', hook_text).strip().strip('"').strip("*")
        if hook_text:
            sentences.append(hook_text)
        
        # Convert each outline point into a clean sentence
        for point in outline:
            # Strip numbering like "1. " or "- "
            clean = re.sub(r'^\d+[\.\)]\s*', '', point).strip()
            clean = re.sub(r'^[-•]\s*', '', clean).strip()
            if clean and len(clean) > 10:
                sentences.append(clean)
        
        # Add a strong closing fact based on the strategy
        if strategy and strategy.objective:
            sentences.append(f"This is exactly why {strategy.objective.lower().rstrip('.')} matters right now.")
        
        # Join with double newlines so the scene planner splits them properly
        return "\n\n".join(sentences)

