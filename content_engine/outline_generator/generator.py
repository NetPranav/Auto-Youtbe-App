from typing import Any, List
from common import logger
from ..models import ContentStrategy

class OutlineGenerator:
    """
    Generates a logical structure for the video without writing the full script.
    """
    def __init__(self, ai_provider: Any = None):
        self.ai = ai_provider

    def generate_outline(self, context_doc: str, strategy: ContentStrategy) -> List[str]:
        if self.ai:
            from providers.models import TaskCategory
            prompt = f"Generate a video outline for a video about {strategy.objective}."
            raw_response = self.ai.generate_text(
                prompt=prompt, 
                system_prompt="You are an expert YouTube outline writer.",
                task_category=TaskCategory.CONTENT_OUTLINE_GENERATION
            )
            lines = [line.strip() for line in raw_response.split('\n') if line.strip() and not line.startswith("Error")]
            if lines:
                return lines[:5]

        logger.info("Generating structural outline...")
        
        # Mock outline generation
        outline = [
            "1. The Hook and Problem Statement",
            "2. What is this new technology?",
            "3. Why it matters right now",
            "4. A practical code example",
            "5. Conclusion and Call to Action"
        ]
        
        return outline
