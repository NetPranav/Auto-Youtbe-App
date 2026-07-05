from video_engine.models.state import Timeline
from common.logger import get_logger

logger = get_logger(__name__)

class QualityValidator:
    def validate(self, timeline: Timeline) -> bool:
        logger.info("[QualityValidator] Validating timeline integrity before render...")
        
        if timeline.total_duration <= 0:
            logger.error("Timeline has 0 or negative duration.")
            return False
            
        visual_clips = timeline.get_clips_by_type("VISUAL")
        if not visual_clips:
            logger.error("Timeline has no visual clips.")
            return False
            
        # Check for gaps in visual timeline
        expected_time = 0.0
        for clip in sorted(visual_clips, key=lambda x: x.start_time):
            # Allow for very small floating point inaccuracies (1ms)
            if abs(clip.start_time - expected_time) > 0.01:
                logger.error(f"Timeline gap detected at {expected_time}s. Next clip starts at {clip.start_time}s")
                return False
            expected_time = clip.end_time
            
        if abs(expected_time - timeline.total_duration) > 0.1:
            logger.error(f"Visual clips total time {expected_time} does not match timeline total duration {timeline.total_duration}")
            return False
            
        logger.info("[QualityValidator] Timeline passed quality checks!")
        return True
