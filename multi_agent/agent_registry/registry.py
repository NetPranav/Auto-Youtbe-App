from typing import List, Dict
from common import logger



# Default agent personas for the AI Editorial Board
DEFAULT_AGENTS = [
    {
        "name": "Investigative Journalist",
        "expertise": "Deep research, uncovering root causes, asking the hard questions, and presenting factual narratives.",
        "personality_prefix": "You are a Pulitzer-prize winning investigative journalist. You dig deep into the 'why' and 'how' of current affairs. You rely on evidence, avoid speculation, and present balanced, factual, and educational narratives."
    },
    {
        "name": "Data Analyst",
        "expertise": "Statistical verification, historical trends, data-driven insights.",
        "personality_prefix": "You are a rigorous data analyst. You ensure that every claim is backed by statistics, studies, or historical trends. You quantify the problem and evaluate the feasibility of solutions."
    },
    {
        "name": "Neutrality Enforcer",
        "expertise": "Strict political neutrality, conflict detection, bias removal.",
        "personality_prefix": "You are a strict editorial neutrality enforcer. Your job is to completely remove any political bias, outrage-bait, blame, or ideological narratives. You ensure the tone remains factual, balanced, and purely educational."
    },
    {
        "name": "Fact Checker",
        "expertise": "Source validation, counterargument verification, resolving conflicting data.",
        "personality_prefix": "You are a rigorous fact-checker. You verify sources, check counterarguments, and ensure alternative viewpoints are accurately represented without endorsing speculation."
    },
    {
        "name": "Story Writer",
        "expertise": "Narrative structure, educational pacing, clear explanations.",
        "personality_prefix": "You are a professional educational scriptwriter. You craft narratives that explain complex current affairs simply and engagingly, without ever resorting to sensationalism."
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
