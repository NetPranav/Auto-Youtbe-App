from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class SubtitleWord(BaseModel):
    text: str
    start_time: float
    end_time: float

class SubtitleSegment(BaseModel):
    text: str
    start_time: float
    end_time: float
    words: List[SubtitleWord] = []
    
class TimelineClip(BaseModel):
    id: str
    scene_id: Optional[str] = None
    clip_type: str # VISUAL, AUDIO, SUBTITLE
    asset_path: str
    start_time: float
    end_time: float
    layer: int = 0
    duration: float = 0.0
    properties_json: Dict[str, Any] = Field(default_factory=dict)
    
    # Visual specific
    motion_type: Optional[str] = None
    motion_intensity: float = 1.0
    transition_in: Optional[str] = None
    transition_out: Optional[str] = None
    
    # Subtitle specific
    segments: List[SubtitleSegment] = []
    
    # Audio specific
    volume: float = 1.0
    fade_in: float = 0.0
    fade_out: float = 0.0

class Timeline(BaseModel):
    project_id: str
    clips: List[TimelineClip] = []
    total_duration: float = 0.0
    resolution: str = "1080x1920"
    fps: int = 30
    
    def get_clips_by_type(self, clip_type: str) -> List[TimelineClip]:
        return [c for c in self.clips if c.clip_type == clip_type]
