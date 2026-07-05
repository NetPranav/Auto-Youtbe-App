from typing import Any
import json
from openai import OpenAI
from config import config
from .ai_provider import BaseAIProvider
from common import logger

class NimAIProvider(BaseAIProvider):
    def __init__(self):
        # NVIDIA NIM provides an OpenAI-compatible endpoint
        api_key = config.nvidia_nim_api_key or "NO_KEY"
        if api_key == "NO_KEY":
            logger.warning("NVIDIA_NIM_API_KEY is not set. NIM AI Provider will likely fail.")
            
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key
        )
        self.model = "meta/llama3-70b-instruct" # Standard high quality model on NIM
        
    def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1024,
            )
            return completion.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"NimAIProvider Text Generation Error: {e}")
            return f"Error: {e}"
            
    def generate_json(self, prompt: str, system_prompt: str = "") -> str:
        try:
            # Note: Not all NIM models support true JSON mode natively via response_format. 
            # We append JSON instruction to the system prompt.
            sys_prompt = system_prompt + "\nIMPORTANT: Return ONLY valid JSON."
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1024,
            )
            content = completion.choices[0].message.content or "{}"
            # Attempt to strip markdown code blocks if the model outputs them
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            return content
        except Exception as e:
            logger.error(f"NimAIProvider JSON Generation Error: {e}")
            return "{}"
