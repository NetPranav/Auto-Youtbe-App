from typing import Any
from common import logger
from database.models import Topic

class ResearchContextBuilder:
    """
    Collects and organizes supporting information available from the Research Engine.
    Creates a structured context document for downstream AI modules.
    """
    
    def build_context(self, topic: Topic) -> str:
        """
        Builds a text dossier based on the approved topic.
        """
        logger.info(f"Building research context for topic: {topic.title}")
        
        context = (
            f"Topic: {topic.title}\n"
            f"Problem Definition: {topic.problem_definition}\n"
            f"Historical Comparison: {topic.historical_comparison}\n"
            f"Root Cause Analysis: {topic.root_cause_analysis}\n"
            f"Supporting Evidence: {topic.supporting_evidence}\n"
            f"Counterarguments: {topic.counterarguments}\n"
            f"Global Comparison: {topic.global_comparison}\n"
            f"Practical Solutions: {topic.practical_solutions}\n"
        )
        
        return context
