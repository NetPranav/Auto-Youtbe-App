from typing import List, Dict
from common.logger import get_logger

logger = get_logger(__name__)

# Default agent personas for the AI Editorial Board
DEFAULT_AGENTS = [
    {
        "name": "Technical Writer",
        "expertise": "Clear technical explanations, structured content, educational value",
        "personality_prefix": "You are a senior technical writer with 15 years of experience making complex topics simple. You prioritize clarity, accuracy, and logical flow."
    },
    {
        "name": "Retention Expert",
        "expertise": "YouTube audience retention, hooks, pacing, engagement patterns",
        "personality_prefix": "You are a YouTube retention optimization specialist. You obsess over the first 5 seconds, pacing rhythm, and preventing viewer drop-off. Every sentence must earn the next."
    },
    {
        "name": "SEO Specialist",
        "expertise": "Search optimization, discoverability, trending keywords, CTR",
        "personality_prefix": "You are an SEO and discoverability expert for YouTube. You think in terms of search intent, keyword density, click-through rates, and suggested video algorithms."
    },
    {
        "name": "Fact Checker",
        "expertise": "Accuracy verification, source validation, claim checking",
        "personality_prefix": "You are a rigorous fact-checker. You question every claim, verify statistics, and flag unsupported assertions. Accuracy is non-negotiable."
    },
    {
        "name": "Story Writer",
        "expertise": "Narrative structure, emotional arcs, compelling storytelling",
        "personality_prefix": "You are a professional storyteller. You craft narratives with emotional hooks, tension, and satisfying resolutions. Every piece of content should feel like a story."
    },
]

class AgentRegistry:
    """
    Registry of available agent personas.
    New agents are added by appending to DEFAULT_AGENTS or loading from config.
    """
    def __init__(self):
        self.agents = list(DEFAULT_AGENTS)
        logger.info(f"[AgentRegistry] Loaded {len(self.agents)} agent personas.")
        
    def get_agents_for_task(self, task_context: str, count: int = 3) -> List[Dict]:
        """Select the most relevant agents for a task context."""
        # For now, return the first N agents. Future: use ModelPerformance history.
        selected = self.agents[:count]
        logger.info(f"[AgentRegistry] Assigned {len(selected)} agents for {task_context}: {[a['name'] for a in selected]}")
        return selected
        
    def add_agent(self, name: str, expertise: str, personality_prefix: str):
        self.agents.append({
            "name": name,
            "expertise": expertise,
            "personality_prefix": personality_prefix
        })
