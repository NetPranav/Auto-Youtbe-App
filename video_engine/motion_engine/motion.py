import random
from video_engine.models.state import Timeline
from common import logger



class MotionEngine:
    """
    Assigns cinematic Ken Burns motion to visual clips.
    Uses complementary sequential patterns to avoid repetition,
    and scales intensity based on clip duration.
    """

    # Pre-defined complementary motion sequences.
    # Each sequence is designed so consecutive clips feel visually balanced.
    MOTION_SEQUENCES = [
        ["zoom_in", "pan_right", "zoom_out", "pan_left"],
        ["pan_left", "zoom_in", "pan_right", "zoom_out"],
        ["zoom_in", "static", "pan_left", "zoom_out", "pan_right"],
        ["pan_right", "zoom_out", "static", "zoom_in", "pan_left"],
    ]

    def apply_motion(self, timeline: Timeline) -> Timeline:
        logger.info("[MotionEngine] Applying motion dynamics to visual clips...")

        visual_clips = timeline.get_clips_by_type("VISUAL")

        if not visual_clips:
            return timeline

        # Pick a random sequence to keep things fresh across runs
        sequence = random.choice(self.MOTION_SEQUENCES)
        seq_len = len(sequence)

        for i, clip in enumerate(visual_clips):
            selected_motion = sequence[i % seq_len]
            clip.motion_type = selected_motion

            # Scale intensity based on clip duration:
            #   Short clips (< 3s)  → subtle motion (1.03–1.06)
            #   Medium clips (3-6s) → moderate motion (1.06–1.12)
            #   Long clips (> 6s)   → dramatic motion (1.10–1.18)
            if selected_motion == "static":
                clip.motion_intensity = 1.0
            elif clip.duration < 3.0:
                clip.motion_intensity = random.uniform(1.03, 1.06)
            elif clip.duration < 6.0:
                clip.motion_intensity = random.uniform(1.06, 1.12)
            else:
                clip.motion_intensity = random.uniform(1.10, 1.18)

            logger.debug(
                f"Assigned motion {selected_motion} (intensity {clip.motion_intensity:.2f}) "
                f"to scene {clip.scene_id}"
            )

        return timeline

