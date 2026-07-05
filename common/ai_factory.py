from typing import Any
from config import config
from .ai_provider import BaseAIProvider, MockAIProvider
from .nim_provider import NimAIProvider

def get_ai_provider() -> BaseAIProvider:
    provider_name = config.ai_text_provider.lower()
    
    if provider_name == "nim":
        return NimAIProvider()
    elif provider_name == "mock":
        return MockAIProvider()
    else:
        # Fallback to mock
        return MockAIProvider()
