import re
from typing import Any, List
from common import logger
from ..models import ContentStrategy, HookData

class HookGenerator:
    """
    Generates multiple opening hooks and selects the best one.
    """
    def __init__(self, ai_provider: Any = None):
        self.ai = ai_provider

    def generate_hook(self, context_doc: str, strategy: ContentStrategy) -> HookData:
        """
        Generates 3 hooks, scores them via LLM, and returns the highest scored hook.
        """
        logger.info("Generating and scoring opening hooks...")

        hooks = []
        if self.ai:
            from providers.models import TaskCategory

            # Step 1: Generate hooks
            gen_prompt = (
                f"Write 3 punchy, attention-grabbing opening hooks for a YouTube Shorts documentary.\n"
                f"Topic: {strategy.objective}\n"
                f"Tone: {strategy.tone}\n"
                f"Target audience: {strategy.target_audience}\n\n"
                f"Rules:\n"
                f"- Each hook must be 1-2 sentences max\n"
                f"- No filler, no 'hey guys', no questions like 'did you know'\n"
                f"- Start with a powerful fact or shocking statement\n"
                f"- Number them 1. 2. 3.\n"
            )
            raw_response = self.ai.generate_text(
                prompt=gen_prompt,
                system_prompt="You are an expert YouTube hook writer. Write hooks that stop the scroll.",
                task_category=TaskCategory.CONTENT_HOOK_GENERATION
            )

            lines = [line.strip() for line in raw_response.split('\n') if line.strip()]
            # Clean numbering
            hook_texts = []
            for line in lines:
                clean = re.sub(r'^\d+[\.\)]\s*', '', line).strip().strip('"').strip("*")
                if clean and len(clean) > 15:
                    hook_texts.append(clean)
            hook_texts = hook_texts[:3]

            # Step 2: Score each hook via LLM
            for hook_text in hook_texts:
                score = self._score_hook(hook_text, strategy)
                hooks.append(HookData(text=hook_text, score=score))

        if not hooks:
            hooks = [
                HookData(text="You won't believe what just launched.", score=7.0),
                HookData(text="Stop writing code the old way. This changes everything.", score=7.5),
                HookData(text="Is this the end of traditional programming?", score=7.0)
            ]

        # Select highest scoring hook
        best_hook = max(hooks, key=lambda h: h.score)

        logger.info(f"Selected Hook (Score: {best_hook.score}): {best_hook.text}")
        return best_hook

    def _score_hook(self, hook_text: str, strategy: ContentStrategy) -> float:
        """Ask the LLM to score a single hook on a 1-10 scale."""
        if not self.ai:
            return 7.0

        from providers.models import TaskCategory
        prompt = (
            f"Score this YouTube hook on a scale of 1 to 10 for attention-grabbing power.\n"
            f"Hook: \"{hook_text}\"\n"
            f"Target audience: {strategy.target_audience}\n\n"
            f"Respond with ONLY a single number."
        )
        try:
            resp = self.ai.generate_text(
                prompt=prompt,
                system_prompt="You are a YouTube analytics expert. Respond with ONLY a number.",
                task_category=TaskCategory.CONTENT_HOOK_GENERATION
            )
            numbers = re.findall(r'\b(\d+(?:\.\d+)?)\b', resp)
            if numbers:
                return max(1.0, min(10.0, float(numbers[0])))
        except Exception as e:
            logger.warning(f"[HookGenerator] Failed to score hook: {e}")

        return 7.0

