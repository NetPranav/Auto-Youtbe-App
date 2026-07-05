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
            f"Main Technology: {topic.main_technology}\n"
            f"Secondary Technologies: {', '.join(topic.secondary_technologies) if topic.secondary_technologies else 'None'}\n"
            f"Industry: {topic.industry}\n"
            f"Importance: {topic.importance}\n"
            f"Audience: {topic.estimated_audience}\n\n"
            f"Description:\n{topic.description}\n"
        )
        
        return context
