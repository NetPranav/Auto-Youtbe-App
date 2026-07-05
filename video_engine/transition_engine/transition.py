import random
from video_engine.models.state import Timeline
from common.logger import get_logger

logger = get_logger(__name__)

class TransitionEngine:
    def apply_transitions(self, timeline: Timeline) -> Timeline:
        logger.info("[TransitionEngine] Calculating transitions...")
        
        visual_clips = timeline.get_clips_by_type("VISUAL")
        if not visual_clips:
            return timeline
            
        transitions = ["fade", "cut"]
        
        for i in range(len(visual_clips) - 1):
            current_clip = visual_clips[i]
            next_clip = visual_clips[i+1]
            
            # Avoid altering mathematical duration to maintain audio sync.
            # So we use 'fade' out on current and 'fade' in on next instead of xfade,
            # or just 'cut' (no transition).
            
            t_type = random.choice(transitions)
            if t_type == "fade":
                current_clip.transition_out = "fade"
                next_clip.transition_in = "fade"
            else:
                current_clip.transition_out = "cut"
                next_clip.transition_in = "cut"
                
        return timeline
