from pydantic import BaseModel
from typing import List, Optional

class ContentStrategy(BaseModel):
    target_audience: str
    tone: str
    video_length_minutes: int
    objective: str
    key_learning_outcomes: List[str]
    curiosity_level: str

class HookData(BaseModel):
    text: str
    score: float

class SceneData(BaseModel):
    scene_number: int
    start_time: str
    end_time: str
    narration_text: str
    visual_description: str
    animation_suggestions: str
    asset_type_required: str # IMAGE, VIDEO, NONE
    transition_suggestion: str
    camera_movement: str
    subtitle_segment: str

class QualityScores(BaseModel):
    fact_score: float = 0.0
    retention_score: float = 0.0
    script_quality_score: float = 0.0
    feedback_notes: List[str] = []

class ContentPackageData(BaseModel):
    """
    In-memory representation of the final package.
    """
    topic_id: str
    strategy: Optional[ContentStrategy] = None
    winning_hook: Optional[HookData] = None
    outline: Optional[List[str]] = None
    final_script: Optional[str] = None
    scene_timeline: List[SceneData] = []
    scores: Optional[QualityScores] = None
