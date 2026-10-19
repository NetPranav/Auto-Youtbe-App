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
        
        script = None
        
        if self.provider_manager and self.db:
            prompt = (
                f"Write a YouTube Shorts script about a real, true-life love story based on this hook: {hook.text}\n"
                f"Context:\n{context_doc[:2000]}\n\n"
                f"Tone: {strategy.tone}\n\n"
                f"RULES:\n"
                f"- Tell a captivating, emotional romance story (include funny or fiercely loyal moments if present).\n"
                f"- The climax/resolution MUST NOT use meta-language like 'This is a true story' or 'Here is their photo'.\n"
                f"- INSTEAD, simply end the script by revealing the names of the couple (e.g., 'This was the story of John and Mary.'). The visuals will handle the photo reveal.\n"
                f"- Do NOT use markdown. Do NOT use headers like 'Hook' or 'Video Title'.\n"
                f"- Do NOT say 'welcome back', 'hey guys', 'subscribe', or any channel promotion.\n"
                f"- Write in short, punchy sentences. One idea per sentence.\n"
                f"- Target length: EXACTLY 10 to 15 sentences total.\n"
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
        
        # Fallback: Build a clean script
        logger.warning("AI script generation unavailable. Building fallback script.")
        script = self._build_fallback_script(hook, outline, strategy, context_doc)
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
    
    def _build_fallback_script(self, hook: HookData, outline: List[str], strategy: ContentStrategy, context_doc: str = "") -> str:
        """
        Builds a clean, information-dense fallback script from the context doc.
        Uses the structured research fields to create flowing documentary narration.
        """
        import re
        sentences = []
        
        # 1. Start with the hook (cleaned)
        hook_text = hook.text.strip()
        hook_text = re.sub(r'^\d+\.\s*\**', '', hook_text).strip().strip('"').strip("*")
        if hook_text:
            sentences.append(hook_text)
        
        # 2. Parse context doc fields for structured narration
        fields = self._parse_context_fields(context_doc)
        
        # Problem definition → sets up the conflict
        if fields.get("problem_definition"):
            sentences.append(fields["problem_definition"])
        
        # Historical comparison → gives depth
        if fields.get("historical_comparison"):
            sentences.append(f"Historically, {fields['historical_comparison'].lstrip('Historically, ').lstrip('historically, ')}")
        
        # Root cause analysis → the "why"
        if fields.get("root_cause_analysis"):
            sentences.append(f"The root cause? {fields['root_cause_analysis']}")
        
        # Supporting evidence → credibility
        if fields.get("supporting_evidence"):
            sentences.append(fields["supporting_evidence"])
        
        # Counterarguments → fairness
        if fields.get("counterarguments"):
            sentences.append(f"Some argue the opposite. {fields['counterarguments']}")
        
        # Global comparison → perspective
        if fields.get("global_comparison"):
            sentences.append(fields["global_comparison"])
        
        # Practical solutions → resolution
        if fields.get("practical_solutions"):
            sentences.append(fields["practical_solutions"])
        
        # 3. If we didn't get enough from context, pad with outline points
        if len(sentences) < 8:
            for point in outline:
                clean = re.sub(r'^\d+[\.)]?\s*', '', point).strip()
                clean = re.sub(r'^[-•]\s*', '', clean).strip()
                if clean and len(clean) > 15 and clean not in sentences:
                    sentences.append(clean)
        
        # 4. Closing statement
        if strategy and strategy.objective:
            sentences.append(f"This is exactly why {strategy.objective.lower().rstrip('.')} matters right now.")
        
        return " ".join(sentences)
    
    def _parse_context_fields(self, context_doc: str) -> dict:
        """Extract structured fields from the context document."""
        fields = {}
        if not context_doc:
            return fields
        
        # Parse "Key: Value" lines
        field_map = {
            "Problem Definition": "problem_definition",
            "Historical Comparison": "historical_comparison",
            "Root Cause Analysis": "root_cause_analysis",
            "Supporting Evidence": "supporting_evidence",
            "Counterarguments": "counterarguments",
            "Global Comparison": "global_comparison",
            "Practical Solutions": "practical_solutions",
        }
        
        for line in context_doc.split("\n"):
            for label, key in field_map.items():
                if line.startswith(f"{label}:"):
                    value = line[len(label) + 1:].strip()
                    if value and value.lower() != "none":
                        fields[key] = value
                    break
        
        return fields
