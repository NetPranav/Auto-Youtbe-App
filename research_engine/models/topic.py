from pydantic import BaseModel
from typing import List, Optional

class TopicCandidate(BaseModel):
    """
    Extracted Topic data structure before it is scored.
    """
    title: str
    problem_definition: str
    historical_comparison: str
    root_cause_analysis: str
    supporting_evidence: str
    counterarguments: str
    global_comparison: str
    practical_solutions: str

class TopicScoreData(BaseModel):
    """
    Scores assigned to a TopicCandidate.
    """
    evidence_strength: float = 0.0
    source_reliability: float = 0.0
    historical_coverage: float = 0.0
    expert_consensus: float = 0.0
    conflict_risk: float = 0.0
    educational_value: float = 0.0
    practical_relevance: float = 0.0
    total_score: float = 0.0
    confidence_score: float = 0.0
    
class RankedTopic(BaseModel):
    """
    A topic paired with its computed score and DB id.
    """
    topic_id: str
    candidate: TopicCandidate
    score: TopicScoreData
