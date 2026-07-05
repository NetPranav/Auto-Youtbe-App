from typing import Optional
from providers.models import TaskCategory

class BaseLLMProvider:
    def generate_text(self, prompt: str, system_prompt: str = "", task_category: TaskCategory = TaskCategory.DEFAULT_REASONING) -> str:
        raise NotImplementedError
        
    def generate_json(self, prompt: str, system_prompt: str = "", task_category: TaskCategory = TaskCategory.DEFAULT_REASONING) -> str:
        raise NotImplementedError
