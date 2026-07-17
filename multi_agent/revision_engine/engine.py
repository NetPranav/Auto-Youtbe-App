from common import logger
from providers.manager import ProviderManager
from multi_agent.prompt_variants.prompts import REVISION_PROMPT



class RevisionEngine:
    """
    Performs a final editorial polish on the consensus output.
    """
    def __init__(self, provider_manager: ProviderManager):
        self.provider = provider_manager.get_provider("content")
        
    def polish(self, content: str) -> str:
        logger.info("[RevisionEngine] Performing final editorial polish...")
        
        prompt = REVISION_PROMPT.format(content=content)
        
        try:
            polished = self.provider.generate_text(prompt, max_tokens=2500)
            return polished
        except Exception as e:
            logger.error(f"[RevisionEngine] Polish failed: {e}. Returning original content.")
            return content
