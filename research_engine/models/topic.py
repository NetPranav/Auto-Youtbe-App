from pydantic import BaseModel
from typing import List, Optional

class TopicCandidate(BaseModel):
    """
    Extracted Topic data structure before it is scored.
    """
    title: str
    main_technology: str
    secondary_technologies: List[str] = []
    industry: Optional[str] = None
    importance: str = "Minor"  # Breaking, Major, Minor
    estimated_audience: str = "Niche" # Mass, Broad, Niche
    description: str

class TopicScoreData(BaseModel):
    """
    Scores assigned to a TopicCandidate.
    """
    novelty: float = 0.0
    audience_size: float = 0.0
    educational_value: float = 0.0
    search_interest: float = 0.0
    competition: float = 0.0
    recency: float = 0.0
    total_score: float = 0.0
    
class RankedTopic(BaseModel):
    """
    A topic paired with its computed score and DB id.
    """
    topic_id: str
    candidate: TopicCandidate
    score: TopicScoreData
