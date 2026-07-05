import json
from common.logger import get_logger
from providers.manager import ProviderManager
from publisher.prompts.metadata_prompt import METADATA_GENERATION_PROMPT

logger = get_logger(__name__)

class MetadataGenerator:
    def __init__(self, provider_manager: ProviderManager):
        self.provider = provider_manager.get_provider("seo")
        
    def generate(self, script_text: str) -> dict:
        logger.info("[MetadataGenerator] Generating YouTube metadata...")
        
        prompt = METADATA_GENERATION_PROMPT.format(script=script_text)
        
        try:
            response = self.provider.generate_text(prompt, max_tokens=1000)
            
            # Clean JSON if wrapped in markdown
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].strip()
                
            metadata = json.loads(response)
            
            if "title" not in metadata or "description" not in metadata:
                raise ValueError("Incomplete metadata JSON returned.")
                
            logger.info(f"[MetadataGenerator] Generated Title: {metadata['title']}")
            return metadata
            
        except Exception as e:
            logger.error(f"[MetadataGenerator] Failed to generate metadata: {e}")
            # Fallback
            return {
                "title": "Automated YouTube Video",
                "description": "This video was automatically generated. #automation #ai",
                "tags": ["automation", "ai", "youtube"],
                "hashtags": ["#automation", "#ai"]
            }
