import json
from typing import Any
from common import logger
from ..models import ContentStrategy

class ContentStrategist:
    """
    Determines the overall strategy before writing.
    """
    def __init__(self, ai_provider: Any = None):
        self.ai = ai_provider

    def generate_strategy(self, context_doc: str) -> ContentStrategy:
        """
        Uses AI to generate a content strategy based on the context.
        """
        logger.info("Generating content strategy...")

        if self.ai:
            from providers.models import TaskCategory
            prompt = (
                f"Based on this research context, create a content strategy for a YouTube Shorts documentary.\n\n"
                f"Context:\n{context_doc[:2000]}\n\n"
                f"Return ONLY a JSON object with these keys:\n"
                f'{{"target_audience": "...", "tone": "...", "video_length_minutes": 1, '
                f'"objective": "...", "key_learning_outcomes": ["...", "..."], "curiosity_level": "High/Medium/Low"}}\n'
                f"Do NOT include markdown blocks."
            )
            try:
                response = self.ai.generate_text(
                    prompt=prompt,
                    system_prompt="You are a YouTube content strategist. Return ONLY valid JSON.",
                    task_category=TaskCategory.CONTENT_STRATEGY
                )
                # Extract JSON from response
                if "```" in response:
                    response = response.split("```json")[-1].split("```")[0] if "```json" in response else response.split("```")[1]
                start = response.find("{")
                end = response.rfind("}")
                if start != -1 and end > start:
                    parsed = json.loads(response[start:end+1])
                    strategy = ContentStrategy(
                        target_audience=parsed.get("target_audience", "General audience"),
                        tone=parsed.get("tone", "Educational but energetic"),
                        video_length_minutes=int(parsed.get("video_length_minutes", 1)),
                        objective=parsed.get("objective", f"Explain {context_doc[:50]}"),
                        key_learning_outcomes=parsed.get("key_learning_outcomes", ["Key insight 1", "Key insight 2"]),
                        curiosity_level=parsed.get("curiosity_level", "High"),
                    )
                    logger.info(f"[ContentStrategist] Parsed AI strategy: audience={strategy.target_audience}, tone={strategy.tone}")
                    return strategy
            except Exception as e:
                logger.warning(f"[ContentStrategist] Failed to parse AI strategy: {e}. Using fallback.")

        # Fallback: build strategy from context
        # Extract the topic line from the context doc
        topic_line = context_doc.split("\n")[0].replace("Topic: ", "").strip() if context_doc else "this topic"
        strategy = ContentStrategy(
            target_audience="Curious adults interested in world events and science",
            objective=f"Explain why {topic_line[:80]} matters right now.",
            tone="Informative, documentary-style, with urgency",
            video_length_minutes=1,
            key_learning_outcomes=["Understand the root cause", "Learn the global impact"],
            curiosity_level="High"
        )

        return strategy

