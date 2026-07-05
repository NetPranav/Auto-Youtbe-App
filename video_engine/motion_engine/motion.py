import random
from video_engine.models.state import Timeline
from common.logger import get_logger

logger = get_logger(__name__)

class MotionEngine:
    def apply_motion(self, timeline: Timeline) -> Timeline:
        logger.info("[MotionEngine] Applying motion dynamics to visual clips...")
        
        motions = ["zoom_in", "zoom_out", "pan_left", "pan_right"]
        
        visual_clips = timeline.get_clips_by_type("VISUAL")
        
        # Don't repeat the exact same motion twice in a row if possible
        last_motion = None
        for clip in visual_clips:
            # Randomly select a motion
            available_motions = [m for m in motions if m != last_motion]
            if not available_motions:
                available_motions = motions
                
            selected_motion = random.choice(available_motions)
            
            clip.motion_type = selected_motion
            clip.motion_intensity = random.uniform(1.05, 1.15) # zoom scale limit
            
            last_motion = selected_motion
            logger.debug(f"Assigned motion {selected_motion} to scene {clip.scene_id}")
            
        return timeline
