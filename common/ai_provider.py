import os
from typing import Any
from config import config

class BaseAIProvider:
    def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError
        
    def generate_json(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError

class MockAIProvider(BaseAIProvider):
    def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        return f"Mocked AI response for prompt: {prompt[:30]}..."
        
    def generate_json(self, prompt: str, system_prompt: str = "") -> str:
        return '{"status": "mocked", "result": "success"}'
