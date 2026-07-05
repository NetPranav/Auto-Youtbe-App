from common.logger import get_logger

logger = get_logger(__name__)

class PromptManager:
    """
    Manages prompt variants for A/B testing and experimentation.
    Future: Connect to database to track which variants win the Judge decisions most often.
    """
    
    def __init__(self):
        self.variants = {}
        
    def get_prompt(self, task_context: str) -> str:
        # In a fully fleshed out system, this would randomly select between
        # variant A and variant B to see which produces better retention.
        logger.debug(f"[PromptManager] Returning default prompt for {task_context}")
        return f"Perform the task: {task_context}"
        
    def register_variant(self, task_context: str, template: str, version: str):
        if task_context not in self.variants:
            self.variants[task_context] = []
        self.variants[task_context].append({
            "version": version,
            "template": template
        })
